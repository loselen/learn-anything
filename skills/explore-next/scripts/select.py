#!/usr/bin/env python3
"""Deterministic, read-only learning activity selection. No dependencies or telemetry."""
from collections import Counter
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import sys

POLICY_VERSION = 'rules-1'
MODES = {'continue', 'explore', 'review'}
SOURCES = {'saved_action', 'due_review', 'repair', 'frontier', 'saved_question', 'nearby', 'catalog'}
CHALLENGE = {'intro': 0, 'practice': 1, 'stretch': 2}
WEIGHTS = dict(goal_relevance=.25, review_urgency=.20, interest=.15, readiness=.15,
               evidence_value=.15, diversity=.10, repetition=-.15,
               context_switch=-.10, time_mismatch=-.10)
REASONS = dict(saved_action='This is your saved next action.',
               due_review='This is due for independent retrieval.',
               repair='This revisits material that needs repair.',
               frontier='This is ready on the path to your chosen goal.',
               saved_question='You saved this question.',
               nearby='This is a nearby application within your chosen topics.',
               catalog='This is a checked starter within your chosen topics.')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def member(value, options):
    return isinstance(value, str) and value in options


def groups(node):
    return [[p] for p in node.get('prerequisites', [])] + node.get('prerequisite_groups', [])


def iso_date(value):
    if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
        raise ValueError('dates must use YYYY-MM-DD')
    return date.fromisoformat(value)


def validate(snapshot):
    if not isinstance(snapshot, dict):
        raise ValueError('snapshot must be an object')
    iso_date(snapshot['today'])
    if not member(snapshot.get('mode'), MODES) or not member(snapshot.get('challenge'), CHALLENGE):
        raise ValueError('choose mode and challenge explicitly')
    topics = snapshot.get('allowed_topics')
    if not isinstance(topics, list) or not all(text(t) for t in topics):
        raise ValueError('allowed_topics must be explicit strings')
    if snapshot.get('goal_topic') is not None and not text(snapshot['goal_topic']):
        raise ValueError('goal_topic must be a topic string or null')
    budget = snapshot.get('budget_minutes')
    if budget is not None and (not number(budget) or budget <= 0):
        raise ValueError('budget_minutes must be positive or null')
    if not isinstance(snapshot.get('sustained_work', False), bool):
        raise ValueError('sustained_work must be an explicit boolean')
    remaining = snapshot.get('batch_remaining', 1)
    if type(remaining) is not int or not 0 <= remaining <= 5:
        raise ValueError('batch_remaining must be 0–5')
    if not isinstance(snapshot.get('candidates'), list):
        raise ValueError('candidates must be a list')
    nodes = snapshot.get('capabilities')
    if not isinstance(nodes, dict):
        raise ValueError('capabilities must be an object')
    for identity, node in nodes.items():
        if not text(identity) or not isinstance(node, dict):
            raise ValueError('capability records need IDs and properties')
        if not member(node.get('status'), {'planned', 'learning', 'review', 'solid'}):
            raise ValueError('invalid capability status')
        if not isinstance(node.get('taught', False), bool):
            raise ValueError('taught must be an explicit boolean')
        required, alternatives = node.get('prerequisites', []), node.get('prerequisite_groups', [])
        if not isinstance(required, list) or not all(text(p) for p in required):
            raise ValueError('resolve legacy prerequisites to IDs before selecting')
        if not isinstance(alternatives, list) or not all(
                isinstance(g, list) and g and all(text(p) for p in g) for g in alternatives):
            raise ValueError('alternative prerequisite groups must be nonempty ID lists')
    for key in ('seen_units', 'repeated_misconceptions', 'goal_capability_ids'):
        value = snapshot.get(key, [])
        if not isinstance(value, list) or not all(text(p) for p in value):
            raise ValueError(f'{key} must be a string list')
    active = snapshot.get('active_unit')
    if active is not None and (not isinstance(active, dict) or not all(
            text(active.get(k)) for k in ('id', 'version', 'topic', 'prompt_reference'))):
        raise ValueError('active_unit needs id, version, topic and prompt_reference')


def reachable(nodes):
    found = set()
    while True:
        before = found.copy()
        for identity, node in nodes.items():
            if all(any(p in found for p in group) for group in groups(node)):
                found.add(identity)
        if before == found:
            return found


