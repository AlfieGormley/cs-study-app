---
id: dist-consensus-raft
title: Consensus, Raft and Paxos
level: advanced
minutes: 18
summary: What consensus is, why FLP says it can't always terminate, how Raft elects leaders and replicates logs safely, Paxos in outline, and etcd and ZooKeeper.
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

## Raft

Raft (Ongaro and Ousterhout, 2014) was designed to be understandable. It decomposes consensus into leader election, log replication and safety.

### Roles and terms

Each node is a **follower**, **candidate** or **leader**. Time is divided into **terms**, numbered 1, 2, 3, ... Each term has at most one leader. Terms act as a logical clock: every message carries the sender's term.

- If a node sees a higher term, it adopts it and becomes a follower.
- If it receives a message with a lower term, it rejects it.

```
term:  | 1      | 2  | 3          |
       | leader |elec| leader     |
       |  n1    |fail|  n3        |
                 (split vote)
```

### Leader election

1. Followers expect heartbeats (empty `AppendEntries`) from the leader.
2. If none arrive within the **election timeout** (randomised, e.g. 150–300 ms), the follower increments its term, becomes a candidate, votes for itself and sends `RequestVote` to all.
3. Each node grants **at most one vote per term**, first come first served, and only if the candidate's log is **at least as up to date** as its own.
4. A candidate with votes from a **majority** becomes leader and sends heartbeats immediately.
5. If it hears from a leader with term ≥ its own, it steps down. If the timeout passes with no winner (split vote), it starts a new term.

```
n1(F)   n2(F)   n3(F)
  |  timeout!
n1(C) term=5
  |--RequestVote-->n2
  |--RequestVote---------->n3
  |<--granted------n2
n1 has 2/3 -> LEADER term 5
  |--AppendEntries-->n2, n3
```

Randomised timeouts make split votes rare: usually one node times out first and wins before others start.

"Up to date" means: compare the last entry's term; higher wins. If equal, the longer log wins. This rule is what guarantees a new leader has every committed entry.

### Log replication

Each log entry has an **index**, a **term** and a **command**.

1. Client sends a command to the leader.
2. Leader appends it to its log and sends `AppendEntries` to followers, including the index and term of the **preceding** entry.
3. A follower accepts only if its log has an entry at that preceding index with the same term (the **consistency check**). Otherwise it rejects, and the leader retries with an earlier index until they match, then overwrites the follower's conflicting suffix.
4. Once an entry **from the leader's current term** is stored on a **majority** (counting the leader itself), the leader marks it **committed**, along with every entry before it, applies it to its state machine and replies to the client. (Why "current term" matters is the subtle rule below.)
5. Followers learn the commit index from later `AppendEntries` and apply it.

```
idx:    1  2  3  4  5
leader [1][1][2][3][3]
f1     [1][1][2][3][3]  match
f2     [1][1][2]        behind
f3     [1][1][2][2]     conflict
                ^ idx 4 overwritten
```

**Log Matching Property**: if two logs have an entry with the same index and term, they're identical up to that index. The consistency check enforces it by induction.

### Safety

The crucial guarantee is **Leader Completeness**: once an entry is committed, it's present in the logs of all future leaders.

Why: a committed entry is on a majority. To win, a candidate needs votes from a majority. Two majorities always overlap, so at least one voter has the entry, and it refuses to vote for a candidate whose log is less up to date.

> [!warning] The subtle rule
> A leader only counts replicas to commit entries **from its own term**. Entries from earlier terms become committed indirectly when a current-term entry after them commits. Figure 8 in the Raft paper shows an old-term entry replicated to a majority that is still overwritten. That's why new leaders append a no-op entry at the start of their term: committing it also commits everything before it.

Here is the Figure 8 scenario, step by step, with five nodes:

```
term 2: S1 leader, writes X at idx 2
        reaches S1, S2 only; S1 dies
term 3: S5 elected (S3, S4, S5)
        writes Y at idx 2, on S5 only
term 4: S1 back, elected; copies X
        to S3. X now on S1 S2 S3
```

X (term 2) is now on a majority. If S1 treated that as committed and then crashed, S5 could win term 5: its last entry has term 3, which beats the term-2 entries on S2, S3 and S4, so they vote for it. S5 would then overwrite X with Y on every node, "un-committing" X. Raft forbids this: S1 may only commit X once an entry from term 4 is also on a majority, and then S5 can no longer win, because a majority holds a term-4 entry that beats its log.

### Cluster size

| Nodes | Majority | Tolerates |
|---|---|---|
| 3 | 2 | 1 failure |
| 4 | 3 | 1 failure |
| 5 | 3 | 2 failures |
| 7 | 4 | 3 failures |

Even sizes add cost without extra tolerance. Each write needs a majority; more replicas add work, but commit latency depends on placement and acknowledgement speeds, not node count alone. Three or five nodes are the usual production choices; spreading them over three availability zones survives losing a zone.

