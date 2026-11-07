#!/usr/bin/env python3
"""Local learning memory. Normal operation uses only the Python standard library."""
import argparse
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import uuid

VERSION = '1.4.0-experimental.5'
SCHEMA = 1
MUTABLE = {'topics', 'capabilities', 'topic_capabilities', 'outcomes', 'sessions',
           'questions', 'preferences', 'sources', 'capability_sources'}
APPEND = {'units', 'cycles', 'tests', 'test_items', 'attempts', 'assessments',
          'notes', 'recommendations', 'baselines', 'prerequisite_groups', 'prerequisite_members'}
DERIVED = {'status', 'placement', 'retention', 'repair', 'interval', 'last_reviewed', 'next_review'}
TIME_TABLES = {'sessions', 'units', 'cycles', 'tests', 'attempts', 'assessments', 'notes', 'recommendations', 'baselines'}
JSON_FIELDS = {'recommendations': ('snapshot', 'result'), 'baselines': ('snapshot',),
               'preferences': ('value',), 'tests': ('blueprint',)}


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def rows(db, sql, args=()):
    return [dict(row) for row in db.execute(sql, args)]


def revision(db):
    return int(db.execute("SELECT value FROM meta WHERE key='revision'").fetchone()[0])


def db_path(root):
    return Path(root) / '.learning' / 'memory.sqlite3'


