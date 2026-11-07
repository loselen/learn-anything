#!/usr/bin/env python3
"""Explicit read-only SQLite projections for the optional policy helpers."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sqlite3
import sys


def connect(root):
    path = Path(root).absolute()/'.learning/memory.sqlite3'
    if not path.is_file() or path.is_symlink() or path.parent.is_symlink():
        raise ValueError('unsafe or uninitialized learning memory')
    db = sqlite3.connect(path.as_uri()+'?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA query_only=ON')
    version = db.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
    if not version or version[0] != '1':
        db.close()
        raise ValueError('unsupported memory schema')
    return db


def selection(db, config):
    """Host supplies consent/candidate metadata, never reconstructed grades or status."""
    required = {'today', 'mode', 'allowed_topics', 'goal_topic', 'goal_capability_ids',
                'budget_minutes', 'sustained_work', 'challenge', 'candidates', 'taught_capability_ids'}
    if not isinstance(config, dict) or not required <= set(config) or set(config)-required-{'batch_remaining', 'active_topic'}:
        raise ValueError('selection config requires explicit consent, scope, candidates and taught_capability_ids')
    snapshot = {k: v for k, v in config.items() if k not in {'taught_capability_ids', 'active_topic'}}
    taught = config['taught_capability_ids']
    if not isinstance(taught, list) or not all(isinstance(identity, str) for identity in taught):
        raise ValueError('taught_capability_ids must explicitly assert full taught scope; placement is not teaching')
    pending = list(config['goal_capability_ids'])+[c['capability_id'] for c in config['candidates']]
    nodes = {}
    while pending:
        identity = pending.pop()
        if identity in nodes:
            continue
        row = db.execute('SELECT * FROM capabilities WHERE id=? AND archived=0', (identity,)).fetchone()
        if not row:
            continue
        groups = {}
        for member in db.execute('''SELECT g.id,m.prerequisite_id FROM prerequisite_groups g
            JOIN prerequisite_members m ON m.group_id=g.id WHERE g.capability_id=? ORDER BY g.id,m.prerequisite_id''', (identity,)):
            groups.setdefault(member['id'], []).append(member['prerequisite_id'])
        nodes[identity] = dict(status=row['status'], taught=identity in taught,
                               prerequisites=[], prerequisite_groups=list(groups.values()))
        pending.extend(p for group in groups.values() for p in group)
    snapshot['capabilities'] = nodes
    # Only candidate identities matter; do not export every historical unit ID.
    snapshot['seen_units'] = []
    for identity in sorted({c['id'] for c in config['candidates']}):
        unit = db.execute('SELECT id,version FROM units WHERE id=?', (identity,)).fetchone()
        if unit:
            snapshot['seen_units'].append(unit['id']+'@'+unit['version'])
    snapshot['active_unit'] = None
    session = db.execute("SELECT * FROM sessions WHERE closure!='closed' ORDER BY (closure='active') DESC,updated_at DESC LIMIT 1").fetchone()
    if session and session['active_unit_id']:
        unit = db.execute('SELECT id,version,capability_id FROM units WHERE id=?', (session['active_unit_id'],)).fetchone()
        topic = session['topic_id'] or config.get('active_topic')
        if not topic:
            memberships = list(db.execute('SELECT topic_id FROM topic_capabilities WHERE capability_id=?', (unit['capability_id'],)))
            if len(memberships) != 1:
                raise ValueError('active task has no unambiguous topic; supply active_topic rather than guessing consent')
            topic = memberships[0]['topic_id']
        snapshot['active_unit'] = dict(id=unit['id'], version=unit['version'], topic=topic,
                                       prompt_reference='units:'+unit['id'])
    scope = sorted(nodes)
    snapshot['repeated_misconceptions'] = [r['capability_id'] for r in db.execute('''
        SELECT u.capability_id FROM current_assessments a JOIN attempts t ON t.id=a.attempt_id
        JOIN units u ON u.id=t.unit_id JOIN capabilities c ON c.id=u.capability_id
        WHERE (c.repair=1 OR c.status='learning') AND c.archived=0 AND a.failure_type='bug' AND a.score<1
          AND a.complete=1 AND a.verified=1 AND a.disputed=0
          AND u.capability_id IN ('''+','.join('?' for _ in scope)+''')
        GROUP BY u.capability_id HAVING count(DISTINCT u.id)>=2''', scope)] if scope else []
    candidates = []
    for candidate in config['candidates']:
        candidate = dict(candidate)
        state = db.execute('SELECT next_review FROM capabilities WHERE id=? AND archived=0', (candidate['capability_id'],)).fetchone()
        if candidate['source'] == 'due_review' and state:
            candidate['purpose'], candidate['due_date'] = 'review', state['next_review']
        elif candidate['source'] == 'repair':
            candidate['purpose'] = 'repair'
        candidates.append(candidate)
    snapshot['candidates'] = candidates
    snapshot['memory_revision'] = int(db.execute("SELECT value FROM meta WHERE key='revision'").fetchone()[0])
    return snapshot


def observations(db, topic, identities):
    if not isinstance(identities, list) or not all(isinstance(identity, str) for identity in identities):
        raise ValueError('assessment IDs must be an explicit list')
    result = []
    for identity in dict.fromkeys(identities):
        row = db.execute('''SELECT a.*,t.unit_id,t.hinted,t.revealed,t.skipped,t.created_at AS attempted_at,
            u.version,u.capability_id,u.purpose,u.challenge,u.verified AS unit_verified,
            EXISTS(SELECT 1 FROM attempts x WHERE x.unit_id=u.id AND (x.hinted=1 OR x.revealed=1 OR x.skipped=1)) AS supported,
            EXISTS(SELECT 1 FROM attempts x WHERE x.unit_id=u.id AND x.rowid<t.rowid) AS reused,
            (SELECT max(c.created_at) FROM cycles c WHERE c.capability_id=u.capability_id AND c.created_at<=t.created_at) AS taught_at
            FROM current_assessments a JOIN attempts t ON t.id=a.attempt_id JOIN units u ON u.id=t.unit_id
            JOIN topic_capabilities tc ON tc.capability_id=u.capability_id
            WHERE a.id=? AND tc.topic_id=?''', (identity, topic)).fetchone()
        if not row:
            raise ValueError('unknown, superseded or out-of-topic assessment: '+identity)
        if row['purpose'] == 'placement':
            continue
        delay = 0
        if row['taught_at']:
            delay = max(0, (datetime.fromisoformat(row['attempted_at'])-datetime.fromisoformat(row['taught_at'])).total_seconds()/86400)
        result.append(dict(assessment_id=identity, attempt_id=row['attempt_id'], unit_id=row['unit_id'],
            unit_version=row['version'], capability_id=row['capability_id'], topic=topic,
            challenge=row['challenge'], purpose=row['purpose'], independent=bool(row['independent'] and not row['supported'] and not row['reused'] and not row['skipped']),
            hinted=bool(row['hinted']), revealed=bool(row['revealed']), verified=bool(row['verified'] and row['unit_verified']),
            disputed=bool(row['disputed']), complete=bool(row['complete']), score=row['score'], delay_days=delay))
    return result


def measurement(db, config):
    required = {'topic', 'preference', 'baseline_id', 'history_assessment_ids', 'review_capability_id'}
    if not isinstance(config, dict) or set(config) != required:
        raise ValueError('measurement config requires topic, preference, baseline_id, history_assessment_ids and review_capability_id')
    baseline = db.execute('SELECT * FROM baselines WHERE id=? AND topic_id=?', (config['baseline_id'], config['topic'])).fetchone()
    if not baseline:
        raise ValueError('freeze a consented baseline first; no baseline is invented')
    # Frozen observations stay frozen; do not silently recompute a historical baseline.
    frozen = json.loads(baseline['snapshot'])
    if not isinstance(frozen, list):
        raise ValueError('baseline snapshot must contain frozen projected observations')
    from personalize import digest, evidence
    frozen = evidence(frozen)
    if digest(frozen) != baseline['digest']:
        raise ValueError('baseline digest does not match its frozen observations')
    current = observations(db, config['topic'], [r['assessment_id'] for r in frozen])
    if current != frozen:
        raise ValueError('baseline evidence changed; reconcile superseded, supported or reused observations explicitly')
    capability = db.execute('''SELECT c.interval,c.repair FROM capabilities c
        JOIN topic_capabilities tc ON tc.capability_id=c.id
        WHERE c.id=? AND c.archived=0 AND tc.topic_id=?''', (config['review_capability_id'], config['topic'])).fetchone()
    if not capability or capability['repair'] or capability['interval'] not in (3, 7, 30, 90):
        raise ValueError('review requires an existing ladder interval and no unresolved repair')
    return dict(topic=config['topic'], preference=config['preference'], baseline=frozen,
                history=observations(db, config['topic'], config['history_assessment_ids']),
                review=dict(capability_id=config['review_capability_id'], interval=capability['interval']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('command', choices=('selection', 'observations', 'measurement'))
    parser.add_argument('config', help='JSON file or - for stdin')
    args = parser.parse_args()
    config = json.load(sys.stdin) if args.config == '-' else json.loads(Path(args.config).read_text())
    db = connect(args.root)
    try:
        db.execute('BEGIN')
        if args.command == 'observations':
            result = observations(db, config['topic'], config['assessment_ids'])
        else:
            result = (selection if args.command == 'selection' else measurement)(db, config)
    finally:
        db.close()
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (KeyError, TypeError, ValueError, OSError, sqlite3.Error) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        raise SystemExit(2)
