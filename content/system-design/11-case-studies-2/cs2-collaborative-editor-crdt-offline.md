---
id: cs2-collaborative-editor-crdt-offline
title: CRDT structure and offline permissions
level: advanced
minutes: 4
summary: Use stable sequence identifiers while separating convergence, intent and current access rights.
sourceLesson: cs2-collaborative-editor
---

## Deep dive 2: CRDTs

A **Conflict-free Replicated Data Type** designs the data structure so that the required concurrent operations are **commutative**. Concurrent operations can be reordered while respecting the CRDT’s causal-dependency and duplicate-delivery requirements, with no central transformer.

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
| Topology here | central-server OT | any (P2P OK) |
| Offline | rebase, can be painful | merges naturally |
| Metadata | small | per-element ids |
| Example | Google Docs (2010 account) | Yjs, Automerge apps |

For a cloud product like Google Docs, with always-on servers and a need for access control, **server-ordered OT** is proven. For offline-first or local-first apps, **CRDTs** are compelling. Many modern editors use a CRDT library (Yjs) with a central relay server, getting CRDT merging *and* a server for auth and persistence.

Figma, notably, uses neither pure approach for its object tree. Its multiplayer system is server-authoritative, with **last-writer-wins per object property**, inspired by CRDTs. Design documents need much less character-level merging than text.

## Conflict handling and offline

- **Online concurrent edits**: OT or CRDT handles them automatically, character by character.
- **Offline**: the client keeps working on its local copy and queues ops. On reconnect, OT rebases the queue onto everything committed meanwhile, and CRDTs exchange missing ops (via version vectors or state vectors) and merge.
- **Semantic conflicts** (both people rewrite the same sentence differently) can't be resolved by an algorithm. Some effects may be combined, hidden or overwritten according to the algorithm; convergence does not promise both rewrites remain visible. Product answers include highlighting large offline merges and "suggestion mode" workflows.
- **Permissions change while offline**: the server must re-check authorisation on every op at reconnect, and reject ops from users who no longer have edit rights.

## Evolving at 10x

- **20 M concurrent editors**: more session servers. Sharding by `doc_id` distributes independent documents, subject to shared storage, network and hot-document limits, and the gateway tier scales horizontally.
- **Global latency**: place each document's owner in the region where most of its editors are, migrating it as activity moves. Remote editors still get instant local echo and see others' edits after network transit, batching, durable commit and processing delays.
- **Rich structures** (tables, embedded spreadsheets, drawings): use a tree CRDT or per-object LWW registers, as Figma does, alongside text sequences.
- **Local-first**: move towards CRDT sync so clients work fully offline, with the server as a relay and backup.

## Key takeaways
- Stable identifiers avoid shifting-index transforms under the library’s causal and delivery rules.
- Tombstone metadata and content reclamation have different safety requirements.
- Convergence does not ensure human-readable merges or override revoked edit permission.

## Further reading
- [Operational transformation (Wikipedia)](https://en.wikipedia.org/wiki/Operational_transformation)
- [Conflict-free replicated data type (Wikipedia)](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)
- [CRDTs: the hard parts (Martin Kleppmann)](https://martin.kleppmann.com/2020/07/06/crdt-hard-parts-hydra.html)
- [How Figma's multiplayer technology works (Figma blog)](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/)
- [CRDT resources (crdt.tech)](https://crdt.tech/)
- [Yjs (GitHub)](https://github.com/yjs/yjs)
- [Yjs binary-update semantics](https://docs.yjs.dev/api/document-updates)
- [Fugue research paper](https://arxiv.org/abs/2305.00583)
