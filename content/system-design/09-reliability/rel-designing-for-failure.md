---
id: rel-designing-for-failure
title: Designing for failure
level: basic
minutes: 11
summary: Classify how components fail, find single points of failure, contain the blast radius and use redundancy that actually helps.
---

At scale, failure is not an exception; it is the normal background noise. A fleet of 10,000 disks with a 2% annual failure rate loses roughly **200 disks a year** (10,000 × 0.02), or about four a week.

Fan-out makes rare slowness common. If one request makes many independent downstream calls, the chance that *at least one* of them is slow is one minus the chance that *every* call is fast:

```formula
P_slow = 1 − (1 − p)^n
P_slow = 1 − (1 − 0.01)^50
P_slow = 1 − 0.99^50
P_slow ≈ 1 − 0.605 ≈ 0.395 = 39.5%
where
P_slow: the probability that a request hits at least one slow downstream call, a number from 0 to 1 (0.395 = 39.5%)
p: the probability that any single downstream call is slow, here 1% = 0.01
n: the number of independent downstream calls one request makes, here 50
^: "to the power of"; 0.99^50 means 50 copies of 0.99 multiplied together
≈: approximately equal to (the result is rounded)
%: per cent, parts per hundred; 0.395 = 39.5%
In words: each call is fast 99% of the time, but all 50 being fast happens only about 60% of the time, so roughly 4 requests in 10 meet at least one slow call.
```

This assumes the calls are slow independently of each other. Real delays are often correlated (one overloaded host slows many calls at once), and the answer also depends on where you draw the line for "slow".

Reliability engineering starts by accepting this and asking three questions of every design:

1. *How* can each component fail?
2. If it fails, *how much* of the system goes with it?
3. What keeps working, and does anyone have to wake up?

The fundamentals module covered availability "nines" and how availability multiplies across hard dependencies in series. This lesson is about the shapes of failure behind those numbers and the structural tools for containing them.

## A taxonomy of failure modes

Distributed systems literature classifies faults by how badly a component can misbehave. These categories highlight different symptoms; they are not a universal strict hierarchy. A Byzantine model permits arbitrary behavior, including omission or timing faults.

| Mode | What happens | Example |
|---|---|---|
| Crash | Stops executing; detection may be uncertain | Kernel panic, OOM kill |
| Omission | Drops some messages | Full queue, lost packet |
| Timing / latency | Responds, but too late | GC pause, noisy neighbour |
| Byzantine | Responds wrongly | Bit flip, bug, attacker |

### Crash failures

The easiest to handle, because silence is unambiguous *if you can detect it*. Health checks, heartbeats and leases can suspect loss of responsiveness; a load balancer stops routing to the dead node and a container orchestrator replaces it.

The catch: in an asynchronous network you cannot distinguish "crashed" from "very slow". Remote timeout-based detectors can be wrong; local process/OS notifications can also provide failure evidence.

### Omission failures

The component is up but some requests or replies vanish. A saturated connection pool, a dropped UDP packet, a message broker that discards on overflow. Omissions look like timeouts to the caller, which is why they push people towards retries (next lesson).

### Latency failures: the dangerous middle

A node that is **slow but alive** is often worse than a dead one. It still passes shallow health checks, still receives traffic, and ties up the caller's threads and connections while it dawdles.

```
Healthy:  req ──▶ 20ms ──▶ ok
Crashed:  req ──▶ reset or timeout
Gray:     req ──▶ ........ 9s ..... ok
          (threads held the whole time)
```

Microsoft researchers named this kind of fault **gray failure** (Huang et al., HotOS 2017): the system's failure detector sees a healthy component while the applications using it see a broken one. They argue that subtle faults like this, rather than clean crashes, are behind many major cloud availability breakdowns. Typical examples are a degraded disk, a NIC dropping a few per cent of packets, or a JVM stuck in GC. The fix is a combination of tight timeouts, latency-aware load balancing, and health checks that test real work, not just "is the process listening".

### Byzantine failures

The component returns *wrong* answers: corrupted data, a buggy release computing the wrong price, or a malicious node. Tolerating liars costs far more replicas than tolerating crashes. Classic partially synchronous Byzantine consensus protocols such as PBFT need:

```formula
R ≥ 3 × f + 1
R ≥ 3 × 1 + 1 = 4
where
R: the number of replicas (copies of the service) running the protocol
f: the number of replicas that may be Byzantine (faulty or lying) at the same time, here 1
≥: "is at least"
In words: to survive one replica that lies, you need at least four replicas; to survive two, at least seven.
```

For comparison, a crash-tolerant protocol such as Raft needs only three replicas to survive one crash, because a majority of two can still agree. Bounds differ with timing, authentication and trust assumptions; this is not a universal rule for every Byzantine-tolerant system.

In practice, ordinary systems defend against the *accidental* Byzantine cases cheaply:

- **Checksums** on disk blocks and network payloads (S3, HDFS and Kafka all checksum data).
- **Validation** of inputs and invariants at service boundaries.
- **End-to-end verification**, e.g. reconciling ledgers nightly.

