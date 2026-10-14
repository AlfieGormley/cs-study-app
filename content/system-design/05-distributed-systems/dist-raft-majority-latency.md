---
id: dist-raft-majority-latency
title: Raft majority size and commit latency
level: advanced
minutes: 4
summary: Calculate failure tolerance and choose the follower acknowledgement that sets commit latency.
sourceLesson: dist-consensus-raft
---

Raft commits a current-term log entry after durable replication to a majority. That requirement determines both the failures the cluster tolerates and the network acknowledgements on its critical path.

### Cluster size

A majority is more than half the nodes, and the cluster keeps working as long as a majority is alive:

```formula
M = ⌊N / 2⌋ + 1
F = N − M = ⌊(N − 1) / 2⌋
M = ⌊5 / 2⌋ + 1 = 2 + 1 = 3
F = 5 − 3 = 2
where
N: the number of nodes in the cluster; here 5
M: the majority, the smallest number of nodes that is more than half of N
F: the number of nodes that can fail while a majority is still alive
⌊ ⌋: floor: round down to the nearest whole number, so ⌊2.5⌋ = 2
In words: a majority is half the cluster rounded down, plus one; the cluster survives losing everyone else.
```

Because M + M is always more than N, any two majorities share at least one node. That shared node is what carries committed entries from one leader to the next.

| Nodes | Majority | Tolerates |
|---|---|---|
| 3 | 2 | 1 failure |
| 4 | 3 | 1 failure |
| 5 | 3 | 2 failures |
| 7 | 4 | 3 failures |

Even sizes add cost without extra tolerance. Each write needs a majority; more replicas add work, but commit latency depends on placement and acknowledgement speeds, not node count alone. Three or five nodes are the usual production choices; balanced placement over three availability zones survives one zone loss when no zone holds more than the tolerated number of failures.

Commit latency is set by the **majority's** slowest member, not the cluster's. The leader counts itself, so in a five-node cluster it waits for the second-fastest follower acknowledgement (including its `fsync`). With a fast leader and two fast followers, even two slow followers can be bypassed; three slow followers force the leader to wait for at least one slow acknowledgement.

```formula
k = M − 1
T_commit ≈ RTT_k
where
M: the majority, the number of nodes that must store the entry, counting the leader
k: how many follower acknowledgements the leader needs (the leader counts itself, so one fewer than M)
RTT_k: the round-trip time to the k-th fastest follower, in milliseconds (ms)
T_commit: the time from the leader sending the entry to it being committed, ignoring disk writes, in ms
ms: millisecond, one thousandth of a second
≈: approximately equal to
In words: commit latency is the round trip to the slowest member of the fastest majority, not to the slowest node in the cluster.
```

Worked example: a five-node cluster needs a majority of 3, so its leader needs 2 follower acknowledgements. Its leader is in London and its followers are 1 ms, 15 ms, 15 ms and 75 ms away. Sorted, the second-fastest follower is 15 ms away, so commits take about 15 ms. The 75 ms follower never slows a commit while the others are healthy. If both 15 ms followers fail, the second-fastest becomes the 75 ms one and commits slow to about 75 ms.

## Key takeaways
- A Raft group makes progress with a reachable majority; adding an even-numbered node gives no additional crash tolerance.
- The leader counts itself, so a five-node group needs acknowledgements from two followers.
- Ignoring disks, commit latency follows the slowest member of the fastest available majority, not the slowest node.

## Further reading
- [The Raft consensus algorithm (visualisations, implementations)](https://raft.github.io/)
- [In Search of an Understandable Consensus Algorithm (Raft paper)](https://raft.github.io/raft.pdf)
