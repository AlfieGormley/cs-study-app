---
id: dist-network-timing-pauses
title: Network timing, partitions and process pauses
level: basic
minutes: 3
summary: Separate safety from progress when networks delay messages and healthy processes pause.
sourceLesson: dist-why-hard
---

Timeouts reveal silence, not its cause. To reason about failover, distinguish network timing assumptions from the behaviour of the nodes themselves.

## The network is asynchronous

Most real networks (Ethernet, IP, the internet) are **asynchronous packet networks**. They promise nothing about delivery time. A packet can be:

- dropped (a switch buffer overflows),
- delayed arbitrarily (queueing in switches, TCP retransmits, a busy receiver),
- duplicated (a retransmit after an ack was lost),
- reordered (different paths).

TCP hides drops, duplicates and reordering from you, but it cannot hide *delay*, and it cannot tell you whether the far side processed your data once the connection breaks.

Distributed systems theory names three timing models:

| Model | Assumption |
|---|---|
| Synchronous | Known upper bounds on delay and clock drift |
| Partially synchronous | Bounds unknown, or hold after an unknown stabilisation time |
| Asynchronous | No bounds at all |

Real systems are best described as **partially synchronous**: they behave well most of the time, then occasionally a link saturates or a VM is paused for 30 seconds. Algorithms like Raft are designed so that *safety* never depends on timing, and only *liveness* (making progress) needs the network to calm down.

### Network partitions

A **partition** is when the network splits nodes into groups that cannot talk to each other, even though every node is still running. They happen far more than people expect: misconfigured switches, a cut fibre, a firewall rule, a NIC dropping only inbound packets.

```
 Region A            Region B
+--------+   XXXX   +--------+
| n1  n2 |---XXXX---| n3  n4 |
+--------+   XXXX   +--------+
 both sides think the other is dead
```

This is exactly the situation the CAP theorem talks about: during a partition, each side either refuses some requests (choosing consistency) or accepts them and risks divergence (choosing availability). PACELC adds that even with no partition you trade latency against consistency.

## Unreliable clocks and process pauses

Every machine has its own quartz clock, and they drift (Google assumes up to 200 ppm, around 17 seconds a day if never corrected). NTP corrects them, but only to within a few milliseconds on a good LAN, and much worse over the internet. Clocks can even **jump backwards** when NTP steps them.

Processes can also pause without noticing:

- a stop-the-world garbage collection (seconds, occasionally minutes),
- a VM being live-migrated or its hypervisor stealing CPU,
- the OS swapping memory to disk,
- a laptop lid closing.

A paused thread resumes at its next instruction; a deadline check performed before the pause may now be obsolete. If it was holding a lease ("I'm the leader for 10 more seconds"), it may now act on a lease that expired long ago. The resource-fencing unit later in this module shows how fencing tokens defend against this.

## Key takeaways
- Asynchronous packet networks can lose, delay, duplicate or reorder messages; TCP cannot remove uncertainty about remote work.
- A partition separates working nodes, and one-way failures can give each side a different view.
- Clock jumps and process pauses make lease holders stale; timing assumptions control progress, not Raft log safety.

## Further reading
- [Timeouts, retries and backoff with jitter (AWS Builders' Library)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Jepsen analyses of real databases under partition](https://jepsen.io/analyses)
