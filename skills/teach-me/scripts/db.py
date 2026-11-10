#!/usr/bin/env python3
"""learn-anything SQLite helper. Stdlib only. All output is JSON.

Usage (run from the learner's project root; the database is created at ./.learn/learn.db):
  python3 scripts/db.py new-map      '{"goal": "...", "baseline": "..."}'
  python3 scripts/db.py add-nodes    '{"map_id": 1, "nodes": [{"key": "a", "title": "...", "requires": []},
                                                              {"key": "b", "title": "...", "requires": ["a"]}]}'
  python3 scripts/db.py add-outcomes '{"node_id": 3, "outcomes": ["Learner can ...", "..."]}'
  python3 scripts/db.py attempt      '{"outcome_id": 7, "activity": "...", "answer": "...",
                                      "verdict": "correct|partial|incorrect", "feedback": "..."}'
  python3 scripts/db.py met          '{"outcome_id": 7}'
  python3 scripts/db.py next         '{"map_id": 1}'
  python3 scripts/db.py status       '{"map_id": 1}'      (omit map_id to list all maps)

The JSON argument may also be piped on stdin instead of passed as an argument.
"""
import json
import os
import sqlite3
import sys
import time
from contextlib import closing

DB_PATH = os.environ.get("LEARN_DB", os.path.join(os.getcwd(), ".learn", "learn.db"))
SCHEMA_VERSION = 1

SCHEMA = """
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS maps (
  id       INTEGER PRIMARY KEY,
  goal     TEXT NOT NULL,
  baseline TEXT NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS nodes (
  id         INTEGER PRIMARY KEY,
  map_id     INTEGER NOT NULL REFERENCES maps(id) ON DELETE CASCADE,
  position   INTEGER NOT NULL,
  title      TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  UNIQUE (map_id, position)
) STRICT;

CREATE TABLE IF NOT EXISTS node_requires (
  node_id     INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  requires_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  PRIMARY KEY (node_id, requires_id)
) STRICT, WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS node_requires_requires ON node_requires(requires_id);

CREATE TABLE IF NOT EXISTS outcomes (
  id      INTEGER PRIMARY KEY,
  node_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  text    TEXT NOT NULL,
  met_at  INTEGER
) STRICT;
CREATE INDEX IF NOT EXISTS outcomes_node ON outcomes(node_id, met_at);

CREATE TABLE IF NOT EXISTS attempts (
  id         INTEGER PRIMARY KEY,
  outcome_id INTEGER NOT NULL REFERENCES outcomes(id) ON DELETE CASCADE,
  activity   TEXT NOT NULL,
  answer     TEXT NOT NULL,
  verdict    TEXT NOT NULL CHECK (verdict IN ('correct', 'partial', 'incorrect')),
  feedback   TEXT NOT NULL DEFAULT ''
) STRICT;
CREATE INDEX IF NOT EXISTS attempts_outcome ON attempts(outcome_id);
"""


def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=5.0, isolation_level=None)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA synchronous = NORMAL")
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA temp_store = MEMORY")
    if con.execute("PRAGMA user_version").fetchone()[0] < SCHEMA_VERSION:
        con.executescript(SCHEMA + f"PRAGMA user_version = {SCHEMA_VERSION};")
    return con


class tx:
    """BEGIN IMMEDIATE ... COMMIT / ROLLBACK."""

    def __init__(self, con):
        self.con = con

    def __enter__(self):
        self.con.execute("BEGIN IMMEDIATE")
        return self.con

    def __exit__(self, exc_type, *_):
        self.con.execute("ROLLBACK" if exc_type else "COMMIT")
        return False


def need(args, *keys):
    missing = [k for k in keys if args.get(k) in (None, "")]
    if missing:
        raise ValueError(f"missing field(s): {', '.join(missing)}")


def iso(ts):
    return None if ts is None else time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def cmd_new_map(con, a):
    need(a, "goal", "baseline")
    with tx(con):
        cur = con.execute("INSERT INTO maps (goal, baseline) VALUES (?, ?)", (a["goal"], a["baseline"]))
    return {"map_id": cur.lastrowid}


def cmd_add_nodes(con, a):
    need(a, "map_id", "nodes")
    now = int(time.time())
    with tx(con):
        if not con.execute("SELECT 1 FROM maps WHERE id = ?", (a["map_id"],)).fetchone():
            raise ValueError(f"map {a['map_id']} not found")
        start = con.execute(
            "SELECT COALESCE(MAX(position), 0) FROM nodes WHERE map_id = ?", (a["map_id"],)
        ).fetchone()[0]
        ids = {}
        for i, n in enumerate(a["nodes"], start=1):
            need(n, "key", "title")
            cur = con.execute(
                "INSERT INTO nodes (map_id, position, title, created_at) VALUES (?, ?, ?, ?)",
                (a["map_id"], start + i, n["title"], now),
            )
            ids[n["key"]] = cur.lastrowid
        edges = []
        for n in a["nodes"]:
            for r in n.get("requires", []):
                if isinstance(r, int):
                    rid = r  # an existing node id
                elif r in ids:
                    rid = ids[r]
                else:
                    raise ValueError(f"node '{n['key']}' requires unknown key '{r}'")
                edges.append((ids[n["key"]], rid))
        con.executemany("INSERT OR IGNORE INTO node_requires (node_id, requires_id) VALUES (?, ?)", edges)
    return {"node_ids": ids}


