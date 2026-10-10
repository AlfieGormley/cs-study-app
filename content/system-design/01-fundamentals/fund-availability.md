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

There are two common ways to turn availability into a number: count time, or count requests.

```formula
A_time = T_up / T_total
A_req = N_ok / N_total
where
A_time: time-based availability, the fraction of time the service was up, from 0 to 1 (multiply by 100 for a percentage)
T_up: the time the service was up and serving correctly during the measurement period, e.g. in minutes
T_total: the length of the whole measurement period, in the same unit as T_up
A_req: request-based availability, the fraction of requests that succeeded, from 0 to 1
N_ok: the number of requests that succeeded in the period
N_total: the total number of requests received in the period
In words: availability is the share of the time, or the share of the requests, for which the service did its job.
```

Example: a 30-day month has 43,200 minutes. A service down for 43 of them has a time-based availability of 43,157 / 43,200 ≈ 0.999, i.e. 99.9%. If it received 1 billion requests and 1 million failed, its request-based availability is 999 million / 1 billion = 0.999, also 99.9%.

> [!note] Time-based vs request-based
> Request-based availability is usually more meaningful for large services (Google SRE favours it), because a 5-minute outage at 3 a.m. affects far fewer users than one at peak.

## The nines

Availability is usually quoted in "nines". Here's the equivalent downtime, using a 365.25-day year and an average month (year/12):

| Availability | Downtime/year | Downtime/month |
|---|---|---|
| 99% (two nines) | 3.65 days | 7.3 hours |
| 99.9% | 8.77 hours | 43.8 min |
| 99.95% | 4.38 hours | 21.9 min |
| 99.99% | 52.6 min | 4.4 min |
| 99.999% | 5.26 min | 26 s |

The formula behind the table: the fraction of time you are allowed to be down is 1 minus the availability.

```formula
D = (1 − A) × T
D = (1 − 0.9999) × 525,960 min
D = 0.0001 × 525,960 min ≈ 52.6 min
where
D: the allowed downtime in the period, in minutes (min)
A: the availability target as a fraction, e.g. 99.99% = 0.9999
T: the length of the period, in minutes; a 365.25-day year is 365.25 × 24 × 60 = 525,960 min
min: minute
≈: approximately equal to (rounded)
In words: the unavailable fraction multiplied by the length of the period gives the downtime you are allowed.
```

Each extra nine cuts allowed downtime by 10x. The cost of achieving it depends on the architecture and failure modes; there is no universal cost multiplier. At 99.999%, you have 26 seconds a month. Manual detection and recovery can easily consume that budget, so automated recovery is usually essential.

> [!tip] Think in error budgets
> If your SLO is 99.9%, you have a 0.1% **error budget**: about 43 minutes a month. Spend it on deploys, experiments and incidents. When it's gone, slow down releases. This turns availability into an engineering trade-off rather than a moral absolute.

## Components in series

If a request needs **every** component to work, the components are in **series**. Assuming independent failures, the chance that all of them are up at once is the product of their availabilities:

```formula
A_total = A_1 × A_2 × … × A_n
where
A_total: the availability of the whole chain, as a fraction from 0 to 1
A_1, A_2, A_n: the availability of the first, second and last (n-th) component, each as a fraction (99.9% = 0.999)
n: the number of components the request needs
…: and so on: one factor for every component in between
In words: the chain is up only when every link is up, so multiply the links' availabilities together.
```

```
client -> [LB] -> [App] -> [DB]
         99.99%  99.9%   99.95%
```

```formula
A = A_LB × A_App × A_DB
A = 0.9999 × 0.999 × 0.9995
A ≈ 0.99840 ≈ 99.84%
where
A: the end-to-end availability of the chain, as a fraction
A_LB: the load balancer's availability, 99.99% = 0.9999
A_App: the app tier's availability, 99.9% = 0.999
A_DB: the database's availability, 99.95% = 0.9995
≈: approximately equal to (rounded)
In words: multiplying three high availabilities gives one that is lower than any of them.
```

The chain is **less** available than its weakest link. Every synchronous dependency you add lowers the ceiling. With independent failures, a service requiring 10 dependencies at 99.9% each has modelled availability of 0.999 raised to the power 10, about 0.990 (99.0%), i.e. about 3.65 days of downtime a year.

This is the mathematical reason to:

- Remove dependencies from the critical path (do work asynchronously).
- Degrade gracefully: show the page without recommendations rather than failing it.
- Be suspicious of deep synchronous microservice call chains.

## Components in parallel

If the system works as long as **at least one** of several redundant components works, they're in **parallel**. The system fails only if *all* fail, so work out the chance that every one is down and subtract it from 1:

```formula
A_total = 1 − (1 − A_1) × … × (1 − A_n)
A_total = 1 − ∏(1 − A_i)
where
A_total: the availability of the redundant group, as a fraction from 0 to 1
A_1, A_n: the availability of the first and last (n-th) component, each as a fraction
A_i: the availability of component number i, where i runs from 1 to n
1 − A_1: the unavailability of component 1, the fraction of time it is down
n: the number of redundant components
…: and so on: one factor for every component in between
∏: capital pi, "multiply together": the product of the bracket over every component i; the second line is just a compact way of writing the first
In words: the group is down only when every member is down at once, so multiply their down-fractions and subtract from 1.
```

```
            +--> [App 99%] --+
client ->LB-|                |-> ok
            +--> [App 99%] --+
```

