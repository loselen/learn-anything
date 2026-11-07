"""Audit regressions against the installed SQLite contract, not the legacy reducer."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import test_sqlite as fixtures

m = fixtures.m


class AuditRegressionTests(unittest.TestCase):
    def setUp(self):
        self.t = fixtures.MemoryTests()
        self.t.setUp()
        self.db = self.t.db

    def tearDown(self):
        self.t.tearDown()

    def turn(self, **payload):
        payload.setdefault('expected_revision', m.revision(self.db))
        return m.turn(self.db, payload)

    def test_repair_survives_placement_and_delayed_until_transfer(self):
        t = self.t
        t.capability(); t.transfer()
        t.write([t.activity('failed', purpose='delayed'), *t.response('failed', score=0, today='2026-11-09')], today='2026-11-09')
        schedule = t.state()['next_review']
        for unit in ('p1', 'p2'):
            t.write([t.activity(unit, purpose='placement'), *t.response(unit, today='2026-11-10')], today='2026-11-10')
        self.assertEqual((t.state()['status'], t.state()['repair'], t.state()['next_review']), ('learning', 1, schedule))
        t.write([t.activity('retry', purpose='delayed'), *t.response('retry', today='2026-11-13')], today='2026-11-13')
        self.assertEqual((t.state()['status'], t.state()['repair']), ('learning', 1))
        t.transfer('fresh-transfer', today='2026-11-13')
        self.assertEqual((t.state()['status'], t.state()['repair']), ('review', 0))

    def test_hint_only_turn_keeps_prompt_and_blocks_replacement(self):
        t = self.t
        t.capability()
        t.write([t.activity('u', purpose='practice'), t.activity('next', purpose='practice'),
                 t.record('sessions', id='s', active_unit_id='u')])
        saved = self.turn(operation_id='hint', attempt=dict(unit_id='u', response='', hinted=True, revealed=False, skipped=False))
        self.assertEqual(m.context(self.db)['active_prompt'][0]['id'], 'u')
        self.assertEqual(m.get(self.db, 'attempts', saved['saved']['attempts'][0])[0]['session_id'], 's')
        with self.assertRaisesRegex(ValueError, 'unanswered'):
            t.write([t.record('sessions', id='s', active_unit_id='next')])
        self.turn(operation_id='skip', attempt=dict(unit_id='u', response='', hinted=True, revealed=False, skipped=True))
        t.write([t.record('sessions', id='s', active_unit_id='next')])
        self.assertEqual(m.context(self.db)['active_prompt'][0]['id'], 'next')

    def test_freshness_blocks_repeated_review_unit(self):
        t = self.t
        t.capability(); t.transfer()
        t.write([t.activity('r', purpose='delayed'), *t.response('r', identity='first', today='2026-11-09')], today='2026-11-09')
        before = t.state()
        t.write(t.response('r', identity='repeat', today='2026-11-16'), today='2026-11-16')
        self.assertEqual(t.state(), before)
        evidence = {r['id']: r for r in m.summary_context(self.db, t.root)['evidence']}
        self.assertTrue(evidence['repeat-grade']['unit_reused'])
        t.write([t.activity('fresh', purpose='delayed'), *t.response('fresh', today='2026-11-16')], today='2026-11-16')
        self.assertEqual(t.state()['interval'], 30)

    def declare_recheck(self, blueprint=None):
        t = self.t
        t.capability(); t.transfer()
        t.write([t.record('tests', id='test', blueprint=blueprint or {'description': 'Review', 'rechecks': {'retry': 'q'}}),
                 t.activity('q', purpose='delayed'), t.activity('retry', purpose='delayed'),
                 t.record('test_items', id='i1', test_id='test', unit_id='q', ordinal=1),
                 t.record('test_items', id='i2', test_id='test', unit_id='retry', ordinal=2)])

    def test_declared_successful_slip_recheck_passes_and_is_applied_once(self):
        self.declare_recheck()
        t = self.t
        t.write(t.response('q', score=.5, failure_type='slip', today='2026-11-09'), today='2026-11-09')
        t.write(t.response('retry', today='2026-11-09'), today='2026-11-09', finalize_tests=['test'])
        self.assertEqual((t.state()['status'], t.state()['repair'], t.state()['interval']), ('solid', 0, 7))
        t.write([], today='2026-11-09', finalize_tests=['test'])
        self.assertEqual(t.state()['interval'], 7)
        correction = t.response('q')[1]['data']
        correction.update(id='correction', supersedes='q-attempt-grade', score=1)
        with self.assertRaisesRegex(ValueError, 'already applied'):
            t.write([t.record('assessments', **correction)])

    def test_unused_conditional_recheck_does_not_block_pass(self):
        self.declare_recheck()
        t = self.t
        t.write(t.response('q', today='2026-11-09'), today='2026-11-09', finalize_tests=['test'])
        self.assertEqual(t.state()['status'], 'solid')
        self.assertEqual(m.get(self.db, 'tests', 'test')[0]['closure'], 'closed')

    def test_supported_slip_recheck_leaves_schedule_unchanged(self):
        self.declare_recheck()
        t = self.t
        before = t.state()
        t.write(t.response('q', score=0, failure_type='slip', today='2026-11-09'), today='2026-11-09')
        t.write(t.response('retry', hinted=True, today='2026-11-09'), today='2026-11-09', finalize_tests=['test'])
        self.assertEqual(t.state(), before)
        self.assertEqual(m.get(self.db, 'tests', 'test')[0]['closure'], 'partial')

    def test_non_slip_failure_cannot_be_erased_by_recheck(self):
        self.declare_recheck()
        t = self.t
        t.write(t.response('q', score=0, failure_type='bug', today='2026-11-09'), today='2026-11-09')
        t.write(t.response('retry', today='2026-11-09'), today='2026-11-09', finalize_tests=['test'])
        self.assertEqual((t.state()['status'], t.state()['repair']), ('learning', 1))

    def test_recheck_answered_before_original_does_not_resolve_slip(self):
        self.declare_recheck()
        t = self.t
        t.write(t.response('retry', today='2026-11-09'), today='2026-11-09')
        t.write(t.response('q', score=0, failure_type='slip', today='2026-11-09'), today='2026-11-09', finalize_tests=['test'])
        self.assertEqual((t.state()['status'], t.state()['repair']), ('learning', 1))

    def test_slip_exception_cannot_replace_two_successful_placement_items(self):
        t = self.t
        t.capability()
        with self.assertRaisesRegex(ValueError, 'recheck'):
            t.write([t.record('tests', id='placement', blueprint={'rechecks': {'retry': 'q'}}),
                     t.activity('q', purpose='placement'), t.activity('retry', purpose='placement'),
                     t.record('test_items', id='i1', test_id='placement', unit_id='q', ordinal=1),
                     t.record('test_items', id='i2', test_id='placement', unit_id='retry', ordinal=2)])
        self.assertEqual(t.state()['placement'], 'unknown')

    def test_latest_unassessed_response_blocks_finalization(self):
        self.declare_recheck()
        t = self.t
        before = t.state()
        t.write(t.response('q', today='2026-11-09'), today='2026-11-09')
        t.write([t.record('attempts', id='unmarked', unit_id='q', response='A revision', hinted=False, revealed=False, skipped=False)],
                today='2026-11-09', finalize_tests=['test'])
        self.assertEqual(t.state(), before)
        self.assertEqual(m.get(self.db, 'tests', 'test')[0]['closure'], 'partial')

    def test_invalid_or_retroactive_recheck_blueprint_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'recheck'):
            self.declare_recheck({'rechecks': {'q': 'retry'}})
        self.assertFalse(m.get(self.db, 'tests', 'test'))
        self.declare_recheck()
        self.t.write(self.t.response('q', today='2026-11-09'), today='2026-11-09')
        with self.assertRaisesRegex(ValueError, 'append-only'):
            self.t.write([self.t.record('tests', id='test', blueprint={'rechecks': {}})])

    def test_partial_coverage_in_one_purpose_blocks_entire_capability(self):
        t = self.t
        t.capability(); t.transfer()
        t.write([t.record('tests', id='test', blueprint='Mixed scope'),
                 t.activity('review', purpose='delayed'), t.activity('practice', purpose='practice'),
                 t.record('test_items', id='i1', test_id='test', unit_id='review', ordinal=1),
                 t.record('test_items', id='i2', test_id='test', unit_id='practice', ordinal=2)])
        before = t.state()
        t.write(t.response('review', today='2026-11-09'), today='2026-11-09', finalize_tests=['test'])
        self.assertEqual(t.state(), before)

    def test_explicit_topic_and_capability_queries_preserve_scope_and_active_reference(self):
        t = self.t
        t.capability('a'); t.capability('b')
        t.write([t.record('topics', id='topic', title='Other topic'),
                 t.record('topic_capabilities', id='tb', topic_id='topic', capability_id='b'),
                 t.activity('active', purpose='practice', capability='a'),
                 t.record('sessions', id='s', active_unit_id='active')])
        context = m.context(self.db, topic='topic')
        self.assertEqual(context['topic'][0]['id'], 'topic')
        self.assertEqual(context['active_prompt'][0]['id'], 'active')
        self.assertEqual(context['frontier'][0]['id'], 'b')
        self.assertEqual(m.context(self.db, capability='b')['capability'][0]['id'], 'b')

    def test_notes_can_be_archived_without_editing_content_or_time(self):
        t = self.t
        t.capability()
        t.write([t.record('notes', id='n', title='Owner words', body='  verbatim\n', capability_id='c', kind='own_words')])
        original = m.get(self.db, 'notes', 'n')[0]
        t.write([t.record('notes', id='n', archived=1)])
        archived = m.get(self.db, 'notes', 'n')[0]
        self.assertEqual(archived, dict(original, archived=1))
        self.assertEqual(m.context(self.db, capability='c')['notes'], [])
        with self.assertRaisesRegex(ValueError, 'append-only'):
            t.write([t.record('notes', id='n', body='Changed')])
        t.write([t.record('notes', id='n', archived=0)])
        self.assertEqual(m.get(self.db, 'notes', 'n')[0], original)

    def test_new_session_is_linked_to_first_attempt_in_same_turn(self):
        t = self.t
        t.capability(); t.write([t.activity('u', purpose='practice')])
        result = self.turn(operation_id='answer', attempt=dict(unit_id='u', response='3', hinted=False, revealed=False, skipped=False))
        attempt = m.get(self.db, 'attempts', result['saved']['attempts'][0])[0]
        self.assertEqual(attempt['session_id'], result['saved']['sessions'][0])
        self.assertEqual(len(result['saved']['sessions']), 1)

    def test_revision_is_required_and_identical_retries_still_work(self):
        for command in (m.apply, m.turn):
            with self.assertRaisesRegex(ValueError, 'expected_revision'):
                command(self.db, {'operation_id': 'missing'})
            payload = {'operation_id': command.__name__, 'expected_revision': m.revision(self.db)}
            result = command(self.db, payload)
            self.assertEqual(command(self.db, payload), result)

    def test_summary_can_cite_supplied_session_evidence(self):
        t = self.t
        t.write([t.record('sessions', id='s', next_action='Continue counting', closure='paused')])
        self.assertEqual(m.summary_context(self.db, t.root)['sessions'][0]['id'], 's')
        result = m.save_summary(self.db, t.root, dict(id='summary', request='Summarize me',
            body='# My Summary\n\nPaused counting. [sessions:s]\n', evidence_ids=['sessions:s'], expected_revision=m.revision(self.db)))
        self.assertEqual(result['snapshot_id'], 'summary')

    def test_rename_does_not_revalidate_whole_graph(self):
        self.t.capability()
        with patch.object(m, 'check_graph', side_effect=AssertionError('unnecessary graph scan')):
            self.t.write([self.t.record('capabilities', id='c', title='Renamed')])

    def test_optimize_adds_index_to_existing_database_without_revision_change(self):
        self.db.execute('DROP INDEX evidence_capability')
        before = m.revision(self.db)
        m.optimize(self.db)
        plan = ' '.join(str(tuple(r)) for r in self.db.execute("EXPLAIN QUERY PLAN SELECT assessment_ids FROM applied_evidence WHERE capability_id='c'"))
        self.assertIn('evidence_capability', plan)
        self.assertEqual(m.revision(self.db), before)

    def test_evidence_ids_are_exact_json_values_not_substrings_or_like_patterns(self):
        self.t.capability()
        self.db.execute('INSERT INTO applied_evidence VALUES (?,?,?,?,?)',
                        ('history', 'c', 'delayed', m.canonical(['prefix"foo', 'a_1', 'a%2']), '2026-11-09'))
        self.assertTrue(m.evidence_used(self.db, 'c', ['prefix"foo']))
        for identity in ('foo', 'aX1', 'aZZ2'):
            self.assertFalse(m.evidence_used(self.db, 'c', [identity]))

    def test_benchmark_exercises_actual_transitions_and_next_cycle_writes(self):
        spec = importlib.util.spec_from_file_location('benchmark_memory', fixtures.ROOT/'evals/benchmark_memory.py')
        benchmark = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(benchmark)
        result = benchmark.run(capabilities=4, units_per_capability=2, samples=3)
        for purpose in ('transfer', 'delayed'):
            self.assertEqual(result['timings'][purpose+'_answer_with_next_cycle']['capability_updates'], 3)
        self.assertIn('new_capability_first_turn_with_graph_validation', result['timings'])

    def test_export_query_count_does_not_grow_per_unit(self):
        t = self.t
        t.capability()
        def query_count(name):
            queries = []
            self.db.set_trace_callback(queries.append)
            try:
                m.export_markdown(self.db, t.root, t.root.parent/name)
            finally:
                self.db.set_trace_callback(None)
            return sum(q.lstrip().upper().startswith('SELECT') for q in queries)
        before = query_count('small')
        for n in range(10):
            t.write([t.activity('u'+str(n), purpose='practice'), *t.response('u'+str(n))])
        self.assertEqual(query_count('larger'), before)


class InitializationRegressionTests(unittest.TestCase):
    def test_process_exit_during_initialization_can_be_resumed(self):
        code = '''import os,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import memory
original=memory.atomic_file
def interrupted(path,*args,**kwargs):
    original(path,*args,**kwargs)
    if Path(path).name=='AGENTS.md':
        os._exit(23)
memory.atomic_file=interrupted
memory.initialize(sys.argv[2])
'''
        with tempfile.TemporaryDirectory(dir=fixtures.SCRATCH) as tmp:
            root = Path(tmp)/'root'
            result = subprocess.run([sys.executable, '-c', code, str(fixtures.SCRIPTS), str(root)], capture_output=True)
            self.assertEqual(result.returncode, 23, result.stderr)
            self.assertFalse(m.db_path(root).exists())
            self.assertTrue((root/'.learning/init.json').exists())
            m.initialize(root)
            db = m.connect(root)
            try:
                self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            finally:
                db.close()

    def test_dangling_database_symlink_is_refused_without_touching_target(self):
        with tempfile.TemporaryDirectory(dir=fixtures.SCRATCH) as tmp:
            root = Path(tmp)/'root'
            (root/'.learning').mkdir(parents=True)
            target = Path(tmp)/'external.sqlite3'
            (root/'.learning/memory.sqlite3').symlink_to(target)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                m.initialize(root)
            self.assertFalse(target.exists())

    def test_interrupted_file_installation_is_retryable_and_owner_edits_are_protected(self):
        with tempfile.TemporaryDirectory(dir=fixtures.SCRATCH) as tmp:
            root = Path(tmp)/'root'
            original = m.atomic_file
            def fail_on_claude(path, *args, **kwargs):
                if Path(path).name == 'CLAUDE.md':
                    raise OSError('simulated interruption')
                return original(path, *args, **kwargs)
            with patch.object(m, 'atomic_file', side_effect=fail_on_claude):
                with self.assertRaises(OSError):
                    m.initialize(root)
            self.assertFalse(m.db_path(root).exists())
            rules = root/'AGENTS.md'
            before = rules.read_bytes()
            rules.write_bytes(before+b'\nOwner edit\n')
            with self.assertRaisesRegex(ValueError, 'changed'):
                m.initialize(root)
            self.assertTrue(rules.read_bytes().endswith(b'Owner edit\n'))
            rules.write_bytes(before)
            m.initialize(root)
            db = m.connect(root)
            try:
                self.assertEqual(m.revision(db), 0)
            finally:
                db.close()
            self.assertFalse((root/'.learning/init.json').exists())


if __name__ == '__main__':
    unittest.main()
