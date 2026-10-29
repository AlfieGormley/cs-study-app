---
id: ip-subnet-route-aggregation
title: Aggregate aligned routes
level: basic
minutes: 4
sourceLesson: ip-subnetting
summary: Recognise when aligned prefixes can be summarised exactly and predict what an aggregate does to traffic.
---

Every route a router advertises costs table space in every router that hears it. Summarising many prefixes into one keeps tables small, but changes which traffic a router attracts.

## Supernetting and route aggregation

CIDR's other half is **route aggregation** (also called **supernetting** or **summarisation**): advertising several contiguous networks as one shorter prefix.

Suppose an ISP has customers on `200.10.0.0/24`, `200.10.1.0/24`, `200.10.2.0/24` and `200.10.3.0/24`. Write the third octets in binary:

```
0 = 000000|00
1 = 000000|01
2 = 000000|10
3 = 000000|11
```

The first 22 bits match (16 from the first two octets, 6 here), so the ISP advertises one route: **200.10.0.0/22**. The rest of the Internet needs one entry instead of four.

The general rule: merging two equal, adjacent blocks takes one bit off the prefix, four take two bits, eight take three. So four /24s become a /22 and two /25s become a /24.

Aggregation requires **prefix alignment**. The block must start on a multiple of its size: to merge four /24s, the first one's number (here the third octet) must be a multiple of four. `200.10.1.0` to `200.10.4.0` is also four /24s, but no single /22 covers exactly them. The best summary is `200.10.1.0/24`, `200.10.2.0/23` and `200.10.4.0/24`:

```python
import ipaddress as ip

nets = [ip.ip_network(f"200.10.{i}.0/24")
        for i in range(1, 5)]
# Merge only adjacent, aligned prefixes.
print(list(ip.collapse_addresses(nets)))
# [200.10.1.0/24, 200.10.2.0/23,
#  200.10.4.0/24]  (reprs shortened)
```

Aggregation reduces entries advertised to other networks, saving routing/forwarding state. How a router stores control-plane and forwarding tables is implementation-dependent. A maintained aggregate can hide a component route's changes from upstream peers, depending on advertisement policy.

The catch is that a summary can attract traffic for addresses that don't exist, or that live elsewhere. A more-specific route wins by **longest-prefix match**, but only if it exists. An aggregate can still attract traffic for unavailable destinations. The advertising router needs appropriate component routes and discard handling for unmatched portions to avoid forwarding loops.

For example, a router that advertises 10.1.0.0/21 but only has routes for 10.1.4.0/22 attracts traffic for 10.1.0.0 to 10.1.3.255 too. With no more-specific route for those addresses, it either discards them (with a discard or "null" route for the aggregate) or, if its own default route points back towards the sender, bounces them in a loop until TTL expires.

> [!analogy] Real-world analogy: Telephone area codes
> A caller abroad does not need a list of every London subscriber. Their phone network only needs "numbers starting +44 20 go to the London exchange". The London exchange holds the detailed list.
>
> **How it maps:** The area code is the aggregate prefix; the detailed subscriber list is the set of more-specific routes held only by the router that summarises them. Distant routers keep one entry instead of thousands.
>
> **Where it stops:** A call to an unassigned London number still travels to the London exchange before it fails, just as an aggregate attracts traffic for unused addresses. And unlike area codes, prefixes can only be summarised when the blocks are numerically aligned on a power-of-two boundary.

## Address exhaustion

IPv4 has 2³² possible address values (32 copies of 2 multiplied together: 4,294,967,296, about 4.3 billion), and special-purpose ranges reduce the pool available for globally unique assignments. Address sharing, transfers and allocation policies address scarcity in different ways; IPv6 provides a much larger address space.

> [!note] Content omitted after review
> Current global route counts, address-market prices and a regional exhaustion/allocation timeline are absent because they require dated measurements and registry-policy evidence not established in this lesson. No universal purchase price or route-memory design is assumed.

## Key takeaways
- Exact aggregation requires contiguous, correctly aligned blocks.
- A larger covering route can attract traffic for unavailable component destinations.
- More-specific installed routes win; discard handling can prevent loops through aggregate gaps.
- IPv4 scarcity concerns usable allocations, not only the raw 32-bit value count.

## Further reading
- [RFC 4632: Classless Inter-domain Routing (CIDR)](https://www.rfc-editor.org/rfc/rfc4632)
- [Classless Inter-Domain Routing — Wikipedia](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)
- [ipaddress module — Python docs](https://docs.python.org/3/library/ipaddress.html)