def cmd_add_outcomes(con, a):
    need(a, "node_id", "outcomes")
    with tx(con):
        if not con.execute("SELECT 1 FROM nodes WHERE id = ?", (a["node_id"],)).fetchone():
            raise ValueError(f"node {a['node_id']} not found")
        ids = [
            con.execute("INSERT INTO outcomes (node_id, text) VALUES (?, ?)", (a["node_id"], t)).lastrowid
            for t in a["outcomes"]
        ]
    return {"outcome_ids": ids}


def cmd_attempt(con, a):
    need(a, "outcome_id", "activity", "answer", "verdict")
    with tx(con):
        cur = con.execute(
            "INSERT INTO attempts (outcome_id, activity, answer, verdict, feedback) VALUES (?, ?, ?, ?, ?)",
            (a["outcome_id"], a["activity"], a["answer"], a["verdict"], a.get("feedback", "")),
        )
    return {"attempt_id": cur.lastrowid}


def cmd_met(con, a):
    need(a, "outcome_id")
    with tx(con):
        row = con.execute("SELECT node_id FROM outcomes WHERE id = ?", (a["outcome_id"],)).fetchone()
        if not row:
            raise ValueError(f"outcome {a['outcome_id']} not found")
        con.execute(
            "UPDATE outcomes SET met_at = ? WHERE id = ? AND met_at IS NULL", (int(time.time()), a["outcome_id"])
        )
        left = con.execute(
            "SELECT COUNT(*) FROM outcomes WHERE node_id = ? AND met_at IS NULL", (row["node_id"],)
        ).fetchone()[0]
    return {"outcome_id": a["outcome_id"], "node_id": row["node_id"], "node_outcomes_left": left}


def node_detail(con, node_id):
    outs = []
    for o in con.execute("SELECT id, text, met_at FROM outcomes WHERE node_id = ? ORDER BY id", (node_id,)):
        atts = con.execute(
            "SELECT activity, answer, verdict, feedback FROM attempts WHERE outcome_id = ? ORDER BY id",
            (o["id"],),
        ).fetchall()
        outs.append({"id": o["id"], "text": o["text"], "met_at": iso(o["met_at"]), "attempts": [dict(r) for r in atts]})
    return outs


# A node is done when it has outcomes and none are unmet.
NODE_DONE = """
  EXISTS (SELECT 1 FROM outcomes o WHERE o.node_id = {n}.id)
  AND NOT EXISTS (SELECT 1 FROM outcomes o WHERE o.node_id = {n}.id AND o.met_at IS NULL)
"""


def cmd_next(con, a):
    need(a, "map_id")
    row = con.execute(
        f"""
        SELECT n.id, n.position, n.title FROM nodes n
        WHERE n.map_id = ?
          AND NOT ({NODE_DONE.format(n='n')})
          AND NOT EXISTS (
            SELECT 1 FROM node_requires r JOIN nodes p ON p.id = r.requires_id
            WHERE r.node_id = n.id AND NOT ({NODE_DONE.format(n='p')}))
        ORDER BY n.position LIMIT 1
        """,
        (a["map_id"],),
    ).fetchone()
    if not row:
        return {"map_id": a["map_id"], "next": None, "message": "all nodes done (or map empty)"}
    return {"map_id": a["map_id"], "next": {**dict(row), "outcomes": node_detail(con, row["id"])}}


def cmd_status(con, a):
    if not a.get("map_id"):
        return {"maps": [dict(r) for r in con.execute("SELECT id, goal FROM maps ORDER BY id")]}
    m = con.execute("SELECT id, goal, baseline FROM maps WHERE id = ?", (a["map_id"],)).fetchone()
    if not m:
        raise ValueError(f"map {a['map_id']} not found")
    nodes = []
    for n in con.execute(
        f"""
        SELECT n.id, n.position, n.title, n.created_at,
               (SELECT COUNT(*) FROM outcomes o WHERE o.node_id = n.id) AS outcomes,
               (SELECT COUNT(*) FROM outcomes o WHERE o.node_id = n.id AND o.met_at IS NOT NULL) AS met,
               (SELECT group_concat(r.requires_id) FROM node_requires r WHERE r.node_id = n.id) AS requires
        FROM nodes n WHERE n.map_id = ? ORDER BY n.position
        """,
        (a["map_id"],),
    ):
        d = dict(n)
        d["created_at"] = iso(d["created_at"])
        d["requires"] = [int(x) for x in d["requires"].split(",")] if d["requires"] else []
        nodes.append(d)
    return {**dict(m), "nodes": nodes}


COMMANDS = {
    "new-map": cmd_new_map,
    "add-nodes": cmd_add_nodes,
    "add-outcomes": cmd_add_outcomes,
    "attempt": cmd_attempt,
    "met": cmd_met,
    "next": cmd_next,
    "status": cmd_status,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(2)
    raw = sys.argv[2] if len(sys.argv) > 2 else (sys.stdin.read() if not sys.stdin.isatty() else "")
    try:
        args = json.loads(raw) if raw.strip() else {}
        with closing(connect()) as con:
            out = COMMANDS[sys.argv[1]](con, args)
            con.execute("PRAGMA optimize")
        print(json.dumps(out, ensure_ascii=False))
    except (ValueError, sqlite3.Error, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
