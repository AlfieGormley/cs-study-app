---
id: rel-user-journey-sli-contracts
title: User journeys, SLIs and contracts
level: advanced
minutes: 4
summary: Define measurable good events and distinguish internal objectives from customer contracts.
sourceLesson: rel-slos-error-budgets
---

The observability units introduced measurements and actionable symptoms. An objective now specifies the acceptable user outcome over time. Use a clear event definition before choosing how many nines to promise.

"Make it as reliable as possible" is not a target. Higher reliability targets generally require investment. Choose them from user needs and measured end-to-end behavior; the benefit depends on the workload and its other failure modes.

Google's SRE approach replaces vague goals with three precise concepts, and turns the gap between perfect and good enough into a budget teams can spend.

The fundamentals module covered what the nines mean in downtime per year. Here we use those numbers operationally.

## The vocabulary

| Term | What it is | Example |
|---|---|---|
| SLI | a measurement | % of requests < 300ms |
| SLO | a target for an SLI | 99.9% over 28 days |
| SLA | a contract with penalties | 99.5% or credits |
| Error budget | the failure the SLO allows | 0.1% may fail |

- **SLI (service level indicator)**: a carefully defined quantitative measure of some aspect of service, ideally a ratio of good events to total events.
- **SLO (service level objective)**: the target value for the SLI over a window.
- **SLA (service level agreement)**: a business contract stating consequences (refunds, credits) if a level is missed. SLAs should be *looser* than internal SLOs, so you notice and react long before you owe customers money.

## Choosing good SLIs

The SRE workbook recommends expressing every SLI as:

```formula
SLI = G / V × 100%
SLI = 999,000 / 1,000,000 × 100%
SLI = 99.9%
where
SLI: the service level indicator, as a percentage from 0 to 100%
G: good events, e.g. requests that succeeded within the latency threshold, here 999,000
V: valid events, all events that count (excluding things like health checks), here 1,000,000
%: per cent
In words: the SLI is the share of valid events that were good. 999,000 good requests out of a million valid ones is an SLI of 99.9%.
```

This gives a number between 0 and 100% that's easy to reason about and aggregate.

Common SLI types by kind of system:

| System | SLI types |
|---|---|
| Request/response API | availability, latency, quality |
| Data pipeline | freshness, correctness, coverage |
| Storage | durability, latency |

### Make SLIs reflect what users feel

- **Measure as close to the user as practical.** Server logs miss requests that never arrived (DNS, load balancer, TLS failures). Load balancer logs are better; client-side measurements or synthetic probes are closer still, but noisier.
- **Define "good" precisely.** "Availability" might be "HTTP status not 5xx", but a `200` with an empty search result due to a backend timeout is also bad. Latency SLIs need thresholds, e.g. "served in under 300 ms".
- **Use percentile thresholds via ratios.** "99% of requests faster than 300 ms" is a ratio SLI, so it can have an error budget. “a p99 below 300 milliseconds” is harder to budget.
- **Focus on critical user journeys.** For a shop: search, view product, add to basket, checkout. A slow "update avatar" endpoint matters less than a failing checkout.
- **Exclude invalid events**, such as health checks or requests rejected for bad input (4xx caused by the client).

> [!example] A concrete SLI spec
> "Proportion of `POST /checkout` requests, measured at the load balancer, that return a non-5xx status in under 800 ms, excluding synthetic health checks." SLO: 99.9% over a rolling 28 days.

### How many nines?

Pick an SLO from what users need and what you can achieve, not from aspiration. Start from historical performance, then tighten if users are unhappy. Remember the maths of hard dependencies in series: a hard, synchronous dependency with 99.9% achieved availability caps its caller under the same measurement and failure conditions unless retries, caching or another recovery mechanism masks its failures. A dependency's contractual target alone is not a measured ceiling.

## Key takeaways

- An SLI measures, an SLO targets it over a window and an SLA states contractual consequences.
- Count valid events and define good outcomes precisely near the user.
- Choose critical journeys and realistic objectives; contractual dependency targets are not measured availability ceilings.

## Further reading

- [Service level objectives (Google SRE book)](https://sre.google/sre-book/service-level-objectives/)
- [Implementing SLOs (Google SRE workbook)](https://sre.google/workbook/implementing-slos/)
- [Embracing risk (Google SRE book)](https://sre.google/sre-book/embracing-risk/)
