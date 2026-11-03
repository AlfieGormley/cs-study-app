---
id: rel-fanout-gray-faults
title: Fan-out, timing faults and gray failure
level: basic
minutes: 5
summary: Recognise failure symptoms and why remote health checks can misclassify slow components.
sourceLesson: rel-designing-for-failure
---

This unit builds on fault models, leases and fencing in Distributed Systems. A fencing token is a monotonically increasing leadership epoch checked by the storage service: writes from an older epoch are rejected, even if the old leader resumes after a pause.

At scale, failure is not an exception; it is the normal background noise. Even a small per-device failure rate produces routine failures across a large fleet.

Fan-out makes rare slowness common. If one request makes many independent downstream calls, waiting for every result exposes the request to each call’s slow tail.

With 50 independent downstream calls, each slow on 1% of attempts, roughly four requests in ten encounter at least one slow call. Waiting for every result therefore exposes the user to much more tail latency than one call alone.

This assumes the calls are slow independently of each other. Real delays are often correlated (one overloaded host slows many calls at once), and the answer also depends on where you draw the line for "slow".

Reliability engineering starts by accepting this and asking three questions of every design:

1. *How* can each component fail?
2. If it fails, *how much* of the system goes with it?
3. What keeps working, and does anyone have to wake up?

The fundamentals module covered availability "nines" and how availability multiplies across hard dependencies in series. This lesson is about the shapes of failure behind those numbers and the structural tools for containing them.

## A taxonomy of failure modes

Distributed systems literature classifies faults by how badly a component can misbehave. These categories highlight different symptoms; they are not a universal strict hierarchy. A Byzantine model permits arbitrary behavior, including omission or timing faults.

| Mode | What happens | Example |
|---|---|---|
| Crash | Stops executing; detection may be uncertain | Kernel panic, OOM kill |
| Omission | Drops some messages | Full queue, lost packet |
| Timing / latency | Responds, but too late | GC pause, noisy neighbour |
| Byzantine | Responds wrongly | Bit flip, bug, attacker |

### Crash failures

The easiest to handle, because silence is unambiguous *if you can detect it*. Health checks, heartbeats and leases can suspect loss of responsiveness; a load balancer stops routing to the dead node and a container orchestrator replaces it.

The catch: in an asynchronous network you cannot distinguish "crashed" from "very slow". Remote timeout-based detectors can be wrong; local process/OS notifications can also provide failure evidence.

### Omission failures

The component is up but some requests or replies vanish. A saturated connection pool, a dropped UDP packet, a message broker that discards on overflow. Omissions look like timeouts to the caller, which is why they push people towards retries (next lesson).

### Latency failures: the dangerous middle

A node that is **slow but alive** is often worse than a dead one. It still passes shallow health checks, still receives traffic, and ties up the caller's threads and connections while it dawdles.

```
Healthy:  req ──▶ 20ms ──▶ ok
Crashed:  req ──▶ reset or timeout
Gray:     req ──▶ ........ 9s ..... ok
          (threads held the whole time)
```

Microsoft researchers named this kind of fault **gray failure** (Huang et al., HotOS 2017): the system's failure detector sees a healthy component while the applications using it see a broken one. They argue that subtle faults like this, rather than clean crashes, are behind many major cloud availability breakdowns. Typical examples are a degraded disk, a NIC dropping a few per cent of packets, or a JVM stuck in GC. The fix is a combination of tight timeouts, latency-aware load balancing, and health checks that test real work, not just "is the process listening".

> [!analogy] Real-world analogy: an open shop with an unusable till
> A shop can have its lights on and front door open while every payment takes minutes.
>
> **How it maps:** An open door resembles a shallow health check; a completed purchase resembles the useful operation whose latency matters.
>
> **Where it stops:** A service can fail differently for different callers. Measure real request paths rather than replacing one shallow check with another.

## Key takeaways

- Large fleets experience routine failures; fan-out increases exposure to independently slow calls.
- Crash, omission and timing faults present different symptoms; a shallow health check can miss gray failure.
- A timeout suspects a remote failure. Use fencing so a paused former leader cannot resume stale writes.

## Further reading

- [Gray failure: the Achilles' heel of cloud-scale systems (Huang et al., HotOS 2017)](https://www.microsoft.com/en-us/research/wp-content/uploads/2017/06/paper-1.pdf)
- [Addressing cascading failures (Google SRE book)](https://sre.google/sre-book/addressing-cascading-failures/)
- [AWS Well-Architected Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
