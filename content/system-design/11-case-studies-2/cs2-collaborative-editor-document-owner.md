---
id: cs2-collaborative-editor-document-owner
title: Document contracts and durable ownership
level: advanced
minutes: 3
summary: Route a document to one fenced owner and atomically append each unique edit.
sourceLesson: cs2-collaborative-editor
---

## API design

This is an illustrative endpoint contract, not a runnable HTTP request. Arrows distinguish responses from submitted fields.

```
GET /v1/docs/{id}
  -> { snapshot, revision, ... }

WS  /v1/docs/{id}/session
  client -> server:
    {type:"op", base_rev: 41,
     client_id, seq: 17, ops:[...]}
    {type:"presence", cursor, selection}
  server -> client:
    {type:"ack", seq: 17, rev: 42}
    {type:"op", rev: 43, author, ops}
    {type:"presence", user, cursor}

GET /v1/docs/{id}/revisions?before=..
POST /v1/docs/{id}/restore {rev}
```

the pair `(client_id, seq)` makes op submission **idempotent**. A resend after a reconnect is recognised and acknowledged, not applied twice.

## Data model

This is a schema sketch: PK marks the primary key. It omits executable type declarations and migrations.

```
documents(doc_id PK, owner, title,
  latest_rev, latest_snapshot_rev, acl)

doc_ops(doc_id, rev,         PK both
  author, client_id, seq, ops(blob),
  created_at)

doc_snapshots(doc_id, rev,   PK both
  content_ref (blob store), created_at)

named_versions(doc_id, rev, label, by)
```

`(doc_id, rev)` as the op log key gives a **total order per document**. Commit the append atomically with a check of the expected current revision, the current owner epoch and a unique client-operation ID. Revision uniqueness alone does not fence a stale owner or deduplicate retried edits.

## High-level architecture

Follow the arrows as data paths; the drawing is not a deployment specification.

```
 Browsers / apps
      |  WebSocket
      v
+---------------+
| WS gateway    |  auth, routing by
| (stateless)   |  doc_id
+---------------+
      |
      v
+---------------+    +-------------+
| Doc session   |--->| Presence    |
| server (owner |    | pub/sub     |
| per doc_id)   |    | (ephemeral) |
+---------------+    +-------------+
   |         |
   v         v
+--------+ +-----------+
| Op log | | Snapshots |
| (KV/   | | (blob)    |
|  SQL)  | +-----------+
+--------+
```

All sessions for a document route to **one session server**, its owner, chosen by consistent hashing on `doc_id` and held by a lease. The owner keeps the document in memory, orders incoming ops, appends them to the op log, and broadcasts them. If the owner dies, another server takes the lease, loads the latest snapshot, replays ops after it, and clients reconnect.

## Bottlenecks and trade-offs

- **The per-document owner** is a natural serialisation point, which is a bottleneck for very hot documents. Cap editors, and fan out to viewers through a pub/sub tree.
- **Owner failover** creates a short gap, so clients must buffer and resend. The durable store must atomically reject appends from an obsolete owner epoch, in addition to checking the expected revision and deduplicating operation IDs. A unique revision alone cannot reject every stale owner.
- **Large documents** (100-page specs) make snapshots expensive. Split the document into blocks or sections with their own op streams.
- **The cost of OT complexity vs CRDT memory**. Pick based on the offline requirements and the team's appetite for subtle algorithms.

## Key takeaways
- Append the revision, owner epoch and operation-deduplication record atomically.
- A unique revision does not independently fence stale owners.
- Clients retain unacknowledged edits and retry after owner recovery.

## Further reading

- [CRDT resources (crdt.tech)](https://crdt.tech/)
- [Yjs (GitHub)](https://github.com/yjs/yjs)
