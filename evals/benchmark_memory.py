"""Synthetic local runtime measurements; not an end-to-end agent benchmark."""
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/setup-learning/scripts'))
import memory as m


def run(capabilities=2000, units_per_capability=10, samples=50):
    if min(capabilities, units_per_capability, samples) < 1:
        raise ValueError('benchmark sizes must be positive')
    with tempfile.TemporaryDirectory(dir='/tmp/opencode' if Path('/tmp/opencode').is_dir() else None) as tmp:
        root = Path(tmp)
        m.initialize(root)
        db = m.connect(root)
        with m.transaction(db):
            for n in range(capabilities):
                cap = 'c'+str(n)
                db.execute("INSERT INTO capabilities(id,title,objective,status,interval,next_review) VALUES (?,?,?,'review',3,'2026-11-06')", (cap, 'Capability '+str(n), 'A synthetic observable outcome'))
                db.execute('INSERT INTO notes(id,title,body,capability_id,created_at) VALUES (?,?,?,?,?)', ('n'+str(n),'Saved note','note '*400,cap,m.now()))
                for i in range(units_per_capability):
                    unit = cap+'u'+str(i)
                    db.execute("INSERT INTO units(id,capability_id,version,purpose,prompt,answer,verified,verification,created_at) VALUES (?,?,'1','practice',?, 'SECRET',1,'synthetic fixture',?)", (unit,cap,'Predict the result. '*10,m.now()))
                    db.execute('INSERT INTO cycles VALUES (?,?,?,?,?)', ('cycle'+unit,cap,unit,'An explanation. '*30,m.now()))
                    db.execute('INSERT INTO attempts VALUES (?,?,NULL,?,0,0,0,?)', ('a'+unit,unit,'A learner response. '*10,m.now()))
                    db.execute("INSERT INTO assessments(id,attempt_id,score,independent,complete,verified,disputed,feedback,evaluator,created_at) VALUES (?,?,1,1,1,1,0,?,'synthetic fixture',?)", ('g'+unit,'a'+unit,'Specific feedback. '*10,m.now()))
        target = 'c'+str(min(1000, capabilities-1))
        timings = {}

        def stats(elapsed):
            return {'median_ms': round(statistics.median(elapsed), 3),
                    'p95_ms': round(sorted(elapsed)[max(0, int(len(elapsed)*.95)-1)], 3)}
        for label, function in (
            ('targeted_context', lambda: m.context(db, capability=target)),
            ('due_queue', lambda: m.due(db, '2026-11-06')),
            ('free_text_search', lambda: m.search(db, 'Capability 1000')),
        ):
            elapsed = []
            result = None
            for _ in range(samples):
                start = time.perf_counter()
                result = function()
                elapsed.append((time.perf_counter()-start)*1000)
            timings[label] = dict(stats(elapsed), returned_bytes=len(json.dumps(result).encode()))

        active = None
        for purpose in ('practice', 'transfer', 'delayed', 'placement'):
            opening = dict(operation_id='open-'+purpose, expected_revision=m.revision(db),
                unit=dict(capability_id=target, purpose=purpose, prompt='Fresh synthetic '+purpose,
                          answer='3', verification='Synthetic checked fixture'), explanation='A small explanation.')
            if active:
                opening['attempt'] = dict(unit_id=active, response='', hinted=False, revealed=False, skipped=True)
            active = m.turn(db, opening)['saved']['units'][0]
            elapsed, transitions = [], 0
            for n in range(samples):
                day = db.execute('SELECT next_review FROM capabilities WHERE id=?', (target,)).fetchone()[0] if purpose == 'delayed' else '2026-11-06'
                payload = dict(operation_id=purpose+str(n), expected_revision=m.revision(db), today=day,
                    attempt=dict(unit_id=active, response='3', hinted=False, revealed=False, skipped=False,
                                 created_at=day+'T12:00:00+00:00'),
                    assessment=dict(score=1, independent=True, complete=True, verified=True, disputed=False,
                                    feedback='Correct.', evaluator='synthetic benchmark'),
                    unit=dict(capability_id=target, purpose=purpose, prompt='Fresh synthetic '+purpose+' '+str(n),
                              answer='3', verification='Synthetic checked fixture'),
                    explanation='The next small step.', session=dict(next_action='Wait for this attempt.'))
                start = time.perf_counter()
                saved = m.turn(db, payload)
                elapsed.append((time.perf_counter()-start)*1000)
                active = saved['saved']['units'][0]
                transitions += bool(saved['changed_capabilities'])
            if purpose in ('transfer', 'delayed') and transitions != samples:
                raise AssertionError('benchmark did not exercise actual scheduling transitions')
            timings[purpose+'_answer_with_next_cycle'] = dict(stats(elapsed), capability_updates=transitions)

        elapsed = []
        for n in range(samples):
            # Finish the old prompt outside the measured first-turn operation.
            m.turn(db, dict(operation_id='finish'+str(n), expected_revision=m.revision(db),
                attempt=dict(unit_id=active, response='', hinted=False, revealed=False, skipped=True)))
            payload = dict(operation_id='new-capability'+str(n), expected_revision=m.revision(db),
                capability=dict(id='new'+str(n), title='A new capability'), explanation='A small example.',
                unit=dict(prompt='Predict three objects', answer='3', verification='Counted'))
            start = time.perf_counter()
            saved = m.turn(db, payload)
            elapsed.append((time.perf_counter()-start)*1000)
            active = saved['saved']['units'][0]
        timings['new_capability_first_turn_with_graph_validation'] = stats(elapsed)
        cli = []
        for _ in range(5):
            start = time.perf_counter()
            subprocess.run([sys.executable, str(root/'.learning/memory.py'), '--root',str(root),'context','--capability',target], capture_output=True, check=True)
            cli.append((time.perf_counter()-start)*1000)
        timings['cli_context_including_process_start'] = {'median_ms':round(statistics.median(cli),3)}
        db.close()
        return {'capabilities_before_benchmark':capabilities, 'units_before_benchmark':capabilities*units_per_capability,
                'attempts_before_benchmark':capabilities*units_per_capability, 'samples':samples,
                'timings':timings, 'scope':'Synthetic local runtime only; excludes model generation, host tool latency, network and fresh-session prompt behavior.'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
