import json
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    def test_version_and_skill_discovery(self):
        version = json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())['plugins'][0]['version']
        rules = (ROOT/'skills/setup-learning/assets/AGENTS.md').read_text()
        self.assertIn('Template version: '+version+'\n', rules)
        self.assertIn('## '+version+'\n', (ROOT/'CHANGELOG.md').read_text())
        skills = list((ROOT/'skills').glob('*/SKILL.md'))
        self.assertEqual(len(skills), 13)
        for skill in skills:
            metadata = yaml.safe_load(skill.read_text().split('---', 2)[1])
            self.assertEqual(metadata['name'], skill.parent.name)
            self.assertFalse(set(metadata) - {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'})

    def test_sqlite_runtime_and_documentation(self):
        scripts = ROOT/'skills/setup-learning/scripts'
        version = json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())['plugins'][0]['version']
        self.assertIn("VERSION = '"+version+"'", (scripts/'memory.py').read_text())
        self.assertTrue((scripts/'schema.sql').is_file())
        self.assertTrue((scripts/'legacy.py').is_file())
        for path in ROOT.glob('skills/*/SKILL.md'):
            self.assertNotIn('(references/learner-state.md)', path.read_text())
        self.assertIn('make-activity', (ROOT/'README.md').read_text())
        self.assertIn('summarize-me', (ROOT/'README.md').read_text())
