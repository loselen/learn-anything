import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('state', ROOT / 'evals/reference_state.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


class StateTests(unittest.TestCase):
    def event(self, **kw):
        return dict(id='a1', purpose='delayed review', complete=True, correct=True, **kw)

    def test_review_ladder_failure_restart_and_repair(self):
        state = dict(status='solid', interval=7)
        passed = s.assess(state, self.event(), '2026-11-05')
        self.assertEqual((passed['interval'], passed['next_review']), (30, '2026-12-05'))
        event = self.event(); event.update(correct=False)
        failed = s.assess(state, event, '2026-11-05')
        import json
        failed = json.loads(json.dumps(failed))
        q = s.queues([failed, dict(status='learning')], '2026-11-06')
        self.assertEqual((len(q['repair']), len(q['learning']), len(q['due'])), (1, 1, 0))
        repaired = s.assess(failed, dict(id='b', purpose='transfer', complete=True, correct=True), '2026-11-06')
        self.assertFalse(repaired['repair'])
        self.assertEqual(repaired['status'], 'review')

    def test_placement_not_retention_or_schedule_extension(self):
        e = self.event(); e.update(purpose='placement', independent_items=2)
        placed = s.assess(dict(status='planned'), e, '2026-11-05')
        self.assertEqual((placed['status'], placed['interval']), ('review', 3))
        self.assertNotIn('retention', placed)
        old = s.assess(dict(status='solid', interval=90), e, '2026-11-05')
        self.assertEqual(old['interval'], 90)

    def test_exposure_partial_dispute_and_duplicate(self):
        state = dict(status='review', interval=3)
        for key in ['hinted', 'revealed', 'skipped']:
            result = s.assess(state, self.event(**{key: True}), '2026-11-05')
            self.assertEqual(result['status'], 'review')
            self.assertNotIn('retention', result)
        for key in ['complete', 'verified']:
            e = self.event(); e[key] = False
            self.assertEqual(s.assess(state, e, '2026-11-05')['status'], 'review')
        once = s.assess(state, self.event(), '2026-11-05')
        self.assertEqual(s.assess(once, self.event(), '2026-11-05'), once)
        # Unassessed capability B is untouched when A is assessed.
        b = dict(status='solid', interval=30)
        notes = {'a': state, 'b': b.copy()}
        notes['a'] = s.assess(notes['a'], self.event(), '2026-11-05')
        self.assertEqual(notes['b'], b)

    def test_dependencies(self):
        nodes = {'a': {'status': 'review'}, 'b': {'status': 'planned'},
                 'c': {'prerequisites': ['a'], 'prerequisite_groups': [['b', 'a']]}}
        self.assertTrue(s.readiness(nodes['c'], nodes))
        nodes['c']['prerequisites'].append('unknown')
        self.assertFalse(s.readiness(nodes['c'], nodes))
        self.assertEqual(s.ready_nodes({'a': {'prerequisites': ['b']}, 'b': {'prerequisites': ['a']}}), set())
        escaped = {'a': {'prerequisite_groups': [['b', 'c']]}, 'b': {'prerequisites': ['a']}, 'c': {}}
        self.assertEqual(s.ready_nodes(escaped), set(escaped))

    def test_migration_bytes_idempotence_rename_recovery(self):
        raw = (ROOT / 'evals/fixtures/legacy-lesson.md').read_bytes().replace(b'\n', b'\r\n')
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp); (vault/'Lessons').mkdir()
            (vault/'AGENTS.md').write_text('# Learning vault rules\nTemplate version: 1.3.0\n')
            note = vault/'Lessons/Original.md'; note.write_bytes(raw)
            self.assertEqual(s.migrate(vault, True), ['Lessons/Original.md'])
            self.assertEqual(note.read_bytes(), raw)
            s.migrate(vault)
            migrated = note.read_bytes()
            props, _, _ = s.frontmatter(migrated)
            self.assertTrue(props['repair'])
            self.assertTrue(migrated.endswith(raw[raw.index(b'---\r\n', 5):]))
            # Every original byte remains, with additions before the closing delimiter.
            _, lines, end = s.frontmatter(raw)
            self.assertTrue(migrated.startswith(b''.join(lines[:end])))
            renamed = note.rename(vault/'Lessons/Renamed.md')
            self.assertEqual(s.migrate(vault), [])
            self.assertEqual(renamed.read_bytes(), migrated)
            self.assertEqual(s.frontmatter(renamed.read_bytes())[0]['capability_id'], props['capability_id'])
            with self.assertRaises(ValueError):
                s.atomic_replace(renamed, raw, b'wrong')
            self.assertEqual(renamed.read_bytes(), migrated)

    def test_invalid_migration_does_not_write(self):
        with self.assertRaises(ValueError):
            s.migrate_note(b'---\nstatus: learning\nstatus: solid\n---\nmy text')
        plain = b'---\nstatus: learning\n---\nMy own text\n'
        props, _, _ = s.frontmatter(s.migrate_note(plain))
        self.assertFalse(props['repair'])

    def test_vault_graph_resolves_legacy_links_and_unknowns(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp); (vault/'Lessons').mkdir()
            (vault/'Lessons/Base.md').write_text('---\ncapability_id: base\nstatus: review\nprerequisites: []\n---\n')
            (vault/'Lessons/Next.md').write_text('---\ncapability_id: next\nstatus: planned\nprerequisites: ["[[Base]]"]\n---\n')
            report = s.inspect_graph(vault)
            self.assertFalse(report['blocked'])
            self.assertIn('next', report['ready'])
            (vault/'Lessons/Base.md').unlink()
            report = s.inspect_graph(vault)
            self.assertEqual(report['blocked'], ['next'])
            self.assertEqual(report['unknown'], [('next', 'Base')])

    def test_hot_path_has_one_installed_contract(self):
        rules = (ROOT/'skills/setup-learning/assets/AGENTS.md').read_text()
        self.assertIn('# Learning memory rules', rules)
        self.assertFalse(list(ROOT.glob('skills/*/references/learner-state.md')))
        self.assertIn('one compact `turn', rules)


if __name__ == '__main__':
    unittest.main()
