"""One-time Markdown import. PyYAML is needed here only, never for normal turns."""
from datetime import date
import hashlib
from pathlib import Path
import re
import uuid

import memory as m


def identity(path):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'learn-anything:markdown:'+path))


def parse(raw):
    import yaml

    class UniqueLoader(yaml.SafeLoader):
        pass

    def mapping(loader, node):
        result = {}
        for key, value in node.value:
            name = loader.construct_object(key)
            if name in result:
                raise ValueError('duplicate YAML property: '+str(name))
            result[name] = loader.construct_object(value)
        return result

    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    text = raw.decode('utf-8')
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != '---':
        return {}, text
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
    if end is None:
        raise ValueError('unclosed frontmatter')
    props = yaml.load(''.join(lines[1:end]), Loader=UniqueLoader)
    if props is None:
        props = {}
    if not isinstance(props, dict):
        raise ValueError('frontmatter is not a mapping')
    return props, ''.join(lines[end+1:])


def link_target(link):
    return str(link).removeprefix('[[').removesuffix(']]').split('|')[0].split('#')[0].removesuffix('.md')


def sequence(value):
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError('expected a YAML list of links/groups')
    return value


def section(text, name):
    match = re.search(r'^## '+re.escape(name)+r'\s*\r?\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    return match.group(1) if match else ''


def goal_parts(text):
    """1.x map goals hold **Now:**, **Long-term:** and **Path:** lines."""
    found = {k: re.search(r'^\*\*'+k+r':\*\*[ \t]*(.*)$', text, re.M) for k in ('Now', 'Long-term', 'Path')}
    if not found['Now']:
        return {'goal': text.strip()}
    return {'goal': found['Now'].group(1).strip(), 'long_term': found['Long-term'].group(1).strip() if found['Long-term'] else '',
            'path': found['Path'].group(1).strip() if found['Path'] else ''}


def outcome_rows(text):
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 2 or not cells[0] or cells[0].lower() == 'outcome' or set(cells[0]) <= set('-: '):
            continue
        met = re.search(r'met\s+(\d{4}-\d{2}-\d{2})', cells[1])
        yield cells[0], met.group(1) if met else None


def classify(relative, props):
    """Route a document to a table; 'raw' keeps only its original bytes."""
    parts = relative.parts
    if parts[0] == 'Templates' or (len(parts) == 1 and parts[0] in ('AGENTS.md', 'CLAUDE.md', 'My Summary.md', 'my-summary.md')):
        return 'raw', False
    category = parts[0] if len(parts) > 1 else ''
    if category == 'Archive':
        tags = props.get('tags') or []
        if 'status' in props or 'prerequisites' in props:
            return 'capabilities', True
        if 'map' in (tags if isinstance(tags, list) else [tags]):
            return 'topics', True
        return 'notes', False
    return {'Lessons': 'capabilities', 'Maps': 'topics', 'References': 'sources'}.get(category, 'notes'), False


def plan(source):
    source = Path(source)
    if not source.is_dir() or source.is_symlink() or any(p.is_symlink() for p in source.parents):
        raise ValueError('source must be an existing non-symlink folder')
    source = source.resolve()
    docs, by_path, by_title = [], {}, {}
    for path in sorted(source.rglob('*.md')):
        relative = path.relative_to(source)
        if any(part.startswith('.') for part in relative.parts):
            continue
        if path.is_symlink() or any(p.is_symlink() for p in path.parents):
            raise ValueError('symlinked source: '+str(relative))
        raw = path.read_bytes()
        props, body = parse(raw)
        kind, archived = classify(relative, props)
        ident = props.get('capability_id') if kind == 'capabilities' else None
        ident = ident or identity(str(relative))
        if not isinstance(ident, str):
            raise ValueError('invalid capability ID: '+str(relative))
        doc = dict(path=str(relative), raw=raw, props=props, body=body,
                   table=kind, archived=archived, id=ident, title=path.stem)
        docs.append(doc)
        by_path[str(relative.with_suffix(''))] = doc
        by_title.setdefault(path.stem, []).append(doc)
    if not docs:
        raise ValueError('source contains no Markdown documents')
    ids = [d['id'] for d in docs if d['table'] == 'capabilities']
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate capability IDs')

    def resolve(link, table):
        target = link_target(link)
        exact = by_path.get(target)
        options = [exact] if exact else by_title.get(target, [])
        options = [d for d in options if d['table'] == table]
        if len(options) != 1:
            raise ValueError('unknown or ambiguous '+table+' link: '+target)
        return options[0]['id']

    records, dependencies, warnings = [], [], []
    stamp = m.now()
    for doc in docs:
        props, body, ident, table = doc['props'], doc['body'], doc['id'], doc['table']
        if table == 'raw':
            continue
        data = {'id': ident, 'title': doc['title']}
        if doc['archived']:
            data['archived'] = 1
        if table == 'capabilities':
            data.update(kind=str(props.get('kind') or 'concept').lower(), status=props.get('status') or 'planned',
                        placement=props.get('placement') or 'unknown', retention=props.get('retention') or 'unmeasured',
                        repair=int(bool(props.get('repair', False))))
            for field in ('interval', 'last_reviewed', 'next_review'):
                if props.get(field) is not None and props[field] != '':
                    data[field] = str(props[field]) if field != 'interval' else props[field]
            # A legacy failed-review marker is not certain enough to silently infer repair.
            if 'repair' not in props and data['status'] == 'learning' and data.get('next_review'):
                warnings.append(doc['path']+': repair was not explicit; preserved as ordinary learning')
            data['objective'] = section(body, 'Outcome').strip()
            words = section(body, 'In my words').strip()
            if words:
                dependencies.append({'table': 'notes', 'data': {'id': identity(doc['path']+':own_words'), 'title': doc['title']+': in my words',
                                'body': words, 'capability_id': ident, 'kind': 'own_words', 'created_at': stamp}})
        elif table == 'topics':
            data.update(goal_parts(section(body, 'Goal')))
            for index, (description, met) in enumerate(outcome_rows(section(body, 'Outcomes'))):
                dependencies.append({'table': 'outcomes', 'data': {'id': identity(doc['path']+':outcome:'+str(index)),
                                     'topic_id': ident, 'description': description, 'met_on': met}})
        elif table == 'sources':
            url = re.search(r'https?://[^\s)>]+', body)
            data.update(body=body, url=url.group(0) if url else '', source_type='primary' if props.get('source_type') == 'primary' else 'secondary')
        else:
            data.update(body=body, kind='legacy', created_at=stamp)
        records.append({'table': table, 'data': data})
    for doc in docs:
        if doc['table'] != 'capabilities':
            continue
        props, cap = doc['props'], doc['id']
        groups = [[resolve(link, 'capabilities')] for link in sequence(props.get('prerequisites'))]
        for group in sequence(props.get('prerequisite_groups')):
            if not isinstance(group, list) or not group or any(p not in ids for p in group):
                raise ValueError('invalid prerequisite group: '+doc['path'])
            groups.append(group)
        for index, group in enumerate(groups):
            gid = identity(doc['path']+':group:'+str(index))
            dependencies.append({'table': 'prerequisite_groups', 'data': {'id': gid, 'capability_id': cap}})
            for prereq in group:
                dependencies.append({'table': 'prerequisite_members', 'data': {'id': identity(gid+':'+prereq), 'group_id': gid, 'prerequisite_id': prereq}})
        for topic in sequence(props.get('topic')):
            tid = resolve(topic, 'topics')
            dependencies.append({'table': 'topic_capabilities', 'data': {'id': identity(tid+':'+cap), 'topic_id': tid, 'capability_id': cap}})
        for source in sequence(props.get('references')):
            sid = resolve(source, 'sources')
            dependencies.append({'table': 'capability_sources', 'data': {'id': identity(cap+':'+sid), 'capability_id': cap, 'source_id': sid}})
        # Preserve prose as a searchable note, not invented verified assessment records.
        records.append({'table': 'notes', 'data': {'id': identity(doc['path']+':body'), 'title': doc['title']+' (imported)',
                       'body': doc['body'], 'capability_id': cap, 'kind': 'legacy', 'created_at': stamp}})
    for doc in docs:
        if doc['path'] != 'Sessions/Current.md':
            continue
        props = doc['props']
        saved = str(props.get('saved_next_action') or section(doc['body'], 'Saved next action') or '')
        if props.get('active_unit_id') or props.get('prompt_reference'):
            saved += '\nResume the unanswered legacy prompt before choosing another. Read notes:'+doc['id']+'. Original prompt reference: '+str(props.get('prompt_reference') or props.get('active_unit_id'))
            warnings.append('Legacy active prompt retained in saved action; inspect its original note before resuming')
        records.append({'table': 'sessions', 'data': {'id': str(props.get('session_id') or identity(doc['path']+':session')),
                        'mode': props.get('mode') or 'continue', 'next_action': saved,
                        'closure': props.get('closure') or 'paused', 'budget_minutes': props.get('budget_minutes'), 'updated_at': stamp}})
    return docs, records+dependencies, warnings


def import_markdown(root, source, dry_run=False):
    root, source = Path(root), Path(source)
    docs, records, warnings = plan(source)
    signature = m.digest([[d['path'], hashlib.sha256(d['raw']).hexdigest()] for d in docs])
    report = {'documents': len(docs), 'records': len(records), 'digest': signature, 'warnings': warnings,
              'note': 'Original bytes retained. Historical prose is not synthesized into verified assessments; imported state is legacy evidence.'}
    if dry_run:
        # Exercise constraints and graph validation in a disposable database too.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            m.initialize(tmp, install=False)
            db = m.connect(tmp)
            try:
                m.apply(db, {'operation_id': 'dry-run', 'records': records}, importing=True)
            finally:
                db.close()
        return report
    if not m.db_path(root).exists():
        raise ValueError('initialize destination first; import never changes source rules or notes')
    db = m.connect(root)
    try:
        with m.transaction(db):
            previous = db.execute("SELECT value FROM meta WHERE key='markdown_import_digest'").fetchone()
            if previous:
                if previous[0] == signature:
                    return dict(report, already_imported=True)
                raise ValueError('source changed after import; reconcile explicitly instead of overwriting memory')
            if any(db.execute(f'SELECT 1 FROM {t} LIMIT 1').fetchone() for t in ('capabilities', 'topics', 'notes', 'sessions')):
                raise ValueError('import requires an empty destination memory')
            for record in records:
                m.put(db, record['table'], record['data'], importing=True)
            m.check_graph(db)
            for doc in docs:
                actual = (source / doc['path']).read_bytes()
                if actual != doc['raw']:
                    raise ValueError('source changed during import: '+doc['path'])
                db.execute('INSERT INTO legacy_documents VALUES (?,?,?,?,?)',
                           (identity(doc['path']+':raw'), doc['path'], hashlib.sha256(doc['raw']).hexdigest(), doc['raw'], m.now()))
            db.execute('INSERT INTO meta VALUES (?,?)', ('markdown_import_digest', signature))
            db.execute("UPDATE meta SET value=CAST(value AS INTEGER)+1 WHERE key='revision'")
        return dict(report, revision=m.revision(db))
    finally:
        db.close()