def connect(root):
    path = db_path(root)
    if not path.is_file() or path.is_symlink() or path.parent.is_symlink():
        raise ValueError('memory not initialized, or unsafe database path')
    db = sqlite3.connect(path, timeout=5, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA busy_timeout=5000')
    db.execute('PRAGMA synchronous=FULL')
    version = db.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
    if version is None or int(version[0]) != SCHEMA:
        db.close()
        raise ValueError('unsupported database schema; use the matching update-learning version')
    return db


@contextmanager
def transaction(db):
    db.execute('BEGIN IMMEDIATE')
    try:
        yield
        db.commit()
    except BaseException:
        db.rollback()
        raise


def atomic_file(path, content, expected=None):
    path = Path(path)
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError('refusing symlink output')
    path.parent.mkdir(parents=True, exist_ok=True)
    if expected is None and path.exists():
        raise ValueError('new output already exists; refusing overwrite')
    if expected is not None and (not path.exists() or path.read_bytes() != expected):
        raise ValueError('output changed; refusing overwrite')
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.learning-')
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        if expected is None and path.exists():
            raise ValueError('new output appeared; refusing overwrite')
        if expected is not None and path.read_bytes() != expected:
            raise ValueError('output changed; refusing overwrite')
        if expected is None:
            # Publish without replacing a file that appeared after the check.
            os.link(name, path)
        else:
            os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def initialize(root, install=True):
    root = Path(root).resolve()
    folder = root / '.learning'
    if folder.is_symlink():
        raise ValueError('symlinked memory folder')
    folder.mkdir(parents=True, exist_ok=True)
    path = db_path(root)
    if path.is_symlink():
        raise ValueError('symlinked database path')
    if path.exists():
        raise ValueError('memory already exists; use update-learning')
    assets = Path(__file__).resolve().parent.parent / 'assets'
    outputs = {folder / name: Path(__file__).with_name(name).read_bytes()
               for name in ('memory.py', 'schema.sql', 'legacy.py')}
    if install:
        if not all((assets / name).is_file() for name in ('AGENTS.md', 'CLAUDE.md')):
            raise ValueError('initialize from the setup-learning skill, whose assets include the rules')
        outputs.update({root / name: (assets / name).read_bytes() for name in ('AGENTS.md', 'CLAUDE.md')})
    journal = folder / 'init.json'
    expected = {str(p.relative_to(root)): hashlib.sha256(body).hexdigest() for p, body in outputs.items()}
    if journal.is_symlink():
        raise ValueError('symlinked initialization journal')
    recovering = journal.exists()
    if recovering and json.loads(journal.read_text()) != expected:
        raise ValueError('interrupted initialization used different files; reconcile before retrying')
    for target, body in outputs.items():
        if target.is_symlink() or (target.exists() and (
                target.read_bytes() != body or (target.parent == root and not recovering))):
            raise ValueError(f'{target.name} already exists or changed; preserve it and use init --database-only or reconcile')
    if not recovering:
        atomic_file(journal, canonical(expected).encode())
    # A journal makes partial file installation retryable, without claiming ownership
    # of arbitrary existing rules. Publish the database only after all files exist.
    for target, body in outputs.items():
        if not target.exists():
            atomic_file(target, body)
    fd, staging = tempfile.mkstemp(dir=folder, prefix='.init-', suffix='.sqlite3')
    os.close(fd)
    db = sqlite3.connect(staging)
    try:
        db.executescript(Path(__file__).with_name('schema.sql').read_text())
        db.execute('PRAGMA journal_mode=WAL')
    finally:
        db.close()
    try:
        atomic_file(path, Path(staging).read_bytes())
    finally:
        Path(staging).unlink()
    journal.unlink()
    return {'schema': SCHEMA, 'database': str(path), 'version': VERSION}


def check_graph(db):
    nodes = {r['id'] for r in db.execute('SELECT id FROM capabilities')}
    groups = {}
    for row in db.execute('SELECT id,capability_id FROM prerequisite_groups'):
        groups.setdefault(row['capability_id'], []).append((row['id'], []))
    members = {}
    for row in db.execute('SELECT group_id,prerequisite_id FROM prerequisite_members'):
        members.setdefault(row['group_id'], []).append(row['prerequisite_id'])
    ready = set()
    while True:
        before = len(ready)
        for node in nodes - ready:
            if all(any(p in ready for p in members.get(gid, [])) for gid, _ in groups.get(node, [])):
                ready.add(node)
        if len(ready) == before:
            break
    if nodes - ready:
        raise ValueError('empty prerequisite group or hard dependency cycle: ' + ', '.join(sorted(nodes-ready)))


def evidence_used(db, capability, identities):
    # JSON string tokens are quoted/escaped by canonical(), not LIKE patterns.
    # Parse only candidate matches: an escaped quote inside another ID is not a token boundary.
    return any(identity in json.loads(row[0]) for identity in identities for row in db.execute(
        'SELECT assessment_ids FROM applied_evidence WHERE capability_id=? AND instr(assessment_ids,?)>0',
        (capability, canonical(identity))))


def put(db, table, data, importing=False):
    if table not in MUTABLE | APPEND or not isinstance(data, dict) or not data.get('id'):
        raise ValueError('unknown table, missing ID, or invalid record')
    data = dict(data)
    for field in JSON_FIELDS.get(table, ()):
        if isinstance(data.get(field), (dict, list)):
            data[field] = canonical(data[field])
    columns = {r['name'] for r in db.execute(f'PRAGMA table_info({table})')}
    if set(data) - columns:
        raise ValueError(f'unknown {table} fields: {sorted(set(data)-columns)}')
    old = db.execute(f'SELECT * FROM {table} WHERE id=?', (data['id'],)).fetchone()
    archive_only = table == 'notes' and set(data) <= {'id', 'archived'}
    if table in APPEND and old and not archive_only:
        if all(old[k] == v for k, v in data.items()):
            return
        raise ValueError(f'append-only record changed: {table}/{data["id"]}')
    if table == 'capabilities' and DERIVED & data.keys() and not importing:
        raise ValueError('progress is derived from evidence, not direct capability edits')
    if table == 'outcomes' and 'met_on' in data and not importing:
        raise ValueError('outcome achievement is derived from transfer evidence')
    if table == 'assessments':
        current = db.execute('SELECT id FROM current_assessments WHERE attempt_id=?', (data.get('attempt_id'),)).fetchone()
        if current and data.get('supersedes') != current['id']:
            raise ValueError('assessment correction must supersede the current assessment')
        if not current and data.get('supersedes'):
            raise ValueError('invalid superseding assessment')
        if current:
            # Schedule corrections require explicit reconciliation, not a second promotion.
            capability = db.execute('SELECT u.capability_id FROM attempts t JOIN units u ON u.id=t.unit_id WHERE t.id=?',
                                    (data['attempt_id'],)).fetchone()[0]
            affected = evidence_used(db, capability, [current['id']])
            if affected:
                raise ValueError('already applied assessment; reconcile its schedule before correcting')
    if table == 'units' and data.get('verified') and not data.get('verification', '').strip():
        raise ValueError('verified units require a verification method')
    if table == 'tests' and old and set(data) - {'id'}:
        raise ValueError('tests are immutable; close through finalize_tests')
    if table == 'test_items':
        test = db.execute('SELECT closure FROM tests WHERE id=?', (data.get('test_id'),)).fetchone()
        started = db.execute('SELECT 1 FROM attempts a JOIN test_items i ON i.unit_id=a.unit_id WHERE i.test_id=? LIMIT 1',
                             (data.get('test_id'),)).fetchone()
        exposed = db.execute('SELECT 1 FROM attempts WHERE unit_id=? LIMIT 1', (data.get('unit_id'),)).fetchone()
        if not test or test['closure'] != 'active' or started or exposed:
            raise ValueError('test coverage is locked after the first attempt')
    if table == 'sessions' and old and old['active_unit_id'] and data.get('active_unit_id', old['active_unit_id']) != old['active_unit_id']:
        if not db.execute("SELECT 1 FROM attempts WHERE unit_id=? AND (length(response)>0 OR skipped=1)",
                          (old['active_unit_id'],)).fetchone():
            raise ValueError('unanswered active prompt; resume it or record an explicit skip')
    if table in TIME_TABLES and not archive_only:
        field = 'updated_at' if table == 'sessions' else 'created_at'
        data.setdefault(field, now())
    names = list(data)
    marks = ','.join('?' for _ in names)
    sql = f'INSERT INTO {table} ({",".join(names)}) VALUES ({marks})'
    if old:
        fields = [k for k in names if k != 'id']
        if not fields:
            return
        db.execute(f'UPDATE {table} SET '+','.join(k+'=?' for k in fields)+' WHERE id=?',
                   [*[data[k] for k in fields], data['id']])
    else:
        db.execute(sql, [data[k] for k in names])
    if table == 'cycles':
        unit = db.execute('SELECT capability_id FROM units WHERE id=?', (data['unit_id'],)).fetchone()
        if unit['capability_id'] != data['capability_id']:
            raise ValueError('cycle and unit capability mismatch')
        db.execute("UPDATE capabilities SET status='learning' WHERE id=? AND status='planned'", (data['capability_id'],))


def eligible(row):
    return (row['complete'] and row['verified'] and row['unit_verified'] and row['independent']
            and not any(row[k] for k in ('hinted', 'revealed', 'skipped', 'disputed', 'unit_supported', 'unit_reused')))


EVIDENCE_SQL = '''SELECT a.*, t.unit_id,t.hinted,t.revealed,t.skipped,t.created_at AS attempted_at,t.rowid AS attempt_order,
 u.capability_id,u.purpose,u.verified AS unit_verified,u.created_at AS unit_created,
 EXISTS(SELECT 1 FROM attempts exposure WHERE exposure.unit_id=u.id
        AND (exposure.hinted=1 OR exposure.revealed=1 OR exposure.skipped=1)) AS unit_supported,
 EXISTS(SELECT 1 FROM attempts prior WHERE prior.unit_id=u.id AND prior.rowid<t.rowid) AS unit_reused
 FROM current_assessments a JOIN attempts t ON t.id=a.attempt_id JOIN units u ON u.id=t.unit_id'''


def transition(db, capability_id, purpose, evidence, day, identity, resolved_slip=False):
    if not evidence or not all(eligible(r) for r in evidence):
        return False
    ids = sorted(r['id'] for r in evidence)
    if evidence_used(db, capability_id, ids):
        return False
    state = dict(db.execute('SELECT * FROM capabilities WHERE id=?', (capability_id,)).fetchone())
    passed = all(r['score'] == 1 for r in evidence) or (resolved_slip and purpose in ('practice', 'delayed'))
    update = {}
    if purpose == 'placement':
        if not passed or len({r['unit_id'] for r in evidence}) < 2:
            return False
        update['placement'] = 'demonstrated'
        if state['status'] not in ('review', 'solid') and not state['repair']:
            update.update(status='review', interval=3, next_review=str(day+timedelta(days=3)))
    elif purpose == 'transfer' and passed:
        update.update(status='review', repair=0, interval=3, next_review=str(day+timedelta(days=3)))
        db.execute('UPDATE outcomes SET met_on=? WHERE capability_id=? AND met_on IS NULL', (str(day), capability_id))
    elif purpose == 'delayed' and state['status'] in ('review', 'solid') and not state['repair']:
        # The review must be due and conducted on/after the saved due date.
        if not state['next_review'] or str(day) < state['next_review']:
            return False
        if any(r['attempted_at'][:10] < state['next_review'] for r in evidence):
            return False
        old = state['interval'] or 3
        interval = next((n for n in (3, 7, 30, 90) if n > old), 90) if passed else 3
        update.update(status='solid' if passed else 'learning', repair=0 if passed else 1,
                      interval=interval, last_reviewed=str(day), next_review=str(day+timedelta(days=interval)))
        if passed:
            update['retention'] = 'demonstrated'
    if not update:
        return False
    db.execute('UPDATE capabilities SET '+','.join(k+'=?' for k in update)+' WHERE id=?',
               [*update.values(), capability_id])
    db.execute('INSERT INTO applied_evidence VALUES (?,?,?,?,?)', (identity, capability_id, purpose, canonical(ids), str(day)))
    return True


def assess_pending(db, new_ids, day):
    changed = []
    for assessment_id in new_ids:
        row = db.execute(EVIDENCE_SQL+' WHERE a.id=?', (assessment_id,)).fetchone()
        if not row:
            raise ValueError('assessment not found')
        if db.execute('SELECT 1 FROM test_items WHERE unit_id=?', (row['unit_id'],)).fetchone():
            continue
        evidence = [row]
        if row['purpose'] == 'placement':
            evidence = list(db.execute(EVIDENCE_SQL+" WHERE u.capability_id=? AND u.purpose='placement' ORDER BY a.created_at DESC,a.id DESC", (row['capability_id'],)))
            evidence = [r for r in evidence if eligible(r) and r['score'] == 1]
            # Distinct activities, not retries of one prompt.
            unique = {}
            for r in evidence:
                unique.setdefault(r['unit_id'], r)
            evidence = list(unique.values())[:2]
        if transition(db, row['capability_id'], row['purpose'], evidence, day, 'assessment:'+assessment_id):
            changed.append(row['capability_id'])
    return changed


def test_rechecks(db, test):
    """Optional immutable blueprint mapping: recheck unit ID -> original unit ID."""
    try:
        blueprint = json.loads(test['blueprint'])
    except json.JSONDecodeError:
        return {}
    if not isinstance(blueprint, dict) or 'rechecks' not in blueprint:
        return {}
    rechecks = blueprint['rechecks']
    if not isinstance(rechecks, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in rechecks.items()):
        raise ValueError('blueprint rechecks must map recheck unit IDs to original unit IDs')
    if len(set(rechecks.values())) != len(rechecks) or set(rechecks) & set(rechecks.values()):
        raise ValueError('one fresh recheck per original; chained rechecks are not allowed')
    items = {r['id']: r for r in db.execute('''SELECT u.id,u.capability_id,u.purpose,i.ordinal
        FROM test_items i JOIN units u ON u.id=i.unit_id WHERE i.test_id=?''', (test['id'],))}
    for retry, original in rechecks.items():
        a, b = items.get(retry), items.get(original)
        if not a or not b or a['capability_id'] != b['capability_id'] or a['purpose'] != b['purpose'] or a['purpose'] not in ('practice', 'delayed') or a['ordinal'] <= b['ordinal']:
            raise ValueError('declare a later recheck for the same capability and purpose in the same test')
    return rechecks


def finalize_test(db, identity, day):
    test = db.execute('SELECT * FROM tests WHERE id=?', (identity,)).fetchone()
    if not test:
        raise ValueError('test not found')
    if test['closure'] != 'active':
        return []
    units = rows(db, 'SELECT u.* FROM test_items i JOIN units u ON u.id=i.unit_id WHERE i.test_id=? ORDER BY i.ordinal', (identity,))
    if not units:
        raise ValueError('test has no predeclared coverage')
    rechecks = test_rechecks(db, test)
    reverse = {original: retry for retry, original in rechecks.items()}
    groups = {}
    for unit in units:
        if unit['id'] in rechecks:
            continue
        groups.setdefault((unit['capability_id'], unit['purpose']), []).append(unit['id'])
    changed, partial = [], False
    incomplete = set()
    prepared = []
    for (capability, purpose), unit_ids in groups.items():
        evidence = []
        for unit_id in unit_ids:
            candidates = list(db.execute(EVIDENCE_SQL+''' WHERE u.id=?
                AND t.rowid=(SELECT max(rowid) FROM attempts WHERE unit_id=u.id)''', (unit_id,)))
            if not candidates or not eligible(candidates[0]):
                partial = True
                incomplete.add(capability)
                break
            evidence.extend(candidates)
        else:
            failures = [r for r in evidence if r['score'] != 1]
            resolved = False
            if len(failures) == 1 and failures[0]['failure_type'] == 'slip':
                original = failures[0]
                retry_id = reverse.get(original['unit_id'])
                retry = db.execute(EVIDENCE_SQL+''' WHERE u.id=?
                    AND t.rowid=(SELECT max(rowid) FROM attempts WHERE unit_id=u.id)''', (retry_id,)).fetchone()
                if retry_id and (not retry or not eligible(retry)):
                    partial = True
                    incomplete.add(capability)
                elif retry and retry['score'] == 1 and retry['attempt_order'] > original['attempt_order'] and retry['attempted_at'] >= original['attempted_at']:
                    evidence.append(retry)
                    resolved = True
            prepared.append((capability, purpose, evidence, resolved))
    # Missing coverage in any purpose leaves the entire capability unchanged.
    for capability, purpose, evidence, resolved in prepared:
        if capability not in incomplete and transition(db, capability, purpose, evidence, day,
                'test:'+identity+':'+capability+':'+purpose, resolved_slip=resolved):
            changed.append(capability)
    db.execute('UPDATE tests SET closure=? WHERE id=?', ('partial' if partial else 'closed', identity))
    return changed


def apply(db, payload, importing=False, fingerprint=None):
    if not isinstance(payload, dict) or not payload.get('operation_id'):
        raise ValueError('operation_id required')
    fingerprint = fingerprint or digest(payload)
    with transaction(db):
        old = db.execute('SELECT * FROM operations WHERE id=?', (payload['operation_id'],)).fetchone()
        if old:
            if old['digest'] != fingerprint:
                raise ValueError('operation ID reused with different content')
            return json.loads(old['result'])
        if not importing and type(payload.get('expected_revision')) is not int:
            raise ValueError('expected_revision required')
        if payload.get('expected_revision', revision(db)) != revision(db):
            raise ValueError('stale revision; reload targeted context')
        day = date.fromisoformat(payload.get('today', str(date.today())))
        assessment_ids, graph_changed, tests_changed = [], False, set()
        for record in payload.get('records', []):
            table, data = record['table'], record['data']
            if table in {'prerequisite_groups', 'prerequisite_members'} or (
                    table == 'capabilities' and not db.execute('SELECT 1 FROM capabilities WHERE id=?', (data['id'],)).fetchone()):
                graph_changed = True
            put(db, table, data, importing)
            if table == 'assessments':
                assessment_ids.append(data['id'])
            if table in {'tests', 'test_items'}:
                tests_changed.add(data['id'] if table == 'tests' else data['test_id'])
        if graph_changed:
            check_graph(db)
        for identity in tests_changed:
            test_rechecks(db, db.execute('SELECT * FROM tests WHERE id=?', (identity,)).fetchone())
        changed = assess_pending(db, assessment_ids, day)
        for identity in payload.get('finalize_tests', []):
            changed.extend(finalize_test(db, identity, day))
        db.execute("UPDATE meta SET value=CAST(value AS INTEGER)+1 WHERE key='revision'")
        saved = {}
        for record in payload.get('records', []):
            identities = saved.setdefault(record['table'], [])
            if record['data']['id'] not in identities:
                identities.append(record['data']['id'])
        result = {'revision': revision(db), 'changed_capabilities': sorted(set(changed)), 'saved': saved}
        db.execute('INSERT INTO operations VALUES (?,?,?,?)', (payload['operation_id'], fingerprint, canonical(result), now()))
    return result


def turn(db, payload):
    """Compact hot-path wrapper. Expand one teaching turn to one atomic apply."""
    allowed = {'operation_id', 'expected_revision', 'today', 'capability', 'unit', 'explanation',
               'attempt', 'assessment', 'session', 'finalize_tests'}
    if not isinstance(payload, dict) or set(payload)-allowed or not payload.get('operation_id'):
        raise ValueError('invalid turn fields or missing operation_id')
    fingerprint = digest(payload)
    previous = db.execute('SELECT digest,result FROM operations WHERE id=?', (payload['operation_id'],)).fetchone()
    if previous:
        if previous['digest'] != fingerprint:
            raise ValueError('operation ID reused with different content')
        return json.loads(previous['result'])
    operation = payload['operation_id']
    def new_id(suffix):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, 'learn-anything:'+operation+':'+suffix))
    records = []
    def add(table, data):
        records.append({'table': table, 'data': data})
    cap = payload.get('capability')
    if cap:
        add('capabilities', cap)
    session = dict(payload.get('session', {}))
    current = db.execute("SELECT * FROM sessions WHERE closure!='closed' ORDER BY (closure='active') DESC,updated_at DESC LIMIT 1").fetchone()
    session.setdefault('id', current['id'] if current else new_id('session'))
    # A new session must precede its attempts to satisfy their foreign key.
    if not db.execute('SELECT 1 FROM sessions WHERE id=?', (session['id'],)).fetchone():
        add('sessions', {k: v for k, v in session.items() if k != 'active_unit_id'})
    attempt = payload.get('attempt')
    if attempt:
        attempt = dict(attempt)
        attempt.setdefault('id', new_id('attempt'))
        attempt.setdefault('session_id', session['id'])
        for flag in ('hinted', 'revealed', 'skipped'):
            # Explicit support flags keep exposure distinct from retrieval.
            if flag not in attempt:
                raise ValueError('turn attempt requires hinted, revealed and skipped flags')
        add('attempts', attempt)
    assessment = payload.get('assessment')
    if assessment:
        assessment = dict(assessment)
        assessment.setdefault('id', new_id('assessment'))
        if attempt:
            assessment.setdefault('attempt_id', attempt['id'])
        add('assessments', assessment)
    unit = payload.get('unit')
    if unit:
        unit = dict(unit)
        unit.setdefault('id', new_id('unit'))
        unit.setdefault('version', '1')
        unit.setdefault('purpose', 'practice')
        unit.setdefault('verified', bool(unit.get('verification')))
        if cap:
            unit.setdefault('capability_id', cap['id'])
        add('units', unit)
        if 'explanation' in payload:
            add('cycles', {'id': new_id('cycle'), 'capability_id': unit['capability_id'],
                           'unit_id': unit['id'], 'explanation': payload['explanation']})
    if unit:
        session.setdefault('active_unit_id', unit['id'])
    elif attempt and current and current['active_unit_id'] == attempt['unit_id'] and (attempt.get('response') or attempt['skipped']):
        session.setdefault('active_unit_id', None)
    if current and current['closure'] == 'paused' and 'closure' not in session:
        session['closure'] = 'active'
    add('sessions', session)
    batch = {key: payload[key] for key in ('operation_id', 'expected_revision', 'today', 'finalize_tests') if key in payload}
    batch['records'] = records
    return apply(db, batch, fingerprint=fingerprint)


