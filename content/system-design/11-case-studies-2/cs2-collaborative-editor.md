---
id: cs2-collaborative-editor
title: Collaborative editor (Google Docs)
level: advanced
minutes: 17
summary: Design real-time co-editing, covering operational transformation versus CRDTs, a per-document session server, presence and cursors, offline edits, and storing revisions as an op log plus snapshots.
---

Real-time collaborative editing asks for something that sounds impossible. Several people type into the **same** document at the **same** moment, everyone sees their own keystrokes instantly, and everyone ends up with **the same** document, with deterministic conflict handling. Convergence does not guarantee that every competing human intention survives.

The interview centres on one decision, **Operational Transformation (OT) or CRDTs**, and on the architecture that follows from it.

## Requirements

### Functional
- Several users edit a rich-text document at once, and see each other's changes within about 100–200 ms.
- Presence: who's here, plus live cursors and selections.
- Offline editing that merges on reconnect.
- Revision history: view or restore earlier versions, and see who changed what.
- Comments anchored to text ranges, and sharing permissions.

### Non-functional
- **Local echo with no wait**. Your own typing must never wait for the network (optimistic local apply).
- **Convergence**. All replicas reach an identical state once they've seen the same operations.
- **Intention preservation**. My insertion goes where I meant it to, even after concurrent edits.
- **Durability**. An acknowledged edit is never lost.
- High availability, with tolerance for flaky connections.

## Back-of-the-envelope

```
DAU: 50 M; peak concurrent editors: 2 M
Concurrently *typing*: ~10% = 200 k
Client batches keystrokes every ~200 ms
  -> 200 k x 5 msgs/s = 1 M ops/s in
Avg 3 collaborators per doc: each op
  goes to the ~2 others
  -> ~2 M msgs/s fan-out
Op size ~100 B -> 100 MB/s in
  = ~8.6 TB/day if peak is sustained
```

What matters:

- **Per-document load is tiny** (a few to a few hundred ops a second), but there are **millions of documents**. Shard by document, and benchmark how many active documents each server can host under its actual fan-out and document sizes.
- The op log grows fast. You need **snapshots plus compaction**, or storage and load time grow without limit.
- Google Docs limits how many people can work in one file at the same time (its help pages put it at around 100), and beyond that further users get a reduced, mostly view-only experience. A cap like that bounds the worst case for any one document.

## API design

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

`client_id + seq` makes op submission **idempotent**. A resend after a reconnect is recognised and acknowledged, not applied twice.

## Data model

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

## Deep dive 1: Operational Transformation

Google described its use of OT in a 2010 engineering post; this is a historical implementation account. OT represents edits as operations such as `insert(pos, text)` and `delete(pos, len)`. When two operations are concurrent, one is **transformed** against the other so it still makes sense.

### Example
The document is `abc` at revision 10.

- Alice: `insert(1, "X")`, giving `aXbc`.
- Bob, at the same time: `delete(2)` (removing `c`), giving `ab`.

The server receives Alice's op first and commits it as rev 11. Bob's op says `base_rev = 10`, so the server transforms it against everything committed since rev 10:

```
transform(delete(2), insert(1,"X"))
  insert is before pos 2 -> shift right
  = delete(3)
```

Applying `delete(3)` to `aXbc` gives `aXb`. That's correct: Bob's `c` is gone and Alice's `X` is kept. Alice receives Bob's transformed op, Bob receives Alice's op (transformed against his pending op on his client), and both converge to `aXb`.

### Client-server OT in practice
- The client keeps three things: the last acknowledged server revision, **one in-flight op** awaiting ack, and a **buffer** of ops typed since.
- Incoming server ops are transformed against the in-flight and buffered ops before being applied locally.
- Certain central-server OT protocols avoid the need for TP2 by constraining causal delivery and transformation paths; centralisation alone is insufficient. TP1 requires two concurrent ops to converge when transformed and applied in either order. More general transformation paths also require TP2, which is notoriously hard to get right, and several published algorithms were later shown to be incorrect.

**Pros**: compact ops, no per-character metadata, a mature approach, and a natural fit for a server-authoritative product.