> [!note] Fail-fast is a design choice
> Failing fast on a detected broken invariant can contain corruption; consider redundancy and recovery before terminating a process. A process that detects a broken invariant and exits is far easier for the rest of the system to handle than one that keeps serving corrupt data.

## Single points of failure

A **single point of failure (SPOF)** is any component whose failure takes the whole service down. The obvious ones are easy to spot: one database primary, one load balancer. The dangerous ones hide:

- **Shared configuration**: one bad config push to every node at once.
- **DNS and certificates**: an expired TLS certificate is a global SPOF with a calendar date.
- **Control planes**: your redundant VMs are fine, but you can't launch new ones because the provider's API is down.
- **People and process**: the only engineer who knows how to restore backups.
- **Hidden dependencies**: every "independent" region authenticates against one identity service in `us-east-1`.

A useful exercise is to draw the request path and ask, for each box and arrow, "what if this vanished right now?"

```
 Client
   │
   ▼
 [DNS] ─── SPOF? (one provider)
   │
   ▼
 [LB] ──── SPOF? (one instance)
   │
 ┌─┴──────┐
 ▼        ▼
[App]   [App]  ok: redundant
 └──┬─────┘
    ▼
 [Primary DB] ── SPOF!
```

## Blast radius

Redundancy stops a failure taking *everything* down. **Blast radius** asks the next question: when something does fail, how many users or requests are affected?

Techniques for shrinking it:

- **Cells**: split the service into independent full copies (cells), each serving a slice of customers. A bad deploy or poison request takes out one cell, not all of them. AWS uses cell-based architecture widely for this reason. The thin routing layer that maps customers to cells is shared by all of them, so it must be kept as simple and static as possible.
- **Shuffle sharding**: give each customer a random subset of workers. A customer who sends poison requests only damages their own subset. The number of different subsets ("shuffle shards") is a combination count (see the formula below).
- **Availability zones and regions** as fault boundaries, so a power or network event is contained.
- **Staged rollouts**: deploy to one host, then one zone, then one region (covered in the deployments lesson).

How much does shuffle sharding help? Count the distinct subsets a customer could be given. Choosing k workers out of n, where order doesn't matter, is the "n choose k" count:

```formula
S = C(n, k) = n! / (k! × (n − k)!)
S = C(8, 2) = (8 × 7) / (2 × 1)
S = 56 / 2 = 28
where
S: the number of distinct worker subsets (shuffle shards) available
C(n, k): "n choose k", the number of ways to pick k items from n when order doesn't matter
n: the total number of workers, here 8
k: the number of workers given to each customer, here 2
!: factorial; 4! = 4 × 3 × 2 × 1 = 24
In words: with 8 workers and 2 per customer there are 28 different pairs, so a randomly chosen other customer has only a 1 in 28 chance (about 3.6%) of sharing both workers with a poisonous customer.
```

Customers who share just *one* worker still have a healthy second worker, so they degrade rather than fail. The calculation assumes shards are assigned at random and that a customer survives as long as one of its workers is healthy.

> [!example] Shuffle sharding in numbers
> AWS has described Route 53 shuffle sharding over 2,048 virtual name servers, giving each domain 4 of them. The number of possible combinations, 2,048 choose 4, is about 730 billion, so an attack against one customer's servers almost never fully overlaps another's.

## Redundancy that actually works

Adding a second copy helps against failures not shared by all copies; full statistical independence is needed for the simple product-probability calculation. Two servers in the same rack share a power supply and a switch; two databases in the same region share a control plane; two replicas running the same buggy binary fail together.

| Redundancy | Protects against | Doesn't protect against |
|---|---|---|
| N+1 instances | One host dying | Bad deploy to all |
| Multi-AZ | Data-centre outage | Region control plane |
| Multi-region | Regional disaster | Global config error |
| Diverse software | Shared bug | Shared bad data |

### Active-active vs active-passive

- **Active-passive**: a standby takes over when the primary fails. Simple, but an unexercised standby may hide faults until failover; drills and validation reduce this risk, and failover itself can fail.
- **Active-active**: all copies serve traffic. Normal serving paths are exercised continuously; failure paths still need testing, but you must handle concurrent writes and must keep **enough headroom** that the survivors can absorb the load.

### Capacity for failure: N+1 and static stability

If you run 3 nodes at 80% utilisation and lose one, the remaining two need to carry 120% each. They fall over, and you have turned a single failure into a total outage. The total work stays the same when a node dies; it is just shared among fewer survivors:

```formula
U_after = (N × U) / (N − k)
U_after = (3 × 80%) / (3 − 1)
U_after = 240% / 2 = 120%  ✗
U_after = (3 × 60%) / 2 = 90%  ✓
where
U_after: the utilisation of each surviving node after the failure, as a percentage of one node's capacity
N: the number of nodes before the failure, here 3
U: each node's utilisation before the failure, here 80% (or 60%)
k: the number of nodes that fail, here 1
%: per cent of one node's full capacity; above 100% the node is overloaded
✗ / ✓: overloaded / within capacity
In words: three nodes at 80% are doing 2.4 nodes' worth of work; split over two survivors that is 120% each, which they can't do. At 60% the survivors land on 90%, which they can.
```

