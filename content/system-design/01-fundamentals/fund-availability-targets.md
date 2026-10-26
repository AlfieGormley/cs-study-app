---
id: fund-availability-targets
title: Translate availability targets into error budgets
level: intermediate
minutes: 4
summary: Distinguish availability, reliability and durability, and turn nines into measurable SLO budgets.
sourceLesson: fund-availability
---

"Is the system up?" sounds like a yes/no question. In practice, availability is a number you design for, measure and trade against cost. This lesson explains how the target becomes a practical failure allowance.

## Availability vs reliability vs durability

These words are often used interchangeably. They shouldn't be.

- **Availability**: the fraction of time (or of requests) the system is able to serve correctly. "99.9% of minutes this month the API returned successful responses."
- **Reliability**: the probability the system works correctly *without failure* over a period. A system that fails for 100 ms every minute is about 99.83% available but terrible for reliability: almost any long-running job or long-lived connection will hit a failure.
- **Durability**: the probability that stored data is *not lost*. Amazon S3 is designed for 99.999999999% (eleven nines) durability but offers a much lower availability SLA. Data can be safe yet temporarily unreachable.

There are two common ways to turn availability into a number: count time, or count requests.

Availability can count **successful time** or **successful requests**. Choose what counts as good service and the observation window before comparing targets.

For a 30-day month, 99.9% time-based availability allows about 43 minutes of downtime. A request-based 99.9% target allows one failed request per thousand. These allowances differ when traffic varies or an incident affects only some requests.

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

```formula reference
D = (1 − A) × T
where
D: the allowed downtime in the period, in minutes
A: the time-based availability target as a fraction, such as 0.999 for 99.9%
T: the length of the observation period, in minutes
In words: the share of time outside the availability target determines the downtime allowance. A stricter target leaves less room for outages in the same period.
```

Each extra nine cuts allowed downtime by 10x. The cost of achieving it depends on the architecture and failure modes; there is no universal cost multiplier. At 99.999%, you have 26 seconds a month. Manual detection and recovery can easily consume that budget, so automated recovery is usually essential.

> [!tip] Think in error budgets
> If your SLO is 99.9%, you have a 0.1% **error budget**: about 43 minutes a month. Spend it on deploys, experiments and incidents. When it's gone, slow down releases. This turns availability into an engineering trade-off rather than a moral absolute.

## SLIs, SLOs and SLAs (briefly)

- **SLI** (indicator): the measurement, e.g. proportion of requests returning non-5xx in under 300 ms.
- **SLO** (objective): the target for that SLI, e.g. 99.9% over 30 days.
- **SLA** (agreement): a contract with consequences, e.g. service credits. AWS's EC2 Region-Level SLA specifies 99.99% under its stated multi-AZ deployment and measurement conditions; an individual instance has a separate commitment.

SLAs are normally looser than internal SLOs, so you're warned before you owe customers money. The reliability and observability module goes deeper.

## Key takeaways
- Availability measures successful service, reliability measures failure-free operation, and durability measures retained data.
- Time-based and request-based availability weight partial and peak-hour outages differently.
- An SLI is a measurement, an SLO its target, and an SLA a contractual commitment; the remaining failure allowance is the error budget.

## Further reading
- [Availability table (Google SRE)](https://sre.google/sre-book/availability-table/)
- [Embracing Risk (Google SRE)](https://sre.google/sre-book/embracing-risk/)
- [Service Level Objectives (Google SRE)](https://sre.google/sre-book/service-level-objectives/)
