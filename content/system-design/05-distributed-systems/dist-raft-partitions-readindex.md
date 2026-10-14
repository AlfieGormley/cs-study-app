---
id: dist-raft-partitions-readindex
title: Raft partitions, reads and rejoining nodes
level: advanced
minutes: 3
summary: Handle stale minority leaders, confirm read authority and prevent disruptive term inflation.
sourceLesson: dist-consensus-raft
---

A network partition can leave an old leader running while a majority elects a new one. The write quorum preserves log safety, but read authority and recovery behaviour still need explicit protocols.

### Partitions in Raft

```
 n1(L,t3) n2 | n3 n4 n5
  minority   |  majority
```

The old leader n1 can still accept client writes but can't commit them (no majority). n3–n5 time out, elect a new leader in term 4 and continue. When the partition heals, n1 sees term 4, steps down, and any conflicting uncommitted suffix is overwritten. An entry that matches the new leader's log may remain.

Reads need care too. A leader that was partitioned may not know it's been deposed, so serving reads from local state can return stale data. Raft offers **ReadIndex** (confirm leadership with a heartbeat round before reading) or **leader leases** (rely on bounded clock drift). etcd uses ReadIndex for linearizable reads.

### Disruptive rejoiners: Pre-Vote and CheckQuorum

Partitions cause a second, nastier problem. An isolated follower keeps timing out and incrementing its term: 5, 6, 7 ... 40. When it reconnects, its high term forces the healthy leader to step down, and the cluster holds a needless election (which the rejoiner can't even win, since its log is behind).

Two common extensions fix this, and etcd implements both:

- **Pre-Vote**: before incrementing its term, a candidate asks "would you vote for me?". Peers say no if the candidate's log is behind or (in etcd, with CheckQuorum on) if they've heard from a live leader recently. Only a candidate that could actually win goes on to increment its term, so an isolated node never inflates it.
- **CheckQuorum**: a leader that hasn't heard from a majority within an election timeout steps down by itself, so a stale minority leader doesn't keep accepting writes indefinitely.

### Membership changes and snapshots

Adding or removing nodes is done one at a time (or via **joint consensus**) so that old and new majorities can't both decide independently. Logs are compacted into **snapshots**; a far-behind follower receives `InstallSnapshot` instead of every entry.

A safe read protocol also needs a committed entry from the leader’s current term and a state machine applied through the required commit index. A quorum heartbeat then confirms the leader has not been superseded; the current-term commit establishes the committed prefix for that term.

## Key takeaways
- A minority leader can accept proposals but cannot commit them; it steps down after learning the majority’s higher term.
- Local leader state alone does not prove authority for a linearizable read; use a safe ReadIndex or bounded lease protocol.
- Pre-Vote reduces rejoin disruption, CheckQuorum makes isolated leaders step down, and membership changes preserve quorum overlap.

## Further reading
- [The Raft consensus algorithm (visualisations, implementations)](https://raft.github.io/)
- [In Search of an Understandable Consensus Algorithm (Raft paper)](https://raft.github.io/raft.pdf)
- [etcd API guarantees](https://etcd.io/docs/v3.6/learning/api_guarantees/)
- [etcd's Raft library (Pre-Vote, CheckQuorum, ReadIndex)](https://github.com/etcd-io/raft)
