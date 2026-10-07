---
id: dist-why-hard
title: Why distributed systems are hard
level: basic
minutes: 11
summary: Partial failure, unreliable networks and clocks, the eight fallacies, and why the Two Generals problem has no solution.
---

A distributed system is a set of computers that cooperate over a network and, ideally, look like one machine to the user. You build one because a single machine can't give you enough capacity, availability or geographic reach.

The price is that you inherit a class of problems that simply do not exist inside one process. Almost every technique in this module (quorums, consensus, fencing tokens, sagas, CRDTs) exists to tame one of the problems in this lesson.

## Partial failure

On a single computer, failure is mostly *total*: the process crashes, the kernel panics, the power goes. A program either runs or it doesn't, and that makes it easy to reason about.

In a distributed system, failure is **partial**. Some nodes work, some don't, and some are in an unknown state. Worse, failures are **non-deterministic**: the same request might succeed, fail, or hang.

Consider a client calling a remote service:

```
Client                  Server
  |---- request ------->|
  |                     |  (does work?)
  |       ...           |
  |   (no reply)        |
  |                     |
 timeout!
```

When the timeout fires, the client has no idea which of these happened:

1. The request was lost before reaching the server.
2. The server is down or paused (e.g. a long GC pause).
3. The server processed the request, but the reply was lost.
4. The server is just slow and will reply in 5 seconds.

All four look identical to the client. Cases 1 and 3 are the dangerous pair: in case 1 nothing happened, while in case 3 the side effect (charging a card, sending an email) **already happened**. This is why retries must be designed with idempotency in mind: an idempotency key lets the server recognise and discard a duplicate.

> [!warning] The core uncertainty
> A remote node can't tell "dead" from "slow" from "network broken". All it ever has is "I haven't heard back yet". Every failure detector is a guess.

## Living with timeouts

Since a timeout is the only failure signal you get, its value is a real design decision.

- **Too short**: a slow but healthy node is declared dead. You fail over, retry or rebalance for nothing, and the extra work can make the overload that caused the slowness worse.
- **Too long**: a genuinely dead node stalls requests (and users) for the whole timeout before anything happens.

A common starting point is to set request timeouts a little above the latency percentile you're willing to give up on (say the p99.9 of healthy calls), rather than picking a round number. Failure detectors used for cluster membership go further and *adapt* to observed latency; lesson 8 covers the phi accrual detector.

### Retries need care too

Retrying after a timeout is natural, but naive retries cause their own outages:

- **Use the same idempotency key on every attempt.** A fresh key per attempt makes each retry look like a new request, which defeats the point.
- **Back off exponentially, with jitter.** If thousands of clients retry on the same schedule, they hit the recovering server in synchronised waves.
- **Retry at one layer only.** If three layers each make up to 3 attempts, one user request can become 3 × 3 × 3 = 27 calls at the bottom layer, just when it is least able to cope.

```
web (3 tries)
 -> api (3 tries each)  = 9
   -> db (3 tries each) = 27
```

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
| Partially synchronous | Usually bounded, but bounds are sometimes violated |
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

This is exactly the situation CAP talks about: during a partition, each side either refuses some requests (choosing consistency) or accepts them and risks divergence (choosing availability). PACELC adds that even with no partition you trade latency against consistency.

## Unreliable clocks and process pauses

Every machine has its own quartz clock, and they drift (Google assumes up to 200 ppm, around 17 seconds a day if never corrected). NTP corrects them, but only to within a few milliseconds on a good LAN, and much worse over the internet. Clocks can even **jump backwards** when NTP steps them.

Processes can also pause without noticing:

- a stop-the-world garbage collection (seconds, occasionally minutes),
- a VM being live-migrated or its hypervisor stealing CPU,
- the OS swapping memory to disk,
- a laptop lid closing.

A paused thread resumes and carries on as if no time had passed. If it was holding a lease ("I'm the leader for 10 more seconds"), it may now act on a lease that expired long ago. Lesson 6 shows how fencing tokens defend against this.

## The eight fallacies of distributed computing

Peter Deutsch and colleagues at Sun Microsystems listed the false assumptions that newcomers make. Each one causes real outages.

| Fallacy | What goes wrong |
|---|---|
| The network is reliable | Lost requests, half-done operations |
| Latency is zero | Chatty APIs become slow over a WAN |
| Bandwidth is infinite | Large payloads saturate links |
| The network is secure | Unencrypted internal traffic is sniffed |
| Topology doesn't change | Hard-coded IPs break on failover |
| There is one administrator | Conflicting configs, firewalls |
| Transport cost is zero | Serialisation CPU, cross-AZ fees |
| The network is homogeneous | Mixed MTUs, protocols, versions |

