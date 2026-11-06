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
        timings = {}
        for label, function in (
            ('targeted_context', lambda: m.context(db, capability='c1000')),
            ('due_queue', lambda: m.due(db, '2026-11-06')),
            ('free_text_search', lambda: m.search(db, 'Capability 1000')),
        ):
            elapsed = []
            result = None
            for _ in range(samples):
                start = time.perf_counter()
                result = function()
                elapsed.append((time.perf_counter()-start)*1000)
            timings[label] = {'median_ms': round(statistics.median(elapsed),3),
                              'p95_ms': round(sorted(elapsed)[int(samples*.95)-1],3),
                              'returned_bytes': len(json.dumps(result).encode())}
        elapsed = []
        for n in range(samples):
            payload = {'operation_id': 'save'+str(n), 'expected_revision': m.revision(db),
                       'attempt': {'unit_id':'c1000u0', 'response':'My response', 'hinted':False,'revealed':False,'skipped':False},
                       'assessment': {'score':1,'independent':True,'complete':True,'verified':True,'disputed':False,
                                      'feedback':'Correct.', 'evaluator':'synthetic benchmark'},
                       'session': {'next_action':'Continue later','closure':'paused'}}
            start = time.perf_counter()
            m.turn(db, payload)
            elapsed.append((time.perf_counter()-start)*1000)
        timings['atomic_turn_save'] = {'median_ms':round(statistics.median(elapsed),3), 'p95_ms':round(sorted(elapsed)[int(samples*.95)-1],3)}
        cli = []
        for _ in range(5):
            start = time.perf_counter()
            subprocess.run([sys.executable, str(root/'.learning/memory.py'), '--root',str(root),'context','--capability','c1000'], capture_output=True, check=True)
            cli.append((time.perf_counter()-start)*1000)
        timings['cli_context_including_process_start'] = {'median_ms':round(statistics.median(cli),3)}
        db.close()
        return {'capabilities':capabilities, 'units':capabilities*units_per_capability,
                'attempts_before_benchmark':capabilities*units_per_capability, 'samples':samples,
                'timings':timings, 'scope':'Synthetic local runtime only; excludes model generation, host tool latency, network and fresh-session prompt behavior.'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
