---
id: fund-cost-availability-decisions
title: Price availability and data movement
level: advanced
minutes: 3
summary: Compare the cost of downtime with resilience spending, and account for transfer, storage and idle headroom.
sourceLesson: fund-tradeoffs
---

Technical resilience and cloud usage both consume a budget. Make the assumptions visible so a design review can compare the cost of the system with the cost of its failure.

## Cost

Cost is a first-class requirement, not an afterthought.

- **Each nine is expensive.** Going from 99.9% to 99.99% often means multi-zone everything, automated failover and on-call staffing. Ask what an hour of downtime actually costs the business.
- **Data transfer adds up.** Some cross-zone and internet egress traffic is charged per GB; routes, service exceptions and free allowances vary by provider. A chatty cross-zone microservice architecture can cost more in transfer than in compute. Zone-aware routing (prefer a same-zone replica), compression and consumers that fetch from the nearest replica all cut the bill.
- **Storage tiers.** Hot SSD, object storage and archive tiers have different storage, request and retrieval prices; compare current provider pricing for the expected workload. Lifecycle policies move cold data down.
- **Over-provisioning vs autoscaling.** Headroom costs money; too little costs outages.

To price a time-based availability target, combine its downtime allowance with an explicit cost per hour. A request-based target needs a model of affected requests and their impact.

This is a **budget scenario**, not a prediction that the service will use every minute it is allowed. Compare the plausible reduction in downtime losses with the full extra infrastructure, staffing and operational cost. Include contractual and reputational consequences when they matter.

> [!example] Pricing the trade-off
> Suppose an outage costs £20k per hour. 99.9% allows about 8.8 hours a year (about £175k of downtime cost if you use the whole budget); 99.99% allows about 53 minutes (about £18k). The upgrade saves roughly £157k a year. If moving to 99.99% costs £300k/year in extra infrastructure and staff, it isn't worth it on these numbers, unless downtime also causes reputational or regulatory damage.

## Key takeaways
- An availability target is a business choice: compare additional infrastructure and staffing with the downtime risk it reduces.
- Cross-zone and internet traffic, retrieval prices and spare capacity can dominate costs.
- The downtime-budget calculation is a scenario, not a forecast that the full budget will actually be used.

## Further reading
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
- [Embracing Risk (Google SRE)](https://sre.google/sre-book/embracing-risk/)
- [Magic Pocket (Dropbox)](https://dropbox.tech/infrastructure/magic-pocket-infrastructure)
