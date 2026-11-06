"""Executable SQLite contracts; synthetic scratch data only, never a real vault."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/setup-learning/scripts'
SCRATCH = '/tmp/opencode' if Path('/tmp/opencode').is_dir() else None
sys.path.insert(0, str(SCRIPTS))
import memory as m
import legacy


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.root = Path(self.scratch.name) / 'learning'
        m.initialize(self.root)
        self.db = m.connect(self.root)
        self.counter = 0

    def tearDown(self):
        self.db.close()
        self.scratch.cleanup()

    def write(self, records, **extra):
        self.counter += 1
        return m.apply(self.db, dict(operation_id='op'+str(self.counter), records=records, **extra))

    def record(self, table, **data):
        return {'table': table, 'data': data}

    def capability(self, identity='c', **data):
        self.write([self.record('capabilities', id=identity, title=data.pop('title', identity), **data)])

    def state(self, identity='c'):
        return dict(self.db.execute('SELECT * FROM capability_state WHERE id=?', (identity,)).fetchone())

    def activity(self, identity, purpose='transfer', capability='c', **data):
        return self.record('units', id=identity, capability_id=capability, purpose=purpose,
                           version='1', prompt='Predict '+identity, answer='SECRET-'+identity,
                           verified=1, verification='Executed synthetic fixture assertion', **data)

    def response(self, unit, identity=None, score=1, today='2026-11-06', **flags):
        identity = identity or unit+'-attempt'
        attempt_flags = {k: flags.pop(k, False) for k in ('hinted', 'revealed', 'skipped')}
        grade_flags = {k: flags.pop(k, True) for k in ('independent', 'complete', 'verified')}
        grade_flags['disputed'] = flags.pop('disputed', False)
        return [
            self.record('attempts', id=identity, unit_id=unit, response='  My answer π\n',
                        created_at=today+'T12:00:00+00:00', **attempt_flags),
            self.record('assessments', id=identity+'-grade', attempt_id=identity, score=score,
                        feedback='fixture feedback', evaluator='synthetic-test', created_at=today+'T12:01:00+00:00', **grade_flags, **flags)
        ]

    def transfer(self, identity='transfer', today='2026-11-06'):
        self.write([self.activity(identity), *self.response(identity, today=today)], today=today)

    def test_initialize_stdlib_runtime_and_no_markdown_bookkeeping(self):
        self.assertEqual(set(p.name for p in self.root.iterdir()), {'AGENTS.md', 'CLAUDE.md', '.learning'})
        code = subprocess.run([sys.executable, '-S', str(self.root/'.learning/memory.py'), '--root', str(self.root), 'context'], capture_output=True, text=True)
        self.assertEqual(code.returncode, 0, code.stderr)
        self.assertEqual(json.loads(code.stdout)['revision'], 0)
        with self.assertRaises(ValueError):
            m.initialize(self.root)

    def test_turn_round_trip_one_save_replay_and_resume_no_keys(self):
        first = dict(operation_id='first', expected_revision=0,
                     capability={'id': 'c', 'title': 'Count', 'kind': 'procedure'},
                     explanation='One small explanation.',
                     unit={'prompt': 'How many?', 'answer': 'SECRET', 'verification': 'Counted three objects.'},
                     session={'next_action': 'Wait for the answer.'})
        saved = m.turn(self.db, first)
        unit = saved['saved']['units'][0]
        self.assertEqual(self.state()['status'], 'learning')
        self.assertEqual(m.turn(self.db, first), saved)
        self.db.close()
        self.db = m.connect(self.root)
        context = m.context(self.db)
        self.assertEqual(context['active_prompt'][0]['id'], unit)
        self.assertNotIn('SECRET', json.dumps(context))
        self.assertNotIn('answer', m.get(self.db, 'units', unit)[0])
        self.assertEqual(m.get(self.db, 'units', unit, keys=True)[0]['answer'], 'SECRET')
        answer = dict(operation_id='answer', expected_revision=saved['revision'],
                      attempt={'unit_id': unit, 'response': '3', 'hinted': False, 'revealed': False, 'skipped': False},
                      assessment={'score': 1, 'independent': True, 'complete': True, 'verified': True,
                                  'disputed': False, 'feedback': 'Correct.', 'evaluator': 'fixture'},
                      unit={'capability_id': 'c', 'prompt': 'New surface?', 'answer': 'Yes', 'verification': 'Checked'},
                      explanation='Next small step.')
        result = m.turn(self.db, answer)
        self.assertEqual(result['revision'], 2)
        self.assertEqual(m.turn(self.db, answer), result)
        self.assertEqual(self.db.execute('SELECT count(*) FROM attempts').fetchone()[0], 1)
        self.assertFalse((self.root/'My Summary.md').exists())
        self.assertEqual(list(self.root.glob('Lessons/*')), [])

    def test_batch_rollback_foreign_key_conflict_and_stale_revision(self):
        self.capability()
        before = m.revision(self.db)
        with self.assertRaises(sqlite3.IntegrityError):
            self.write([self.record('notes', id='n', title='N', body='Must roll back'), self.activity('bad', capability='unknown')])
        self.assertEqual(self.db.execute('SELECT count(*) FROM notes').fetchone()[0], 0)
        self.assertEqual(m.revision(self.db), before)
        payload = {'operation_id': 'same', 'records': []}
        m.apply(self.db, payload)
        with self.assertRaises(ValueError):
            m.apply(self.db, dict(payload, today='2026-11-01'))
        with self.assertRaises(ValueError):
            self.write([], expected_revision=0)

    def test_two_writers_stale_revision_rolls_back(self):
        other = m.connect(self.root)
        try:
            self.capability()
            with self.assertRaises(ValueError):
                m.apply(other, {'operation_id': 'concurrent', 'expected_revision': 0,
                               'records': [self.record('capabilities', id='other', title='Other')]})
            self.assertFalse(m.get(other, 'capabilities', 'other'))
        finally:
            other.close()

    def test_process_exit_mid_transaction_leaves_no_partial_write(self):
        code = '''import os,sys
sys.path.insert(0, sys.argv[1])
import memory
db=memory.connect(sys.argv[2])
db.execute('BEGIN IMMEDIATE')
db.execute("INSERT INTO capabilities(id,title) VALUES ('crashed','Must not survive')")
os._exit(23)
'''
        result = subprocess.run([sys.executable, '-c', code, str(SCRIPTS), str(self.root)], capture_output=True)
        self.assertEqual(result.returncode, 23)
        self.assertFalse(m.get(self.db, 'capabilities', 'crashed'))
        self.assertEqual(m.revision(self.db), 0)

    def test_no_direct_progress_updates_and_append_only(self):
        self.capability()
        with self.assertRaises(ValueError):
            self.write([self.record('capabilities', id='c', status='solid')])
        self.write([self.activity('u')])
        with self.assertRaises(ValueError):
            self.write([self.record('units', id='u', prompt='changed')])
        with self.assertRaises(ValueError):
            self.write([self.record('units', id='bad', capability_id='c', purpose='practice', version='1', prompt='?', verified=True)])

    def test_placement_is_not_retention_or_longer_schedule(self):
        self.capability()
        self.write([self.activity('p1', purpose='placement'), *self.response('p1')], today='2026-11-06')
        self.assertEqual(self.state()['status'], 'planned')
        self.write([self.activity('p2', purpose='placement'), *self.response('p2')], today='2026-11-06')
        self.assertEqual((self.state()['status'], self.state()['interval'], self.state()['retention']), ('review', 3, 'unmeasured'))
        self.db.execute("UPDATE capabilities SET status='solid',interval=90,next_review='2027-02-01' WHERE id='c'")
        self.write([self.activity('p3', purpose='placement'), *self.response('p3')], today='2026-11-06')
        self.assertEqual(self.state()['interval'], 90)

    def test_transfer_updates_outcome_atomically_then_review_and_repair(self):
        self.capability()
        self.write([self.record('topics', id='t', title='T'), self.record('outcomes', id='o', topic_id='t', capability_id='c', description='Do the thing')])
        self.transfer()
        self.assertEqual(self.state()['next_review'], '2026-11-09')
        self.assertEqual(m.get(self.db, 'outcomes', 'o')[0]['met_on'], '2026-11-06')
        self.write([self.activity('r1', purpose='delayed'), *self.response('r1', today='2026-11-09')], today='2026-11-09')
        self.assertEqual((self.state()['status'], self.state()['interval'], self.state()['retention']), ('solid', 7, 'demonstrated'))
        self.write([self.activity('r2', purpose='delayed'), *self.response('r2', score=0, today='2026-11-16')], today='2026-11-16')
        self.db.close(); self.db = m.connect(self.root)
        self.assertEqual((self.state()['status'], self.state()['repair']), ('learning', 1))
        self.write([self.activity('practice', purpose='practice'), *self.response('practice')], today='2026-11-17')
        self.assertEqual(self.state()['repair'], 1)
        self.transfer('repair', '2026-11-17')
        self.assertEqual((self.state()['status'], self.state()['repair']), ('review', 0))

    def test_review_ladder_reaches_cap(self):
        self.capability()
        self.transfer()
        for n, day, expected in [('r1','2026-11-09',7), ('r2','2026-11-16',30), ('r3','2026-12-16',90), ('r4','2027-03-16',90)]:
            self.write([self.activity(n, purpose='delayed'), *self.response(n, today=day)], today=day)
            self.assertEqual(self.state()['interval'], expected)

    def test_supported_unverified_disputed_incomplete_and_early_review_do_not_promote(self):
        self.capability()
        for n, flags in enumerate([{'hinted': True}, {'revealed': True}, {'skipped': True}, {'independent': False}, {'complete': False}, {'verified': False}, {'disputed': True}]):
            name = 'u'+str(n)
            self.write([self.activity(name), *self.response(name, **flags)], today='2026-11-06')
            self.assertEqual(self.state()['status'], 'planned')
        self.transfer()
        self.write([self.activity('early', purpose='delayed'), *self.response('early', today='2026-11-07')], today='2026-11-09')
        self.assertEqual(self.state()['interval'], 3)

    def test_exposed_unit_cannot_become_independent_on_retry(self):
        self.capability()
        self.write([self.activity('u'), *self.response('u', identity='exposed', revealed=True)], today='2026-11-06')
        self.write(self.response('u', identity='retry'), today='2026-11-06')
        self.assertEqual(self.state()['status'], 'planned')
        self.transfer('fresh')
        self.assertEqual(self.state()['status'], 'review')

    def test_and_or_dependencies_cycle_escape_unknown_and_rename(self):
        for c in ('a','b','c'):
            self.capability(c)
        r = self.record
        self.write([r('prerequisite_groups', id='ag', capability_id='a'), r('prerequisite_members', id='ab', group_id='ag', prerequisite_id='b'),
                    r('prerequisite_members', id='ac', group_id='ag', prerequisite_id='c'),
                    r('prerequisite_groups', id='bg', capability_id='b'), r('prerequisite_members', id='ba', group_id='bg', prerequisite_id='a')])
        self.assertEqual(self.state('a')['map_class'], 'notyet')
        self.write([self.activity('ct', capability='c'), *self.response('ct')], today='2026-11-06')
        self.assertEqual(self.state('a')['map_class'], 'next')
        self.write([r('topics', id='topic', title='Topic'),
                    r('topic_capabilities', id='ta', topic_id='topic', capability_id='a'),
                    r('topic_capabilities', id='tb', topic_id='topic', capability_id='b')])
        frontier = m.context(self.db, topic='topic')['frontier']
        self.assertEqual([c['id'] for c in frontier], ['a'])
        self.write([r('capabilities', id='c', title='Renamed')])
        self.assertEqual(self.state('a')['map_class'], 'next')
        self.write([r('capabilities', id='c', archived=1)])
        self.assertEqual(self.state('a')['map_class'], 'notyet')
        with self.assertRaises(ValueError):
            self.write([r('prerequisite_groups', id='cg', capability_id='c'), r('prerequisite_members', id='ca', group_id='cg', prerequisite_id='a')])
        with self.assertRaises(sqlite3.IntegrityError):
            self.write([r('prerequisite_groups', id='unknown', capability_id='c'), r('prerequisite_members', id='cx', group_id='unknown', prerequisite_id='missing')])

    def test_active_prompt_cannot_be_replaced_without_attempt_or_skip(self):
        self.capability()
        self.write([self.activity('u'), self.activity('v'), self.record('sessions', id='s', active_unit_id='u', next_action='Wait')])
        with self.assertRaises(ValueError):
            self.write([self.record('sessions', id='s', active_unit_id='v')])
        self.write([self.record('attempts', id='skip', unit_id='u', response='', hinted=0, revealed=0, skipped=1), self.record('sessions', id='s', active_unit_id='v')])
        self.assertEqual(m.context(self.db)['active_prompt'][0]['id'], 'v')

    def test_partial_test_only_complete_capability_changes_and_coverage_locks(self):
        self.capability('a'); self.capability('b')
        self.db.execute("UPDATE capabilities SET status='review',interval=3,next_review='2026-11-06'")
        r = self.record
        self.write([r('tests', id='test', blueprint='One per capability'),
                    self.activity('a1', purpose='delayed', capability='a'), self.activity('b1', purpose='delayed', capability='b'),
                    r('test_items', id='i1', test_id='test', unit_id='a1', ordinal=1), r('test_items', id='i2', test_id='test', unit_id='b1', ordinal=2)])
        self.write(self.response('a1'), today='2026-11-06')
        self.assertEqual(self.state('a')['status'], 'review')
        with self.assertRaises(ValueError):
            self.write([self.activity('extra', purpose='delayed', capability='b'), r('test_items', id='extra', test_id='test', unit_id='extra', ordinal=3)])
        self.write([], today='2026-11-06', finalize_tests=['test'])
        self.assertEqual(self.state('a')['status'], 'solid')
        self.assertEqual(self.state('b')['status'], 'review')
        self.assertEqual(m.get(self.db, 'tests', 'test')[0]['closure'], 'partial')

    def test_verbatim_response_and_superseding_unapplied_grade(self):
        self.capability()
        self.write([self.activity('u', purpose='practice'), *self.response('u')])
        self.assertEqual(m.get(self.db, 'attempts', 'u-attempt')[0]['response'], '  My answer π\n')
        grade = self.response('u', identity='u-attempt')[1]['data']
        grade.update(id='corrected', supersedes='u-attempt-grade', score=0)
        self.write([self.record('assessments', **grade)])
        self.assertEqual(self.db.execute('SELECT id FROM current_assessments').fetchone()[0], 'corrected')
        self.transfer()
        grade = self.response('transfer')[1]['data']
        grade.update(id='invalid-regrade', supersedes='transfer-attempt-grade', score=0)
        with self.assertRaises(ValueError):
            self.write([self.record('assessments', **grade)])

    def test_summary_only_explicit_publication_and_no_automatic_refresh(self):
        self.capability()
        self.assertFalse((self.root/'My Summary.md').exists())
        payload = dict(id='summary', request='Summarize me', body='# My Summary\n\nDeveloping c. [capabilities:c]\n',
                       evidence_ids=['capabilities:c'], expected_revision=m.revision(self.db))
        m.save_summary(self.db, self.root, payload)
        original = (self.root/'My Summary.md').read_bytes()
        self.transfer()
        m.context(self.db)
        m.export_markdown(self.db, self.root, Path(self.scratch.name)/'export')
        self.assertEqual((self.root/'My Summary.md').read_bytes(), original)
        m.save_summary(self.db, self.root, payload)  # same-ID publication retry
        self.assertEqual(self.db.execute('SELECT count(*) FROM summary_snapshots').fetchone()[0], 1)
        changed = dict(payload, id='summary2', expected_revision=m.revision(self.db), body='# My Summary\n\nNow demonstrated.\n')
        m.save_summary(self.db, self.root, changed)
        self.assertEqual(self.db.execute('SELECT count(*) FROM summary_snapshots').fetchone()[0], 2)
        with self.assertRaises(ValueError):
            m.save_summary(self.db, self.root, payload)

    def test_summary_owner_edits_preserved_merge_hash_and_interrupted_publication(self):
        self.capability()
        path = self.root/'My Summary.md'
        path.write_text('# My Summary\n\nMy personal edit.\n')
        payload = dict(id='s', request='Summarize me', body='# My Summary\n\nMy personal edit. Developing c.\n', evidence_ids=['capabilities:c'], expected_revision=m.revision(self.db))
        with self.assertRaises(ValueError):
            m.save_summary(self.db, self.root, payload)
        payload['expected_file_hash'] = hashlib.sha256(path.read_bytes()).hexdigest()
        with patch.object(m, 'atomic_file', side_effect=OSError('simulated publication failure')):
            with self.assertRaises(OSError):
                m.save_summary(self.db, self.root, payload)
        self.assertEqual(self.db.execute('SELECT count(*) FROM summary_snapshots').fetchone()[0], 1)
        m.save_summary(self.db, self.root, payload)
        self.assertEqual(path.read_text(), payload['body'])

    def test_summary_stale_unknown_evidence_or_absent_request_refused(self):
        self.capability()
        payload = dict(id='s', request='Summarize me', body='# My Summary\n', evidence_ids=['capabilities:missing'], expected_revision=m.revision(self.db))
        with self.assertRaises(ValueError):
            m.save_summary(self.db, self.root, payload)
        payload.update(evidence_ids=['capabilities:c'], request='')
        with self.assertRaises(ValueError):
            m.save_summary(self.db, self.root, payload)
        payload.update(request='Summarize me', expected_revision=0)
        with self.assertRaises(ValueError):
            m.save_summary(self.db, self.root, payload)

    def test_export_no_keys_safe_names_new_target_only_and_backup(self):
        self.capability(title='../../Strange "title"')
        self.transfer()
        target = Path(self.scratch.name)/'export'
        m.export_markdown(self.db, self.root, target)
        lessons = list((target/'Lessons').glob('*.md'))
        self.assertEqual(len(lessons), 1)
        self.assertNotIn('SECRET', lessons[0].read_text())
        with self.assertRaises(ValueError):
            m.export_markdown(self.db, self.root, target)
        with_keys = Path(self.scratch.name)/'with-keys'
        m.export_markdown(self.db, self.root, with_keys, include_keys=True)
        self.assertIn('SECRET', next((with_keys/'Lessons').glob('*.md')).read_text())
        dest = Path(self.scratch.name)/'backup.sqlite3'
        m.backup(self.db, dest)
        db = sqlite3.connect(dest)
        self.assertEqual(db.execute('SELECT count(*) FROM capabilities').fetchone()[0], 1)
        db.close()

    def test_context_excerpts_and_literal_search(self):
        self.capability()
        self.write([self.record('notes', id='n', title='100%_literal', body='x'*200000, capability_id='c')])
        context = m.context(self.db, capability='c')
        self.assertLess(len(json.dumps(context)), 5000)
        self.assertEqual(len(m.search(self.db, '100%_literal')), 1)
        self.assertEqual(len(m.search(self.db, '100XXliteral')), 0)

    def test_legacy_keys_are_not_in_ordinary_context(self):
        self.capability()
        self.write([self.record('notes', id='legacy', title='Imported', body='SECRET legacy answer', kind='legacy', capability_id='c')])
        self.assertNotIn('SECRET', json.dumps(m.context(self.db, capability='c')))
        self.assertIn('SECRET', m.get(self.db, 'notes', 'legacy')[0]['body'])


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.source = Path(self.scratch.name)/'old'
        self.source.mkdir()
        self.dest = Path(self.scratch.name)/'new'
        (self.source/'Maps').mkdir(); (self.source/'Lessons').mkdir(); (self.source/'Sessions').mkdir()
        (self.source/'Maps/My map.md').write_text('## Goal\nRead a graph.\n')
        self.raw = (ROOT/'evals/fixtures/legacy-lesson.md').read_bytes().replace(b'\n', b'\r\n')
        (self.source/'Lessons/Original.md').write_bytes(self.raw)
        (self.source/'Sessions/Current.md').write_text('---\nsession_id: old-session\nactive_unit_id: old-unit\nprompt_reference: "[[Original#Cycle 1]]"\nclosure: paused\n---\n## Saved next action\nFinish the old prompt.\n')

    def tearDown(self):
        self.scratch.cleanup()

    def test_dry_run_byte_preservation_idempotence_and_resume(self):
        report = legacy.import_markdown(self.dest, self.source, dry_run=True)
        self.assertFalse(self.dest.exists())
        self.assertEqual(report['documents'], 3)
        m.initialize(self.dest)
        legacy.import_markdown(self.dest, self.source)
        db = m.connect(self.dest)
        try:
            cap = db.execute('SELECT * FROM capabilities').fetchone()
            self.assertEqual((cap['status'],cap['retention'],cap['repair']), ('learning','unmeasured',0))
            self.assertEqual(db.execute("SELECT raw FROM legacy_documents WHERE path='Lessons/Original.md'").fetchone()[0], self.raw)
            self.assertEqual((self.source/'Lessons/Original.md').read_bytes(), self.raw)
            self.assertIn('Resume the unanswered legacy prompt', m.context(db)['session'][0]['next_action'])
            self.assertIn('My personal note', m.search(db, 'personal note')[0]['excerpt'])
            first_id = cap['id']
        finally:
            db.close()
        self.assertTrue(legacy.import_markdown(self.dest, self.source)['already_imported'])
        db = m.connect(self.dest)
        self.assertEqual(db.execute('SELECT id FROM capabilities').fetchone()[0], first_id)
        db.close()
        (self.source/'Lessons/Original.md').write_bytes(self.raw+b'new content')
        with self.assertRaises(ValueError):
            legacy.import_markdown(self.dest, self.source)

    def test_unknown_ambiguous_duplicate_and_cycle_are_preflight_failures(self):
        lesson = self.source/'Lessons/Original.md'
        for text in ['---\nstatus: solid\nstatus: planned\n---\n',
                     '---\nprerequisites: ["[[Missing]]"]\n---\n',
                     '---\ncapability_id: a\nprerequisite_groups: [[a]]\n---\n']:
            lesson.write_text(text)
            with self.assertRaises(ValueError):
                legacy.import_markdown(self.dest, self.source, dry_run=True)
        lesson.write_text('---\nprerequisites: ["[[Base]]"]\n---\n')
        (self.source/'Lessons/a').mkdir(); (self.source/'Lessons/b').mkdir()
        for folder in ('a', 'b'):
            (self.source/f'Lessons/{folder}/Base.md').write_text('Base')
        with self.assertRaises(ValueError):
            legacy.import_markdown(self.dest, self.source, dry_run=True)

    def test_import_rolls_back_and_does_not_modify_rules(self):
        m.initialize(self.dest)
        before = (self.dest/'AGENTS.md').read_bytes()
        (self.source/'Lessons/Original.md').write_text('---\nstatus: invalid\n---\n')
        with self.assertRaises(sqlite3.IntegrityError):
            legacy.import_markdown(self.dest, self.source)
        db = m.connect(self.dest)
        self.assertEqual(db.execute('SELECT count(*) FROM topics').fetchone()[0], 0)
        db.close()
        self.assertEqual((self.dest/'AGENTS.md').read_bytes(), before)


class PackagingTests(unittest.TestCase):
    def test_independent_setup_archive_installs_working_runtime(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            scratch = Path(tmp)
            archive = scratch/'setup-learning.skill'
            skill = ROOT/'skills/setup-learning'
            with zipfile.ZipFile(archive, 'w') as output:
                for path in skill.rglob('*'):
                    if path.is_file() and '__pycache__' not in path.parts:
                        output.write(path, path.relative_to(skill.parent))
            with zipfile.ZipFile(archive) as source:
                source.extractall(scratch/'installed')
            script = scratch/'installed/setup-learning/scripts/memory.py'
            learning = scratch/'learning'
            result = subprocess.run([sys.executable, '-S', str(script), '--root', str(learning), 'init'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for command in ('context', 'check'):
                result = subprocess.run([sys.executable, '-S', str(learning/'.learning/memory.py'), '--root',str(learning),command], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((learning/'My Summary.md').exists())

    def test_activity_handoffs_and_summary_triggers(self):
        for name in ('clarify-goal','check-level','teach-me','test-me','understand-me'):
            self.assertIn('`make-activity`', (ROOT/'skills'/name/'SKILL.md').read_text())
        summary = (ROOT/'skills/summarize-me/SKILL.md').read_text()
        self.assertIn('Only run on an explicit owner request', summary)
        self.assertIn('No automatic refresh hooks', summary)
        for name in ('teach-me', 'test-me'):
            text = (ROOT/'skills'/name/'SKILL.md').read_text()
            self.assertNotIn('references/learner-state.md', text)
        self.assertIn('only for requested exploration', (ROOT/'skills/teach-me/SKILL.md').read_text())


if __name__ == '__main__':
    unittest.main()
