---
id: wm-fabric-queues-dctcp
title: Incast, microbursts and DCTCP
level: intermediate
minutes: 4
summary: Fine-grained queue and drop measurements can reveal bursts hidden by low average utilisation.
sourceLesson: wm-datacentre
---

This unit focuses on incast, microbursts and DCTCP. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Inside-the-fabric problems

- **Incast.** Concurrent replies can create a short burst exceeding a destination port’s service rate and available buffer. Loss may then trigger fast recovery, RACK/TLP or an RTO, depending on the trace and stack. Linux’s documented global default minimum RTO is 200 ms, but route/socket options and newer configurable controls can alter it; not every tail loss waits for that timeout.
- **Finite buffers.** Switch buffer capacity and allocation vary by model. Burst demand and shared-buffer contention matter even when average utilisation is low.
- **Fixes.** **DCTCP** estimates the fraction of marked bytes and adjusts its congestion window proportionally, aiming to keep queues short (the formula is below); some RoCE deployments combine priority flow control with congestion notification; RDMA does not universally require PFC, and PFC introduces head-of-line/deadlock risks that require engineering. Applications can stagger fan-out replies or limit outstanding requests.

DCTCP's reaction comes from RFC 8257. Switches mark packets with ECN once a queue passes a threshold; the sender keeps a running average of the marked fraction and cuts its window in proportion:

```formula
α ← (1 − g)α + gF
cwnd ← cwnd(1 − (α / 2))
where
α: alpha, the sender's running estimate of the fraction of its bytes that were ECN-marked, between 0 and 1
←: "is updated to": the new value replaces the old one, once per window of data
g: the estimation gain, a small weighting fraction between 0 and 1; RFC 8257 leaves the choice to the implementation and notes that 1/16 is used in some
F: the fraction of bytes marked in the most recent window of data
cwnd: the congestion window: how much unacknowledged data the sender may have in flight, in bytes or segments
In words: if few bytes were marked the window shrinks slightly; if marking persists until α approaches 1, it halves, like ordinary TCP.
```

For an estimate of 0.2, this reduction rule changes a 100-segment window to 90 segments. It is a proportional response, not a guarantee of low queues or unchanged throughput. The standalone calculation is:

```formula
W_new = W_old(1 − (α / 2))
W_new = 100(1 − (0.2 / 2)) = 90
where
W_new: the congestion window after this reduction, in segments
W_old: the congestion window before this reduction, 100 segments
α: alpha, the smoothed marked-byte fraction, 0.2 in this example
In words: this supplied marking estimate reduces the example window by ten segments rather than halving it.
```

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
- DCTCP reacts proportionally to a smoothed marked-byte fraction; low queueing is an aim, not an unconditional result.

## Further reading
- [Introducing data center fabric — Engineering at Meta](https://engineering.fb.com/2014/11/14/production-engineering/introducing-data-center-fabric-the-next-generation-facebook-data-center-network/)
- [RFC 8257: Data Center TCP](https://www.rfc-editor.org/rfc/rfc8257)
