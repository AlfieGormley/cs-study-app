---
id: ip-subnet-special-ranges
title: Private, shared and link-local space
level: basic
minutes: 3
sourceLesson: ip-subnetting
summary: Distinguish RFC 1918, CGN shared space and link-local addresses, including overlap risks.
---

Distinguish RFC 1918, CGN shared space and link-local addresses, including overlap risks.

## Special and private ranges

Some special-purpose blocks are listed below. This is not a complete registry:

| Block | Purpose |
|---|---|
| 10.0.0.0/8 | Private (RFC 1918) |
| 172.16.0.0/12 | Private (RFC 1918) |
| 192.168.0.0/16 | Private (RFC 1918) |
| 100.64.0.0/10 | Shared address space, intended for CGN deployments |
| 127.0.0.0/8 | Loopback |
| 169.254.0.0/16 | Link-local |

**Private** RFC 1918 addresses can be routed within cooperating private networks. They are not globally reachable address space and should not be advertised into the public Internet. NAT is one way to reach public services; application proxies and gateways are alternatives. `172.32.0.1` lies outside RFC 1918, but being outside a private block alone does not prove an address is assigned or reachable.

**100.64.0.0/10** (RFC 6598) is distinct shared address space intended to reduce conflict with customers' RFC 1918 networks in CGN deployments. It cannot guarantee absence of overlap when other networks also use shared space.

**169.254.0.0/16** is IPv4 link-local space. Automatic assignment can occur when routable configuration is unavailable, but the presence of a link-local address alone does not prove a DHCP failure. RFC 3927 reserves the first and last /24 within this block from automatic selection, and routers must not forward link-local traffic to other links.

> [!warning] Overlapping private ranges
> Connecting networks with overlapping addresses can make destination-only routing ambiguous. Coordinate an address plan with connected organisations and cloud networks. Renumbering, translation or separate routing contexts can address different cases; choosing a supposedly unusual RFC 1918 block does not guarantee uniqueness.

## Key takeaways
- RFC 1918 has three specific private blocks; nearby addresses need not be private.
- Shared 100.64.0.0/10 space is distinct and cannot guarantee that interconnected networks never overlap.
- A link-local address does not by itself establish a DHCP failure.
- Overlapping destination addresses need an addressing or routing-context solution.

## Further reading
- [RFC 4632: Classless Inter-domain Routing (CIDR)](https://www.rfc-editor.org/rfc/rfc4632)
- [RFC 1918: Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918)
- [RFC 3021: Using 31-Bit Prefixes on Point-to-Point Links](https://www.rfc-editor.org/rfc/rfc3021)
- [Classless Inter-Domain Routing — Wikipedia](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)
- [Subnet — Wikipedia](https://en.wikipedia.org/wiki/Subnet)
- [ipaddress module — Python docs](https://docs.python.org/3/library/ipaddress.html)

- [RFC 3927: IPv4 link-local addressing](https://www.rfc-editor.org/rfc/rfc3927.html)
- [RFC 6598: Shared address space](https://www.rfc-editor.org/rfc/rfc6598.html)
