---
id: rel-wrong-answers-hidden-dependencies
title: Wrong answers and hidden dependencies
level: basic
minutes: 3
summary: Choose proportionate defences for wrong answers and identify single points of failure.
sourceLesson: rel-designing-for-failure
---

The previous unit covered silence and slowness. Here the component may answer incorrectly, or a shared dependency may disable every otherwise healthy replica. For the availability question, recall Fundamentals: independent hard dependency availabilities multiply, while independent redundant copies fail together only when all copies are down.

### Byzantine failures

The component returns *wrong* answers: corrupted data, a buggy release computing the wrong price, or a malicious node. Tolerating liars costs far more replicas than tolerating crashes. Classic partially synchronous Byzantine consensus protocols such as PBFT need:

```formula
R ≥ 3f + 1
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
- **Input validation** of inputs and invariants at service boundaries.
- **End-to-end data verification**, e.g. reconciling ledgers nightly.

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

## Key takeaways

- Classic PBFT needs four replicas to tolerate one Byzantine participant under its stated assumptions.
- Checksums, boundary validation and reconciliation address many accidental wrong-answer failures.
- Redundant app servers cannot mask a shared configuration, certificate, database or identity dependency.

## Further reading

- [Byzantine fault (Wikipedia)](https://en.wikipedia.org/wiki/Byzantine_fault)
- [Single point of failure (Wikipedia)](https://en.wikipedia.org/wiki/Single_point_of_failure)
- [AWS Well-Architected Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
- [Practical Byzantine fault tolerance (Castro and Liskov)](https://www.usenix.org/legacy/publications/library/proceedings/osdi99/full_papers/castro/castro_html/castro.html)
