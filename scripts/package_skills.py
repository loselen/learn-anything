#!/usr/bin/env python3
"""Build current skill archives into a new directory; never reuse stale dist files."""
import argparse
import json
from pathlib import Path
import re
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build(output, tag=None):
    version = json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())['plugins'][0]['version']
    rules = (ROOT/'skills/setup-learning/assets/AGENTS.md').read_text()
    runtime = (ROOT/'skills/setup-learning/scripts/memory.py').read_text()
    if ('Template version: '+version+'\n' not in rules or
            re.search(r"^VERSION = '([^']+)'", runtime, re.M).group(1) != version or
            '## '+version+'\n' not in (ROOT/'CHANGELOG.md').read_text()):
        raise ValueError('release versions disagree')
    if tag is not None and tag != 'v'+version:
        raise ValueError('release tag must match v'+version)
    output = Path(output).absolute()
    if output.exists() or output.is_symlink() or any(p.is_symlink() for p in output.parents):
        raise ValueError('package output must be a new non-symlink directory')
    output.parent.mkdir(parents=True, exist_ok=True)
    # Build off to the side, so a failed build never looks like a complete release.
    with tempfile.TemporaryDirectory(dir=output.parent, prefix='.skills-build-') as tmp:
        staging = Path(tmp)/'packages'
        staging.mkdir()
        for skill in sorted((ROOT/'skills').iterdir()):
            if not (skill/'SKILL.md').is_file():
                continue
            with zipfile.ZipFile(staging/(skill.name+'.skill'), 'w', zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(skill.rglob('*')):
                    if path.is_symlink():
                        raise ValueError('symlink in skill package: '+str(path))
                    if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                        archive.write(path, path.relative_to(skill.parent))
        if output.exists() or output.is_symlink():
            raise ValueError('package output appeared during build')
        staging.rename(output)
    return {'version': version, 'output': str(output), 'packages': len(list(output.glob('*.skill')))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--tag')
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.output, args.tag)))
    except (ValueError, OSError) as error:
        parser.exit(2, str(error)+'\n')
