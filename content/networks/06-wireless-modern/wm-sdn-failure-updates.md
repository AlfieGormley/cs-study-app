---
id: wm-sdn-failure-updates
title: Controller failures and safe forwarding updates
level: intermediate
minutes: 3
summary: Controller-loss behaviour depends on mode, installed entries, timeouts and preinstalled failover.
sourceLesson: wm-sdn
---

Centralising control raises two practical questions: what happens when the controller is unreachable, and how do you change the rules on many switches without breaking traffic halfway through? Both have answers that depend on careful ordering rather than on the controller being perfect.

## Trade-offs and failure modes

- **Controller availability.** Controller-loss behaviour is configured: in OpenFlow fail-secure mode retained entries can continue, subject to timeout expiry and other changes. Fail-standalone/hybrid behaviour and preinstalled local failover differ. Replication can improve availability but is not mandated by SDN itself.
- **Consistency during updates.** Changing many switches is not atomic; for a moment some use old rules and some new, which can cause loops or packets silently dropped for lack of a matching rule. Techniques include two-phase updates with version numbers carried in packets.
- **Scale of reactive control.** Reactive control consumes controller/channel/table resources. Test its capacity and use aggregate/proactive rules where suitable; no universal flow-rate cutoff or deployment share is assumed here.
- **Debuggability.** The state of a virtual network lives in software and hypervisors. Cloud tools like VPC Flow Logs and reachability analysers exist because `traceroute` inside an overlay often tells you little.

> [!note] Evidence limits
> Universal SDN adoption shares, TCAM capacities, controller rate limits and unverified provider-specific datapaths are omitted. Cloud rules and product features must be rechecked against current documentation. This lesson’s arithmetic and table traces are models; no live AWS or OpenFlow fabric was deployed during review.

## Preparing and draining a replacement path

Suppose healthy traffic currently follows A → B → D and should move to A → C → D. C initially has no matching entry. Install the required forwarding at C first, then confirm successful installation (including checking errors, not merely receiving a barrier reply). Change A to send new traffic through C only after that confirmation. Keep B’s old forwarding while packets already on the old path can still arrive; remove it only after an appropriate drain condition. Link health alone does not make separately arriving updates atomic.

> [!analogy] Real-world analogy: Opening a road diversion
> Highway crews opening a diversion first make sure the new route is passable, then change the signs at the junction, and only close the old road once the cars already on it have left. Closing the old road first, or signposting a route that is not ready yet, strands drivers.
>
> **How it maps:** Making the new route passable is installing and confirming C's rule; changing the junction signs is updating A's next hop; waiting for cars to clear is draining packets in flight; closing the road is removing B's old rule.
>
> **Where it stops:** Drivers can see a closed road and turn back; packets that hit a missing rule are silently dropped. Switches also receive their updates separately with no shared clock, so "after confirmation" needs explicit acknowledgments or version numbers rather than a glance down the road.

This is a basic path-transition model. More general consistent updates can use version numbers carried in packets and two phases, with a strategy for overlapping versions, finite table space and failures.

## Key takeaways
- Controller-loss behaviour depends on mode, installed entries, timeouts and preinstalled failover.
- Install a new path before directing traffic to it, and drain the old path before removing its rules.

## Further reading
- [OpenFlow Switch Specification 1.3.5](https://opennetworking.org/wp-content/uploads/2014/10/openflow-switch-v1.3.5.pdf)
- [Reitblatt et al.: Abstractions for Network Update](https://www.cs.cornell.edu/~jnfoster/papers/frenetic-consistent-updates.pdf)
