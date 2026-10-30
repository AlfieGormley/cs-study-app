---
id: wm-fabric-queues-dctcp
title: Incast, microbursts and DCTCP
level: intermediate
minutes: 4
summary: Fine-grained queue and drop measurements can reveal bursts hidden by low average utilisation.
sourceLesson: wm-datacentre
---

A data-centre link can look nearly idle on a five-minute graph and still drop packets. The culprit is usually bursts lasting microseconds to milliseconds, often caused by many servers answering one request at the same moment.

## Inside-the-fabric problems

- **Incast.** A request fans out to many servers, which all reply at nearly the same moment through the one switch port leading back to the requester. For a short time, arrivals exceed that port's sending rate and its available buffer. Loss may then trigger fast recovery, RACK/TLP or an RTO, depending on the trace and stack. Linux's documented global default minimum RTO is 200 ms, but route/socket options and newer configurable controls can alter it; not every tail loss waits for that timeout.
- **Finite buffers.** Switch buffer capacity and allocation vary by model. Burst demand and shared-buffer contention matter even when average utilisation is low. As a sense of scale, 200 replies of 20 KB (4 MB in total) take about 1.3 ms to leave a 25 Gbit/s port, so if they all arrive within much less than that, most of the 4 MB must wait in the switch.
- **Fixes.** Applications can stagger fan-out replies or limit outstanding requests. **DCTCP** keeps queues short by reacting early and proportionally (below). Some RoCE deployments combine priority flow control with congestion notification; RDMA does not universally require PFC, and PFC introduces head-of-line/deadlock risks that require engineering.

> [!analogy] Real-world analogy: A whole class handing in work through one door
> A teacher asks 200 pupils to hand in their homework, and all 200 rush to the single staffroom door at once. The doorway can only pass a few at a time, the corridor fills, and late arrivals are turned away and have to come back later. Spread over ten minutes, the same 200 hand-ins would have gone through without a queue.
>
> **How it maps:** The pupils are the replying servers, the door is the switch port towards the requester, and the corridor is its buffer. Being turned away is a dropped packet, and coming back later is a retransmission, possibly after a long timeout. Staggering the hand-ins is pacing or limiting outstanding requests.
>
> **Where it stops:** Packets cannot see the queue and wait politely; they are dropped the instant the buffer is full. The whole episode lasts about a millisecond, which is why minute-scale averages hide it.

## DCTCP: braking early and gently

Ordinary loss-based TCP waits for a drop and then roughly halves its window. **DCTCP** (RFC 8257) instead uses **ECN** marks: switches mark packets once a queue passes a low threshold, and the sender cuts its window in proportion to how much of its data was marked. A little marking gives a small cut; persistent marking approaches the usual halving.

```formula reference
α ← (1 − g)α + gF
cwnd ← cwnd(1 − (α / 2))
where
α: alpha, the sender's running estimate of the fraction of its bytes that were ECN-marked, between 0 and 1
←: "is updated to": the new value replaces the old one, once per window of data
g: the estimation gain, a small weighting fraction between 0 and 1; RFC 8257 leaves the choice to the implementation and notes that 1/16 is used in some
F: the fraction of bytes marked in the most recent window of data
cwnd: the congestion window: how much unacknowledged data the sender may have in flight, in bytes or segments
In words: the sender keeps a running average of how much of its data was marked; if few bytes were marked the window shrinks slightly, and only if marking persists does it approach halving like ordinary TCP.
```

For example, if the running estimate of marked bytes has settled at about a fifth, a 100-segment window shrinks to 90 segments rather than 50. Queues therefore stay short without throughput collapsing, which leaves buffer headroom for incast bursts. This is the aim, not a guarantee: it needs ECN-capable switches with suitable thresholds. RFC 8257 says DCTCP should only be deployed inside a data centre whose endpoints and switches are under one administrative domain. Because DCTCP and conventional TCP do not coexist well in the same network, it recommends segregating DCTCP traffic from conventional TCP traffic, for example into separately managed queues.

> [!tip] Reading a utilisation graph
> A link showing 30% average utilisation over five minutes can still drop packets: microbursts lasting a millisecond can overflow a shallow buffer and vanish in the average. Look at drop counters and queue depth, not just utilisation.

## Trade-offs at a glance

| Choice | Benefit | Cost |
|---|---|---|
| More spines | capacity, small failure blast | ports, optics |
| Lower oversub | headroom for bursts | money |
| L3 + ECMP | no blocked links | L2 needs overlay |
| Per-flow hash | avoids selector-induced reordering while mapping is stable | elephant collisions |

> [!note] Evidence limits
> Universal data-centre traffic percentages, switch-buffer sizes, workload oversubscription ratios and fixed recovery times are omitted because no applicable deployment measurements were established. The capacity, hash and probability examples are models, not hardware benchmarks. This review did not measure fabric convergence, switch queues or an RDMA deployment.

## Key takeaways
- Fine-grained queue and drop measurements can reveal bursts hidden by low average utilisation.
- DCTCP reacts early and proportionally to ECN marks; low queueing is an aim, not an unconditional result.

## Further reading
- [Introducing data center fabric — Engineering at Meta](https://engineering.fb.com/2014/11/14/production-engineering/introducing-data-center-fabric-the-next-generation-facebook-data-center-network/)
- [RFC 8257: Data Center TCP](https://www.rfc-editor.org/rfc/rfc8257)