def goal_scope(snapshot):
    pending = list(snapshot.get('goal_capability_ids', []))
    scope = set()
    while pending:
        identity = pending.pop()
        if identity in scope or identity not in snapshot['capabilities']:
            continue
        scope.add(identity)
        pending.extend(p for group in groups(snapshot['capabilities'][identity]) for p in group)
    return scope


def shape(candidate):
    if not isinstance(candidate, dict) or not all(text(candidate.get(k)) for k in
            ('id', 'version', 'capability_id', 'topic', 'title')):
        return 'malformed'
    if not member(candidate.get('source'), SOURCES) or not member(candidate.get('purpose'), {'practice', 'review', 'repair'}):
        return 'malformed'
    modes = candidate.get('modes')
    if not isinstance(modes, list) or not modes or not all(member(m, MODES) for m in modes):
        return 'malformed'
    if not member(candidate.get('challenge'), CHALLENGE):
        return 'malformed'
    effort = candidate.get('effort_minutes')
    if not number(effort) or effort <= 0:
        return 'malformed'
    verification = candidate.get('verification')
    if not isinstance(verification, dict) or not all(text(verification.get(k)) for k in ('method', 'key_version')):
        return 'unverified'
    if verification.get('status') != 'verified':
        return 'unverified'
    if all(k in candidate for k in ('prompt', 'key', 'rubric')):
        authored = {k: candidate[k] for k in ('prompt', 'key', 'rubric', 'introduction') if k in candidate}
        digest = hashlib.sha256(canonical(authored).encode()).hexdigest()
        if verification.get('content_digest') != digest:
            return 'verification_content_changed'
    features = candidate.get('features', {})
    if not isinstance(features, dict) or set(features) - set(WEIGHTS):
        return 'invalid_features'
    if any(not number(v) or not 0 <= v <= 1 for v in features.values()):
        return 'invalid_features'
    if candidate.get('due_date') is not None:
        try:
            iso_date(candidate['due_date'])
        except (TypeError, ValueError):
            return 'invalid_due_date'
    if candidate['source'] == 'due_review' and (not candidate.get('due_date') or candidate['purpose'] != 'review'):
        return 'invalid_due_review'
    if candidate['source'] == 'repair' and candidate['purpose'] != 'repair':
        return 'invalid_repair'
    return None


def exclusion(candidate, snapshot, structurally_reachable):
    reason = shape(candidate)
    if reason:
        return reason
    if candidate['topic'] not in snapshot['allowed_topics']:
        return 'topic_not_consented'
    mode = snapshot['mode']
    if mode not in candidate['modes'] or (mode == 'review' and candidate['purpose'] not in {'review', 'repair'}):
        return 'mode_mismatch'
    if mode == 'continue' or candidate['source'] == 'frontier':
        if candidate['capability_id'] not in goal_scope(snapshot):
            return 'outside_chosen_goal'
    if candidate['id'] + '@' + candidate['version'] in snapshot.get('seen_units', []):
        return 'already_seen'
    if CHALLENGE[candidate['challenge']] > CHALLENGE[snapshot['challenge']]:
        return 'challenge_mismatch'
    budget = snapshot.get('budget_minutes')
    if budget and candidate['effort_minutes'] > budget and not snapshot.get('sustained_work', False):
        return 'time_mismatch'
    node = snapshot['capabilities'].get(candidate['capability_id'])
    if node is None:
        return 'unknown_capability'
    if candidate['capability_id'] not in structurally_reachable:
        return 'blocked_dependency_graph'
    if not all(any(snapshot['capabilities'].get(p, {}).get('status') in {'review', 'solid'}
                   for p in group) for group in groups(node)):
        return 'prerequisites_not_ready'
    if candidate['purpose'] in {'review', 'repair'} and not node.get('taught', False):
        return 'untaught_scope'
    if candidate['source'] == 'due_review' and node.get('status') not in {'review', 'solid'}:
        return 'not_reviewable'
    if candidate['source'] == 'due_review' and candidate['due_date'] > snapshot['today']:
        return 'not_due'
    return None


