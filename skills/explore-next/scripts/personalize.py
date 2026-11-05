#!/usr/bin/env python3
"""Local, read-only measurement and reversible suggestions. No learner-state writes."""
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import sys

VERSION = 'adaptive-shadow-1'
LADDER = [3, 7, 30, 90]
LEVELS = ['intro', 'practice', 'stretch']
FIELDS = {'assessment_id', 'attempt_id', 'unit_id', 'unit_version', 'capability_id',
          'topic', 'challenge', 'purpose', 'independent', 'hinted', 'revealed',
          'verified', 'disputed', 'complete', 'score', 'delay_days'}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def string(value):
    return isinstance(value, str) and bool(value.strip())


def evidence(rows):
    """Strict aggregate-input contract; duplicate assessments collapse, conflicts fail."""
    if not isinstance(rows, list):
        raise ValueError('assessments must be a list')
    unique, attempts = {}, {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise ValueError('assessment fields must match the contract; exclude raw answers')
        if not all(string(row[k]) for k in ('assessment_id', 'attempt_id', 'unit_id',
                'unit_version', 'capability_id', 'topic')):
            raise ValueError('assessment IDs and provenance are required')
        if row['challenge'] not in LEVELS or row['purpose'] not in ('practice', 'delayed', 'transfer'):
            raise ValueError('invalid challenge or purpose')
        if any(type(row[k]) is not bool for k in ('independent', 'hinted', 'revealed', 'verified', 'disputed', 'complete')):
            raise ValueError('evidence flags must be explicit booleans')
        if not number(row['score']) or not 0 <= row['score'] <= 1:
            raise ValueError('score must be finite in [0,1]')
        if not number(row['delay_days']) or row['delay_days'] < 0:
            raise ValueError('delay_days must be nonnegative')
        identity = row['assessment_id']
        if identity in unique and unique[identity] != row:
            raise ValueError('conflicting assessment; resolve corrections before exporting')
        attempt = row['attempt_id']
        if attempt in attempts and attempts[attempt] != identity:
            raise ValueError('one current assessment per attempt; resolve superseded grades')
        unique[identity] = row
        attempts[attempt] = identity
    return sorted(unique.values(), key=lambda row: row['assessment_id'])


def usable(row):
    return (row['independent'] and row['verified'] and row['complete'] and
            not any(row[k] for k in ('hinted', 'revealed', 'disputed')) and
            (row['purpose'] == 'transfer' or (row['purpose'] == 'delayed' and row['delay_days'] >= 3)))


def measurement(rows):
    valid = [row for row in rows if usable(row)]
    return dict(assessments=len(rows), eligible=len(valid), excluded=len(rows)-len(valid),
                mean_score=sum(r['score'] for r in valid)/len(valid) if valid else None,
                delayed=sum(r['purpose'] == 'delayed' for r in valid),
                transfer=sum(r['purpose'] == 'transfer' for r in valid))


def analyze(snapshot):
    if not isinstance(snapshot, dict) or set(snapshot) != {'topic', 'preference', 'baseline', 'history', 'review'}:
        raise ValueError('expected topic, preference, baseline, history and review')
    topic, pref = snapshot['topic'], snapshot['preference']
    if not string(topic) or not isinstance(pref, dict) or set(pref) != {'enabled', 'challenge', 'allow_harder'}:
        raise ValueError('explicit topic and preference required')
    if type(pref['enabled']) is not bool or type(pref['allow_harder']) is not bool or pref['challenge'] not in LEVELS:
        raise ValueError('invalid explicit preference')
    baseline, history = evidence(snapshot['baseline']), evidence(snapshot['history'])
    # A frozen pre-adaptation baseline must not be counted again in later history.
    if {r['attempt_id'] for r in baseline} & {r['attempt_id'] for r in history}:
        raise ValueError('baseline and subsequent history must not overlap')
    baseline_scope = [r for r in baseline if r['topic'] == topic and usable(r)]
    current = [r for r in history if r['topic'] == topic and usable(r) and r['challenge'] == pref['challenge']]
    gate = (len(baseline_scope) >= 6 and len({r['unit_id'] for r in baseline_scope}) >= 3
            and any(r['purpose'] == 'delayed' for r in baseline_scope)
            and any(r['purpose'] == 'transfer' for r in baseline_scope))
    enough = len(current) >= 6 and len({r['unit_id'] for r in current}) >= 3
    target = pref['challenge']
    reason = 'Keep the explicit difficulty preference.'
    if not pref['enabled']:
        reason = 'Personalization is off.'
    elif not gate:
        reason = 'Collect a topic baseline: six independent delayed/transfer assessments across three units, including both outcomes.'
    elif not enough:
        reason = 'Keep measuring at the chosen difficulty before suggesting a change.'
    else:
        mean = sum(r['score'] for r in current)/len(current)
        index = LEVELS.index(target)
        if mean < .5 and index > 0:
            target = LEVELS[index-1]
            reason = 'Independent delayed/transfer performance suggests offering one easier level.'
        elif mean >= .85 and pref['allow_harder'] and index < 2:
            target = LEVELS[index+1]
            reason = 'Independent delayed/transfer performance supports offering one harder level.'
    review = snapshot['review']
    if not isinstance(review, dict) or set(review) != {'capability_id', 'interval'} or not string(review['capability_id']) or type(review['interval']) is not int or review['interval'] not in LADDER:
        raise ValueError('review requires capability_id and a ladder interval')
    interval = review['interval']
    scoped = [r for r in history if usable(r) and r['topic'] == topic and
              r['capability_id'] == review['capability_id'] and r['purpose'] == 'delayed' and
              r['delay_days'] >= interval]
    proposed = interval
    if pref['enabled'] and gate and len(scoped) >= 2 and len({r['unit_id'] for r in scoped}) >= 2:
        average = sum(r['score'] for r in scoped)/len(scoped)
        if average < .5:
            proposed = max(3, round(interval * .75))
        elif average >= .85:
            proposed = min(90, round(interval * 1.25))
    return dict(policy_version=VERSION, input_digest=digest(snapshot), baseline_digest=digest(baseline),
                baseline=measurement([r for r in baseline if r['topic'] == topic]),
                history=measurement([r for r in history if r['topic'] == topic]), baseline_ready=gate,
                challenge=dict(current=pref['challenge'], suggested=target, reason=reason,
                               requires_learner_choice=True, eligible_assessments=len(current)),
                review=dict(capability_id=review['capability_id'], baseline_interval=interval,
                            shadow_interval=proposed, eligible_assessments=len(scoped), applied=False),
                bandit_enabled=False)


def compare(snapshot):
    """Report a predeclared fixed-policy trial, including missing delayed outcomes."""
    if not isinstance(snapshot, dict) or set(snapshot) != {'plan', 'as_of', 'participants'}:
        raise ValueError('comparison requires plan, as_of and participants')
    plan = snapshot['plan']
    required = {'id', 'registered_on', 'baseline_digest', 'primary', 'minimum_per_arm',
                'practical_effect', 'stopping_rule', 'retention_days', 'consented'}
    if not isinstance(plan, dict) or set(plan) != required:
        raise ValueError('predeclare the comparison plan')
    if plan['primary'] != 'delayed_independent_score' or plan['consented'] is not True:
        raise ValueError('consented delayed-outcome comparison required')
    if not all(string(plan[k]) for k in ('id', 'baseline_digest', 'stopping_rule')):
        raise ValueError('plan provenance required')
    if len(plan['baseline_digest']) != 64 or any(c not in '0123456789abcdef' for c in plan['baseline_digest']):
        raise ValueError('baseline_digest must be SHA-256')
    if type(plan['minimum_per_arm']) is not int or plan['minimum_per_arm'] < 2 or type(plan['retention_days']) is not int or plan['retention_days'] < 1:
        raise ValueError('declare sample size and local retention')
    if not number(plan['practical_effect']) or not 0 < plan['practical_effect'] <= 1:
        raise ValueError('declare an effect threshold in (0,1]')
    def day(value):
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError('use YYYY-MM-DD')
        return parsed
    registered, as_of = day(plan['registered_on']), day(snapshot['as_of'])
    if as_of < registered or not isinstance(snapshot['participants'], list):
        raise ValueError('invalid comparison date or participants')
    arms = {arm: dict(assigned=0, due=0, observed=0, missing=0, scores=[], transfer=[], minutes=0.0) for arm in ('ladder', 'adaptive')}
    seen = set()
    fields = {'id', 'arm', 'probability', 'assigned_on', 'due_on', 'chosen_minutes', 'delayed', 'transfer'}
    for row in snapshot['participants']:
        if not isinstance(row, dict) or set(row) != fields or not string(row['id']) or row['id'] in seen:
            raise ValueError('unique pseudonymous participant IDs required')
        seen.add(row['id'])
        if row['arm'] not in arms or row['probability'] != .5 or type(row['probability']) is bool:
            raise ValueError('only preassigned fixed 1:1 randomized trials supported; no bandit')
        assigned, due = day(row['assigned_on']), day(row['due_on'])
        if not registered <= assigned <= as_of or (due-assigned).days < 3:
            raise ValueError('assignment must follow registration; delayed outcome at least three days later')
        if not number(row['chosen_minutes']) or row['chosen_minutes'] <= 0:
            raise ValueError('explicit chosen study minutes required')
        for key in ('delayed', 'transfer'):
            value = row[key]
            if value is not None and (not number(value) or not 0 <= value <= 1):
                raise ValueError('outcomes must be independent checked scores or null')
        arm = arms[row['arm']]; arm['assigned'] += 1
        arm['minutes'] += row['chosen_minutes']
        if due <= as_of:
            arm['due'] += 1
            if row['delayed'] is None:
                arm['missing'] += 1
            else:
                arm['observed'] += 1; arm['scores'].append(row['delayed'])
            if row['transfer'] is not None:
                arm['transfer'].append(row['transfer'])
        elif row['delayed'] is not None or row['transfer'] is not None:
            raise ValueError('delayed result cannot precede the registered due date')
    for arm in arms.values():
        scores, transfers = arm.pop('scores'), arm.pop('transfer')
        arm['mean_delayed'] = sum(scores)/len(scores) if scores else None
        arm['mean_transfer'] = sum(transfers)/len(transfers) if transfers else None
        arm['transfer_observed'] = len(transfers)
        arm['retained_score_total'] = sum(scores)
        arm['retained_score_per_chosen_minute'] = sum(scores)/arm['minutes'] if arm['minutes'] else None
        arm['attrition'] = arm['missing']/arm['due'] if arm['due'] else None
    ready = all(a['observed'] >= plan['minimum_per_arm'] for a in arms.values())
    means = [arms[a]['mean_delayed'] for a in ('adaptive', 'ladder')]
    difference = means[0]-means[1] if all(v is not None for v in means) else None
    return dict(policy_version=VERSION, plan=plan, input_digest=digest(snapshot), arms=arms,
                planned_sample_reached=ready, observed_difference=difference,
                practical_threshold_reached=ready and difference is not None and difference >= plan['practical_effect'],
                decision='Descriptive only. Review attrition, scoring and uncertainty; never auto-promote a policy.')


if __name__ == '__main__':
    try:
        if len(sys.argv) != 3 or sys.argv[1] not in ('analyze', 'compare'):
            raise ValueError('usage: personalize.py analyze|compare snapshot.json')
        value = json.loads(Path(sys.argv[2]).read_text(), parse_constant=lambda v: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
        result = (analyze if sys.argv[1] == 'analyze' else compare)(value)
        print(json.dumps(result, indent=2, allow_nan=False))
    except (KeyError, TypeError, ValueError) as error:
        print(json.dumps({'error': str(error), 'policy_version': VERSION}), file=sys.stderr)
        raise SystemExit(2)
