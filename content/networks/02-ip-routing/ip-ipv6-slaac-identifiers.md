---
id: ip-ipv6-slaac-identifiers
title: SLAAC, prefixes and identifiers
level: intermediate
minutes: 4
sourceLesson: ip-nat-ipv6
summary: Count delegated /64 subnets and trace router advertisements, DAD and interface-identifier choices.
---

Count delegated /64 subnets and trace router advertisements, DAD and interface-identifier choices.

### The /64 convention

A global address is typically split 64/64: a **prefix** (routing) and an **interface identifier** (the host). Ethernet SLAAC uses **/64** prefixes. Other uses include /127 point-to-point router links and /128 host routes, so IPv6 routing is not limited to /64. Delegation sizes vary. How many /64 subnets a delegated prefix holds depends on the bits between its length and 64:

```formula
S = 2^(64 − p)
S = 2^(64 − 56) = 2^8 = 256
S = 2^(64 − 48) = 2^16 = 65,536
where
S: the number of /64 subnets that fit inside the delegated prefix
p: the delegated prefix length, for example 56 for a /56; at most 64
2^8, 2^16: 8 or 16 copies of 2 multiplied together
In words: the bits between the delegated prefix and the /64 boundary number the subnets; 8 such bits give 256 subnets and 16 give 65,536.
```

### SLAAC: configuring without a server

**Stateless address autoconfiguration** (RFC 4862) lets a host configure itself:

1. Form a **link-local** address by combining the link-local prefix with an interface identifier.
2. Run **duplicate address detection** (DAD): probe the tentative address with Neighbor Solicitation. A conflicting Advertisement or another host's DAD Solicitation can reveal a duplicate; absence of a reply is not an absolute uniqueness guarantee.
3. Send a **Router Solicitation** to `ff02::2` (all routers).
4. A **Router Advertisement** (RA) may carry prefix information and flags. A usable autonomous prefix must have its A flag set and suitable length/lifetimes. The RA source becomes a default-router candidate only with a nonzero router lifetime; an RA need not advertise a prefix or a default route.
5. The host can form an address from an eligible prefix and interface identifier, then perform DAD. Working routing, neighbour resolution and other configuration are still needed for external connectivity.

One historical interface-identifier method derives it from the MAC (**modified EUI-64**): split the 48-bit MAC in half, insert `ff:fe` between the halves to make 64 bits, and flip the universal/local (**U/L**) bit, worth 0x02, in the first byte. Flipping one bit is an exclusive-or:

```formula
y = x XOR 0x02
y = 0x00 XOR 0x02 = 0x02
y = 0x3c XOR 0x02 = 0x3e
where
x: the first byte of the MAC address, written in hexadecimal (0x prefix: base 16, digits 0–9 and a–f)
y: the first byte of the interface identifier
XOR: exclusive or: compare two values bit by bit; each result bit is 1 when the two bits differ, so XOR with 0x02 flips only the second-lowest bit
In words: the first byte is copied with just its U/L bit flipped: 00 becomes 02 and 3c becomes 3e. Every other byte is copied unchanged.
```

So `00:1a:2b:3c:4d:5e` becomes `021a:2bff:fe3c:4d5e`. That leaks a stable hardware ID everywhere you go, so alternatives include opaque, prefix-dependent **stable identifiers** (RFC 7217) and changing **temporary addresses** (RFC 8981). Which method is enabled depends on the system and configuration; stable identifiers are not freshly randomised for every connection.

RA flags say whether to also use **DHCPv6**: M (managed: get addresses from DHCPv6) and O (other: get options such as DNS from DHCPv6). DNS servers can also be sent in the RA itself (RDNSS). Support for DHCPv6 modes varies across client versions. M/O flags do not force a client to implement a mode, and SLAAC prefix processing is controlled separately by the prefix A flag.

## Key takeaways
- Ethernet SLAAC uses /64 prefixes; routing also supports other lengths.
- Router lifetimes, prefix flags and address lifetimes serve different purposes.
- Modified EUI-64 inserts ff:fe and flips the first byte’s U/L bit.
- Stable opaque and temporary identifiers avoid exposing a MAC-derived identifier; DHCPv6 mode support varies.

## Further reading
- [RFC 4787: NAT Behavioral Requirements for Unicast UDP](https://www.rfc-editor.org/rfc/rfc4787)
- [RFC 8445: Interactive Connectivity Establishment (ICE)](https://www.rfc-editor.org/rfc/rfc8445)
- [RFC 8200: IPv6 Specification](https://www.rfc-editor.org/rfc/rfc8200)
- [RFC 4862: IPv6 Stateless Address Autoconfiguration](https://www.rfc-editor.org/rfc/rfc4862)
- [RFC 8305: Happy Eyeballs Version 2](https://www.rfc-editor.org/rfc/rfc8305)
- [Network address translation — Wikipedia](https://en.wikipedia.org/wiki/Network_address_translation)
- [IPv6 adoption statistics — Google](https://www.google.com/intl/en/ipv6/statistics.html)
