---
id: cs2-collaborative-editor-edit-budget
title: Collaborative editing workload
level: advanced
minutes: 4
summary: Budget operation fan-out and storage using explicit active-editor assumptions.
sourceLesson: cs2-collaborative-editor
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

Assume 50 M DAU (daily active users: distinct people who use the product on a given day) and 2 M editors with a document open at the peak. Only some of those are typing at any instant, say 10%. Clients don't send every keystroke separately; they batch keystrokes and send one message about every 200 ms (milliseconds), which is 5 messages a second while someone types:

```formula
T = E × f = 2,000,000 × 0.1 = 200,000
m = 1 msg / (200 ms) = 5 msgs/s
O = T × m = 200,000 × 5/s = 1 M ops/s
where
T: editors typing at the same moment
E: editors with a document open at peak; 2 million
f: fraction typing at any instant; assumed 10% = 0.1
m: messages per second from one typing client
ms: milliseconds, thousandths of a second; 1,000 ms = 1 s
msgs: messages sent to the server
msg: one message
O: operations (edits) arriving at the servers per second
M: million
ops: operations, the edit messages
s: seconds
In words: 200,000 people typing, each sending 5 batched messages a second, is about a million operations a second.
```

Each operation must reach the other people in the same document. With about 3 collaborators per document, each op goes to about 2 others. With about 100 bytes per op:

```formula
F = O × (c − 1) = 1 M/s × 2 = 2 M msgs/s
I = O × b = 1,000,000/s × 100 B = 100 MB/s
D = 100 MB/s × 86,400 s ≈ 8.6 TB/day
where
F: messages per second sent out to other collaborators (fan-out)
O: operations arriving per second; 1 million
c: average people editing one document; about 3
I: incoming data per second
b: bytes per operation (B); about 100
D: data per day, if the peak rate lasted all day
M: million
msgs: messages
s: seconds; a day has 86,400 s
B: bytes
MB: megabytes, 1,000,000 bytes
TB: terabytes, 10^12 bytes
day: one day
≈: approximately equal to
In words: a million ops a second fans out to about 2 million messages a second, about 100 MB a second coming in, or up to about 8.6 TB a day.
```

The 8.6 TB/day figure is an upper bound: real traffic falls well below peak for most of the day.

What matters:

- **Per-document load is tiny** (a few to a few hundred ops a second), but there are **millions of documents**. Shard by document, and benchmark how many active documents each server can host under its actual fan-out and document sizes.
- The op log grows fast. You need **snapshots plus compaction**, or storage and load time grow without limit.
- Google Docs limits how many people can work in one file at the same time (its help pages put it at around 100), and beyond that further users get a reduced, mostly view-only experience. A cap like that bounds the worst case for any one document.

## Key takeaways
- Local echo gives immediate typing while durable acknowledgements arrive later.
- Multiply active typists by their batched message rate and collaborator fan-out.
- Snapshot lag and hot-document limits matter beyond fleet-wide totals.

## Further reading

- [CRDTs: the hard parts (Martin Kleppmann)](https://martin.kleppmann.com/2020/07/06/crdt-hard-parts-hydra.html)
- [CRDT resources (crdt.tech)](https://crdt.tech/)
- [Yjs (GitHub)](https://github.com/yjs/yjs)
- [Google Docs sharing limits](https://support.google.com/a/users/answer/9305685?hl=en)
