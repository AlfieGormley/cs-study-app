---
id: net-anycast-bgp-routing
title: "Anycast prefixes and BGP decisions"
level: advanced
minutes: 3
summary: "Explain same-prefix announcements, prefix sizes and why the selected site need not be geographically closest."
sourceLesson: net-global-traffic
---
Anycast makes the destination address stable across locations. The internet’s routing decision then chooses a site using network policy, which is different from choosing the shortest measured RTT.

## Anycast

With anycast, **many locations advertise the same IP prefix** via BGP. Internet routers send each packet to the "nearest" location by BGP's measure, which isn't distance or latency. Each network first applies its own **policy** (typically preferring routes learnt from paying customers over peers, and peers over paid transit), and only then breaks ties on the shortest **AS path** (the number of networks to cross).

Anycast relies on BGP announcing *prefixes* (blocks of addresses), not single addresses. In practice the most specific IPv4 prefix most networks will accept is a /24, a block of 256 addresses (the number after the slash is how many leading bits are fixed), so anycast is done with whole /24s, or /48s in IPv6. That is why even a service that needs one address announces a whole block.

```
      203.0.113.1 announced
      from all three sites
  [London] [Virginia] [Tokyo]
     ^          ^         ^
     |          |         |
  EU users   US users  JP users
```

> [!analogy] Real-world analogy: One emergency number, many call centres
> Everyone in a country dials the same short emergency number, yet a caller in one city usually reaches a different call centre from a caller in another. The phone network, not the caller, decides which centre answers, using how calls are routed rather than a map of distances.
>
> **How it maps:** the shared number is the anycast address announced from every site, the call centres are the sites, and the phone network's routing rules play the part of BGP policy choosing a route. If one centre goes offline, calls are rerouted to another without anyone learning a new number.
>
> **Where it stops:** BGP makes its choice per network and per route announcement, guided by commercial policy, and a route change part-way through a TCP connection can deliver its packets to a site that has no record of it. A rerouted phone call is set up afresh; an anycast flow is not.

Advantages:

- **No DNS caching delay.** If a site withdraws its route, traffic shifts as fast as BGP converges: with deployment-dependent delay as routers propagate withdrawals and try alternatives. No convergence measurement or universal time bound is provided here.
- **One IP everywhere,** which simplifies clients and allow-lists.
- **DDoS absorption:** distributed attack sources can spread across several sites, but routing catchments can concentrate an attack on a subset; anycast alone is not a capacity guarantee.
- **Routes the user's actual packets,** not their resolver's location.

This is how DNS root servers, public resolvers (1.1.1.1, 8.8.8.8), Cloudflare's whole network and Google Cloud's global load balancer front ends work. For IPv4 accelerators, AWS Global Accelerator gives you two static anycast IPv4 addresses (dual-stack accelerators also have two IPv6 addresses) that enter AWS's network at the nearest edge and then ride AWS's backbone to your region.

## Key takeaways

- Anycast announces the same prefix from several locations; BGP policy chooses the route.
- Anycast is done with whole prefixes, in practice at least a /24 (256 IPv4 addresses).
- Anycast avoids DNS-change delay, but convergence and attack distribution depend on the network.

## Further reading

- [Operation of anycast services (RFC 4786)](https://www.rfc-editor.org/rfc/rfc4786)
- [What is AWS Global Accelerator?](https://docs.aws.amazon.com/global-accelerator/latest/dg/what-is-global-accelerator.html)