def features(candidate, snapshot):
    values = {key: 0.0 for key in WEIGHTS}
    values.update(candidate.get('features', {}))
    goal = snapshot.get('goal_topic')
    values['goal_relevance'] = float(candidate['capability_id'] in goal_scope(snapshot))
    values['context_switch'] = float(bool(goal) and candidate['topic'] != goal)
    values['readiness'] = 1.0
    values['review_urgency'] = 0.0
    if candidate.get('due_date'):
        days = (date.fromisoformat(snapshot['today']) - iso_date(candidate['due_date'])).days
        values['review_urgency'] = min(1.0, max(0.0, days / 30))
    budget = snapshot.get('budget_minutes')
    values['time_mismatch'] = min(1.0, candidate['effort_minutes'] / budget) if budget else 0.0
    return values


def select(snapshot):
    validate(snapshot)
    normalized = dict(snapshot, candidates=sorted(snapshot['candidates'], key=canonical))
    record = dict(policy_version=POLICY_VERSION,
                  snapshot_digest=hashlib.sha256(canonical(normalized).encode()).hexdigest(),
                  eligible=[], exclusions=[], choices=[], selected=None)
    active = snapshot.get('active_unit')
    if active:
        consented = active['topic'] in snapshot['allowed_topics']
        record.update(status='resume' if consented else 'paused',
                      reason='Resume the unanswered task.' if consented else 'The active topic is no longer consented; keep it paused.')
        if consented:
            record['active_unit'] = {k: active[k] for k in ('id', 'version', 'topic', 'prompt_reference')}
        return record
    if snapshot.get('batch_remaining', 1) == 0:
        record.update(status='complete', reason='This batch is complete. Save a next action or stop here.')
        return record
    if not snapshot['allowed_topics'] or (snapshot['mode'] == 'continue' and (not snapshot.get('goal_topic') or not snapshot.get('goal_capability_ids') or any(identity not in snapshot['capabilities'] for identity in snapshot['goal_capability_ids']))):
        record.update(status='needs_preference', reason='Choose a topic before selecting an activity.')
        return record
    counts = Counter(c.get('id') for c in snapshot['candidates'] if isinstance(c, dict) and text(c.get('id')))
    graph = reachable(snapshot['capabilities'])
    for candidate in normalized['candidates']:
        identifier = candidate.get('id', '<invalid>') if isinstance(candidate, dict) else '<invalid>'
        reason = exclusion(candidate, snapshot, graph)
        if isinstance(identifier, str) and counts[identifier] > 1:
            reason = 'duplicate_unit'
        if reason:
            record['exclusions'].append(dict(id=identifier, reason=reason))
            continue
        values = features(candidate, snapshot)
        score = round(sum(values[k] * w for k, w in WEIGHTS.items()), 6)
        repair_priority = candidate['purpose'] == 'repair' and candidate['capability_id'] in snapshot.get('repeated_misconceptions', [])
        reason = ('Your repeated attempts suggest repairing this before continuing.' if repair_priority else REASONS[candidate['source']])
        record['eligible'].append(dict(id=candidate['id'], version=candidate['version'],
                                       capability_id=candidate['capability_id'], title=candidate['title'],
                                       source=candidate['source'], purpose=candidate['purpose'], topic=candidate['topic'],
                                       effort_minutes=candidate['effort_minutes'], features=values, score=score,
                                       repair_priority=repair_priority, reason=reason))
    record['eligible'].sort(key=lambda c: (-c['repair_priority'], -c['score'], c['id'], c['version']))
    record['choices'] = record['eligible'][:3]
    record['selected'] = record['choices'][0] if record['choices'] else None
    record['status'] = 'suggested' if record['choices'] else 'blocked'
    if not record['choices']:
        record['reason'] = 'No eligible activity. Offer a bridge, diagnostic, labeled preview, or one preference question.'
    return record


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise ValueError('usage: select.py snapshot.json')
        snapshot = json.loads(Path(sys.argv[1]).read_text(), parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON number')))
        print(json.dumps(select(snapshot), ensure_ascii=False, indent=2, allow_nan=False))
    except (KeyError, TypeError, ValueError) as error:
        print(json.dumps(dict(error=str(error), policy_version=POLICY_VERSION)), file=sys.stderr)
        raise SystemExit(2)
