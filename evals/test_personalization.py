from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'skills/explore-next/scripts/personalize.py'
spec = importlib.util.spec_from_file_location('personalization', SCRIPT)
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)


def rows(prefix, score=1, count=6):
    return [dict(assessment_id=f'{prefix}-grade-{i}', attempt_id=f'{prefix}-attempt-{i}',
                 unit_id=f'unit-{i%3}', unit_version='1', capability_id='cap', topic='python',
                 challenge='practice', purpose='delayed' if i%2 else 'transfer',
                 independent=True, hinted=False, revealed=False, verified=True,
                 disputed=False, complete=True, score=score, delay_days=7) for i in range(count)]


def snapshot():
    return dict(topic='python', preference=dict(enabled=True, challenge='practice', allow_harder=True),
                baseline=rows('base'), history=rows('new'), review=dict(capability_id='cap', interval=7))


def comparison():
    return dict(plan=dict(id='trial-1', registered_on='2026-11-01', baseline_digest='a'*64,
                         primary='delayed_independent_score', minimum_per_arm=2,
                         practical_effect=.1, stopping_rule='Fixed four-person demonstration, not powered.',
                         retention_days=30, consented=True), as_of='2026-11-05', participants=[
        dict(id=str(i), arm='ladder' if i%2 else 'adaptive', probability=.5,
             assigned_on='2026-11-01', due_on='2026-11-04', chosen_minutes=10,
             delayed=.5 if i%2 else 1, transfer=.5) for i in range(4)])


class PersonalizationTests(unittest.TestCase):
    def test_baseline_optin_and_difficulty(self):
        s = snapshot(); original = deepcopy(s)
        r = p.analyze(s)
        self.assertTrue(r['baseline_ready'])
        self.assertEqual(r['challenge']['suggested'], 'stretch')
        self.assertEqual(r['review']['shadow_interval'], 9)
        self.assertFalse(r['review']['applied']); self.assertFalse(r['bandit_enabled'])
        self.assertEqual(s, original)
        s['preference']['enabled'] = False
        r = p.analyze(s)
        self.assertEqual(r['challenge']['suggested'], 'practice')
        self.assertEqual(r['review']['shadow_interval'], 7)
        s['preference']['enabled'] = True; s['baseline'] = []
        self.assertFalse(p.analyze(s)['baseline_ready'])
        self.assertEqual(p.analyze(s)['challenge']['suggested'], 'practice')

    def test_preferences_and_scoping(self):
        s = snapshot(); s['preference']['allow_harder'] = False
        self.assertEqual(p.analyze(s)['challenge']['suggested'], 'practice')
        s['history'] = rows('new', 0)
        self.assertEqual(p.analyze(s)['challenge']['suggested'], 'intro')
        self.assertEqual(p.analyze(s)['review']['shadow_interval'], 5)
        s['topic'] = 'arithmetic'
        self.assertFalse(p.analyze(s)['baseline_ready'])
        s = snapshot(); s['review']['capability_id'] = 'other'
        self.assertEqual(p.analyze(s)['review']['shadow_interval'], 7)
        for row in s['history']: row['challenge'] = 'intro'
        self.assertEqual(p.analyze(s)['challenge']['suggested'], 'practice')

    def test_ineligible_observations_and_diversity(self):
        for flag, value in [('hinted', True), ('revealed', True), ('independent', False),
                            ('verified', False), ('disputed', True), ('complete', False)]:
            s = snapshot()
            for row in s['baseline']: row[flag] = value
            self.assertFalse(p.analyze(s)['baseline_ready'], flag)
        s = snapshot()
        for row in s['baseline']: row['purpose'] = 'practice'
        self.assertFalse(p.analyze(s)['baseline_ready'])
        for row in s['baseline']: row['purpose'] = 'delayed'; row['delay_days'] = 1
        self.assertFalse(p.analyze(s)['baseline_ready'])
        s = snapshot()
        for row in s['baseline']: row['unit_id'] = 'one-unit'
        self.assertFalse(p.analyze(s)['baseline_ready'])
        s = snapshot()
        for row in s['baseline']: row['purpose'] = 'transfer'
        self.assertFalse(p.analyze(s)['baseline_ready'])

    def test_idempotency_corrections_and_replay(self):
        s = snapshot(); r = p.analyze(s)
        s['history'] += deepcopy(s['history'])
        self.assertEqual(p.analyze(s)['challenge'], r['challenge'])
        self.assertEqual(p.analyze(s)['review'], r['review'])
        s['history'][-1]['score'] = 0
        with self.assertRaises(ValueError): p.analyze(s)
        s = snapshot(); s['history'][1]['attempt_id'] = s['history'][0]['attempt_id']
        with self.assertRaises(ValueError): p.analyze(s)
        s = snapshot(); s['history'] = deepcopy(s['baseline'])
        with self.assertRaises(ValueError): p.analyze(s)
        self.assertEqual(p.analyze(snapshot()), p.analyze(snapshot()))

    def test_comparison_missingness_time_and_no_promotion(self):
        s = comparison(); r = p.compare(s)
        self.assertTrue(r['planned_sample_reached'])
        self.assertEqual(r['observed_difference'], .5)
        self.assertTrue(r['practical_threshold_reached'])
        self.assertEqual(r['arms']['adaptive']['retained_score_per_chosen_minute'], .1)
        s['participants'][0]['delayed'] = None
        r = p.compare(s)
        self.assertFalse(r['planned_sample_reached'])
        self.assertEqual(r['arms']['adaptive']['attrition'], .5)
        self.assertEqual(r['arms']['adaptive']['retained_score_per_chosen_minute'], .05)
        s['participants'][0]['due_on'] = '2026-11-10'
        s['participants'][0]['transfer'] = None
        r = p.compare(s)
        self.assertEqual(r['arms']['adaptive']['due'], 1)
        self.assertEqual(r['arms']['adaptive']['attrition'], 0)
        self.assertIn('never auto-promote', r['decision'])

    def test_comparison_rejects_invalid_trial(self):
        mutations = [lambda s: s['participants'].append(deepcopy(s['participants'][0])),
                     lambda s: s['participants'][0].update(probability=.8),
                     lambda s: s['participants'][0].update(assigned_on='2026-10-01'),
                     lambda s: s['participants'][0].update(due_on='2026-11-10'),
                     lambda s: s['plan'].update(consented=False),
                     lambda s: s['plan'].update(baseline_digest='fake')]
        for mutate in mutations:
            s = comparison(); mutate(s)
            with self.assertRaises(ValueError): p.compare(s)

    def test_invalid_evidence_and_cli(self):
        for key, value in [('raw_answer', 'private'), ('score', float('nan')), ('hinted', 0)]:
            s = snapshot(); s['history'][0][key] = value
            with self.assertRaises(ValueError): p.analyze(s)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'input.json'; path.write_text(json.dumps(snapshot()))
            result = subprocess.run([sys.executable, str(SCRIPT), 'analyze', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['policy_version'], p.VERSION)
            self.assertEqual(list(Path(folder).iterdir()), [path])
            path.write_text('{"raw_answer": "private"}')
            result = subprocess.run([sys.executable, str(SCRIPT), 'analyze', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('private', result.stderr)
