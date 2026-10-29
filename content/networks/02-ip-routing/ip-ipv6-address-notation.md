---
id: ip-ipv6-address-notation
title: IPv6 headers and address notation
level: intermediate
minutes: 3
sourceLesson: ip-nat-ipv6
summary: Read IPv6 address forms and types, and contrast its base header and fragmentation rules with IPv4.
---

IPv4's address shortage drove both NAT and IPv6. This lesson covers what is different about IPv6 packets and how to read its much longer addresses.

## IPv6

IPv6 (RFC 8200) is the long-term fix: **128-bit** addresses. Every extra bit doubles the number of possible addresses, so 96 more bits than IPv4 make an enormous difference: about 4.3 billion IPv4 address values against about 340 undecillion (34 followed by 37 zeros) for IPv6. Scarcity of addresses stops being the design constraint; the practical question becomes how to number and route subnets sensibly.

The base header is a fixed 40 bytes with no checksum; TTL is renamed **Hop Limit**, and extras go in optional extension headers.

IPv6 routers **never fragment**. A router that cannot forward a packet because it exceeds the next link's MTU drops it and sends ICMPv6 **Packet Too Big**, carrying that MTU, back to the source (subject to ICMPv6 rate limits). Only the source may fragment, using a Fragment extension header. Every IPv6 link must carry packets of at least 1,280 bytes, so a sender that keeps packets within that size can avoid relying on path MTU feedback.

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
- [RFC 8200: IPv6 Specification](https://www.rfc-editor.org/rfc/rfc8200)
- [RFC 5952: IPv6 Address Text Representation](https://www.rfc-editor.org/rfc/rfc5952)
- [RFC 4291: IPv6 Addressing Architecture](https://www.rfc-editor.org/rfc/rfc4291)
- [IPv6 address — Wikipedia](https://en.wikipedia.org/wiki/IPv6_address)