```formula
A = 1 − (1 − A_s) × (1 − A_s)
A = 1 − (0.01 × 0.01)
A = 1 − 0.0001 = 0.9999 = 99.99%
where
A: the availability of the pair of app servers, as a fraction
A_s: the availability of one app server, 99% = 0.99, so it is down 1 − 0.99 = 0.01 of the time
In words: two servers that are each down 1% of the time are both down only 1% of 1% of the time.
```

Two 99% servers give 99.99%; three give 99.9999%. Redundancy is enormously powerful, which is why replication across availability zones is standard practice.

> [!warning] Redundancy needs spare capacity
> The parallel formula assumes **one survivor can carry the whole load**. If peak traffic needs both servers, losing either one at peak overloads the other, and the pair behaves like two components in series. Plan for **N+1** (or N+2): enough servers that the system still meets its load with one, or one zone, gone.

When some number of identical servers are needed out of a larger group (written "k of n"), the system is up while at least that many are up. For three 99% servers where any two can carry peak load, add up the chances of the states that work: all three up, or exactly two up.

```formula
P_3 = a^3 = 0.99^3 = 0.970299
P_2 = 3 × a^2 × (1 − a)
P_2 = 3 × 0.99^2 × 0.01 = 0.029403
A = P_3 + P_2 = 0.999702 ≈ 99.97%
where
P_3: the probability that all three servers are up
P_2: the probability that exactly two are up and one is down
a: the availability of one server, 0.99
^: "to the power of": a^3 means a × a × a
3: the number of ways to pick which one of the three servers is the one that is down
A: the availability of the tier, the probability at least two servers are up
≈: approximately equal to (rounded)
In words: the tier works when all three are up or when exactly one is down; add the probabilities of those two situations.
```

That's a big step down from the 99.9999% you'd get if any *one* could cope, and a big step up from the 97.03% of needing all three.

### Combining them

Real systems mix both. Compute parallel groups first, then multiply the groups in series:

```formula
A_LB = 1 − 0.001^2 = 0.999999
A_App = 1 − 0.01^3 = 0.999999
A_DB = 1 − 0.005^2 = 0.999975
A = A_LB × A_App × A_DB
A ≈ 0.999973 ≈ 99.997%
where
A_LB: the availability of a pair of load balancers, each 99.9% available (down 0.001 of the time)
A_App: the availability of three app servers, each 99% available (down 0.01 of the time), where any one can carry the load
A_DB: the availability of a pair of databases, each 99.5% available (down 0.005 of the time)
A: the availability of the whole system, the three groups in series
^: "to the power of": 0.001^2 means 0.001 × 0.001
≈: approximately equal to (rounded)
In words: work out each redundant group with the parallel formula, then multiply the groups together because a request needs all three.
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

Over a long run, the system cycles between working (for MTBF on average) and being repaired (for MTTR on average). The fraction of each cycle spent working is the availability:

```formula
A = MTBF / (MTBF + MTTR)
A = 1,000 h / (1,000 h + 1 h) ≈ 0.999
where
A: the steady-state availability, the long-run fraction of time the system is up
MTBF: mean time between failures, the average time it runs before failing, here in hours (h)
MTTR: mean time to repair (or recovery), the average time to restore service after a failure, in the same unit as MTBF
h: hour
≈: approximately equal to (rounded)
In words: availability is the up-time of a typical cycle divided by the whole cycle, up-time plus repair time.
```

Example: a server fails on average every 1,000 hours and takes 1 hour to fix, which gives 1,000 / 1,001 ≈ 99.9%. The formula assumes failures and repairs keep repeating at these average rates; it says nothing about how bad any single outage is.

There are two levers:

1. **Increase MTBF**: better hardware, fewer risky changes, more testing.
2. **Decrease MTTR**: faster detection, automated failover, quick rollbacks, good runbooks.

Lowering MTTR is often cheaper and more effective. Cutting MTTR from 60 minutes to 6 gives the same availability gain as making failures 10x rarer. Recovery time itself breaks down into:

```formula
MTTR = t_detect + t_diagnose
     + t_fix + t_verify
where
MTTR: mean time to repair (or recovery), the average time from failure to restored service
t_detect: the time until anyone (or any alert) notices the failure
t_diagnose: the time to work out what is wrong
t_fix: the time to fix it, fail over to a standby or roll back
t_verify: the time to confirm service is really restored
In words: recovery time is the sum of noticing, understanding, fixing and checking, so shortening any stage shortens recovery.
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
- Parallel: 1 minus the product of the members' down-fractions, so redundancy raises availability dramatically, but only if failures are independent, failover is fast, and the survivors can carry the load (N+1).
- Availability is MTBF divided by (MTBF + MTTR); reducing MTTR through detection and automation is often the cheapest win.
- Correlated failures (shared racks, bugs, configs) break the maths; use separate failure domains and staged rollouts.

## Further reading
- [Availability table (Google SRE book)](https://sre.google/sre-book/availability-table/)
- [Embracing Risk (Google SRE book)](https://sre.google/sre-book/embracing-risk/)
- [Availability and Beyond (AWS whitepaper)](https://docs.aws.amazon.com/whitepapers/latest/availability-and-beyond-improving-resilience/availability-and-beyond-improving-resilience.html)
- [High availability (Wikipedia)](https://en.wikipedia.org/wiki/High_availability)
- [Mean time between failures (Wikipedia)](https://en.wikipedia.org/wiki/Mean_time_between_failures)
