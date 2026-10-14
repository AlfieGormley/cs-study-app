---
id: dist-paxos-coordination-services
title: Paxos and packaged coordination services
level: advanced
minutes: 3
summary: Follow Paxos value preservation and compare the coordination primitives offered by etcd and ZooKeeper.
sourceLesson: dist-consensus-raft
---

Raft is one way to package consensus into a replicated log. Paxos preserves chosen values through numbered proposals, and coordination services expose these protocols through safer application primitives.

## Paxos at a high level

Lamport's Paxos (1989, published 1998) predates Raft and is the basis of Chubby, Spanner and many others. Single-decree Paxos agrees on one value in two phases:

```
Proposer        Acceptors (majority)
 |--Prepare(n)-------->|
 |<--Promise(n, prev)--|  won't accept < n
 |--Accept(n, v)------>|
 |<--Accepted(n)-------|
 chosen once a majority accept
```

The key rule: if any acceptor reports a previously accepted value, the proposer must propose **that** value (the highest-numbered one) rather than its own. That's how a chosen value survives.

**Multi-Paxos** elects a stable leader that skips phase 1 for subsequent slots, which looks a lot like Raft. The differences are mostly in what's specified: Raft prescribes how logs, leaders and membership work; Paxos leaves much of that to implementers, which is why it's known as hard to get right.

| | Raft | Multi-Paxos |
|---|---|---|
| Leader | Required, strong | Optimisation |
| Log gaps | Not allowed | Allowed |
| Spec | Complete system | Core protocol |

## etcd and ZooKeeper

**etcd** is a Raft-based key-value store, used as Kubernetes' brain. It offers linearizable reads and writes, watches, leases (keys that expire unless refreshed) and transactions (compare-and-swap). Every key has a **revision** number that only increases, useful as a fencing token.

**ZooKeeper** uses **Zab**, a Paxos-like atomic broadcast protocol. It offers a hierarchical namespace of znodes, **ephemeral** znodes (deleted when the client session dies) and **sequential** znodes (with an auto-incrementing suffix). Writes are linearizable; reads can be stale. A preceding `sync` improves freshness but does not strictly guarantee it under every failure, because `sync` is not a quorum operation. Classic recipes: leader election (lowest sequential ephemeral node wins), locks and group membership. In the election recipe, each waiting worker watches its next-lower predecessor and rechecks the ordering when that znode disappears. Watching a predecessor avoids waking every waiting worker on each change. Kafka used it for metadata until replacing it with its own Raft-based KRaft; Kafka 4.0 (2025) removed ZooKeeper support entirely.

> [!tip] Don't build it yourself
> Consensus is notoriously easy to get subtly wrong. Use etcd, ZooKeeper or Consul for coordination, or a library like etcd's `raft` package, rather than writing your own.

## Key takeaways
- Paxos prepare discovers previously accepted proposals; the proposer preserves the highest-numbered reported value.
- A stable Multi-Paxos leader can reuse its preparation for later slots.
- etcd packages Raft with revisions and leases; ZooKeeper packages Zab with ephemeral and sequential znodes, while reads can be stale.

## Further reading
- [Paxos Made Simple (Lamport)](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf)
- [etcd API guarantees](https://etcd.io/docs/v3.6/learning/api_guarantees/)
- [ZooKeeper leader election and lock recipes](https://zookeeper.apache.org/doc/current/recipes.html)
- [ZooKeeper overview](https://zookeeper.apache.org/doc/current/zookeeperOver.html)
- [etcd's Raft library (Pre-Vote, CheckQuorum, ReadIndex)](https://github.com/etcd-io/raft)
