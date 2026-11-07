"""SQLite-to-policy adapters preserve scope and exclude raw responses and keys."""
import importlib.util
import json
import subprocess
import sqlite3
import sys
import unittest

import test_sqlite as fixtures

SCRIPTS = fixtures.ROOT/'skills/explore-next/scripts'
sys.path.insert(0, str(SCRIPTS))
import snapshot
import personalize
spec = importlib.util.spec_from_file_location('policy_selection', SCRIPTS/'select.py')
selector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selector)
m = fixtures.m


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.t = fixtures.MemoryTests()
        self.t.setUp()
        self.db = self.t.db
        t = self.t
        t.capability()
        t.write([t.record('topics', id='topic', title='Counting'),
                 t.record('topic_capabilities', id='member', topic_id='topic', capability_id='c'),
                 t.activity('intro', purpose='practice', created_at='2026-11-01T12:00:00+00:00'),
                 t.record('cycles', id='cycle', capability_id='c', unit_id='intro', explanation='Count objects', created_at='2026-11-01T12:00:00+00:00')])

    def tearDown(self):
        self.t.tearDown()

    def config(self):
        return dict(today='2026-11-09', mode='review', allowed_topics=['topic'], goal_topic='topic',
            goal_capability_ids=['c'], budget_minutes=5, sustained_work=False, challenge='practice', taught_capability_ids=['c'],
            candidates=[dict(id='fresh', version='1', capability_id='c', title='Count another set', topic='topic',
                purpose='delayed', source='due_review', modes=['review'], effort_minutes=2, challenge='intro',
                verification=dict(status='verified', method='Counted', key_version='1'))])

    def test_selection_snapshot_runs_selector_with_database_due_date(self):
        self.t.transfer(today='2026-11-03')
        projected = snapshot.selection(self.db, self.config())
        self.assertEqual(projected['candidates'][0]['purpose'], 'review')
        self.assertEqual(projected['candidates'][0]['due_date'], '2026-11-06')
        self.assertEqual(selector.select(projected)['selected']['id'], 'fresh')
        self.assertNotIn('SECRET', json.dumps(projected))
        self.assertNotIn('My answer', json.dumps(projected))
        config = self.config()
        config['taught_capability_ids'] = []
        result = selector.select(snapshot.selection(self.db, config))
        self.assertEqual(result['exclusions'][0]['reason'], 'untaught_scope')

    def test_full_prerequisite_closure_and_archived_dependencies(self):
        t = self.t
        t.capability('a'); t.capability('b')
        t.write([t.record('prerequisite_groups', id='cg', capability_id='c'),
                 t.record('prerequisite_members', id='cb', group_id='cg', prerequisite_id='b'),
                 t.record('prerequisite_groups', id='bg', capability_id='b'),
                 t.record('prerequisite_members', id='ba', group_id='bg', prerequisite_id='a')])
        projected = snapshot.selection(self.db, self.config())
        self.assertEqual(set(projected['capabilities']), {'a', 'b', 'c'})
        t.write([t.record('capabilities', id='a', archived=1)])
        projected = snapshot.selection(self.db, self.config())
        self.assertNotIn('a', projected['capabilities'])
        self.assertEqual(projected['capabilities']['b']['prerequisite_groups'], [['a']])

    def test_active_prompt_is_resumed_without_keys(self):
        t = self.t
        t.write([t.record('sessions', id='s', topic_id='topic', active_unit_id='intro')])
        projected = snapshot.selection(self.db, self.config())
        result = selector.select(projected)
        self.assertEqual(result['status'], 'resume')
        self.assertEqual(result['active_unit']['prompt_reference'], 'units:intro')
        self.assertNotIn('SECRET', json.dumps(projected))

    def test_seen_projection_is_scoped_to_candidates_and_blocks_reuse(self):
        self.t.transfer(today='2026-11-03')
        config = self.config()
        config['candidates'][0]['id'] = 'intro'
        projected = snapshot.selection(self.db, config)
        self.assertEqual(projected['seen_units'], ['intro@1'])
        result = selector.select(projected)
        self.assertEqual(result['exclusions'][0]['reason'], 'already_seen')

    def test_observations_use_real_delays_and_exposure_eligibility(self):
        t = self.t
        t.write([t.activity('review', purpose='delayed'), *t.response('review', today='2026-11-09')], today='2026-11-09')
        rows = snapshot.observations(self.db, 'topic', ['review-attempt-grade'])
        self.assertEqual(rows[0]['delay_days'], 8)
        self.assertTrue(rows[0]['independent'])
        self.assertTrue(personalize.usable(rows[0]))
        self.assertNotIn('response', rows[0])
        self.assertNotIn('answer', rows[0])
        t.write(t.response('review', identity='retry', today='2026-11-10'), today='2026-11-10')
        self.assertFalse(snapshot.observations(self.db, 'topic', ['retry-grade'])[0]['independent'])
        t.write([t.record('attempts', id='exposure', unit_id='review', response='', hinted=True, revealed=False, skipped=False)])
        self.assertFalse(snapshot.observations(self.db, 'topic', ['review-attempt-grade'])[0]['independent'])

    def test_superseded_and_out_of_topic_evidence_is_refused(self):
        t = self.t
        t.write(t.response('intro'))
        grade = t.response('intro')[1]['data']
        grade.update(id='correction', supersedes='intro-attempt-grade', score=0)
        t.write([t.record('assessments', **grade)])
        with self.assertRaisesRegex(ValueError, 'superseded'):
            snapshot.observations(self.db, 'topic', ['intro-attempt-grade'])
        with self.assertRaisesRegex(ValueError, 'out-of-topic'):
            snapshot.observations(self.db, 'other', ['correction'])

    def test_measurement_requires_and_preserves_a_frozen_baseline(self):
        t = self.t
        t.transfer(today='2026-11-03')
        frozen = snapshot.observations(self.db, 'topic', ['transfer-attempt-grade'])
        t.write([t.record('baselines', id='baseline', topic_id='topic', snapshot=frozen, digest=personalize.digest(frozen))])
        config = dict(topic='topic', preference=dict(enabled=False, challenge='practice', allow_harder=False),
                      baseline_id='baseline', history_assessment_ids=[], review_capability_id='c')
        projected = snapshot.measurement(self.db, config)
        self.assertEqual(projected['baseline'], frozen)
        self.assertFalse(personalize.analyze(projected)['baseline_ready'])
        config['baseline_id'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'baseline'):
            snapshot.measurement(self.db, config)

    def test_policy_helpers_accept_stdin_without_sidecar_files(self):
        self.t.transfer(today='2026-11-03')
        projected = snapshot.selection(self.db, self.config())
        result = subprocess.run([sys.executable, str(SCRIPTS/'select.py'), '-'],
            input=json.dumps(projected), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'suggested')
        projected = dict(topic='topic', preference=dict(enabled=False, challenge='practice', allow_harder=False),
                         baseline=[], history=[], review=dict(capability_id='c', interval=3))
        result = subprocess.run([sys.executable, str(SCRIPTS/'personalize.py'), 'analyze', '-'],
            input=json.dumps(projected), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)['baseline_ready'])

    def test_frozen_baseline_is_not_silently_rewritten_after_exposure(self):
        t = self.t
        t.transfer(today='2026-11-03')
        frozen = snapshot.observations(self.db, 'topic', ['transfer-attempt-grade'])
        t.write([t.record('baselines', id='baseline', topic_id='topic', snapshot=frozen, digest=personalize.digest(frozen))])
        t.write([t.record('attempts', id='later-hint', unit_id='transfer', response='', hinted=True, revealed=False, skipped=False)])
        config = dict(topic='topic', preference=dict(enabled=True, challenge='practice', allow_harder=True),
                      baseline_id='baseline', history_assessment_ids=[], review_capability_id='c')
        with self.assertRaisesRegex(ValueError, 'baseline evidence changed'):
            snapshot.measurement(self.db, config)
        self.assertEqual(json.loads(m.get(self.db, 'baselines', 'baseline')[0]['snapshot']), frozen)

    def test_cli_projection_is_read_only_and_writes_no_sidecars(self):
        t = self.t
        t.transfer(today='2026-11-03')
        before = m.revision(self.db)
        result = subprocess.run([sys.executable, str(SCRIPTS/'snapshot.py'), '--root', str(t.root), 'selection', '-'],
                                input=json.dumps(self.config()), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(selector.select(json.loads(result.stdout))['status'], 'suggested')
        self.assertEqual(m.revision(self.db), before)
        readonly = snapshot.connect(t.root)
        try:
            with self.assertRaises(sqlite3.OperationalError):
                readonly.execute("DELETE FROM capabilities")
        finally:
            readonly.close()
        self.assertEqual({p.name for p in t.root.iterdir()}, {'AGENTS.md', 'CLAUDE.md', '.learning'})


if __name__ == '__main__':
    unittest.main()