> [!example] Latency is not zero
> A page that makes 50 sequential calls to a service in the same data centre (0.5 ms round trip) spends 25 ms on the network. Move that service to another region (80 ms round trip) and the same page takes 4 seconds. Nothing in the code changed.

## The Two Generals problem

This thought experiment proves that **no protocol over an unreliable channel can guarantee that two parties agree** to act together.

Two armies, A and B, camp on hills either side of a city. They win only if they attack at the same time. Their only means of communication is a messenger who must run through the valley, where they might be captured.

```
General A                General B
  |-- "attack at 9" ------>|
  |                        | got it, but
  |                        | does A know?
  |<----- "ack" -----------|
  | got ack, but does B    |
  | know I got it?         |
  |-- "ack of ack" ------->|
  |          ... forever   |
```

Suppose some protocol worked, and consider the *shortest* sequence of messages that results in both attacking. The last message in that sequence might be captured. Whoever sent it can't know whether it arrived, so the decision must not depend on it, meaning a shorter protocol also works. Repeat the argument and you reach zero messages, which obviously can't coordinate anything. Contradiction.

### What it means in practice

You can't get *certain* agreement over a lossy network, so real systems settle for something weaker:

- **Probabilistic confidence**: send many messengers; the chance all are lost shrinks quickly.
- **Idempotent retries**: keep retrying until acknowledged, and make repeats harmless.
- **Agreement among a majority**: consensus algorithms (lesson 5) don't need every node to know; a majority is enough, and they tolerate lost messages by retrying.

TCP's connection close runs into the same limitation: the final ACK can be lost, and the side that sent it can't know. That's one reason the `TIME_WAIT` state exists: it lingers so it can re-send the ACK if the peer re-sends its FIN.

> [!note] Two Generals vs Byzantine Generals
> Two Generals is about **unreliable messages** between honest parties. The Byzantine Generals problem is about **dishonest or arbitrarily faulty nodes**. Practical Byzantine fault tolerance (PBFT and its descendants) needs 3f + 1 nodes to tolerate f traitors; most data-centre systems assume nodes are honest and only tolerate crashes, needing 2f + 1.

## Fault models

When you read about an algorithm, check which faults it tolerates:

| Model | Node behaviour |
|---|---|
| Crash-stop | Fails by halting, never returns |
| Crash-recovery | Halts, may restart with its disk |
| Omission | Drops some messages |
| Byzantine | Anything, including lying |

Raft and Paxos assume crash-recovery with durable storage. Blockchains assume Byzantine. Choosing the model is a design decision: Byzantine tolerance is expensive and rarely needed inside one company's data centre.

The fine print matters. "Crash-recovery with durable storage" means a node that restarts still has everything it `fsync`ed. A node that comes back with an empty or rolled-back disk (a replaced VM, a disk cache that lied about flushing) has **amnesia**, and that falls outside the model: it can vote twice in the same term and break safety. Likewise, silent data corruption is closer to a Byzantine fault than a crash, which is why storage systems add checksums.

## Key takeaways
- Failure in distributed systems is partial and non-deterministic; a timeout tells you nothing about whether the work happened.
- Networks can drop, delay, duplicate and reorder messages; partitions split working nodes apart.
- Clocks drift and jump, and processes pause unexpectedly, so time-based reasoning is fragile.
- The eight fallacies are the assumptions that cause outages; latency and reliability are the most common.
- Timeouts are guesses: tune them from real latency, retry with the same idempotency key, back off with jitter and retry at one layer only.
- Two Generals proves certain agreement over a lossy channel is impossible; systems use retries, idempotency and majorities instead.
- Always ask which fault model an algorithm assumes: crash-stop, crash-recovery or Byzantine.

## Further reading
- [Fallacies of distributed computing (Wikipedia)](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing)
- [Two Generals' Problem (Wikipedia)](https://en.wikipedia.org/wiki/Two_Generals%27_Problem)
- [Byzantine fault (Wikipedia)](https://en.wikipedia.org/wiki/Byzantine_fault)
- [Timeouts, retries and backoff with jitter (AWS Builders' Library)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Making retries safe with idempotent APIs (AWS Builders' Library)](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
- [Jepsen analyses of real databases under partition](https://jepsen.io/analyses)
