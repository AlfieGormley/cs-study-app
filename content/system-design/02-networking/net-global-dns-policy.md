---
id: net-global-dns-policy
title: "Global DNS policy and residency limits"
level: advanced
minutes: 3
summary: "Choose geographic, latency or weighted DNS steering while enforcing residency independently."
sourceLesson: net-global-traffic
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

- GeoDNS uses location as a proxy; latency steering uses available measurements.
- Weighted answers support gradual migrations, but request shares need not equal DNS weights.
- Enforce residency in tenant, application, storage and failover policy; DNS routing alone cannot guarantee it.

## Further reading

- [Latency-based routing (Amazon Route 53)](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-latency.html)
- [Traffic Manager routing methods (Azure)](https://learn.microsoft.com/en-us/azure/traffic-manager/traffic-manager-routing-methods)
