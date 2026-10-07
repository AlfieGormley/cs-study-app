---
id: fund-availability
title: Availability, reliability and the maths of nines
level: intermediate
minutes: 13
summary: What "four nines" really allows, how to calculate availability for components in series and in parallel, and how MTBF and MTTR drive it.
---

"Is the system up?" sounds like a yes/no question. In practice, availability is a number you design for, measure and trade against cost. This lesson gives you the vocabulary and the maths.

## Availability vs reliability vs durability

These words are often used interchangeably. They shouldn't be.

- **Availability**: the fraction of time (or of requests) the system is able to serve correctly. "99.9% of minutes this month the API returned successful responses."
- **Reliability**: the probability the system works correctly *without failure* over a period. A system that fails for 100 ms every minute is 99.8% available but terrible for reliability: almost any long-running job or long-lived connection will hit a failure.
- **Durability**: the probability that stored data is *not lost*. Amazon S3 is designed for 99.999999999% (eleven nines) durability but offers a much lower availability SLA. Data can be safe yet temporarily unreachable.

> [!note] Time-based vs request-based
> Time-based availability = uptime / total time. Request-based = successful requests / total requests. Request-based is usually more meaningful for large services (Google SRE favours it), because a 5-minute outage at 3 a.m. affects far fewer users than one at peak.

## The nines

Availability is usually quoted in "nines". Here's the equivalent downtime, using a 365.25-day year and an average month (year/12):

| Availability | Downtime/year | Downtime/month |
|---|---|---|
| 99% (two nines) | 3.65 days | 7.3 hours |
| 99.9% | 8.77 hours | 43.8 min |
| 99.95% | 4.38 hours | 21.9 min |
| 99.99% | 52.6 min | 4.4 min |
| 99.999% | 5.26 min | 26 s |

The formula is simple:

```
downtime = (1 - A) x period

99.99% per year:
0.0001 x 525,960 min = 52.6 min
```

Each extra nine cuts allowed downtime by 10x. The cost of achieving it depends on the architecture and failure modes; there is no universal cost multiplier. At 99.999%, you have 26 seconds a month. Manual detection and recovery can easily consume that budget, so automated recovery is usually essential.

> [!tip] Think in error budgets
> If your SLO is 99.9%, you have a 0.1% **error budget**: about 43 minutes a month. Spend it on deploys, experiments and incidents. When it's gone, slow down releases. This turns availability into an engineering trade-off rather than a moral absolute.

## Components in series

If a request needs **every** component to work, the components are in **series**. Assuming independent failures, multiply their availabilities:

```
A_total = A1 x A2 x ... x An
```

```
client -> [LB] -> [App] -> [DB]
         99.99%  99.9%   99.95%
```

```
A = 0.9999 x 0.999 x 0.9995
  = 0.99840
  ≈ 99.84%
```

The chain is **less** available than its weakest link. Every synchronous dependency you add lowers the ceiling. With independent failures, a service requiring 10 dependencies at 99.9% each has modelled availability 0.999^10 ≈ 99.0%, i.e. about 3.65 days of downtime a year.

This is the mathematical reason to:

- Remove dependencies from the critical path (do work asynchronously).
- Degrade gracefully: show the page without recommendations rather than failing it.
- Be suspicious of deep synchronous microservice call chains.

## Components in parallel

If the system works as long as **at least one** of several redundant components works, they're in **parallel**. The system fails only if *all* fail:

```
A_total = 1 - (1-A1) x (1-A2) x ... x (1-An)
```

```
            +--> [App 99%] --+
client ->LB-|                |-> ok
            +--> [App 99%] --+
```

```
A = 1 - (0.01 x 0.01)
  = 1 - 0.0001
  = 99.99%
```

Two 99% servers give 99.99%; three give 99.9999%. Redundancy is enormously powerful, which is why replication across availability zones is standard practice.

> [!warning] Redundancy needs spare capacity
> The parallel formula assumes **one survivor can carry the whole load**. If peak traffic needs both servers, losing either one at peak overloads the other, and the pair behaves like two components in series. Plan for **N+1** (or N+2): enough servers that the system still meets its load with one, or one zone, gone.

When *k* of *n* identical servers are needed, the system is up while at least *k* are up. For three 99% servers where any two can carry peak load:

```
P(all 3 up)   = 0.99^3        = 0.970299
P(exactly 2)  = 3 x 0.99^2 x 0.01
              = 0.029403
A             = 0.999702  (≈ 99.97%)
```