def context(db, capability=None, topic=None, limit=5):
    limit = max(1, min(limit, 50))
    result = {'revision': revision(db)}
    result['session'] = rows(db, "SELECT * FROM sessions WHERE closure!='closed' ORDER BY (closure='active') DESC,updated_at DESC LIMIT 1")
    if result['session'] and result['session'][0]['active_unit_id']:
        unit = rows(db, 'SELECT id,capability_id,purpose,prompt,version FROM units WHERE id=?', (result['session'][0]['active_unit_id'],))
        result['active_prompt'] = unit
        if unit and not capability and not topic:
            capability = unit[0]['capability_id']
    if capability:
        result['capability'] = rows(db, 'SELECT * FROM capability_state WHERE id=?', (capability,))
        result['recent'] = rows(db, '''SELECT u.id AS unit_id,substr(u.prompt,1,1600) AS prompt,u.purpose,
          substr(c.explanation,1,1600) AS explanation,t.id AS attempt_id,
          substr(t.response,1,1600) AS response,a.id AS assessment_id,a.score,substr(a.feedback,1,1600) AS feedback FROM units u
          LEFT JOIN cycles c ON c.unit_id=u.id LEFT JOIN attempts t ON t.unit_id=u.id
          LEFT JOIN current_assessments a ON a.attempt_id=t.id WHERE u.capability_id=?
          ORDER BY u.created_at DESC,t.created_at DESC LIMIT ?''', (capability, limit))
        result['notes'] = rows(db, "SELECT id,kind,substr(body,1,2000) AS body FROM notes WHERE capability_id=? AND archived=0 AND kind!='legacy' ORDER BY created_at DESC LIMIT ?", (capability, limit))
        result['excerpt_limit'] = 'Recent fields: 1600 characters; note bodies: 2000. Use get for the full record when needed.'
        result['prerequisites'] = rows(db, '''SELECT g.id AS group_id,c.id,c.title,c.status FROM prerequisite_groups g
          JOIN prerequisite_members m ON m.group_id=g.id JOIN capabilities c ON c.id=m.prerequisite_id WHERE g.capability_id=?''', (capability,))
    elif topic:
        result['topic'] = rows(db, 'SELECT * FROM topics WHERE id=?', (topic,))
        result['frontier'] = rows(db, '''SELECT c.* FROM capability_state c JOIN topic_capabilities t ON t.capability_id=c.id
          WHERE t.topic_id=? AND c.archived=0 AND (c.map_class='next' OR c.repair=1
           OR (c.status IN ('review','solid') AND c.next_review<=?))
          ORDER BY c.repair DESC,(c.next_review<=?) DESC,c.next_review,c.title LIMIT ?''',
          (topic, str(date.today()), str(date.today()), limit))
        result['members'] = rows(db, '''SELECT c.id,c.title,c.status,c.map_class FROM capability_state c
          JOIN topic_capabilities t ON t.capability_id=c.id WHERE t.topic_id=? AND c.archived=0 LIMIT 50''', (topic,))
        result['outcomes'] = rows(db, 'SELECT * FROM outcomes WHERE topic_id=? LIMIT 50', (topic,))
    else:
        result['due'] = due(db, str(date.today()), limit)
        result['repair'] = rows(db, 'SELECT id,title,status FROM capabilities WHERE repair=1 AND archived=0 LIMIT ?', (limit,))
    return result


