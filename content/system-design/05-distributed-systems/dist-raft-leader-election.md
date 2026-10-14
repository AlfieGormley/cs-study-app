---
id: dist-raft-leader-election
title: Raft terms and leader election
level: advanced
minutes: 3
summary: Trace a Raft election and apply the last-log-term rule before comparing log length.
sourceLesson: dist-consensus-raft
---

Raft implements the consensus contract by electing a leader and replicating its log. This unit focuses on who can become leader; the next follows the log entries that leader proposes.

## Raft

Raft (Ongaro and Ousterhout, 2014) was designed to be understandable. It decomposes consensus into leader election, log replication and safety.

### Roles and terms

Each node is a **replication follower**, **Raft candidate** or **Raft leader**. Time is divided into **terms**, numbered 1, 2, 3, ... Each term has at most one leader. Terms act as a logical clock: every message carries the sender's term.

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
5. If it hears from a leader whose term is at least its own, it steps down. If the timeout passes with no winner (split vote), it starts a new term.

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

## Key takeaways
- Nodes move between follower, candidate and leader; a higher term makes stale leaders step down.
- Randomised election timeouts reduce split votes, and each node grants at most one vote per term.
- A candidate’s last log term decides freshness first; only equal terms are compared by log length.

## Further reading
- [The Raft consensus algorithm (visualisations, implementations)](https://raft.github.io/)
- [In Search of an Understandable Consensus Algorithm (Raft paper)](https://raft.github.io/raft.pdf)
- [The Secret Lives of Data: Raft animation](https://thesecretlivesofdata.com/raft/)
