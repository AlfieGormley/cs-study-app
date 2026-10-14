---
id: net-region-failover-operations
title: "Operate and practise regional failover"
level: advanced
minutes: 3
summary: "Avoid cold-cache overload, flapping, control-plane dependencies and split brain during recovery."
sourceLesson: net-global-traffic
---
Failover is an operational procedure, not just a routing policy. A standby that has the right data can still fail because it is cold, undersized or promoted inconsistently.

### Failover mechanics that bite

1. **Thundering herd.** Moving traffic all at once to a region with cold caches and unscaled autoscaling groups can knock it over too, turning a one-region outage into a global one. Shift gradually (weighted steps) and keep standby capacity warm.
2. **Flapping.** A region whose health check alternates pass/fail causes traffic to bounce back and forth. Use hysteresis: require several consecutive failures to fail over, and a sustained period of health (with human approval, often) to fail back.
3. **Health checks that lie.** A region can pass `/healthz` while its database is read-only. Health signals should be **end-to-end** (can it complete a real write?) and evaluated from multiple vantage points, so one network blip doesn't trigger global failover.
4. **Dependency on the control plane.** If failover requires calling an API in the region that's failing (or a global control plane having its own bad day), you can't fail over. AWS recommends that recovery actions rely on **data plane** operations, such as Route 53 health checks flipping records, rather than control-plane changes during an incident.
5. **Split brain.** If both regions believe they're primary and accept writes, data diverges. Use fencing and a single source of truth for which region is primary.

> [!example] Practise it
> Teams that fail over regularly (Netflix's region evacuation exercises are the famous example) find problems on a calm Tuesday instead of during a real outage. An untested failover plan is a hypothesis, not a plan.

## Key takeaways

- Keep standby capacity warm and shift load gradually to avoid a second-region overload.
- Use hysteresis and end-to-end health signals from several vantage points before changing regions.
- Prepare data-plane recovery and fence write leaders; practise the complete failover path.

## Further reading

- [Disaster recovery options in the cloud (AWS)](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
- [Amazon Route 53 health checks](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html)