def due(db, today, limit=20):
    date.fromisoformat(today)
    return rows(db, "SELECT id,title,status,interval,next_review FROM capabilities WHERE archived=0 AND status IN ('review','solid') AND next_review<=? ORDER BY next_review,id LIMIT ?", (today, min(max(limit, 1), 100)))


def search(db, text, limit=10):
    # Small bounded results; ID lookups/context and due queues use indexes.
    pattern = '%'+text.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')+'%'
    return rows(db, '''SELECT 'capability' AS type,id,title,substr(objective,1,240) AS excerpt FROM capabilities WHERE title LIKE ? ESCAPE '\\' OR objective LIKE ? ESCAPE '\\'
      UNION ALL SELECT 'topic',id,title,substr(goal,1,240) FROM topics WHERE title LIKE ? ESCAPE '\\' OR goal LIKE ? ESCAPE '\\'
      UNION ALL SELECT 'note',id,title,substr(body,1,240) FROM notes WHERE title LIKE ? ESCAPE '\\' OR body LIKE ? ESCAPE '\\'
      UNION ALL SELECT 'source',id,title,substr(body,1,240) FROM sources WHERE title LIKE ? ESCAPE '\\' OR body LIKE ? ESCAPE '\\'
      LIMIT ?''', (*([pattern]*8), min(max(limit, 1), 50)))


