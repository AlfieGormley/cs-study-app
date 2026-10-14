---
id: net-anycast-bgp-routing
title: "Anycast prefixes and BGP decisions"
level: advanced
minutes: 3
summary: "Explain same-prefix announcements, address counts and why the selected site need not be geographically closest."
sourceLesson: net-global-traffic
---
Anycast makes the destination address stable across locations. The internet’s routing decision then chooses a site using network policy, which is different from choosing the shortest measured RTT.

## Anycast

With anycast, **many locations advertise the same IP prefix** via BGP. Internet routers send each packet to the "nearest" location by BGP's measure, which isn't distance or latency. Each network first applies its own **policy** (typically preferring routes learnt from paying customers over peers, and peers over paid transit), and only then breaks ties on the shortest **AS path** (the number of networks to cross).

Anycast relies on BGP announcing *prefixes*, and in practice the smallest IPv4 prefix most networks will accept is a /24 (256 addresses), so anycast is done with whole /24s (or /48s in IPv6). The number after the slash says how many leading bits of the address are fixed; the rest are free:

```formula
count = 2^{32 − p}
count = 2^{32 − 24} = 2^8 = 256
where
count: how many IPv4 addresses the prefix contains
p: the prefix length, the number after the slash: how many of the address's leading bits are fixed; 24 for a /24
32: the number of bits in an IPv4 address
In words: each bit left free doubles the block, so a /24 leaves 8 free bits and holds 256 addresses.
```

```
      203.0.113.1 announced
      from all three sites
  [London] [Virginia] [Tokyo]
     ^          ^         ^
     |          |         |
  EU users   US users  JP users
```

Advantages:

- **No DNS caching delay.** If a site withdraws its route, traffic shifts as fast as BGP converges: with deployment-dependent delay as routers propagate withdrawals and try alternatives. No convergence measurement or universal time bound is provided here.
- **One IP everywhere,** which simplifies clients and allow-lists.
- **DDoS absorption:** distributed attack sources can spread across several sites, but routing catchments can concentrate an attack on a subset; anycast alone is not a capacity guarantee.
- **Routes the user's actual packets,** not their resolver's location.

This is how DNS root servers, public resolvers (1.1.1.1, 8.8.8.8), Cloudflare's whole network and Google Cloud's global load balancer front ends work. For IPv4 accelerators, AWS Global Accelerator gives you two static anycast IPv4 addresses (dual-stack accelerators also have two IPv6 addresses) that enter AWS's network at the nearest edge and then ride AWS's backbone to your region.

## Key takeaways

- Anycast announces the same prefix from several locations; BGP policy chooses the route.
- IPv4 prefix length fixes leading bits; a /24 leaves 256 addresses.
- Anycast avoids DNS-change delay, but convergence and attack distribution depend on the network.

## Further reading

- [Operation of anycast services (RFC 4786)](https://www.rfc-editor.org/rfc/rfc4786)
- [What is AWS Global Accelerator?](https://docs.aws.amazon.com/global-accelerator/latest/dg/what-is-global-accelerator.html)
