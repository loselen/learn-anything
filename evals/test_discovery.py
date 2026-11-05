from copy import deepcopy
from fractions import Fraction
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('selection', ROOT/'skills/explore-next/scripts/select.py')
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads((ROOT/'evals/fixtures/discovery-snapshot.json').read_text())
        self.snapshot['challenge'] = 'stretch'
        self.snapshot['budget_minutes'] = 10
        self.snapshot['allowed_topics'] = ['arithmetic', 'python']
        self.units = {u['id']: u for u in self.snapshot['candidates']}

    def selected(self, snapshot=None):
        return p.select(snapshot or self.snapshot)

    def exclusion(self, identity):
        return {e['id']: e['reason'] for e in self.selected()['exclusions']}.get(identity)

    def test_prerequisites_and_alternatives(self):
        unit = self.units['fraction-addition']; cap = self.snapshot['capabilities'][unit['capability_id']]
        self.assertEqual(self.exclusion(unit['id']), 'prerequisites_not_ready')
        for identity in cap['prerequisites'][1:]:
            self.snapshot['capabilities'][identity]['status'] = 'review'
        base = self.units['whole-addition']['capability_id']
        self.snapshot['capabilities'][base]['status'] = 'review'
        self.assertIsNone(self.exclusion(unit['id']))
        cap['prerequisites'] = []
        cap['prerequisite_groups'] = [['unknown', base]]
        self.assertIsNone(self.exclusion(unit['id']))
        cap['prerequisite_groups'] = [['unknown']]
        self.assertEqual(self.exclusion(unit['id']), 'blocked_dependency_graph')

    def test_hard_cycle_and_escaping_or(self):
        whole = self.units['whole-addition']['capability_id']
        fraction = self.units['fraction-addition']['capability_id']
        nodes = self.snapshot['capabilities']
        nodes[whole]['prerequisites'] = [fraction]
        nodes[whole]['status'] = nodes[fraction]['status'] = 'solid'
        self.assertEqual(self.exclusion('whole-addition'), 'blocked_dependency_graph')
        escape = self.units['even-classification']['capability_id']
        nodes[escape]['status'] = 'review'
        nodes[whole]['prerequisites'] = []
        nodes[whole]['prerequisite_groups'] = [[fraction, escape]]
        self.assertIsNone(self.exclusion('whole-addition'))

    def test_consent_goal_mode_and_time(self):
        self.snapshot['allowed_topics'] = ['arithmetic']
        self.assertEqual(self.exclusion('print-sequence'), 'topic_not_consented')
        self.snapshot.update(allowed_topics=['arithmetic','python'], mode='continue',goal_topic='arithmetic',goal_capability_ids=[self.units['fraction-addition']['capability_id']])
        self.assertEqual(self.exclusion('even-classification'), 'outside_chosen_goal')
        self.assertIsNone(self.exclusion('whole-addition'))
        self.assertEqual(self.exclusion('print-sequence'), 'outside_chosen_goal')
        self.snapshot.update(mode='review')
        self.assertEqual(self.selected()['status'], 'blocked')
        self.snapshot.update(mode='explore',budget_minutes=1)
        self.assertEqual(self.selected()['status'], 'blocked')
        self.snapshot['sustained_work'] = True
        self.assertEqual(self.selected()['status'], 'suggested')

    def test_consented_cross_topic_goal_prerequisite(self):
        goal = self.units['print-sequence']['capability_id']
        base = self.units['whole-addition']['capability_id']
        self.snapshot['capabilities'][goal]['prerequisites'] = [base]
        self.snapshot.update(mode='continue',goal_topic='python',goal_capability_ids=[goal])
        self.assertIsNone(self.exclusion('whole-addition'))
        self.assertEqual(self.exclusion('even-classification'), 'outside_chosen_goal')
        self.snapshot['allowed_topics'] = ['python']
        self.assertEqual(self.exclusion('whole-addition'), 'topic_not_consented')

    def test_verification_duplicates_and_challenge(self):
        self.units['whole-addition']['verification']['status'] = 'disputed'
        self.assertEqual(self.exclusion('whole-addition'), 'unverified')
        self.units['print-sequence']['key'] = 'incorrect'
        self.assertEqual(self.exclusion('print-sequence'), 'verification_content_changed')
        self.snapshot['candidates'].append(deepcopy(self.units['even-classification']))
        self.assertEqual(self.exclusion('even-classification'), 'duplicate_unit')
        self.snapshot['seen_units'] = ['fraction-addition@1']
        self.assertEqual(self.exclusion('fraction-addition'), 'already_seen')
        self.snapshot.update(challenge='intro')
        self.assertEqual(self.exclusion('function-parts'), 'challenge_mismatch')

    def test_review_requires_taught_due_scope(self):
        unit = self.units['whole-addition']
        unit.update(source='due_review', purpose='review', modes=['review'],due_date='2026-11-04')
        self.snapshot['mode'] = 'review'
        self.assertEqual(self.exclusion(unit['id']), 'untaught_scope')
        self.snapshot['capabilities'][unit['capability_id']].update(taught=True,status='review')
        self.assertEqual(self.selected()['selected']['id'], unit['id'])
        unit['due_date'] = '2026-11-06'
        self.assertEqual(self.exclusion(unit['id']), 'not_due')

    def test_resume_endpoint_and_no_evidence_mutation(self):
        before = deepcopy(self.snapshot)
        result = self.selected()
        self.assertEqual(self.snapshot, before)
        self.assertLessEqual(len(result['choices']), 3)
        self.assertNotIn('key', p.canonical(result))
        self.snapshot.update(batch_remaining=0)
        self.assertEqual(self.selected()['status'], 'complete')
        active = dict(id='unanswered',version='1',topic='python',prompt_reference='Lessons/Trace.md#Activity',key='do not expose')
        self.snapshot.update(active_unit=active)
        resumed = self.selected()
        self.assertEqual(resumed['status'], 'resume')
        self.assertEqual(resumed['choices'], [])
        self.assertNotIn('do not expose', p.canonical(resumed))
        self.snapshot['allowed_topics'] = ['arithmetic']
        self.assertEqual(self.selected()['status'], 'paused')

    def test_replay_features_and_repair_priority(self):
        whole = self.units['whole-addition']
        whole.update(source='repair', purpose='repair')
        cap = whole['capability_id']
        self.snapshot['capabilities'][cap]['taught'] = True
        self.snapshot['repeated_misconceptions'] = [cap]
        other = self.units['even-classification']; other['features'].update(interest=1,diversity=1,evidence_value=1)
        first = self.selected()
        self.assertEqual(first['selected']['id'], whole['id'])
        self.assertTrue(first['selected']['repair_priority'])
        self.snapshot['candidates'].reverse()
        self.assertEqual(first, self.selected())
        self.assertEqual(first['policy_version'], 'rules-1')
        self.assertEqual(len(first['snapshot_digest']), 64)
        whole['features']['readiness'] = 0
        self.assertEqual(self.selected()['selected']['features']['readiness'], 1)
        whole['features']['interest'] = 2
        self.assertEqual(self.exclusion(whole['id']), 'invalid_features')

    def test_missing_preferences_and_malformed_inputs(self):
        self.snapshot['allowed_topics'] = []
        self.assertEqual(self.selected()['status'], 'needs_preference')
        for value in (-1, float('nan'), True):
            with self.subTest(value=value):
                snapshot = deepcopy(self.snapshot); snapshot['budget_minutes'] = value
                with self.assertRaises(ValueError):
                    p.select(snapshot)
        self.snapshot['allowed_topics'] = ['arithmetic']
        invalid = deepcopy(self.snapshot); invalid['today'] = '20261105'
        with self.assertRaises(ValueError):
            p.select(invalid)
        self.units['whole-addition']['source'] = []
        self.assertEqual(self.exclusion('whole-addition'), 'malformed')

    def test_cli_public_output_and_failure(self):
        script = ROOT/'skills/explore-next/scripts/select.py'
        result = subprocess.run([sys.executable, str(script), str(ROOT/'evals/fixtures/discovery-snapshot.json')],capture_output=True,text=True,check=True)
        record = json.loads(result.stdout)
        self.assertEqual(record['status'], 'suggested')
        self.assertNotIn('key', record['selected'])
        invalid = subprocess.run([sys.executable,str(script)],capture_output=True,text=True)
        self.assertEqual(invalid.returncode, 2)
        self.assertIn('error', json.loads(invalid.stderr))


