import json
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    def test_version_and_skill_discovery(self):
        version = json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())['plugins'][0]['version']
        rules = (ROOT/'skills/setup-obsidian/assets/AGENTS.md').read_text()
        self.assertIn('Template version: '+version+'\n', rules)
        self.assertIn('## '+version+'\n', (ROOT/'CHANGELOG.md').read_text())
        skills = list((ROOT/'skills').glob('*/SKILL.md'))
        self.assertEqual(len(skills), 10)
        for skill in skills:
            metadata = yaml.safe_load(skill.read_text().split('---', 2)[1])
            self.assertEqual(metadata['name'], skill.parent.name)
            self.assertFalse(set(metadata) - {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'})

    def test_dashboard_and_templates_parse(self):
        dashboard = yaml.safe_load((ROOT/'skills/setup-obsidian/assets/Dashboard.base').read_text())
        self.assertEqual(len(dashboard['views']), 6)
        for template in (ROOT/'skills/setup-obsidian/assets').glob('*-template.md'):
            self.assertIsInstance(yaml.safe_load(template.read_text().split('---', 2)[1]), dict)
