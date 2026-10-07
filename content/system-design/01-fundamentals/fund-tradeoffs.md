---
id: fund-tradeoffs
title: Thinking in trade-offs
level: advanced
minutes: 13
summary: The recurring trade-offs behind every design decision (consistency vs availability, latency vs durability, cost, complexity, build vs buy) and how to reason about them explicitly.
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

You met this in the CAP and PACELC lesson. In practice it appears as a spectrum:

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

## Latency vs durability

When is a write "done"? The earlier you acknowledge it, the faster it is and the more you can lose.

| Acknowledge after... | Additional work | Remaining loss risks |
|---|---|---|
| Written to process memory | Memory update | Process or machine failure before persistence |
| Written to OS page cache | Kernel write | OS crash or power loss before persistence |
| fsync to local durable storage | Storage flush | Storage failure, corruption or later logical deletion |
| Durably replicated to a second zone | Replication acknowledgement | Loss of required durable copies, common failures or logical deletion |
| Durably replicated across regions | Cross-region acknowledgement | Protocol/storage failures, loss of required copies or logical deletion |

> [!note] Content gap: generic durability latency figures
> Exact latency ranges are omitted because no representative measurements support them. Replication is not itself a promise that remote copies are durably flushed; verify the acknowledgement contract and failure model.

Real knobs that control this:

- **Postgres** `synchronous_commit`: the default `on` waits for the WAL to be flushed locally (and, if synchronous standbys are configured, on them too). `off` acknowledges before the flush; a crash can lose up to about three times `wal_writer_delay` of commits (around 600 ms with the 200 ms default), but never corrupts the database. `remote_apply` waits until a synchronous standby has *applied* the commit, so reads there see it. It can be set per transaction.
- **Kafka** producer `acks`: `0` (fire and forget), `1` (leader only), `all` (all in-sync replicas), combined with the topic's `min.insync.replicas`. Since Kafka 3.0 the producer defaults to `acks=all` with idempotence on, but `min.insync.replicas` still defaults to 1, a value such as 2 with at least 3 appropriately placed replicas improves tolerance of one replica loss, but no setting alone guarantees zero loss under all failures.
- **Redis** persistence: no persistence, RDB snapshots (lose everything since the last snapshot), or the append-only file (AOF) with `appendfsync always` (slow, safest), `everysec` (the usual choice: lose about a second of writes) or `no` (let the OS decide when to flush).

Batching (group commit) softens this trade-off: fsync once for many writes. If an fsync takes 2 ms, one-commit-per-fsync caps a serial log at about 500 commits/s; flushing 50 commits together lifts that towards 25,000/s, with a latency cost determined by the batching policy, queueing and flush completion time. Kafka and most databases do this, which is why throughput can be high even with durable writes.

## Throughput vs latency

Batching, buffering and compression raise throughput at the cost of per-item latency:

- Kafka's `linger.ms` waits a few milliseconds to fill a batch, giving far higher throughput. Recent versions default it to 5 ms (it was 0 before Kafka 4.0); high-volume producers often raise it further.
- Nagle's algorithm in TCP delays small packets to coalesce them (often disabled with `TCP_NODELAY` for interactive traffic).
- Running servers at high utilisation is cheaper but increases queueing latency, as the latency lesson showed.

## Cost

Cost is a first-class requirement, not an afterthought.

- **Each nine is expensive.** Going from 99.9% to 99.99% often means multi-zone everything, automated failover and on-call staffing. Ask what an hour of downtime actually costs the business.
- **Data transfer adds up.** Cross-zone and internet egress traffic is charged per GB on major clouds. A chatty cross-zone microservice architecture can cost more in transfer than in compute. Zone-aware routing (prefer a same-zone replica), compression and consumers that fetch from the nearest replica all cut the bill.
- **Storage tiers.** Hot SSD, object storage and archive tiers have different storage, request and retrieval prices; compare current provider pricing for the expected workload. Lifecycle policies move cold data down.
- **Over-provisioning vs autoscaling.** Headroom costs money; too little costs outages.

