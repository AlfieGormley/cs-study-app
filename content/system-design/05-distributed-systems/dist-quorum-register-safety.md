---
id: dist-quorum-register-safety
title: Why overlap is not linearizability
level: intermediate
minutes: 3
summary: Identify new-then-old reads and the extra steps needed for an ABD-style register.
sourceLesson: dist-quorums
---

Quorum intersection ensures a reader contacts at least one write participant. Linearizability additionally constrains the order and visibility of operations, including incomplete writes.

## Why R + W > N is not linearizable

As before, N is the number of replicas per key, W the acknowledgements a write needs and R the responses a read needs. It's tempting to think overlap gives strong consistency. It doesn't, for several reasons:

1. **Concurrent writes**: two clients write different values; replicas may observe different orders. Concurrent writes have no intrinsic winner imposed by real-time order; a timestamp policy chooses one, and skew can also misorder writes that are not concurrent.
2. **A write in progress**: if a write has reached 1 of 3 replicas, one reader might see it and a later reader might not. That's a linearizability violation (new value, then old).
3. **Timed-out writes have unknown outcomes**: if a write needs 2 acknowledgements but only 1 replica acked, the write may later spread. That alone is allowed by linearisability; a later new-then-old read sequence or a definitive abort followed by application would violate the relevant contract.
4. **Sloppy quorums** (covered in the next unit) break the overlap entirely.
5. A replica holding the new value **fails and is restored** from an older replica, dropping below W copies.

```
W=3 write of x=1 in progress:
B: x=1   C: x=0   D: x=0
read 1 (B,C)  -> sees 1
read 2 (C,D)  -> sees 0   new then old!
```

You *can* make a quorum register linearizable, but it takes more than R + W > N. The ABD algorithm (Attiya, Bar-Noy and Dolev) needs:

1. **Strict quorums**: no sloppy stand-ins.
2. **Readers write back**: before returning, the reader writes the newest value it saw to a write quorum, so no later reader can see anything older (this fixes case 2).
3. **Writers read first** (with several writers): a writer first asks a quorum for the highest version, then writes with a strictly higher one, so versions follow real-time order rather than skewed clocks (this fixes case 1).

That gives linearizable reads and writes of single registers. It still doesn't give compare-and-set or other read-modify-write operations, which need consensus. Cassandra's blocking read repair gives you something like step 2 (monotonic quorum reads), but its writes use client or coordinator timestamps, so step 3 is missing.

> [!note] Quorums give probabilistic freshness
> Peter Bailis's Probabilistically Bounded Staleness (PBS) work modelled real production latency profiles (from LinkedIn and Yammer) and found that even partial quorums such as 3 replicas with just 1 response for each read or write usually returned the latest value within milliseconds to tens of milliseconds of a write. Eventual isn't usually long, but it isn't bounded either.

## Key takeaways
- Set overlap alone does not prevent in-flight writes, skewed version ordering or replica rollback from producing bad histories.
- An unknown-outcome timed-out write becoming visible is not itself a linearizability violation.
- ABD-style registers use strict quorums, reader write-back and multi-writer version discovery; compare-and-set needs more.

## Further reading
- [Dynamo: Amazon's Highly Available Key-value Store (SOSP 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [ABD atomic registers (Attiya, Bar-Noy and Dolev)](https://groups.csail.mit.edu/tds/papers/Attiya/JACM95.pdf)
- [Cassandra blocking read repair](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/read_repair.html)
- [Cassandra Dynamo architecture](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Probabilistically Bounded Staleness (VLDB 2012)](https://www.vldb.org/pvldb/vol5/p776_peterbailis_vldb2012.pdf)
