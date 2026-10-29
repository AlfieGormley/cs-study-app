---
id: ip-ipv6-transition-paths
title: Dual stack and IPv6 transition
level: intermediate
minutes: 3
sourceLesson: ip-nat-ipv6
summary: Explain staggered connection attempts, how NAT64/DNS64 reach IPv4-only servers, and common IPv6 policy pitfalls.
---

IPv4 and IPv6 will run side by side for a long time. This lesson covers how clients choose between them and how IPv6-only networks still reach IPv4-only services.

### Dual stack and transition

The two protocols aren't wire-compatible: an IPv6-only host can't talk to an IPv4-only host directly. The migration uses:

- **Dual stack**: hosts and networks run both protocol families.
- **Happy Eyeballs** (RFC 8305): clients resolve and order addresses, then stagger connection attempts across candidates instead of waiting for a failed family's full timeout. The recommended default connection-attempt delay is 250 ms, but implementations can adapt it; DNS timing, address ordering and path RTT affect the result. It is not a universal 250 ms page-load guarantee.
- **NAT64 + DNS64** (RFC 6146/6147): a translator can connect IPv6-only clients to IPv4 servers. DNS64 can synthesise AAAA records using a configured translation prefix; `64:ff9b::/96` is the well-known prefix, not the only option. 464XLAT adds a translator on the client device for IPv4-dependent applications. Reachability and application compatibility still depend on the deployment.
- **Tunnels** (6in4 and others) carry IPv6 over IPv4 links where native IPv6 isn't available.

How a NAT64 connection works, step by step:

1. An IPv6-only phone asks its DNS64 resolver for the AAAA record of an IPv4-only site.
2. Finding no real AAAA record, DNS64 takes the site's A record and synthesises an IPv6 address by placing the 32-bit IPv4 address inside the NAT64 prefix (with the well-known /96 prefix, it fills the last 32 bits).
3. The phone sends ordinary IPv6 packets to that synthesised address. They are routed to the NAT64 translator.
4. The translator extracts the embedded IPv4 address, translates the packet to IPv4 using one of its own shared public IPv4 addresses, and keeps per-connection state so replies can be translated back, much like NAPT.

The IPv4 server sees an ordinary IPv4 client. Applications that skip DNS and use an IPv4 literal address, or open IPv4-only sockets, never get a synthesised address; 464XLAT handles those with a translation layer on the client.

> [!note] Content omitted after review
> Current IPv6 adoption percentages, client-platform DHCPv6 support, app-store requirements and consumer NAT timeout surveys are omitted because they need versioned or dated evidence not established here. The linked standards define behaviour, not deployment prevalence.

> [!warning] Common IPv6 pitfalls
> - Review IPv6 firewall policy separately: IPv4-only rules do not establish what the IPv6 policy permits or blocks.
> - Blanket ICMPv6 filtering can break neighbour discovery, router advertisements and MTU feedback. Cached/static configuration or probing may mask some failures; ICMPv6 message types need deliberate treatment.
> - Code that stores IPs in 32-bit integers or splits on `:` for ports (`[2001:db8::1]:443` needs brackets).

## Key takeaways
- Happy Eyeballs staggers candidates; its 250 ms recommendation is not a page-load guarantee.
- DNS64 embeds an IPv4 address in a synthesised IPv6 address; a stateful NAT64 translator turns that traffic into IPv4.
- IPv4 literals bypass DNS64 and need translation on the client device, such as 464XLAT.
- IPv6 requires its own firewall policy and appropriate ICMPv6 treatment.
- IPv6 literals containing ports need bracket-aware parsing.

## Further reading
- [RFC 8305: Happy Eyeballs Version 2](https://www.rfc-editor.org/rfc/rfc8305)
- [RFC 6146: Stateful NAT64](https://www.rfc-editor.org/rfc/rfc6146)
- [RFC 6147: DNS64](https://www.rfc-editor.org/rfc/rfc6147)
- [RFC 6052: IPv6 addressing of IPv4/IPv6 translators](https://www.rfc-editor.org/rfc/rfc6052)
- [RFC 6877: 464XLAT](https://www.rfc-editor.org/rfc/rfc6877)
