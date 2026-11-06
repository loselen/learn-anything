#!/usr/bin/env python3
"""Historical schema 2 reference for regression tests; not an installed runtime.

Requires PyYAML. Does not update rules/templates or operate on a real vault by default.
"""
import argparse
from copy import deepcopy
from datetime import date, timedelta
import os
from pathlib import Path
import tempfile
import uuid
import yaml


class UniqueLoader(yaml.SafeLoader):
    pass


def mapping(loader, node):
    result = {}
    for key, value in node.value:
        name = loader.construct_object(key)
        if name in result:
            raise ValueError(f'duplicate YAML key: {name}')
        result[name] = loader.construct_object(value)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def frontmatter(raw):
    lines = raw.splitlines(keepends=True)
    if not lines or lines[0].strip() != b'---':
        raise ValueError('missing frontmatter')
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == b'---'), None)
    if end is None:
        raise ValueError('unclosed frontmatter')
    props = yaml.load(b''.join(lines[1:end]), Loader=UniqueLoader)
    if not isinstance(props, dict):
        raise ValueError('frontmatter must be a mapping')
    return props, lines, end


def migrate_note(raw):
    props, lines, end = frontmatter(raw)
    repair = (props.get('status') == 'learning' and bool(props.get('last_reviewed'))
              and bool(props.get('next_review')) and props.get('interval') == 3)
    defaults = dict(schema_version=2, capability_id=str(uuid.uuid4()), placement='unknown',
                    retention='unmeasured', repair=repair, prerequisite_groups=[])
    missing = {k: v for k, v in defaults.items() if k not in props}
    if not missing:
        return raw
    newline = b'\r\n' if lines[0].endswith(b'\r\n') else b'\n'
    addition = yaml.safe_dump(missing, sort_keys=False).encode().replace(b'\n', newline)
    return b''.join(lines[:end]) + addition + b''.join(lines[end:])


def atomic_replace(path, expected, updated):
    if path.is_symlink() or path.read_bytes() != expected:
        raise ValueError(f'concurrent edit or symlink: {path}')
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.migration-')
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(updated)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(tmp, path.stat().st_mode)
        if path.is_symlink() or path.read_bytes() != expected:
            raise ValueError(f'concurrent edit: {path}')
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def migrate(vault, dry_run=False):
    vault = Path(vault)
    if vault.is_symlink() or not (vault / 'AGENTS.md').read_text().startswith('# Learning vault rules'):
        raise ValueError('not a learning vault')
    lessons = vault / 'Lessons'
    if lessons.is_symlink():
        raise ValueError('symlinked Lessons folder')
    changes, identities = [], set()
    # Validate every note before making any writes.
    for path in sorted(lessons.rglob('*.md')):
        if path.is_symlink() or any(p.is_symlink() for p in path.parents):
            raise ValueError(f'symlink: {path}')
        raw = path.read_bytes()
        updated = migrate_note(raw)
        props, _, _ = frontmatter(updated)
        identity = props['capability_id']
        if not identity or identity in identities:
            raise ValueError(f'empty or duplicate capability ID: {path}')
        identities.add(identity)
        if updated != raw:
            changes.append((path, raw, updated))
    for path, raw, updated in changes:
        if not dry_run:
            atomic_replace(path, raw, updated)
    return [str(path.relative_to(vault)) for path, _, _ in changes]


def ready_nodes(nodes):
    """Return structurally reachable IDs; unknown references remain blocked."""
    reachable = set()
    while True:
        before = reachable.copy()
        for identity, node in nodes.items():
            groups = [[p] for p in node.get('prerequisites', [])] + node.get('prerequisite_groups', [])
            if any(not group for group in groups):
                raise ValueError('empty prerequisite group')
            if all(any(p in reachable for p in group) for group in groups):
                reachable.add(identity)
        if before == reachable:
            return reachable