Commit latency is set by the **majority's** slowest member, not the cluster's. The leader counts itself, so in a five-node cluster it waits for the second-fastest follower acknowledgement (including its `fsync`). With a fast leader and two fast followers, even two slow followers can be bypassed; three slow followers force the leader to wait for at least one slow acknowledgement.

### Partitions in Raft

```
 n1(L,t3) n2 | n3 n4 n5
  minority   |  majority
```

The old leader n1 can still accept client writes but can't commit them (no majority). n3–n5 time out, elect a new leader in term 4 and continue. When the partition heals, n1 sees term 4, steps down, and its uncommitted entries are overwritten.

Reads need care too. A leader that was partitioned may not know it's been deposed, so serving reads from local state can return stale data. Raft offers **ReadIndex** (confirm leadership with a heartbeat round before reading) or **leader leases** (rely on bounded clock drift). etcd uses ReadIndex for linearizable reads.

### Disruptive rejoiners: Pre-Vote and CheckQuorum

Partitions cause a second, nastier problem. An isolated follower keeps timing out and incrementing its term: 5, 6, 7 ... 40. When it reconnects, its high term forces the healthy leader to step down, and the cluster holds a needless election (which the rejoiner can't even win, since its log is behind).

Two common extensions fix this, and etcd implements both:

- **Pre-Vote**: before incrementing its term, a candidate asks "would you vote for me?". Peers say no if the candidate's log is behind or (in etcd, with CheckQuorum on) if they've heard from a live leader recently. Only a candidate that could actually win goes on to increment its term, so an isolated node never inflates it.
- **CheckQuorum**: a leader that hasn't heard from a majority within an election timeout steps down by itself, so a stale minority leader doesn't keep accepting writes indefinitely.

### Membership changes and snapshots

Adding or removing nodes is done one at a time (or via **joint consensus**) so that old and new majorities can't both decide independently. Logs are compacted into **snapshots**; a far-behind follower receives `InstallSnapshot` instead of every entry.

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

**ZooKeeper** uses **Zab**, a Paxos-like atomic broadcast protocol. It offers a hierarchical namespace of znodes, **ephemeral** znodes (deleted when the client session dies) and **sequential** znodes (with an auto-incrementing suffix). Writes are linearizable; reads can be stale. A preceding `sync` improves freshness but does not strictly guarantee it under every failure, because `sync` is not a quorum operation. Classic recipes: leader election (lowest sequential ephemeral node wins), locks and group membership. Kafka used it for metadata until replacing it with its own Raft-based KRaft; Kafka 4.0 (2025) removed ZooKeeper support entirely.

> [!tip] Don't build it yourself
> Consensus is notoriously easy to get subtly wrong. Use etcd, ZooKeeper or Consul for coordination, or a library like etcd's `raft` package, rather than writing your own.

## Key takeaways
- Consensus means agreement, validity, integrity and termination; replicated logs turn it into state machine replication.
- FLP: in a fully asynchronous system, no deterministic algorithm guarantees termination with one crash. Practical algorithms stay safe always and use timeouts for liveness.
- Raft: terms, randomised election timeouts, one vote per term, and a vote only for candidates with up-to-date logs.
- Entries commit once on a majority; the consistency check keeps logs matching; overlapping majorities make committed entries survive leader changes.
- A leader commits only entries from its own term by counting replicas; earlier entries commit with them (Figure 8).
- FLP rules out guaranteed termination, not safety: Raft is always safe and live when the network behaves.
- A minority partition can't commit; stale leaders step down on seeing a higher term. Linearizable reads need ReadIndex or leases. Pre-Vote stops rejoining nodes forcing needless elections.
- Paxos uses prepare/accept with proposal numbers; Multi-Paxos with a stable leader resembles Raft. etcd (Raft) and ZooKeeper (Zab) package consensus for applications.

## Further reading
- [The Raft consensus algorithm (visualisations, implementations)](https://raft.github.io/)
- [In Search of an Understandable Consensus Algorithm (Raft paper)](https://raft.github.io/raft.pdf)
- [The Secret Lives of Data: Raft animation](https://thesecretlivesofdata.com/raft/)
- [Paxos Made Simple (Lamport)](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf)
- [Impossibility of Distributed Consensus with One Faulty Process (FLP)](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf)
- [A Brief Tour of FLP Impossibility (Paper Trail)](https://www.the-paper-trail.org/post/2008-08-13-a-brief-tour-of-flp-impossibility/)
- [etcd API guarantees](https://etcd.io/docs/v3.6/learning/api_guarantees/)
- [ZooKeeper overview](https://zookeeper.apache.org/doc/current/zookeeperOver.html)
- [etcd's Raft library (Pre-Vote, CheckQuorum, ReadIndex)](https://github.com/etcd-io/raft)