def get(db, table, identity, keys=False):
    if table not in MUTABLE | APPEND | {'legacy_documents', 'summary_snapshots', 'applied_evidence'}:
        raise ValueError('unknown readable table')
    result = rows(db, f'SELECT * FROM {table} WHERE id=?', (identity,))
    if table == 'units' and not keys:
        for row in result:
            row.pop('answer', None)
            row.pop('rubric', None)
    if table == 'legacy_documents':
        for row in result:
            row['raw'] = row['raw'].decode('utf-8')
    return result


def backup(db, target):
    path = Path(target)
    if path.exists() or path.is_symlink():
        raise ValueError('backup target exists')
    path.parent.mkdir(parents=True, exist_ok=True)
    dest = sqlite3.connect(path)
    try:
        db.backup(dest)
    finally:
        dest.close()
    os.chmod(path, 0o600)
    return {'backup': str(path)}


def optimize(db):
    """Explicit index-only update for existing schema-1 folders; no logical writes."""
    statements = Path(__file__).with_name('schema.sql').read_text().split(';')
    indexes = [sql.strip() for sql in statements if sql.strip().startswith('CREATE INDEX IF NOT EXISTS')]
    with transaction(db):
        for sql in indexes:
            db.execute(sql)
    return {'schema': SCHEMA, 'indexes_checked': len(indexes), 'revision': revision(db)}