class CatalogTests(unittest.TestCase):
    def test_catalog_identity_and_verification_binding(self):
        catalog = json.loads((ROOT/'skills/explore-next/references/catalog.json').read_text())
        units = catalog['units']
        identities = {u['capability_id'] for u in units + catalog['bridge_capabilities']}
        for unit in units:
            self.assertTrue(set(unit['prerequisites']) <= identities)
        fixture = json.loads((ROOT/'evals/fixtures/discovery-snapshot.json').read_text())
        self.assertEqual(fixture['candidates'], units)
        self.assertEqual(len({u['id'] for u in units}), len(units))
        self.assertEqual(len({u['capability_id'] for u in units}), len(units))
        for unit in units:
            uuid.UUID(unit['capability_id'])
            self.assertIsNone(p.shape(unit))
            self.assertIn(unit['kind'], {'procedure','principle','concept','structure','facts'})
            self.assertEqual(unit['verification']['status'], 'verified')
            self.assertTrue(unit['outcome'])
            self.assertTrue(unit['rubric']['full_credit'])

    def test_checked_keys_against_calculation_execution_and_syntax(self):
        units = {u['id']: u for u in json.loads((ROOT/'skills/explore-next/references/catalog.json').read_text())['units']}
        whole = units['whole-addition']
        # Read quantities from authored prompt; verify by both counting and arithmetic.
        a,b = map(int,re.findall(r'\d+',whole['prompt']))
        self.assertEqual(int(whole['key']), len(list(range(a))+list(range(b))))
        self.assertEqual(int(whole['key']), a+b)
        fraction = units['fraction-addition']
        x,y = map(Fraction,re.findall(r'\d+/\d+',fraction['prompt']))
        self.assertEqual(Fraction(fraction['key']), x+y)
        self.assertEqual(Fraction(fraction['key']), Fraction(3+2,6))
        even = units['even-classification']
        integers = list(map(int,re.findall(r'-?\d+',even['prompt'])))
        self.assertEqual([i for i in integers if i % 2 == 0], [-4,0])
        self.assertEqual(even['key'], '-4 and 0')
        for identity in ('print-sequence','function-parts'):
            code = units[identity]['prompt'].split('\n\n',1)[1]
            # Execute only reviewed repository-authored fixtures, never learner/imported text.
            output = subprocess.run([sys.executable,'-I','-c',code],capture_output=True,text=True,timeout=3,check=True).stdout
            if identity == 'print-sequence':
                self.assertEqual(output.rstrip('\n'), units[identity]['key'])
            else:
                tree = ast.parse(code)
                self.assertIsInstance(tree.body[0], ast.FunctionDef)
                self.assertIsInstance(tree.body[0].body[0].value, ast.Call)
                self.assertEqual(tree.body[1].value.func.id, tree.body[0].name)
                self.assertEqual(output,'hello\n')
                definition_only = code.rsplit('\ngreet()',1)[0]
                self.assertEqual(subprocess.run([sys.executable,'-I','-c',definition_only],capture_output=True,text=True,timeout=3,check=True).stdout,'')
