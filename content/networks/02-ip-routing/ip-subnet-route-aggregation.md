---
id: ip-subnet-route-aggregation
title: Aggregate aligned routes
level: basic
minutes: 4
sourceLesson: ip-subnetting
summary: Build exact summary prefixes and explain the routing consequences of an aggregate.
---

Build exact summary prefixes and explain the routing consequences of an aggregate.

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

The general rule: merging a power-of-two number of equal, adjacent blocks shortens the prefix by that power.

```formula
p_agg = p − log_2(k)
p_agg = 24 − log_2(4) = 24 − 2 = 22
where
p_agg: the prefix length of the summary route
p: the prefix length of each block being merged, here 24
k: how many equal-size, adjacent blocks are merged; must be a power of 2 (2, 4, 8 …), here 4
log_2(k): the base-2 logarithm of k: how many copies of 2 must be multiplied together to make k, so log_2(4) = 2 and log_2(8) = 3
In words: four /24s need 2 fewer prefix bits to cover them all, so they combine into one /22, provided the blocks are aligned as explained next.
```

Aggregation requires **prefix alignment**. The block must start on a multiple of its size: for k blocks, the first one's number (here the third octet) must be a multiple of k. `200.10.1.0` to `200.10.4.0` is also four /24s, but no single /22 covers exactly them. The best summary is `200.10.1.0/24`, `200.10.2.0/23` and `200.10.4.0/24`:

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
- [RFC 1918: Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918)
- [RFC 3021: Using 31-Bit Prefixes on Point-to-Point Links](https://www.rfc-editor.org/rfc/rfc3021)
- [Classless Inter-Domain Routing — Wikipedia](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)
- [Subnet — Wikipedia](https://en.wikipedia.org/wiki/Subnet)
- [ipaddress module — Python docs](https://docs.python.org/3/library/ipaddress.html)

- [RFC 3927: IPv4 link-local addressing](https://www.rfc-editor.org/rfc/rfc3927.html)
- [RFC 6598: Shared address space](https://www.rfc-editor.org/rfc/rfc6598.html)