def summary_context(db, limit=100):
    """Explicit, bounded synthesis input. Not called by context/apply/export."""
    limit = max(1, min(limit, 500))
    return {
        'revision': revision(db),
        'status_counts': rows(db, 'SELECT status,count(*) AS count FROM capabilities WHERE archived=0 GROUP BY status'),
        'topic_rollup': rows(db, '''SELECT t.id,t.title,count(c.id) AS capabilities,
          sum(c.status='solid') AS solid,sum(c.status='review') AS review,sum(c.repair=1) AS repair
          FROM topics t LEFT JOIN topic_capabilities tc ON tc.topic_id=t.id
          LEFT JOIN capabilities c ON c.id=tc.capability_id AND c.archived=0
          WHERE t.archived=0 GROUP BY t.id ORDER BY t.title LIMIT ?''', (limit,)),
        'topics': rows(db, 'SELECT * FROM topics WHERE archived=0 LIMIT ?', (limit,)),
        'capabilities': rows(db, 'SELECT * FROM capability_state WHERE archived=0 ORDER BY last_reviewed DESC,next_review DESC LIMIT ?', (limit,)),
        'outcomes': rows(db, 'SELECT * FROM outcomes LIMIT ?', (limit,)),
        'evidence': rows(db, '''SELECT a.id,a.score,a.feedback,a.independent,a.complete,a.verified,a.disputed,a.created_at,
          t.id AS attempt_id,substr(t.response,1,1600) AS response,t.hinted,t.revealed,t.skipped,u.id AS unit_id,u.version,u.capability_id,u.purpose,u.verified AS unit_verified,
          EXISTS(SELECT 1 FROM attempts exposure WHERE exposure.unit_id=u.id
           AND (exposure.hinted=1 OR exposure.revealed=1 OR exposure.skipped=1)) AS unit_supported,
          EXISTS(SELECT 1 FROM attempts prior WHERE prior.unit_id=u.id AND prior.rowid<t.rowid) AS unit_reused
          FROM current_assessments a JOIN attempts t ON t.id=a.attempt_id JOIN units u ON u.id=t.unit_id
          ORDER BY a.created_at DESC LIMIT ?''', (limit,)),
        'notes': rows(db, 'SELECT id,title,kind,substr(body,1,2000) AS body FROM notes WHERE archived=0 ORDER BY created_at DESC LIMIT ?', (limit,)),
        'preferences': rows(db, 'SELECT * FROM preferences LIMIT ?', (limit,)),
        'questions': rows(db, "SELECT * FROM questions WHERE disposition!='resolved' LIMIT ?", (limit,)),
        'sessions': rows(db, 'SELECT * FROM sessions ORDER BY updated_at DESC LIMIT 3'),
        'previous_summary': rows(db, 'SELECT id,body,created_at FROM summary_snapshots ORDER BY rowid DESC LIMIT 1'),
        'limit_per_section': limit,
        'note': 'Bounded input, not a complete vault scan. Responses/notes are excerpts (1600/2000 chars); use get/search for missing evidence and label gaps.'
    }


