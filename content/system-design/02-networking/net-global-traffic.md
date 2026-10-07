---
id: net-global-traffic
title: "Global traffic management: GeoDNS, anycast and failover"
level: advanced
minutes: 15
summary: How to steer users to the right region with GeoDNS, latency-based routing and anycast, and how to fail over between regions without making things worse.
---

Once a system runs in more than one region, something has to decide **which region each user talks to**, and what happens when a region fails. That's global traffic management (GTM).

The goals usually are:

- **Latency:** send users to a nearby, fast region.
- **Availability:** move traffic away from failing regions quickly.
- **Compliance:** keep EU users' data in the EU, for example.
- **Capacity and cost:** don't overload a region; use cheaper capacity where possible.

There are two main families of technique: **DNS-based** steering and **network-based (anycast)** steering.

## DNS-based steering

The authoritative DNS server returns a different answer depending on who's asking.

### GeoDNS

Map the resolver's (or, with EDNS Client Subnet, the client's) IP to a location, and return the region assigned to that location:

| Client location | Answer |
|---|---|
| Europe | eu-west-1 LB |
| North America | us-east-1 LB |
| Asia-Pacific | ap-southeast-1 LB |
| Default | us-east-1 LB |

Geography is a proxy for latency, but not a perfect one: network paths don't follow borders. A user in Perth might be faster to Singapore than to Sydney on some ISPs. GeoDNS can help steer traffic towards an assigned region, but it cannot enforce **data residency**: IP geolocation, resolvers, VPNs and cached answers can misroute traffic. Enforce tenant residency in application routing, storage, replication and failover policy.

### Latency-based routing

Instead of geography, route by **measured latency**. AWS Route 53 latency routing uses AWS's own measurements between client networks and AWS regions; NS1 and others can use real-user measurements (RUM) collected by JavaScript beacons in browsers. This estimates a fast region using the available measurements; it does not guarantee the fastest path for every client or request.

### Weighted and failover policies

- **Weighted:** select DNS answers with relative weights, e.g. 90/10 between regions (resolver caching and connection reuse mean request traffic need not follow those exact percentages) for a migration, or to balance by capacity.
- **Failover:** a primary/secondary pair; the secondary is returned only when the primary's health check fails.
- Policies can be nested: latency-based between regions, each region with a failover pair behind it.

### The fundamental limit: caching

DNS steering is only as fast as caches expire. With a 60 s TTL, most clients move within a minute or two after a change, but some take much longer (see the DNS lesson). DNS also makes **one decision per lookup**, not per request: a client that resolved once may keep using the same IP for hours via pooled connections.

## Anycast

With anycast, **many locations advertise the same IP prefix** via BGP. Internet routers send each packet to the "nearest" location by BGP's measure, which isn't distance or latency. Each network first applies its own **policy** (typically preferring routes learnt from paying customers over peers, and peers over paid transit), and only then breaks ties on the shortest **AS path** (the number of networks to cross).

Anycast relies on BGP announcing *prefixes*, and in practice the smallest IPv4 prefix most networks will accept is a /24 (256 addresses), so anycast is done with whole /24s (or /48s in IPv6).

```
      203.0.113.1 announced
      from all three sites
  [London] [Virginia] [Tokyo]
     ^          ^         ^
     |          |         |
  EU users   US users  JP users
```

Advantages:

- **No DNS caching delay.** If a site withdraws its route, traffic shifts as fast as BGP converges: often within seconds, though withdrawals can take a minute or more to settle everywhere as routers try alternative paths.
- **One IP everywhere,** which simplifies clients and allow-lists.
- **DDoS absorption:** distributed attack sources can spread across several sites, but routing catchments can concentrate an attack on a subset; anycast alone is not a capacity guarantee.
- **Routes the user's actual packets,** not their resolver's location.

This is how DNS root servers, public resolvers (1.1.1.1, 8.8.8.8), Cloudflare's whole network and Google Cloud's global load balancer front ends work. For IPv4 accelerators, AWS Global Accelerator gives you two static anycast IPv4 addresses (dual-stack accelerators also have two IPv6 addresses) that enter AWS's network at the nearest edge and then ride AWS's backbone to your region.

### Anycast's caveats

- **"Nearest" by BGP isn't always nearest by latency.** ISP peering choices can send a user in Paris to a PoP in Amsterdam or even further.
- **Route changes can break TCP.** If BGP shifts mid-connection, packets start arriving at a different site that has no state for that connection, and it resets. For short HTTP requests this is rare and tolerable; for long-lived connections it hurts. QUIC doesn't escape this either, since the new site has no keys for the connection. Operators keep routes stable and use connection-aware L4 layers.
- **Withdrawing a site sends its traffic to the next-nearest sites,** not evenly everywhere. Taking down a big PoP can overload its neighbours, so capacity planning has to consider who inherits each site's users.
- **Anycast is usually only the front door.** Stateless UDP (DNS) is the ideal fit. For TCP services, operators terminate connections at the anycast edge and use ordinary unicast routing behind it.
- **Capacity control is coarse.** You can't directly say "send 30% to London". Operators shape it with route withdrawals, AS-path prepending or BGP communities, all blunt tools.

