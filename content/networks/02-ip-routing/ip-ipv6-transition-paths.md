---
id: ip-ipv6-transition-paths
title: Dual stack and IPv6 transition
level: intermediate
minutes: 3
sourceLesson: ip-nat-ipv6
summary: Compare staggered connection attempts, NAT64/DNS64 and tunnels, while avoiding IPv6 policy pitfalls.
---

Compare staggered connection attempts, NAT64/DNS64 and tunnels, while avoiding IPv6 policy pitfalls.

### Dual stack and transition

The two protocols aren't wire-compatible: an IPv6-only host can't talk to an IPv4-only host directly. The migration uses:

- **Dual stack**: hosts and networks run both protocol families.
- **Happy Eyeballs** (RFC 8305): clients resolve and order addresses, then stagger connection attempts across candidates instead of waiting for a failed family's full timeout. The recommended default connection-attempt delay is 250 ms, but implementations can adapt it; DNS timing, address ordering and path RTT affect the result. It is not a universal 250 ms page-load guarantee.
- **NAT64 + DNS64** (RFC 6146/6147): a translator can connect IPv6-only clients to IPv4 servers. DNS64 can synthesise AAAA records using a configured translation prefix; `64:ff9b::/96` is the well-known prefix, not the only option. 464XLAT adds client-side translation for IPv4-dependent applications. Reachability and application compatibility still depend on the deployment.

- **Tunnels** (6in4 and others) carry IPv6 over IPv4 links where native IPv6 isn't available.

> [!note] Content omitted after review
> Current IPv6 adoption percentages, client-platform DHCPv6 support, app-store requirements and consumer NAT timeout surveys are omitted because they need versioned or dated evidence not established here. The linked standards define behaviour, not deployment prevalence.

> [!warning] Common IPv6 pitfalls
> - Review IPv6 firewall policy separately: IPv4-only rules do not establish what the IPv6 policy permits or blocks.
> - Blanket ICMPv6 filtering can break neighbour discovery, router advertisements and MTU feedback. Cached/static configuration or probing may mask some failures; ICMPv6 message types need deliberate treatment.
> - Code that stores IPs in 32-bit integers or splits on `:` for ports (`[2001:db8::1]:443` needs brackets).

### Encode a /96 suffix by hand

A /96 prefix leaves 32 bits for the IPv4 suffix. Convert each IPv4 octet into two hexadecimal digits and group adjacent pairs: the documentation address `192.0.2.33` becomes `c000:0221`, so appending its bits to `64:ff9b::/96` gives `64:ff9b::c000:221`. This is only an encoding exercise: RFC 6052 forbids the well-known prefix for IPv4 addresses that are not globally routable, including documentation space. It is not a usable public translation example.


## Key takeaways
- Happy Eyeballs staggers candidates; its 250 ms recommendation is not a page-load guarantee.
- NAT64 and DNS64 can connect IPv6-only clients to IPv4 services within deployment limits.
- IPv6 requires its own firewall policy and appropriate ICMPv6 treatment.
- IPv6 literals containing ports need bracket-aware parsing.

## Further reading
- [RFC 4787: NAT Behavioral Requirements for Unicast UDP](https://www.rfc-editor.org/rfc/rfc4787)
- [RFC 8445: Interactive Connectivity Establishment (ICE)](https://www.rfc-editor.org/rfc/rfc8445)
- [RFC 8200: IPv6 Specification](https://www.rfc-editor.org/rfc/rfc8200)
- [RFC 4862: IPv6 Stateless Address Autoconfiguration](https://www.rfc-editor.org/rfc/rfc4862)
- [RFC 8305: Happy Eyeballs Version 2](https://www.rfc-editor.org/rfc/rfc8305)
- [Network address translation — Wikipedia](https://en.wikipedia.org/wiki/Network_address_translation)
- [IPv6 adoption statistics — Google](https://www.google.com/intl/en/ipv6/statistics.html)
- [RFC 6052: IPv6 addressing of IPv4/IPv6 translators](https://www.rfc-editor.org/rfc/rfc6052)
