-- SQLite is authoritative. Markdown is an explicit projection, never a second store.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
INSERT OR IGNORE INTO meta VALUES ('schema_version','1'), ('revision','0');
CREATE TABLE IF NOT EXISTS operations (
 id TEXT PRIMARY KEY, digest TEXT NOT NULL, result TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS topics (
 id TEXT PRIMARY KEY, title TEXT NOT NULL, goal TEXT NOT NULL DEFAULT '',
 long_term TEXT NOT NULL DEFAULT '', path TEXT NOT NULL DEFAULT '', archived INTEGER NOT NULL DEFAULT 0 CHECK(archived IN (0,1))
);
CREATE TABLE IF NOT EXISTS capabilities (
 id TEXT PRIMARY KEY, title TEXT NOT NULL, objective TEXT NOT NULL DEFAULT '',
 kind TEXT NOT NULL DEFAULT 'concept' CHECK(kind IN ('procedure','principle','concept','structure','facts')),
 status TEXT NOT NULL DEFAULT 'planned' CHECK(status IN ('planned','learning','review','solid')),
 placement TEXT NOT NULL DEFAULT 'unknown' CHECK(placement IN ('unknown','demonstrated')),
 retention TEXT NOT NULL DEFAULT 'unmeasured' CHECK(retention IN ('unmeasured','demonstrated')),
 repair INTEGER NOT NULL DEFAULT 0 CHECK(repair IN (0,1)), interval INTEGER CHECK(interval IN (3,7,30,90)),
 last_reviewed TEXT, next_review TEXT, archived INTEGER NOT NULL DEFAULT 0 CHECK(archived IN (0,1))
);
CREATE TABLE IF NOT EXISTS topic_capabilities (
 id TEXT PRIMARY KEY, topic_id TEXT NOT NULL REFERENCES topics(id),
 capability_id TEXT NOT NULL REFERENCES capabilities(id), UNIQUE(topic_id,capability_id)
);
CREATE TABLE IF NOT EXISTS prerequisite_groups (
 id TEXT PRIMARY KEY, capability_id TEXT NOT NULL REFERENCES capabilities(id)
);
CREATE TABLE IF NOT EXISTS prerequisite_members (
 id TEXT PRIMARY KEY, group_id TEXT NOT NULL REFERENCES prerequisite_groups(id),
 prerequisite_id TEXT NOT NULL REFERENCES capabilities(id), UNIQUE(group_id,prerequisite_id)
);
CREATE TABLE IF NOT EXISTS outcomes (
 id TEXT PRIMARY KEY, topic_id TEXT NOT NULL REFERENCES topics(id),
 capability_id TEXT REFERENCES capabilities(id), description TEXT NOT NULL,
 met_on TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
 id TEXT PRIMARY KEY, mode TEXT NOT NULL DEFAULT 'continue' CHECK(mode IN ('continue','explore','review')),
 topic_id TEXT REFERENCES topics(id), active_unit_id TEXT REFERENCES units(id),
 next_action TEXT NOT NULL DEFAULT '', closure TEXT NOT NULL DEFAULT 'active' CHECK(closure IN ('active','paused','closed')),
 budget_minutes INTEGER CHECK(budget_minutes > 0), updated_at TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_session ON sessions((1)) WHERE closure='active';
CREATE TABLE IF NOT EXISTS units (
 id TEXT PRIMARY KEY, capability_id TEXT NOT NULL REFERENCES capabilities(id),
 version TEXT NOT NULL, purpose TEXT NOT NULL CHECK(purpose IN ('placement','practice','transfer','delayed')),
 prompt TEXT NOT NULL, answer TEXT NOT NULL DEFAULT '', rubric TEXT NOT NULL DEFAULT '',
 verified INTEGER NOT NULL DEFAULT 0 CHECK(verified IN (0,1)), verification TEXT NOT NULL DEFAULT '',
 challenge TEXT NOT NULL DEFAULT 'intro' CHECK(challenge IN ('intro','practice','stretch')),
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cycles (
 id TEXT PRIMARY KEY, capability_id TEXT NOT NULL REFERENCES capabilities(id),
 unit_id TEXT NOT NULL UNIQUE REFERENCES units(id), explanation TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tests (
 id TEXT PRIMARY KEY, topic_id TEXT REFERENCES topics(id), blueprint TEXT NOT NULL,
 created_at TEXT NOT NULL, closure TEXT NOT NULL DEFAULT 'active' CHECK(closure IN ('active','partial','closed'))
);
CREATE TABLE IF NOT EXISTS test_items (
 id TEXT PRIMARY KEY, test_id TEXT NOT NULL REFERENCES tests(id),
 unit_id TEXT NOT NULL UNIQUE REFERENCES units(id), ordinal INTEGER NOT NULL CHECK(ordinal > 0),
 UNIQUE(test_id,ordinal)
);
CREATE TABLE IF NOT EXISTS attempts (
 id TEXT PRIMARY KEY, unit_id TEXT NOT NULL REFERENCES units(id), session_id TEXT REFERENCES sessions(id),
 response TEXT NOT NULL, hinted INTEGER NOT NULL CHECK(hinted IN (0,1)),
 revealed INTEGER NOT NULL CHECK(revealed IN (0,1)), skipped INTEGER NOT NULL CHECK(skipped IN (0,1)),
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assessments (
 id TEXT PRIMARY KEY, attempt_id TEXT NOT NULL REFERENCES attempts(id),
 supersedes TEXT UNIQUE REFERENCES assessments(id), score REAL NOT NULL CHECK(score >= 0 AND score <= 1),
 independent INTEGER NOT NULL CHECK(independent IN (0,1)), complete INTEGER NOT NULL CHECK(complete IN (0,1)),
 verified INTEGER NOT NULL CHECK(verified IN (0,1)), disputed INTEGER NOT NULL CHECK(disputed IN (0,1)),
 feedback TEXT NOT NULL, failure_type TEXT NOT NULL DEFAULT '', evaluator TEXT NOT NULL,
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS applied_evidence (
 id TEXT PRIMARY KEY, capability_id TEXT NOT NULL REFERENCES capabilities(id),
 purpose TEXT NOT NULL, assessment_ids TEXT NOT NULL, applied_on TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sources (
 id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL DEFAULT '',
 source_type TEXT NOT NULL DEFAULT 'secondary' CHECK(source_type IN ('primary','secondary')),
 body TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS capability_sources (
 id TEXT PRIMARY KEY, capability_id TEXT NOT NULL REFERENCES capabilities(id),
 source_id TEXT NOT NULL REFERENCES sources(id), UNIQUE(capability_id,source_id)
);
CREATE TABLE IF NOT EXISTS notes (
 id TEXT PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL, capability_id TEXT REFERENCES capabilities(id),
 kind TEXT NOT NULL DEFAULT 'note' CHECK(kind IN ('note','own_words','preference','legacy')),
 created_at TEXT NOT NULL, archived INTEGER NOT NULL DEFAULT 0 CHECK(archived IN (0,1))
);
CREATE TABLE IF NOT EXISTS questions (
 id TEXT PRIMARY KEY, text TEXT NOT NULL, origin TEXT NOT NULL DEFAULT '',
 capability_id TEXT REFERENCES capabilities(id), disposition TEXT NOT NULL DEFAULT 'saved' CHECK(disposition IN ('open','saved','resolved'))
);
CREATE TABLE IF NOT EXISTS recommendations (
 id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
 policy_version TEXT NOT NULL, snapshot TEXT NOT NULL, result TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS preferences (
 id TEXT PRIMARY KEY, topic_id TEXT REFERENCES topics(id), value TEXT NOT NULL, provenance TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS baselines (
 id TEXT PRIMARY KEY, topic_id TEXT NOT NULL REFERENCES topics(id),
 snapshot TEXT NOT NULL, digest TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS summary_snapshots (
 id TEXT PRIMARY KEY, request TEXT NOT NULL, body TEXT NOT NULL, evidence_ids TEXT NOT NULL,
 source_revision INTEGER NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS legacy_documents (
 id TEXT PRIMARY KEY, path TEXT NOT NULL UNIQUE, sha256 TEXT NOT NULL, raw BLOB NOT NULL,
 imported_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS due_capabilities ON capabilities(next_review) WHERE status IN ('review','solid') AND archived=0;
CREATE INDEX IF NOT EXISTS capability_topics ON topic_capabilities(capability_id);
CREATE INDEX IF NOT EXISTS group_capability ON prerequisite_groups(capability_id);
CREATE INDEX IF NOT EXISTS member_group ON prerequisite_members(group_id);
CREATE INDEX IF NOT EXISTS unit_capability ON units(capability_id,created_at);
CREATE INDEX IF NOT EXISTS attempt_unit ON attempts(unit_id,created_at);
CREATE INDEX IF NOT EXISTS assessment_attempt ON assessments(attempt_id,created_at);
CREATE INDEX IF NOT EXISTS note_capability ON notes(capability_id,created_at);
CREATE INDEX IF NOT EXISTS evidence_capability ON applied_evidence(capability_id);
CREATE INDEX IF NOT EXISTS session_updated ON sessions(updated_at DESC);
CREATE VIEW IF NOT EXISTS capability_state AS
 SELECT c.*, CASE WHEN c.status='solid' THEN 'solid' WHEN c.status='review' THEN 'shaky'
 WHEN NOT EXISTS (
  SELECT 1 FROM prerequisite_groups g WHERE g.capability_id=c.id AND NOT EXISTS (
   SELECT 1 FROM prerequisite_members m JOIN capabilities p ON p.id=m.prerequisite_id
   WHERE m.group_id=g.id AND p.status IN ('review','solid') AND p.archived=0
  )
 ) THEN 'next' ELSE 'notyet' END AS map_class FROM capabilities c;
CREATE VIEW IF NOT EXISTS current_assessments AS
 SELECT a.* FROM assessments a WHERE NOT EXISTS (SELECT 1 FROM assessments n WHERE n.supersedes=a.id);