**Cons**: transform functions multiply with op types (insert, delete, format, table operations...), so correctness is subtle. The client-server OT design here uses a central sequencer per document; decentralized OT protocols also exist. Offline edits that diverge a long way take a lot of transforms to rebase.

## Deep dive 2: CRDTs

A **Conflict-free Replicated Data Type** designs the data structure so that concurrent operations **commute**. Concurrent operations can be reordered while respecting the CRDT’s causal-dependency and duplicate-delivery requirements, with no central transformer.

For text sequences (RGA, YATA in Yjs, Automerge's list type, Fugue):

- Every character gets a **globally unique, ordered id**, such as `(client_id, counter)`.
- An insert says "put this character after character id P" rather than "at index 5". Ids don't shift when others edit, so there's nothing to transform.
- Deletes mark a character as a **tombstone**, because it may still be referenced as an anchor by concurrent inserts.
- Concurrent inserts at the same anchor are ordered by a deterministic tie-break (for example, comparing ids), so every replica picks the same order.

**Pros**:
- No central authority is needed for correctness: **peer-to-peer and offline-first** work naturally.
- A correct CRDT implementation converges when its delivery, merge and causal assumptions are met; application-level intent is a separate issue.
- The server can be a dumb relay plus storage.

**Cons**:
- **Metadata overhead**: ids and tombstones per character. Modern implementations (Yjs, Automerge 2) compress runs well, but a heavily edited document can still carry several times its visible size.
- **Interleaving anomalies**: some algorithms interleave two users' concurrent words character by character. Newer designs (such as Fugue) avoid this.
- Rich text (formatting spans across concurrent edits) needs extra work. Peritext is one research answer.
- Removing structural identifiers requires an algorithm-specific safety protocol. Reclaiming deleted payload bytes is different: systems such as Yjs can collect content while retaining enough structure for synchronization.

Martin Kleppmann's talk "CRDTs: the hard parts" is the standard reference for these issues.

### Which to choose?

| | OT | CRDT |
|---|---|---|
| Topology | central server | any (P2P OK) |
| Offline | rebase, can be painful | merges naturally |
| Metadata | small | per-element ids |
| Example | Google Docs (2010 account) | Yjs, Automerge apps |

For a cloud product like Google Docs, with always-on servers and a need for access control, **server-ordered OT** is proven. For offline-first or local-first apps, **CRDTs** are compelling. Many modern editors use a CRDT library (Yjs) with a central relay server, getting CRDT merging *and* a server for auth and persistence.

Figma, notably, uses neither pure approach for its object tree. Its multiplayer system is server-authoritative, with **last-writer-wins per object property**, inspired by CRDTs. Design documents need much less character-level merging than text.

## Deep dive 3: presence and cursors

- Presence is **ephemeral**: never write it to the op log. Broadcast it through the session server or a pub/sub channel, throttled to about 10 updates a second per user, with a heartbeat TTL (around 30 s) to drop ghosts.
- Cursor positions must survive concurrent edits. In OT, transform cursor offsets like inserts. In a CRDT, use a **relative position** tied to stable structure, with defined before/after association and deletion behavior, rather than a raw offset.
- Colour, avatar and name come from the session join message, not from every update.

## Deep dive 4: storing revisions

Every op is appended to `doc_ops` with a monotonically increasing `rev`. On its own, the log grows forever and loading a document would mean replaying millions of ops. So:

1. **Snapshots**: every N ops (say 500) or T minutes, the owner writes immutable full state to blob storage at that revision, including synchronization metadata needed for future merges. Publish the snapshot reference only after the blob is durable.
2. **Load** = latest snapshot + ops after it. Replay is bounded by the actual lag of the latest successfully published snapshot, not merely the configured snapshot interval.
3. **History UI**: group consecutive ops by author and time gap into "edit sessions". The user sees "Alice, 10:42" rather than 4,000 keystrokes. To restore a version, rebuild its state, then commit a **new** op that sets the document to it (history is never rewritten).
4. **Compaction**: after a retention window, coarser snapshots can replace fine-grained history only if the product accepts losing intermediate revisions. Retain required named versions under an explicit policy, and preserve deduplication/rebase metadata or define a protocol for very old clients.

Durability rule: **ack only after the op is durably appended**. Clients keep unacknowledged ops and resend them (idempotent via `client_id + seq`), so an owner crash loses nothing that was acknowledged.

## Conflict handling and offline

- **Online concurrent edits**: OT or CRDT handles them automatically, character by character.
- **Offline**: the client keeps working on its local copy and queues ops. On reconnect, OT rebases the queue onto everything committed meanwhile, and CRDTs exchange missing ops (via version vectors or state vectors) and merge.
- **Semantic conflicts** (both people rewrite the same sentence differently) can't be resolved by an algorithm. Some effects may be combined, hidden or overwritten according to the algorithm; convergence does not promise both rewrites remain visible. Product answers include highlighting large offline merges and "suggestion mode" workflows.
- **Permissions change while offline**: the server must re-check authorisation on every op at reconnect, and reject ops from users who no longer have edit rights.

## Bottlenecks and trade-offs

- **The per-document owner** is a natural serialisation point, which is a bottleneck for very hot documents. Cap editors, and fan out to viewers through a pub/sub tree.
- **Owner failover** creates a short gap, so clients must buffer and resend. The durable store must atomically reject appends from an obsolete owner epoch, in addition to checking the expected revision and deduplicating operation IDs. A unique revision alone cannot reject every stale owner.
- **Large documents** (100-page specs) make snapshots expensive. Split the document into blocks or sections with their own op streams.
- **The cost of OT complexity vs CRDT memory**. Pick based on the offline requirements and the team's appetite for subtle algorithms.

## Evolving at 10x

- **20 M concurrent editors**: more session servers. Sharding by `doc_id` distributes independent documents, subject to shared storage, network and hot-document limits, and the gateway tier scales horizontally.
- **Global latency**: place each document's owner in the region where most of its editors are, migrating it as activity moves. Remote editors still get instant local echo and see others' edits after network transit, batching, durable commit and processing delays.
- **Rich structures** (tables, embedded spreadsheets, drawings): use a tree CRDT or per-object LWW registers, as Figma does, alongside text sequences.
- **Local-first**: move towards CRDT sync so clients work fully offline, with the server as a relay and backup.

## Key takeaways
- Apply edits locally at once, and converge with OT (server-ordered transforms of index-based ops) or CRDTs (unique ids per element, so ops commute).
- A central sequencer can support an OT protocol designed to avoid TP2, but its control algorithm and transformation functions must be verified together. CRDTs shine offline and peer-to-peer, at the cost of per-element metadata and tombstones.
- Route each document to one owner (consistent hashing plus a lease), which orders ops, appends to a `(doc_id, rev)` log, acks after the write is durable, and broadcasts.
- Keep presence ephemeral and throttled. Anchor cursors to element ids (CRDT) or transform them (OT).
- Store revisions as an op log plus periodic snapshots. Restoring is a new op, and old fine-grained ops are compacted over time.

> **Content gap:** no production memory/throughput benchmark or comprehensive proof of a rich-text merge implementation is supplied. Examples demonstrate selected operations; they do not establish every OT transformation law or CRDT invariant. Performance numbers are hypothetical sizing inputs.

## Further reading

- [Google Docs conflict resolution (2010)](https://drive.googleblog.com/2010/09/whats-different-about-new-google-docs_22.html) — the historical engineering explanation of OT.
- [Operational transformation (Wikipedia)](https://en.wikipedia.org/wiki/Operational_transformation)
- [Conflict-free replicated data type (Wikipedia)](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)
- [CRDTs: the hard parts (Martin Kleppmann)](https://martin.kleppmann.com/2020/07/06/crdt-hard-parts-hydra.html)
- [How Figma's multiplayer technology works (Figma blog)](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/)
- [CRDT resources (crdt.tech)](https://crdt.tech/)
- [Yjs (GitHub)](https://github.com/yjs/yjs)
- [Automerge](https://automerge.org/)
