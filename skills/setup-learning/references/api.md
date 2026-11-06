# Memory API

Read once when needed, not on every turn. Python 3.10+; normal operation has no pip dependencies. In an initialized folder:

```sh
python .learning/memory.py context
python .learning/memory.py context --capability CAPABILITY_ID
python .learning/memory.py search "recursion"
python .learning/memory.py get notes NOTE_ID
python .learning/memory.py due
python .learning/memory.py turn - < turn.json
```

Pass JSON on stdin directly when the host supports it; a separate payload file is unnecessary. `--root PATH` goes before the command. `context` returns revision, current session, and at most five recent entries; it never returns answer keys. Keep the returned IDs and revision in chat context. Reuse them next turn, updating the revision from the save result. `get units ID --keys` retrieves a key only for marking an answer or requested disclosure. Local owners can still read all database contents; this is not a security boundary.

## One teaching turn

`turn` is the short hot-path API. Omit keys for work that didn't happen. It allocates retry-stable unit/cycle/attempt/assessment IDs from the operation ID and returns saved IDs. A new unit defaults to version `1`, purpose `practice`; a nonempty verification method marks its key checked. Include capability only to create/rename a capability, not to repeat it every turn. Existing progress cannot be edited directly.

First turn:

```json
{
  "operation_id": "unique-first-turn",
  "expected_revision": 0,
  "capability": {"id": "stable-capability-id", "title": "Predict Python list length", "kind": "procedure"},
  "explanation": "len reports the number of items in a list.",
  "unit": {
    "prompt": "What does len([4, 8, 9]) return?",
    "answer": "3",
    "verification": "Executed len([4, 8, 9]) in Python; returned 3."
  },
  "session": {"next_action": "Wait for the learner's prediction."}
}
```

Answer turn (use the unit ID returned above):

```json
{
  "operation_id": "unique-answer-turn",
  "expected_revision": 1,
  "attempt": {"unit_id": "RETURNED_UNIT_ID", "response": "3", "hinted": false, "revealed": false, "skipped": false},
  "assessment": {
    "score": 1, "independent": true, "complete": true,
    "verified": true, "disputed": false,
    "feedback": "Correct: the list has three items.", "evaluator": "tutor; checked key v1"
  },
  "session": {"next_action": "Try a list containing another list.", "closure": "paused"}
}
```

Batch a next `unit` and `explanation` into the same answer turn when continuing. Give its `capability_id` if capability is omitted. Use `purpose: transfer` for fresh independent final transfer, `placement` for diagnostic items, `delayed` only for due retrieval. The activity still needs a fresh checked prompt; labels alone don't prove independence or transfer.

Support flags describe actual exposure. A hint-only turn doesn't replace the active prompt. For disclosure/skip without an answer, save an explicit exposure attempt with `revealed`/`skipped` true and no assessment. Update the next action appropriately. Never count that as an independent pass/failure. A requested skip permits a new active unit. A new prompt cannot replace an unanswered unit without an attempt/skip.

## Less frequent writes

`apply` accepts:

```json
{
  "operation_id": "unique-batch",
  "expected_revision": 2,
  "records": [
    {"table": "topics", "data": {"id": "topic-id", "title": "Python", "goal": "Read simple list expressions"}},
    {"table": "topic_capabilities", "data": {"id": "membership-id", "topic_id": "topic-id", "capability_id": "stable-capability-id"}}
  ]
}
```

Tables/fields are defined in `scripts/schema.sql`; read only the relevant definition when a new operation needs it. Mutable records accept partial updates; evidence/cycles/notes are append-only. Every record needs an ID. Time fields default to current UTC. Recommendation snapshots/results, baseline snapshots and preference values accept nested JSON directly; the helper encodes them. Don't include status/schedule fields in capability writes; transitions are derived. Don't include `outcomes.met_on`; successful transfer sets it. Declare outcomes before transfer. Own-words notes use kind `own_words`, with verbatim body.

Groups: create `prerequisite_groups(id,capability_id)` and `prerequisite_members(id,group_id,prerequisite_id)` in the same batch. All groups are required; any member satisfies one. The transaction validates the complete graph. Archived prerequisites don't unlock readiness.

Tests: create `tests(id,topic_id?,blueprint)` and all versioned `units`, then `test_items(id,test_id,unit_id,ordinal)` before the first attempt. Save responses and assessments as usual; test items don't promote immediately. Include `finalize_tests: [TEST_ID]` in the last/early-stop `apply` or `turn`. Only complete eligible per-capability coverage affects scheduling. Tests containing unassessed or supported items close as partial. Declare any fresh slip recheck before exposure; don't expand coverage retroactively.

Corrections: append an assessment with `supersedes: CURRENT_ASSESSMENT_ID`; never replace a response. A grade already applied to scheduling is blocked until an explicitly authorized maintenance reconciliation. This release deliberately does not guess historical schedule rollback. Archive capabilities/topics with `archived: 1`; never silently delete history. Owner-requested deletion/reset is explicit maintenance, including derived data, summary files, exports and backups—not a teaching-turn command.

`operation_id` makes identical retries no-ops, including after restart. Reusing it with different content fails. A stale expected revision fails without writes; reload targeted context and create a new operation reflecting the new state. SQLite `BEGIN IMMEDIATE`, foreign keys and WAL give one atomic local write; don't copy a live `.sqlite3` file alone—use `backup`.

## Explicit operations only

```sh
python .learning/memory.py backup NEW_BACKUP.sqlite3
python .learning/memory.py check
python .learning/memory.py export NEW_OBSIDIAN_FOLDER
python .learning/memory.py summary-context
python .learning/memory.py summary-save - < summary.json
```

Exports require a new destination, include a manifest, and omit structured unit keys unless `--include-keys` is explicitly requested. Imported prose/Legacy files may contain original keys; inspect before sharing. Exported notes are snapshots; edits aren't synchronized back. Normal teaching never calls export or scans all notes. A previously written My Summary.md is copied as-is, not regenerated.

`summary-save` requires `id`, actual owner `request`, `body` starting `# My Summary`, `evidence_ids` (`table:id` strings), and `expected_revision`. Only summarize-me/explicit personal snapshot requests call it. If My Summary.md contains owner edits, read/merge them and include `expected_file_hash` (SHA-256 of those exact bytes). The helper rejects changed/unowned output otherwise. It saves the database snapshot before the atomic file write; on interruption retry the same payload ID to finish publishing. This is recoverable publication, not a cross-filesystem transaction. Don't include a new timestamp/body on retry.

The optional Markdown importer additionally needs PyYAML. See update-learning's migration instructions. Do not install a dependency during an ordinary lesson.
