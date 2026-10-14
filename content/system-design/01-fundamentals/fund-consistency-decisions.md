---
id: fund-consistency-decisions
title: Make a consistency decision explicit
level: advanced
minutes: 3
summary: State the gain, cost, acceptable business behaviour and assumptions behind a choice of consistency.
sourceLesson: fund-tradeoffs
---

Every interesting design decision gives something up. Senior engineers aren't distinguished by knowing the "right" technology. They're distinguished by naming what each option costs, quantifying it where possible, and matching it to the requirements.

This lesson collects the trade-offs you'll meet again and again in later modules.

## A template for any decision

When you choose between options, say these four things out loud:

1. **What we gain.** "Reads are served from local replicas in ~2 ms."
2. **What we give up.** "Reads may be up to 1 s stale."
3. **Why that's acceptable here.** "Product prices change rarely; checkout re-reads from the primary."
4. **What would change our mind.** "If we add live auctions, staleness becomes unacceptable."

Point 4 is often skipped and is the most valuable. It records the assumption the design depends on.

## Consistency vs availability (and latency)

The earlier CAP and PACELC units established this trade-off. In practice it appears as a spectrum:

```
 stronger                      weaker
 consistency                   consistency
 <------------------------------------->
 linearisable  causal  read-your  eventual
               writes
 coordination                 fewer read
 may add latency              coordination
                              waits
```

The diagram is only a rough trade-off sketch: weaker consistency does not guarantee faster responses or availability, and consistency models are not all points on a single total order.

How to choose:

| Data | Typical choice |
|---|---|
| Account balance, stock | Strong |
| Username uniqueness | Strong |
| User's own profile edits | Read-your-writes |
| Like counts, view counts | Eventual |
| Recommendations | Eventual, even stale |

> [!tip] Mix within one system
> Most real systems use strong consistency for a small core of critical data and weaker models for everything else. An e-commerce site might serve the catalogue from a cache that's minutes stale, but decrement inventory with a transactional conditional write.

## Key takeaways
- State what an option gains, what it gives up, why that is acceptable and what would change your mind.
- Money, inventory and uniqueness need authoritative decisions; counts and recommendations often permit staleness.
- Consistency models do not form a simple speed guarantee; match the actual contract to each data type.

## Further reading
- [Eventually Consistent (Werner Vogels)](https://www.allthingsdistributed.com/2008/12/eventually_consistent.html)
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
