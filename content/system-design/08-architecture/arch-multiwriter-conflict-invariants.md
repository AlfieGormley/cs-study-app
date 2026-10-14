---
id: arch-multiwriter-conflict-invariants
title: Choosing multi-writer conflict semantics
level: advanced
minutes: 4
summary: Compare LWW, CRDT merge and application resolution while keeping hard invariants explicit.
sourceLesson: arch-multi-region
---

Home-region ownership avoids concurrent regional writes to one record. When local writes to that same record are required in several regions, choose the conflict semantics deliberately.

## Conflict handling across regions

### When you must accept multi-region writes: conflict handling

If two regions can write the same record concurrently (DynamoDB global tables, Cassandra multi-DC, CouchDB, multi-primary MySQL), concurrent writes will collide. Options:

1. **Last-writer-wins (LWW)**: keep the write with the highest timestamp. Simple, and what DynamoDB global tables do in their default, eventually consistent mode, but it **silently discards** the other write, and clock skew can make the "wrong" one win. (Since 2025 DynamoDB also offers a multi-Region *strongly* consistent mode for global tables, which rejects overlapping cross-Region writes with a retryable conflict error and adds cross-region communication latency.)
2. **Merge by data type**: use **CRDTs** (conflict-free replicated data types) that converge under their required delivery and merge assumptions, including eventual exchange of updates: counters (each region increments its own slot; the total is the sum, shown below), sets with add/remove semantics, registers with defined rules. Riak and Redis Enterprise's active-active mode use CRDTs.
3. **Application-level resolution**: keep both versions (siblings) and let the application or the user merge them, as with conflicting edits in a document.
4. **Avoid it for invariants**: anything with a hard constraint (account balance must not go negative; one seat sold once) usually uses a single writer or a consensus-based store (Spanner, CockroachDB). Some bounded invariants can instead use escrow: preallocate disjoint spending or stock rights to regions, and reject locally when rights run out. Transferring rights then requires coordination.

The counter CRDT (often called a G-Counter, a grow-only counter) is the simplest to see. Each region only ever increases its own slot, and merging two copies takes the larger value of each slot, so no increment is ever counted twice or lost:

```formula
C = c_EU + c_US
merge(a, b)_r = max(a_r, b_r)
where
C: the counter's value as read by anyone
c_EU: the EU region's slot: how many increments the EU has made
c_US: the US region's slot
merge(a, b)_r: slot r of the result of merging two copies a and b of the counter
a_r: slot r in copy a
b_r: slot r in copy b
r: one region's slot, e.g. EU
max: the larger of the two values
In words: the total is the sum of every region's slot, and merging keeps the highest value seen for each slot.
```

If one copy has {EU: 41, US: 60} and another has {EU: 40, US: 62}, the merge is {EU: 41, US: 62}, and the counter reads 103.

> [!example] Shopping basket vs bank balance
> A basket can use a CRDT with chosen add/remove semantics, but quantities, checkout, deletion and inventory constraints still need explicit product rules. Convergence alone does not bound every bad outcome. An ordinary mergeable balance counter cannot safely let both regions independently approve £100 against the same £150 balance. Escrow can partition spending rights, but neither region may spend beyond its allocation. Route balance updates to the account's fenced home region, or use a strongly consistent store, and atomically validate and apply each debit.

### Counter identity and decrements

A grow-only counter needs stable unique replica identities, durable slots and atomic local increments. Delivery retries are deduplicated separately from the state merge. To represent decrements, a PN-Counter combines two grow-only counters and reads their difference: total increments minus total decrements. That still does not enforce one like per user without separate identity rules. During a partition totals can disagree without a fixed small bound, then converge after updates are eventually exchanged.

DynamoDB's MREC mode resolves conflicts per item, including different-attribute updates; it does not provide an attribute-wise merge. MRSC is a separately configured strongly consistent mode. Current AWS documentation permits combinations of three supported Regions, including Regions on different continents. You cannot change a global table's consistency mode after creation, so adopting MRSC for an existing EU/US MREC table still requires a migration rather than an in-place switch.

## Key takeaways
- LWW resolves a conflict by discarding one competing write; it does not merge independent whole-item edits.
- CRDT convergence relies on the data type's identity, durable state, merge and eventual-delivery assumptions.
- A counter merge does not enforce one-like-per-user, non-negative balances or unique reservations.
- Use atomic authoritative operations or bounded exclusive rights for invariants that merge semantics cannot preserve.

## Further reading
- [AWS: DynamoDB global tables](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GlobalTables.html)
- [Wikipedia: Conflict-free replicated data type](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)
