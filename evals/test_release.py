import json
from pathlib import Path
import unittest
import importlib.util
import tempfile
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    def test_release_tag_and_fresh_package_directory(self):
        spec = importlib.util.spec_from_file_location('package_skills', ROOT/'scripts/package_skills.py')
        package = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(package)
        with tempfile.TemporaryDirectory(dir='/tmp/opencode' if Path('/tmp/opencode').is_dir() else None) as tmp:
            output = Path(tmp)/'packages'
            with self.assertRaisesRegex(ValueError, 'tag'):
                package.build(output, 'v0.0.0-wrong')
            self.assertFalse(output.exists())
            version = json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())['plugins'][0]['version']
            result = package.build(output, 'v'+version)
            self.assertEqual(result['packages'], 13)
            self.assertEqual({p.stem for p in output.glob('*.skill')}, {p.parent.name for p in ROOT.glob('skills/*/SKILL.md')})
            for path in output.glob('*.skill'):
                with zipfile.ZipFile(path) as archive:
                    self.assertFalse(any('__pycache__' in n or n.endswith('.pyc') for n in archive.namelist()))
            with self.assertRaisesRegex(ValueError, 'new'):
                package.build(output)

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