That's a big step down from the 99.9999% you'd get if any *one* could cope, and a big step up from the 97.03% of needing all three.

### Combining them

Real systems mix both. Compute parallel groups first, then multiply the groups in series:

```
LB pair:  1 - 0.001^2   = 0.999999
App x3:   1 - 0.01^3    = 0.999999
DB pair:  1 - 0.005^2   = 0.999975
Series:   0.999999 x 0.999999 x 0.999975
        ≈ 0.999973  (≈ 99.997%)
```

## The big caveat: independence

The formulas above assume failures are **independent**. In reality, they often aren't:

- Two servers in the same rack share a power supply and switch.
- Replicas running the same software share the same bugs (a bad deploy or a leap-second bug takes them all out at once).
- A bad config push hits every region.
- Failover itself can fail, or take minutes. The parallel formula assumes switching is instant; a 5-minute failover that happens four times a year is 20 minutes of downtime the formula never shows.

Two 99% servers on the same host don't give you 99.99%. This is why cloud providers offer **availability zones** (separate power, cooling and networking) and why multi-region designs exist. It's also why staged rollouts matter: they stop a single bad change from becoming a correlated failure.

> [!warning] Redundancy you haven't tested is a hope, not a design
> A standby database that has never been failed over to is likely to surprise you. Practise failovers regularly (game days, chaos engineering).

## MTBF and MTTR

Two quantities define steady-state availability:

- **MTBF** (mean time between failures): how long, on average, the system runs before failing.
- **MTTR** (mean time to repair/recovery): how long, on average, it takes to restore service.

```
A = MTBF / (MTBF + MTTR)
```

Example: a server fails on average every 1,000 hours and takes 1 hour to fix.

```
A = 1000 / (1000 + 1) = 99.9%
```

There are two levers:

1. **Increase MTBF**: better hardware, fewer risky changes, more testing.
2. **Decrease MTTR**: faster detection, automated failover, quick rollbacks, good runbooks.

Lowering MTTR is often cheaper and more effective. Cutting MTTR from 60 minutes to 6 gives the same availability gain as making failures 10x rarer. Recovery time itself breaks down into:

```
MTTR = time to detect
     + time to diagnose
     + time to fix/fail over
     + time to verify
```

Each piece suggests an investment: alerting on symptoms (detect), good dashboards and tracing (diagnose), automated failover and one-click rollback (fix).

Related terms you'll see: **MTTF** (mean time *to* failure, for non-repairable parts) and **MTTD** (mean time to detect).

## SLIs, SLOs and SLAs (briefly)

- **SLI** (indicator): the measurement, e.g. proportion of requests returning non-5xx in under 300 ms.
- **SLO** (objective): the target for that SLI, e.g. 99.9% over 30 days.
- **SLA** (agreement): a contract with consequences, e.g. service credits. AWS's EC2 Region-Level SLA specifies 99.99% under its stated multi-AZ deployment and measurement conditions; an individual instance has a separate commitment.

SLAs are normally looser than internal SLOs, so you're warned before you owe customers money. The reliability and observability module goes deeper.

## Key takeaways
- Availability is uptime (or successful requests) as a fraction; reliability is failure-free operation; durability is not losing data.
- Each nine cuts allowed downtime by 10x: 99.9% ≈ 43.8 min/month, 99.99% ≈ 4.4 min/month.
- Series: multiply availabilities, so every synchronous dependency lowers your ceiling.
- Parallel: `1 − ∏(1 − Ai)`, so redundancy raises availability dramatically, but only if failures are independent, failover is fast, and the survivors can carry the load (N+1).
- `A = MTBF / (MTBF + MTTR)`; reducing MTTR through detection and automation is often the cheapest win.
- Correlated failures (shared racks, bugs, configs) break the maths; use separate failure domains and staged rollouts.

## Further reading
- [Availability table (Google SRE book)](https://sre.google/sre-book/availability-table/)
- [Embracing Risk (Google SRE book)](https://sre.google/sre-book/embracing-risk/)
- [Availability and Beyond (AWS whitepaper)](https://docs.aws.amazon.com/whitepapers/latest/availability-and-beyond-improving-resilience/availability-and-beyond-improving-resilience.html)
- [High availability (Wikipedia)](https://en.wikipedia.org/wiki/High_availability)
- [Mean time between failures (Wikipedia)](https://en.wikipedia.org/wiki/Mean_time_between_failures)
