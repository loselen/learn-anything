# Selection policy · rules-1

This is a transparent heuristic, not a validated prediction of learning gain. The policy is independent of capability evidence; changing it never changes a grade. It requires Python 3.10+ with only the standard library. The helper reads JSON and prints a recommendation record; it never writes a vault, executes catalog code, updates evidence or transmits data.

## Snapshot

Run `python scripts/select.py snapshot.json` from the explore-next folder. The snapshot is an object with:

- `today`: ISO date; `mode`: continue/explore/review; `allowed_topics`: explicit topic strings; `goal_topic`: chosen topic or null; `goal_capability_ids`: IDs of chosen goal outcomes (required for continue); `budget_minutes`: positive number or null; `sustained_work`: explicit boolean; `challenge`: intro/practice/stretch; `batch_remaining`: 0–5 (default 1).
- `capabilities`: ID → `{status, taught, prerequisites, prerequisite_groups}`. Here `prerequisites` must already be resolved IDs, not wikilinks; preserve unknown targets as unresolved. Read actual lesson content to set `taught`: it asserts the complete candidate outcome/scope was taught, not merely that the lesson has begun. Placement alone is not teaching. Supply the full prerequisite closure, not just one-hop neighbors.
- `seen_units`: `id@version` strings previously presented/answered; `active_unit`: null or `{id, version, topic, prompt_reference}` for an unfinished task. Active tasks resume through their existing prompt reference, with no key payload.
- `repeated_misconceptions`: capability IDs derived from attempts, never from response timing.
- `candidates`: learning units with `id`, `version`, `capability_id`, `topic`, `title`, `purpose` (practice/review/repair), `source` (saved_action/due_review/repair/frontier/saved_question/nearby/catalog), `modes`, `effort_minutes`, `challenge`, `verification` (`status: verified`, method, key_version), and optional `due_date` and `features`.

Catalog IDs are authored stable IDs. If an equivalent vault capability already exists, map catalog IDs to its existing UUID (including prerequisite references) in the snapshot and retain the original catalog/unit provenance. Never re-key existing learner evidence.

Candidate prerequisites come from the capability record, never a second overriding copy. Each required group must have a review/solid member. All legacy prerequisite IDs are singleton groups. Unknown capabilities, unsatisfied groups and dependencies that cannot be reached from roots block selection. An escaping OR branch makes an otherwise cyclic neighborhood reachable. Related/application edges are ignored by readiness.

Verification metadata is a checked-content assertion supplied by the tutor/verifier, not proof established by the selector. Recheck keys before grading, quarantine disputed/stale units by setting verification status, and preserve provenance. The catalog includes bridge capability records with no starter unit: equivalent fractions and common denominators must be diagnosed or taught before fraction addition. Add their records as unknown/planned when no evidence exists; never infer readiness from the activity's introduction.

The catalog's keys are independently exercised by executable evaluation checks; never execute imported content to verify it. Changes to prompt/key/rubric require a new unit version and re-verification. When authored payloads are supplied, verification.content_digest must match SHA-256 of canonical JSON containing introduction (if present), prompt, key and rubric; this detects stale metadata, not malicious assertions.

## Eligibility and ranking

Before ranking, reject unsupported or malformed candidates, duplicates, already-seen unit versions, nonconsented topics, mode mismatch, excessive challenge or effort, unverified/disputed keys, unknown/blocked prerequisites, and untaught review/repair. Continue requires a declared goal; continue and frontier candidates require membership in the prerequisite closure of goal_capability_ids. Cross-topic prerequisites still require explicit topic consent. The helper derives that closure, including alternative routes; a broad topic match alone is insufficient. Review mode permits only review/repair; due_review must have review/solid status and be due today or earlier. Budget overrun is allowed only for explicit sustained work. A blocked preview is never returned as an eligible activity. Offer a bridge or diagnostic separately through check-level, or describe a preview as non-assessing. If nothing fits, explain the exclusions and ask one preference rather than inventing a task.

Features are finite numbers in [0, 1]. Missing values default to 0; out-of-range values reject the candidate. Weights:

| Feature | Weight | Meaning |
|---|---:|---|
| goal_relevance | 0.25 | Chosen goal capability/prerequisite match (derived) |
| review_urgency | 0.20 | Due date overdue/30 days, capped at 1 (derived) |
| interest | 0.15 | Explicit learner interest |
| readiness | 0.15 | Eligible dependencies (derived: 1) |
| evidence_value | 0.15 | Opportunity for independent performance |
| diversity | 0.10 | Useful contrast in current context |
| repetition | −0.15 | Similarity to recent work |
| context_switch | −0.10 | Topic switch from chosen goal (derived) |
| time_mismatch | −0.10 | Fraction of chosen budget used (derived, capped at 1) |

Scores round to 6 decimals; ties break by unit ID then version. Derived features cannot be overridden. The scores are interpretable utilities, not probabilities. Modes filter eligibility rather than claiming one universal ranking. After repeated misconceptions, eligible repair for the affected capability is ranked ahead of other sources. Saved action is offered as a resume choice with its reason rather than guaranteed to outrank useful review. Return at most three choices, one selected suggestion, and exclusions with machine-readable reasons. The learner still chooses; selection does not activate a task.

## Replay and session boundaries

The record includes policy version, SHA-256 of canonical JSON input, eligible candidates with features/scores, exclusions and reasons. Identical input and policy produce identical output regardless of candidate order. Keep the snapshot locally to reproduce with the same policy; the digest alone cannot reconstruct candidates. Candidate selection has no access to raw answers, analytics, view/dwell time or inferred personality. It never updates status or retention. Stop at `batch_remaining: 0`; decrement only after the active task is finished or explicitly skipped, not after opening a preview. Do not queue future activities without reranking after new evidence.

## SQLite memory

This policy remains opt-in, outside the ordinary teaching path. Build snapshots from targeted database records only when running discovery. Store the exact input and returned result in a session-linked `recommendations` row; no Markdown section or sidecar file is required. Recommendations never mutate capability evidence. Owner-requested deletion includes these derived records.