Setting U_after to 100% and solving for U gives the general rule: the highest safe utilisation before a failure.

```formula
U_max = (N − k) / N
U_max = (3 − 1) / 3 = 2/3 ≈ 67%
U_max = (10 − 1) / 10 = 9/10 = 90%
where
U_max: the highest utilisation each node can run at and still let the survivors absorb the failed nodes' work without passing 100%
N: the number of nodes, here 3 (or 10)
k: the number of node failures the system must survive, here 1
≈: approximately equal to (rounded)
%: per cent of one node's capacity
In words: the fraction of nodes that survive is the fraction of capacity you can use. Three nodes surviving one loss can run at about 67%; ten nodes can run at 90%.
```

Treat U_max as a ceiling, not a target. At 60% the survivors land on 90%, and the queueing maths in the overload lesson shows that an illustrative M/M/1 model predicts mean response time ten times mean service time at 90%; this is not a universal latency multiplier. Real teams keep extra margin for traffic growth, uneven load balancing and the failure happening at peak. The rule also assumes load spreads evenly over the survivors.

More, smaller units make redundancy cheaper, as the second formula shows: 3 nodes surviving one loss can only run at 67%, but 10 nodes can run at 90%. The same logic is why three AZs are more efficient than two: two AZs that must each survive the other's loss can run at only 50% (N = 2, k = 1).

AWS calls the stronger version **static stability**: the system keeps working through a failure *without depending on new provisioning or impaired control-plane operations*, such as launching new instances or changing DNS. If you pre-provision capacity in each zone to survive losing another zone, you don't depend on a control plane that may itself be impaired during the event.

## Correlated failure and the "it can't all fail" fallacy

The probability maths of redundancy assumes independence. When two replicas fail independently, the chance both are down at once is the product of their individual chances of being down:

```formula
P_both = (1 − A)^2
P_both = (1 − 0.999)^2
P_both = 0.001 × 0.001 = 0.000001
P_both = 0.0001%
where
P_both: the probability that both replicas are down at the same moment
A: the availability of one replica, the fraction of time it is up, here 99.9% = 0.999
^2: squared, multiplied by itself once (one factor per replica)
%: per cent; 0.000001 = 0.0001%
In words: each replica is down 0.1% of the time; if they fail independently, both are down only one-thousandth of that, 0.0001% of the time.
```

That is only true if the failures really are independent. But real failures correlate:

- The same bad config or software release is applied to both.
- A load spike that kills one replica shifts its load to the other and kills that too (a **cascading failure**).
- Both depend on the same downstream service, DNS or certificate.

Correlation also hides in time. Disks bought in the same batch tend to fail at similar ages, and a RAID rebuild puts heavy load on the surviving disks exactly when you can least afford another failure.

Cascading failures are an important way redundant systems can go fully dark. The rest of this module covers the tools for stopping them: timeouts, retry discipline, circuit breakers, load shedding, and safe deployment.

## A checklist for any design

- List every component and dependency on the request path.
- For each, decide what crash, omission, latency and wrong-answer failures look like.
- Mark SPOFs, including config, DNS, certificates, control planes and humans.
- Decide the fault boundary (host, zone, region, cell) and the blast radius at each.
- Confirm survivors have headroom to absorb a failed peer's load.
- Prefer designs that are statically stable over ones that need a control plane to recover.

## Key takeaways

- Crash, omission, timing and Byzantine models describe different fault behaviors; gray failures can exhaust resources despite appearing alive.
- Timeout-based remote failure detection can be wrong; design for that ambiguity.
- SPOFs hide in config, DNS, certificates, control planes and people, not just in boxes on the diagram.
- Cells, shuffle sharding and fault-isolation zones shrink blast radius when failures do happen.
- Redundancy needs distinct failure exposure and enough headroom; keep utilisation below the fraction of nodes that survive the failures you plan for (about 67% for 3 nodes surviving one loss).
- Static stability means surviving failure without needing new provisioning or an impaired control plane.

## Further reading

- [Static stability using Availability Zones (AWS Builders' Library)](https://aws.amazon.com/builders-library/static-stability-using-availability-zones/)
- [Workload isolation using shuffle-sharding (AWS Builders' Library)](https://aws.amazon.com/builders-library/workload-isolation-using-shuffle-sharding/)
- [Addressing cascading failures (Google SRE book)](https://sre.google/sre-book/addressing-cascading-failures/)
- [Gray failure: the Achilles' heel of cloud-scale systems (Huang et al., HotOS 2017)](https://www.microsoft.com/en-us/research/wp-content/uploads/2017/06/paper-1.pdf)
- [Byzantine fault (Wikipedia)](https://en.wikipedia.org/wiki/Byzantine_fault)
- [Single point of failure (Wikipedia)](https://en.wikipedia.org/wiki/Single_point_of_failure)
- [AWS Well-Architected Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
