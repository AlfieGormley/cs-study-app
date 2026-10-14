---
id: dist-consensus-flp
title: Consensus, replicated state and FLP
level: advanced
minutes: 3
summary: Separate consensus safety from the termination limit of a fully asynchronous network.
sourceLesson: dist-consensus-raft
---

**Consensus** is getting several nodes to agree on a value, even when some of them crash and messages are delayed. It sounds narrow, but it's the foundation for leader election, distributed locks, configuration stores, atomic commit and linearizable databases. Once you can agree on one value, you can agree on a sequence of values: a **replicated log**.

## The problem

A consensus algorithm must satisfy:

| Property | Meaning |
|---|---|
| Agreement | No two nodes decide differently |
| Validity | The decided value was proposed |
| Integrity | Each node decides at most once |
| Termination | Every non-faulty node decides |

The first three are **safety** (nothing bad happens). Termination is **liveness** (something good eventually happens).

### State machine replication

If every replica starts in the same state and applies the same deterministic commands in the same order, they end in the same state. Consensus decides the order. That's how etcd, Consul, ZooKeeper, CockroachDB ranges, Kafka's KRaft controller and TiKV all work.

```
client -> leader
          |  log: [set x=1][set y=2]
          v
   +------+------+
   v      v      v
  log    log    log   same order
   |      |      |
  SM     SM     SM    same state
```

## FLP impossibility (intuition)

Fischer, Lynch and Paterson (1985) proved that in a **fully asynchronous** system, **no deterministic algorithm** can solve consensus, guaranteeing agreement, validity *and* termination, if even **one** process may crash. That holds even when the network is perfectly reliable: every message is eventually delivered, just with no bound on how long it takes.

Put another way: any deterministic algorithm that is always safe has at least one possible execution in which it never decides.

The intuition: a crashed process and a very slow one are indistinguishable. At any point, the algorithm is either waiting for a node (which might be dead, so it waits forever) or proceeding without it (and the slow node might have been the decider). The proof shows there is always an undecided (**bivalent**) state, one from which either outcome is still possible, and that an adversarial scheduler can always delay exactly the message that would tip it, moving to another undecided state, forever.

FLP doesn't say consensus is useless. Real algorithms escape it by:

- **Using timeouts** (partial synchrony): always safe, live when the network behaves. Raft and Paxos do this.
- **Randomisation**: terminates with probability 1 (Ben-Or).

So in a bad network, Raft might fail to elect a leader for a while, but it will never elect two in one term. FLP is about termination, not safety: it doesn't say any algorithm must make mistakes.

## Key takeaways
- Consensus needs agreement, validity and integrity as safety properties, plus termination as liveness.
- A replicated log gives deterministic replicas the same commands in the same order.
- FLP rules out guaranteed deterministic termination with a possible crash under full asynchrony; practical systems keep safety and need favourable timing for progress.

## Further reading
- [In Search of an Understandable Consensus Algorithm (Raft paper)](https://raft.github.io/raft.pdf)
- [Impossibility of Distributed Consensus with One Faulty Process (FLP)](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf)
- [Ben-Or's randomised consensus protocol](https://arxiv.org/pdf/1702.01765)
- [A Brief Tour of FLP Impossibility (Paper Trail)](https://www.the-paper-trail.org/post/2008-08-13-a-brief-tour-of-flp-impossibility/)