def save_summary(db, root, payload):
    """Only this explicit command writes My Summary.md. Retry the same ID after a crash."""
    required = {'id', 'request', 'body', 'evidence_ids', 'expected_revision'}
    if not required <= set(payload) or set(payload)-required-{'expected_file_hash'} or not str(payload['request']).strip():
        raise ValueError('summary requires id, explicit user request, body, evidence_ids, expected_revision')
    if not isinstance(payload['body'], str) or not payload['body'].startswith('# My Summary\n'):
        raise ValueError('summary must start with # My Summary')
    if not isinstance(payload['evidence_ids'], list):
        raise ValueError('evidence_ids must be a list of table:id references')
    body = payload['body'].encode('utf-8')
    path = Path(root) / 'My Summary.md'
    with transaction(db):
        old = db.execute('SELECT * FROM summary_snapshots WHERE id=?', (payload['id'],)).fetchone()
        if old:
            if old['request'] != payload['request'] or old['body'] != payload['body'] or json.loads(old['evidence_ids']) != payload['evidence_ids']:
                raise ValueError('summary ID reused with different content')
            latest = db.execute('SELECT id FROM summary_snapshots ORDER BY rowid DESC LIMIT 1').fetchone()[0]
            if latest != payload['id']:
                raise ValueError('cannot republish an older snapshot over the latest summary')
        else:
            if payload['expected_revision'] != revision(db):
                raise ValueError('stale summary context; reload before summarizing')
            allowed = {'topics', 'capabilities', 'attempts', 'assessments', 'notes', 'preferences', 'outcomes', 'questions', 'sessions', 'legacy_documents'}
            for ref in payload['evidence_ids']:
                table, identity = ref.split(':', 1)
                if table not in allowed or not db.execute(f'SELECT 1 FROM {table} WHERE id=?', (identity,)).fetchone():
                    raise ValueError('unknown summary evidence: '+ref)
            previous = db.execute("SELECT value FROM meta WHERE key='summary_file_hash'").fetchone()
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
            merged = payload.get('expected_file_hash') and payload['expected_file_hash'] == actual_hash
            if path.is_symlink() or (path.exists() and not merged and (not previous or actual_hash != previous[0])):
                raise ValueError('My Summary.md has owner edits or is unowned; preserve/merge them before saving')
            db.execute('INSERT INTO summary_snapshots VALUES (?,?,?,?,?,?)',
                       (payload['id'], payload['request'], payload['body'], canonical(payload['evidence_ids']), revision(db), now()))
            db.execute("UPDATE meta SET value=CAST(value AS INTEGER)+1 WHERE key='revision'")
    # DB snapshot commits first. A failed file write is recoverable with the same payload ID.
    with transaction(db):
        latest = db.execute('SELECT id FROM summary_snapshots ORDER BY rowid DESC LIMIT 1').fetchone()[0]
        if latest != payload['id']:
            raise ValueError('a newer snapshot exists; refusing stale publication')
        expected = path.read_bytes() if path.exists() else None
        previous = db.execute("SELECT value FROM meta WHERE key='summary_file_hash'").fetchone()
        wanted = hashlib.sha256(body).hexdigest()
        if expected is not None and hashlib.sha256(expected).hexdigest() not in {wanted, previous[0] if previous else None, payload.get('expected_file_hash')}:
            raise ValueError('summary snapshot saved; output has owner edits, refusing overwrite')
        atomic_file(path, body, expected)
        db.execute("INSERT INTO meta VALUES ('summary_file_hash',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (wanted,))
    return {'summary': str(path), 'snapshot_id': payload['id'], 'revision': revision(db)}


def filename(title, identity):
    safe = ''.join(c if c.isalnum() or c in ' -_' else '-' for c in title).strip(' .')[:70] or 'Note'
    return safe+'--'+hashlib.sha256(identity.encode()).hexdigest()[:12]


def export_markdown(db, root, target, include_keys=False):
    """Publish a consistent snapshot to a NEW folder; never overwrite owner notes."""
    target = Path(target).absolute()
    if target.is_symlink() or any(p.is_symlink() for p in target.parents):
        raise ValueError('symlink export target')
    if target.exists():
        raise ValueError('export target must be a new folder; existing exports/notes are not overwritten')
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(dir=target.parent, prefix='.learning-export-'))
    manifest = {}

    def emit(relative, content):
        path = staging / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode('utf-8'))
        manifest[relative] = hashlib.sha256(path.read_bytes()).hexdigest()

    db.execute('BEGIN')
    try:
        rev = revision(db)
        capabilities = rows(db, 'SELECT * FROM capability_state ORDER BY title,id')
        names = {c['id']: filename(c['title'], c['id']) for c in capabilities}
        node_ids = {c['id']: 'N'+hashlib.sha256(c['id'].encode()).hexdigest()[:12] for c in capabilities}

        def grouped(sql, key):
            result = {}
            for row in db.execute(sql):
                result.setdefault(row[key], []).append(dict(row))
            return result

        units_by_capability = grouped('''SELECT u.*,c.explanation FROM units u
            LEFT JOIN cycles c ON c.unit_id=u.id ORDER BY u.created_at,u.id''', 'capability_id')
        attempts_by_unit = grouped('SELECT * FROM attempts ORDER BY created_at,id', 'unit_id')
        grades_by_attempt = grouped('SELECT * FROM assessments ORDER BY created_at,id', 'attempt_id')
        notes_by_capability = grouped('SELECT * FROM notes ORDER BY created_at,id', 'capability_id')
        members_by_topic = grouped('''SELECT c.*,t.topic_id FROM capability_state c
            JOIN topic_capabilities t ON t.capability_id=c.id ORDER BY c.title,c.id''', 'topic_id')
        dependencies = grouped('''SELECT g.capability_id,m.prerequisite_id FROM prerequisite_groups g
            JOIN prerequisite_members m ON m.group_id=g.id ORDER BY g.id,m.prerequisite_id''', 'capability_id')
        outcomes_by_topic = grouped('SELECT * FROM outcomes ORDER BY id', 'topic_id')
        units_by_test = grouped('''SELECT i.test_id,i.ordinal,u.id,u.capability_id,u.prompt FROM test_items i
            JOIN units u ON u.id=i.unit_id ORDER BY i.ordinal''', 'test_id')
        for cap in capabilities:
            identity = cap['id']
            props = {k: cap[k] for k in ('status', 'kind', 'placement', 'retention', 'repair', 'interval', 'last_reviewed', 'next_review')}
            props['capability_id'] = identity
            header = '---\n'+'\n'.join(k+': '+json.dumps(v, ensure_ascii=False) for k, v in props.items())+'\n---\n'
            content = header+'# '+cap['title']+'\n\n'+cap['objective']+'\n'
            for unit in units_by_capability.get(identity, []):
                content += '\n## '+unit['purpose']+' · '+unit['id']+'\n\n'
                if unit['explanation']:
                    content += unit['explanation']+'\n\n'
                content += '### Activity\n\n'+unit['prompt']+'\n'
                if include_keys:
                    content += '\n> [!success]- Answer\n'+'\n'.join('> '+line for line in unit['answer'].splitlines())+'\n'
                for attempt in attempts_by_unit.get(unit['id'], []):
                    content += '\n### My attempt · '+attempt['id']+'\n\n'+attempt['response']+'\n'
                    for grade in grades_by_attempt.get(attempt['id'], []):
                        content += '\n### Analysis · '+grade['id']+'\n\n'+grade['feedback']+'\n'
            for note in notes_by_capability.get(identity, []):
                content += '\n## '+('In my words' if note['kind'] == 'own_words' else note['title'])+'\n\n'+note['body']+'\n'
            emit('Lessons/'+names[identity]+'.md', content)
        for topic in rows(db, 'SELECT * FROM topics ORDER BY title,id'):
            members = members_by_topic.get(topic['id'], [])
            graph = ['graph TD']
            for c in members:
                label = c['title'].replace('"', '&quot;').replace('\n', ' ')
                graph.append('    '+node_ids[c['id']]+'("'+label+'"):::'+c['map_class'])
                for dep in dependencies.get(c['id'], []):
                    graph.append('    '+node_ids[dep['prerequisite_id']]+' --> '+node_ids[c['id']])
            content = '# '+topic['title']+'\n\n## Goal\n\n'+topic['goal']+'\n\n'+topic['long_term']+'\n\n'+topic['path']
            content += '\n\n## Map\n\n```mermaid\n'+'\n'.join(graph)+'\n```\n\nOR alternatives share a prerequisite group in SQLite; arrows alone do not show that formula.\n'
            content += '\n'.join('- [[Lessons/'+names[c['id']]+']]' for c in members)+'\n\n## Outcomes\n\n'
            content += '\n'.join('- '+o['description']+': '+(o['met_on'] or 'not yet') for o in outcomes_by_topic.get(topic['id'], []))+'\n'
            emit('Maps/'+filename(topic['title'], topic['id'])+'.md', content)
        for note in notes_by_capability.get(None, []):
            emit('Notes/'+filename(note['title'], note['id'])+'.md', '# '+note['title']+'\n\n'+note['body'])
        for source in rows(db, 'SELECT * FROM sources ORDER BY id'):
            emit('References/'+filename(source['title'], source['id'])+'.md', '# '+source['title']+'\n\n'+source['url']+'\n\n'+source['body'])
        for test in rows(db, 'SELECT * FROM tests ORDER BY id'):
            content = '# Test '+test['id']+'\n\n'+test['blueprint']+'\n\nStatus: '+test['closure']+'\n'
            for unit in units_by_test.get(test['id'], []):
                content += '\n## Q'+str(unit['ordinal'])+'\n\n'+unit['prompt']+'\n\n[[Lessons/'+names[unit['capability_id']]+']]\n'
            emit('Tests/'+filename('Test', test['id'])+'.md', content)
        emit('Sessions/Current.md', '# Saved sessions\n\n```json\n'+json.dumps(rows(db, 'SELECT * FROM sessions'), indent=2, ensure_ascii=False)+'\n```\n')
        emit('Sessions/Questions.md', '# Saved questions\n\n'+'\n'.join('- '+q['text']+' ('+q['disposition']+')' for q in rows(db, 'SELECT * FROM questions'))+'\n')
        for legacy in db.execute('SELECT * FROM legacy_documents'):
            emit('Legacy/'+filename(Path(legacy['path']).stem, legacy['id'])+'.md', legacy['raw'])
        existing_summary = Path(root) / 'My Summary.md'
        if existing_summary.is_file() and not existing_summary.is_symlink():
            emit('My Summary.md', existing_summary.read_bytes())
        emit('README.md', '# Learning snapshot\n\nRead-only export at database revision '+str(rev)+'. SQLite remains authoritative; edits here are not imported automatically. Structured unit answer keys '+('included (not secure).' if include_keys else 'omitted.')+' Imported prose and Legacy files may contain original keys; inspect before sharing.\n')
        emit('Dashboard.base', 'views:\n  - type: table\n    name: Lessons\n    filters: file.inFolder("Lessons")\n    order:\n      - file.name\n      - status\n      - next_review\n')
        emit('manifest.json', json.dumps({'revision': rev, 'files': manifest}, indent=2))
        db.commit()
        staging.rename(target)
    except BaseException:
        db.rollback()
        # Only our own scratch directory, never a user target.
        shutil.rmtree(staging)
        raise
    return {'export': str(target), 'revision': rev, 'files': len(manifest)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--database-only', action='store_true')
    read = sub.add_parser('context')
    read.add_argument('--capability')
    read.add_argument('--topic')
    read.add_argument('--limit', type=int, default=5)
    find = sub.add_parser('search')
    find.add_argument('text')
    find.add_argument('--limit', type=int, default=10)
    exact = sub.add_parser('get')
    exact.add_argument('table')
    exact.add_argument('id')
    exact.add_argument('--keys', action='store_true')
    write = sub.add_parser('apply')
    write.add_argument('payload', help='JSON file, or - for stdin')
    fast = sub.add_parser('turn')
    fast.add_argument('payload', help='Compact teaching turn JSON file, or - for stdin')
    reviews = sub.add_parser('due')
    reviews.add_argument('--today', default=str(date.today()))
    save = sub.add_parser('backup')
    save.add_argument('target', type=Path)
    sub.add_parser('check')
    sub.add_parser('optimize', help='Install compatible indexes after an explicit runtime update')
    summary = sub.add_parser('summary-context')
    summary.add_argument('--limit', type=int, default=100)
    summary_write = sub.add_parser('summary-save')
    summary_write.add_argument('payload')
    publish = sub.add_parser('export')
    publish.add_argument('target', type=Path)
    publish.add_argument('--include-keys', action='store_true')
    migration = sub.add_parser('import-markdown')
    migration.add_argument('source', type=Path)
    migration.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.command == 'init':
        result = initialize(args.root, not args.database_only)
    elif args.command == 'import-markdown':
        from legacy import import_markdown
        result = import_markdown(args.root, args.source, args.dry_run)
    else:
        db = connect(args.root)
        try:
            if args.command == 'context':
                result = context(db, args.capability, args.topic, args.limit)
            elif args.command == 'search':
                result = search(db, args.text, args.limit)
            elif args.command == 'get':
                result = get(db, args.table, args.id, args.keys)
            elif args.command in ('apply', 'turn', 'summary-save'):
                payload = json.load(sys.stdin) if args.payload == '-' else json.loads(Path(args.payload).read_text())
                if args.command == 'summary-save':
                    result = save_summary(db, args.root, payload)
                else:
                    result = (turn if args.command == 'turn' else apply)(db, payload)
            elif args.command == 'due':
                result = due(db, args.today)
            elif args.command == 'backup':
                result = backup(db, args.target)
            elif args.command == 'optimize':
                result = optimize(db)
            elif args.command == 'check':
                check_graph(db)
                result = {'integrity': db.execute('PRAGMA integrity_check').fetchone()[0], 'foreign_key_errors': rows(db, 'PRAGMA foreign_key_check'), 'revision': revision(db)}
            elif args.command == 'summary-context':
                result = summary_context(db, args.limit)
            elif args.command == 'export':
                result = export_markdown(db, args.root, args.target, args.include_keys)
        finally:
            db.close()
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        raise SystemExit(2)
