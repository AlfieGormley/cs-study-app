---
id: ip-ipv6-address-notation
title: IPv6 headers and address notation
level: intermediate
minutes: 3
sourceLesson: ip-nat-ipv6
summary: Read IPv6 address forms and types, then contrast its base header and fragmentation rules with IPv4.
---

Read IPv6 address forms and types, then contrast its base header and fragmentation rules with IPv4.

## IPv6

IPv6 (RFC 8200) is the long-term fix: **128-bit** addresses. Every extra bit doubles the number of possible addresses, so 96 more bits than IPv4 make an enormous difference:

```formula
N_4 = 2^32 ≈ 4.3 × 10^9
N_6 = 2^128 ≈ 3.4 × 10^38
N_6 / N_4 = 2^96 ≈ 7.9 × 10^28
where
N_4: the number of possible IPv4 address values
N_6: the number of possible IPv6 address values
2^32, 2^96, 2^128: 32, 96 or 128 copies of 2 multiplied together
10^9, 10^28, 10^38: 1 followed by 9, 28 or 38 zeros; 10^9 is a billion
≈: approximately equal to (the result is rounded)
In words: IPv4 has about 4.3 billion addresses; IPv6 has about 340 undecillion (34 followed by 37 zeros), roughly 79 thousand trillion trillion times as many.
```

The base header is a fixed 40 bytes with no checksum and no router fragmentation; TTL is renamed **Hop Limit**, and extras go in optional extension headers.

### Writing addresses

Eight groups of four hex digits. Two rules shorten them (RFC 5952 gives the canonical form):

1. Drop leading zeros in each group.
2. Replace the **longest** run of at least two all-zero groups with `::`, once only (if runs tie, the first). RFC 5952 canonical output does not compress a single zero group.

```
2001:0db8:0000:0000:0000:ff00:0042:8329
2001:db8::ff00:42:8329

2001:db8:0:0:1:0:0:1
2001:db8::1:0:0:1
```

### Address types

| Prefix | Type |
|---|---|
| 2000::/3 | Main global-unicast allocation block, including special-use subranges |
| fe80::/10 | Link-local |
| fc00::/7 | Unique local (ULA) |
| ff00::/8 | Multicast |
| ::1/128 | Loopback |

There is no broadcast; multicast groups like `ff02::1` (all nodes on the link) replace it. IPv6 addressing specifies a **link-local** address on each interface, apart from exceptions such as the loopback interface. An interface need not have a global address; multiple addresses are supported. `2001:db8::/32` in these examples is documentation space, not a publicly routed allocation. ULA local generation uses `fd00::/8`; the `fc00::/8` half is not defined for that method.

## Key takeaways
- IPv6 uses 128-bit addresses and a fixed 40-byte base header.
- Canonical notation compresses the first longest run of at least two zero groups.
- IPv6 has multicast rather than broadcast and supports multiple addresses per interface.
- A router drops an oversized IPv6 packet and reports Packet Too Big when permitted.

## Further reading
- [RFC 4787: NAT Behavioral Requirements for Unicast UDP](https://www.rfc-editor.org/rfc/rfc4787)
- [RFC 8445: Interactive Connectivity Establishment (ICE)](https://www.rfc-editor.org/rfc/rfc8445)
- [RFC 8200: IPv6 Specification](https://www.rfc-editor.org/rfc/rfc8200)
- [RFC 4862: IPv6 Stateless Address Autoconfiguration](https://www.rfc-editor.org/rfc/rfc4862)
- [RFC 8305: Happy Eyeballs Version 2](https://www.rfc-editor.org/rfc/rfc8305)
- [Network address translation — Wikipedia](https://en.wikipedia.org/wiki/Network_address_translation)
- [IPv6 adoption statistics — Google](https://www.google.com/intl/en/ipv6/statistics.html)
