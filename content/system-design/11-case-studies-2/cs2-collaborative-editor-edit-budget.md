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
- **Intention preservation**. Preserve the intended targets under defined edit semantics; no merge algorithm can guarantee every competing human intention.
- **Durability**. An acknowledged edit survives the storage contract’s specified failures.
- High availability, with tolerance for flaky connections.

## Budget edits and recipients separately

An illustrative workload has two million open editors at peak, with one tenth actively typing. If a typist sends five batched edit messages per second, the incoming stream is about one million messages per second. A batch can contain several character operations: distinguish protocol messages from the logical edits inside them.

Each batch must reach the other collaborators on its document. More recipients increase outbound fan-out even when incoming edit traffic is unchanged. Presence, acknowledgements and reconnect synchronization add separate streams; do not hide them inside a single “operations per second” number.

## The busiest document matters

Sharding by document spreads independent documents, but all edits to one document still require its integration and durability work. A fleet average can hide a large shared document with hundreds of participants, large snapshots or a burst of offline edits.

Bound the workload with product limits and test their effects. A viewer relay can distribute broadcasts without adding writable owners. Splitting a document into independently owned sections changes cross-section editing and snapshot semantics, so it needs an explicit contract.

## Keep local response and saved state distinct

Optimistic local echo makes typing visible immediately. A saved indicator must wait for the configured durable acknowledgement. Clients retain unacknowledged edits and retry with stable identities after reconnecting.

The operation log grows with retained edits; its physical size includes synchronization metadata, indexes and copies. Snapshots shorten replay, while compaction trades history detail for storage only when the product permits it. Extending the peak rate over a whole day is a stress model, not a prediction of daily traffic. Measure active editors, document fan-out, batch sizes and the actual daily distribution independently.

## Key takeaways
- Local echo gives immediate typing while durable acknowledgements arrive later.
- Multiply active typists by their batched message rate and collaborator fan-out.
- Snapshot lag and hot-document limits matter beyond fleet-wide totals.

## Further reading

- [CRDTs: the hard parts (Martin Kleppmann)](https://martin.kleppmann.com/2020/07/06/crdt-hard-parts-hydra.html)
- [CRDT resources (crdt.tech)](https://crdt.tech/)
- [Yjs (GitHub)](https://github.com/yjs/yjs)
- [Google Docs sharing limits](https://support.google.com/a/users/answer/9305685?hl=en)
