---
id: dist-handoff-read-repair
title: Sloppy quorums, hints and read repair
level: intermediate
minutes: 3
summary: Recover missed writes while distinguishing stand-in replicas from strict consistency acknowledgements.
sourceLesson: dist-quorums
---

A failed replica can miss writes even while the rest of a cluster remains healthy. Handoff and read repair close some of those gaps, with different coverage and consistency consequences.

## Sloppy quorums and hinted handoff

Strict quorums lose availability when replicas are unreachable. If B and C are down (with 3 replicas per key and 2 write acknowledgements needed), a write to key k fails, even though most of the cluster is healthy.

A **sloppy quorum** accepts the write on the next healthy nodes on the ring, outside the preference list:

```
pref list: B, C, D  (B, C down)
write W=2 -> D  and  E (stand-in)
E stores it with a hint: "for B"
```

When B comes back, E's **hinted handoff** process delivers the write to B and deletes its copy.

Trade-off: sloppy quorums boost write availability, but R + W > N no longer guarantees overlap, because the W nodes may not be among the N that a reader asks. Until handoff completes, a read from B, C, D can miss the write. Riak uses sloppy quorums by default (its `PR` and `PW` settings can require that a number of true, "primary" replicas respond); Cassandra stores hints (for up to 3 hours by default, `max_hint_window`) but still counts only true replicas towards the consistency level, except at `ANY`.

If a replica is down for longer than the hint window, hints stop being stored for it, and only repair (below) will bring it back up to date.

## Read repair

When a read that asks more than one replica (R, the number of read responses, is above 1) gets differing versions, the coordinator knows some replicas are stale. **Read repair** writes the newest version back to them.

```
read R=3:
B: v5  C: v5  D: v3
return v5; send v5 -> D
```

This only fixes keys that are read. Rarely read keys can stay stale indefinitely, so you also need background repair.

## Key takeaways
- Sloppy quorums accept stand-in replicas, improving availability while breaking strict replica-set overlap.
- Hints deliver missed writes on recovery, but writes missed beyond the hint window require repair.
- Read repair copies the selected newer version to stale replicas on the read path; cold keys need background repair.

## Further reading
- [Dynamo: Amazon's Highly Available Key-value Store (SOSP 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Cassandra Dynamo architecture](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Cassandra hints](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/hints.html)
