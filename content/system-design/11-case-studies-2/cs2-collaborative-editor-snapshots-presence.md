---
id: cs2-collaborative-editor-snapshots-presence
title: Editor snapshots and cursor presence
level: advanced
minutes: 3
summary: Bound replay using durable snapshots while anchoring ephemeral cursor positions.
sourceLesson: cs2-collaborative-editor
---

## Deep dive 3: presence and cursors

- Presence is **ephemeral**: never write it to the op log. Broadcast it through the session server or a pub/sub channel, throttled to about 10 updates a second per user, with a heartbeat TTL (around 30 s) to drop ghosts.
- Cursor positions must survive concurrent edits. In OT, transform cursor offsets like inserts. In a CRDT, use a **relative position** tied to stable structure, with defined before/after association and deletion behavior, rather than a raw offset.
- Colour, avatar and name come from the session join message, not from every update.

## Deep dive 4: storing revisions

Every op is appended to `doc_ops` with a monotonically increasing `rev`. On its own, the log grows forever and loading a document would mean replaying millions of ops. So:

1. **Snapshots**: every N ops (say 500) or T minutes, the owner writes immutable full state to blob storage at that revision, including synchronization metadata needed for future merges. Publish the snapshot reference only after the blob is durable.
2. **Load** starts from the latest snapshot and replays the operations after it. Replay is bounded by the actual lag of the latest successfully published snapshot, not merely the configured snapshot interval.
3. **History UI**: group consecutive ops by author and time gap into "edit sessions". The user sees "Alice, 10:42" rather than 4,000 keystrokes. To restore a version, rebuild its state, then commit a **new** op that sets the document to it (history is never rewritten).
4. **Compaction**: after a retention window, coarser snapshots can replace fine-grained history only if the product accepts losing intermediate revisions. Retain required named versions under an explicit policy, and preserve deduplication/rebase metadata or define a protocol for very old clients.

Durability rule: **ack only after the op is durably appended**. Clients keep unacknowledged ops and resend them (idempotent via the pair `(client_id, seq)`), so an owner crash loses nothing that was acknowledged.

## What a snapshot proves

A snapshot records the full document state at one known revision. Publishing it only after its blob is durable ensures that recovery can fetch the referenced state. The operation suffix then reconstructs the current document, provided the required operations and synchronization metadata are retained.

The configured interval is a target, not a replay bound. If the snapshot worker is behind or a blob upload fails, the latest published snapshot may be thousands of operations older than planned. Measure the published revision gap and fetch/parse cost. Compaction must respect named historical versions, operation deduplication and very old reconnecting clients rather than deleting every row before a convenient timestamp.

> **Content gap:** no production memory/throughput benchmark or comprehensive proof of a rich-text merge implementation is supplied. Examples demonstrate selected operations; they do not establish every OT transformation law or CRDT invariant. Performance numbers are hypothetical sizing inputs.

## Key takeaways
- Presence is coalesced, throttled and ephemeral rather than written to the durable edit log.
- Cursor association needs transformed offsets or stable relative positions.
- Publish durable snapshots and monitor lag; preserve enough history and sync metadata for the product contract.

## Further reading

- [Conflict-free replicated data type (Wikipedia)](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)
- [CRDT resources (crdt.tech)](https://crdt.tech/)
- [Yjs (GitHub)](https://github.com/yjs/yjs)
- [Automerge](https://automerge.org/)
- [Yjs relative positions](https://docs.yjs.dev/api/relative-positions)