### Combining them

Many large systems use **anycast to the edge, then private routing to regions**:

```
User --anycast--> nearest edge PoP
        (TLS terminates here)
              |
         private backbone
              |
       chosen origin region
  (by latency, health, capacity)
```

The edge picks the origin region per request with up-to-date health data, which avoids DNS caching entirely for the region decision.

## Multi-region failover

Routing is the easy part. The hard part is what happens to **data and capacity** when you move traffic.

### Active-passive vs active-active

| | Active-passive | Active-active |
|---|---|---|
| Normal traffic | One region | All regions |
| Standby cost | Idle capacity | Shared |
| Failover | Promote standby | Shift traffic |
| Data | Often an async standby; synchronous designs are possible | Can use one write leader, partitioned ownership or multi-region coordination |
| Risk | Standby untested | Conflicts, complexity |

**Active-passive** is simpler: one region serves, another holds replicated data. But failover is a rare, scary event. The standby may have drifted, its caches are cold, and the replica may lag. **RPO** is the recovery-point objective, expressed as a time window; actual lag and recovery behavior determine whether that objective is met.

**Active-active** serves from every region all the time, so failover is "just" sending more traffic to regions that are already working. The application tier may be active in several regions while writes still go to one database leader, at the cost of cross-region latency. Local writes in every region require distributed coordination, conflict handling or ownership partitioning, covered in the consistency module.

### Capacity planning for failover

If you run three regions at 70% utilisation and one fails, its traffic lands on the other two:

```
Before: 70% + 70% + 70%  (total 210)
After:  105% + 105%      (overloaded)
```

In an ideal model with equal region capacities, proportional work, no extra failover overhead and even redistribution, the no-overload ceiling before losing one of *N* regions is `(N − 1) / N`: **about 66% for three regions**, 50% for two. Use a lower target when latency SLOs, cold caches or other bottlenecks require spare capacity. (This assumes traffic redistributes evenly. With GeoDNS or anycast it often doesn't: a failed EU region's users may mostly land in the next-nearest region, which needs more headroom than the average.)

### Failover mechanics that bite

1. **Thundering herd.** Moving traffic all at once to a region with cold caches and unscaled autoscaling groups can knock it over too, turning a one-region outage into a global one. Shift gradually (weighted steps) and keep standby capacity warm.
2. **Flapping.** A region whose health check alternates pass/fail causes traffic to bounce back and forth. Use hysteresis: require several consecutive failures to fail over, and a sustained period of health (with human approval, often) to fail back.
3. **Health checks that lie.** A region can pass `/healthz` while its database is read-only. Health signals should be **end-to-end** (can it complete a real write?) and evaluated from multiple vantage points, so one network blip doesn't trigger global failover.
4. **Dependency on the control plane.** If failover requires calling an API in the region that's failing (or a global control plane having its own bad day), you can't fail over. AWS recommends that recovery actions rely on **data plane** operations, such as Route 53 health checks flipping records, rather than control-plane changes during an incident.
5. **Split brain.** If both regions believe they're primary and accept writes, data diverges. Use fencing and a single source of truth for which region is primary.

> [!example] Practise it
> Teams that fail over regularly (Netflix's region evacuation exercises are the famous example) find problems on a calm Tuesday instead of during a real outage. An untested failover plan is a hypothesis, not a plan.

## Choosing a technique

| Need | Technique |
|---|---|
| Data residency | Enforced tenant/storage policy; GeoDNS assists routing |
| Lowest latency | Latency routing or anycast |
| Fast failover | Anycast or edge routing |
| Gradual migration | Weighted DNS |
| DDoS resilience | Anycast |
| Simple start | DNS failover pair |

## Key takeaways

- GeoDNS maps location to region; latency-based routing uses measured latency; weighted and failover policies handle migrations and outages.
- DNS steering is limited by caching and sees the resolver, not the user, unless ECS is used.
- Anycast routes the user's packets to the nearest site with BGP: fast failover and DDoS absorption, but coarse control and BGP-defined "nearest".
- Active-active gives smoother failover but needs multi-region data; active-passive is simpler but risky and rarely tested.
- Keep enough headroom to absorb a lost region (≤ 66% per region with three), shift traffic gradually, and practise failover.

## Further reading

- [Anycast (Wikipedia)](https://en.wikipedia.org/wiki/Anycast)
- [Latency-based routing (Amazon Route 53)](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-latency.html)
- [What is AWS Global Accelerator?](https://docs.aws.amazon.com/global-accelerator/latest/dg/what-is-global-accelerator.html)
- [Traffic Manager routing methods (Azure)](https://learn.microsoft.com/en-us/azure/traffic-manager/traffic-manager-routing-methods)
- [Disaster recovery options in the cloud (AWS whitepaper)](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