> [!example] Pricing the trade-off
> Suppose an outage costs £20k per hour. 99.9% allows ~8.8 h/year (about £175k of downtime cost if you use the whole budget); 99.99% allows ~53 min (about £18k). The upgrade saves roughly £157k a year. If moving to 99.99% costs £300k/year in extra infrastructure and staff, it isn't worth it on these numbers, unless downtime also causes reputational or regulatory damage.

## Complexity

Complexity is the cost that's easiest to underestimate. Every component adds:

- Things to deploy, upgrade, monitor and secure.
- New failure modes and interactions between them.
- Knowledge the team must hold (and lose when people leave).

Questions to ask:

- Could a **simpler** design meet the requirements? A Postgres table with `SELECT ... FOR UPDATE SKIP LOCKED` is a perfectly good job queue at moderate scale.
- Is the complexity **essential** (required by the problem) or **accidental** (introduced by our choices)?
- Is the complexity **reversible**? Prefer decisions you can undo cheaply. Amazon calls these "two-way doors"; spend careful thought on the "one-way doors" (data models, public APIs, core storage).

Microservices are the canonical example. They buy independent deployment and team autonomy, at the price of distributed failure modes, network latency, eventual consistency between services and much more operational work. Martin Fowler's advice is to start with a monolith unless you have a strong reason not to.

## Build vs buy

| Factor | Favours build | Favours buy/managed |
|---|---|---|
| Core differentiator? | Yes | No |
| Team expertise | Deep | Thin |
| Time to market | Flexible | Urgent |
| Scale/cost at volume | Huge | Moderate |
| Control needed | High | Standard |

- **Buy (or use managed)** for undifferentiated heavy lifting: databases, queues, auth, email, payments, observability. Running your own Kafka or Elasticsearch cluster needs real expertise.
- **Build** when it's your core competitive advantage, when vendors can't meet a hard requirement, or when scale makes vendor pricing untenable. Dropbox moved most of its storage off S3 onto its own infrastructure ("Magic Pocket") only once it stored hundreds of petabytes.
- Watch for **lock-in**, but don't over-pay for portability you'll never use. Abstracting every cloud service "in case we migrate" is itself a cost.

## Other recurring trade-offs

- **Normalisation vs denormalisation**: storage and write simplicity vs read speed. (Databases module.)
- **Push vs pull**: precomputing feeds on write (fan-out on write) vs assembling on read. (Case studies.)
- **Synchronous vs asynchronous**: simple and immediately consistent vs decoupled and resilient. (Messaging module.)
- **Generality vs specialisation**: one flexible store vs purpose-built stores for search, analytics and caching.
- **Freshness vs cost**: cache TTLs, CDN expiry. (Caching module.)

## Communicating trade-offs

In design reviews and interviews, it helps to:

- **Present options, not just a conclusion.** "We considered A and B; we chose B because..."
- **Quantify.** "Synchronous cross-region replication adds ~80 ms per write; our p99 budget is 200 ms."
- **Write it down.** An Architecture Decision Record (context, decision, consequences) lets future engineers understand *why*, and see when the assumptions no longer hold.

## Key takeaways
- Every decision trades something; state what you gain, what you give up, why it's acceptable, and what would change your mind.
- Choose consistency per data type: strong for money and uniqueness, weaker for counts and recommendations.
- Earlier acknowledgement means lower latency and more potential data loss; knobs like Postgres `synchronous_commit` and Kafka `acks` control this.
- Treat cost and complexity as requirements; price the cost of downtime against the cost of extra nines.
- Prefer simple, reversible designs; buy or use managed services for undifferentiated work and build what differentiates you.
- Record decisions and their assumptions (ADRs) so they can be revisited.

## Further reading
- [Microservice Trade-Offs (Martin Fowler)](https://martinfowler.com/articles/microservice-trade-offs.html)
- [MonolithFirst (Martin Fowler)](https://martinfowler.com/bliki/MonolithFirst.html)
- [Asynchronous commit (PostgreSQL docs)](https://www.postgresql.org/docs/current/wal-async-commit.html)
- [Redis persistence (Redis docs)](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Scaling to exabytes and beyond: Magic Pocket (Dropbox)](https://dropbox.tech/infrastructure/magic-pocket-infrastructure)
- [Eventually Consistent (Werner Vogels)](https://www.allthingsdistributed.com/2008/12/eventually_consistent.html)
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