def inspect_graph(vault):
    """Resolve legacy wikilinks to IDs, then report unknowns and hard blocked cycles."""
    nodes, titles, paths = {}, {}, {}
    for path in sorted((Path(vault) / 'Lessons').rglob('*.md')):
        props, _, _ = frontmatter(path.read_bytes())
        identity = props.get('capability_id')
        if not identity or identity in nodes:
            raise ValueError(f'empty or duplicate capability ID: {path}')
        nodes[identity] = props
        titles.setdefault(path.stem, []).append(identity)
        paths[str(path.relative_to(vault).with_suffix(''))] = identity
    unknown = []
    for identity, node in nodes.items():
        resolved = []
        for link in node.get('prerequisites', []):
            target = str(link).removeprefix('[[').removesuffix(']]').split('|')[0].split('#')[0]
            matches = titles.get(target, [])
            match = paths.get(target) or (matches[0] if len(matches) == 1 else None)
            if match is None:
                unknown.append((identity, target))
                match = 'unknown:' + target
            resolved.append(match)
        node['prerequisites'] = resolved
        for group in node.get('prerequisite_groups', []):
            if not isinstance(group, list) or not group:
                raise ValueError('prerequisite_groups must contain nonempty lists')
            unknown.extend((identity, member) for member in group if member not in nodes)
    reachable = ready_nodes(nodes)
    return dict(unknown=unknown, blocked=sorted(set(nodes) - reachable),
                ready=sorted(identity for identity, node in nodes.items() if readiness(node, nodes)))


def readiness(node, nodes):
    groups = [[p] for p in node.get('prerequisites', [])] + node.get('prerequisite_groups', [])
    return all(group and any(nodes.get(p, {}).get('status') in ('review', 'solid')
                             for p in group) for group in groups)


def assess(state, event, today):
    """Pure reference reducer. Caller persists evidence and derived state atomically per file."""
    current = deepcopy(state)
    if event['id'] in current.get('processed', []):
        return current
    current.setdefault('processed', []).append(event['id'])
    current.setdefault('evidence', []).append(deepcopy(event))
    if not event.get('complete') or not event.get('verified', True):
        return current
    kind = event['purpose']
    supported = event.get('hinted') or event.get('revealed') or event.get('skipped')
    passed = event.get('correct') and not supported
    day = date.fromisoformat(today)
    if kind == 'placement' and passed and event.get('independent_items', 0) >= 2:
        current['placement'] = 'demonstrated'
        if current.get('status') in ('review', 'solid'):
            return current
        current.update(status='review', interval=3, next_review=str(day + timedelta(days=3)))
    elif kind == 'transfer' and passed:
        current.update(status='review', repair=False, interval=3,
                       next_review=str(day + timedelta(days=3)))
    elif kind == 'delayed review' and current.get('status') in ('review', 'solid'):
        # Disclosure/skip requests are exposure, not assessed failure.
        if supported:
            return current
        if passed:
            ladder = [3, 7, 30, 90]
            old = current.get('interval') or 3
            interval = next((n for n in ladder if n > old), 90)
            current.update(status='solid', repair=False, retention='demonstrated', interval=interval)
        else:
            current.update(status='learning', repair=True, interval=3)
        current.update(last_reviewed=today, next_review=str(day + timedelta(days=current['interval'])))
    return current


def queues(notes, today):
    return {
        'repair': [n for n in notes if n.get('repair') is True],
        'learning': [n for n in notes if n.get('status') == 'learning' and not n.get('repair')],
        'due': [n for n in notes if n.get('status') in ('review', 'solid')
                and n.get('next_review') and str(n['next_review']) <= today],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['migrate', 'check'])
    parser.add_argument('vault', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.command == 'migrate':
        for changed in migrate(args.vault, args.dry_run):
            print(changed)
    else:
        import json
        report = inspect_graph(args.vault)
        print(json.dumps(report, indent=2))
        raise SystemExit(1 if report['blocked'] or report['unknown'] else 0)
