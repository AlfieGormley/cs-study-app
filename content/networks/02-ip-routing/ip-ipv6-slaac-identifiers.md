---
id: ip-ipv6-slaac-identifiers
title: SLAAC, prefixes and identifiers
level: intermediate
minutes: 4
sourceLesson: ip-nat-ipv6
summary: Plan subnets from a delegated prefix and trace router advertisements, DAD and interface-identifier privacy choices.
---

IPv6 hosts can configure their own addresses from information routers advertise. This lesson covers the /64 convention that makes that work, the steps a host follows, and why the host part of an address matters for privacy.

### The /64 convention

A global address is typically split 64/64: a **prefix** (routing) and an **interface identifier** (the host). Ethernet SLAAC uses **/64** prefixes. Other uses include /127 point-to-point router links and /128 host routes, so IPv6 routing is not limited to /64. Delegation sizes vary. How many /64 subnets a delegated prefix holds depends on the bits between its length and 64:

```formula reference
S = 2^(64 − p)
where
S: the number of /64 subnets that fit inside the delegated prefix
p: the delegated prefix length, for example 56 for a /56; at most 64. The 64 − p bits between it and the /64 boundary number the subnets
In words: every bit between the delegated prefix and /64 doubles the number of subnets a site can create. A /56 gives 256 /64 subnets and a /48 gives 65,536; a single /64 gives exactly one, which cannot be split further for SLAAC.
```

This matters for planning: a home or office given only a /64 has one SLAAC-capable subnet, so separate guest, IoT and staff networks need a larger delegation such as a /56.

### SLAAC: configuring without a server

**Stateless address autoconfiguration** (RFC 4862) lets a host configure itself:

1. Form a **link-local** address by combining the link-local prefix with an interface identifier.
2. Run **duplicate address detection** (DAD): probe the tentative address with Neighbor Solicitation. A conflicting Advertisement or another host's DAD Solicitation can reveal a duplicate; absence of a reply is not an absolute uniqueness guarantee.
3. Send a **Router Solicitation** to `ff02::2` (all routers).
4. A **Router Advertisement** (RA) may carry prefix information and flags. A usable autonomous prefix must have its A flag set and suitable length/lifetimes. The RA source becomes a default-router candidate only with a nonzero router lifetime; an RA need not advertise a prefix or a default route.
5. The host can form an address from an eligible prefix and interface identifier, then perform DAD. Working routing, neighbour resolution and other configuration are still needed for external connectivity.

One historical interface-identifier method derives it from the MAC (**modified EUI-64**): split the 48-bit MAC in half, insert `ff:fe` between the halves to make 64 bits, and flip the universal/local (**U/L**) bit, worth 0x02, in the first byte. Flipping that bit turns a first byte of 00 into 02, or 3c into 3e; every other byte is copied unchanged.

So `00:1a:2b:3c:4d:5e` becomes `021a:2bff:fe3c:4d5e`. The tell-tale `ff:fe` in the middle makes such identifiers easy to spot. Because the MAC travels with the device, the same identifier appears on every network it joins, letting observers track it across home, office and café. Alternatives include opaque, prefix-dependent **stable identifiers** (RFC 7217) and changing **temporary addresses** (RFC 8981). Which method is enabled depends on the system and configuration; stable identifiers stay the same on one network but change when the prefix changes, and are not freshly randomised for every connection.

RA flags say whether to also use **DHCPv6**: M (managed: get addresses from DHCPv6) and O (other: get options such as DNS from DHCPv6). DNS servers can also be sent in the RA itself (RDNSS). Support for DHCPv6 modes varies across client versions. M/O flags do not force a client to implement a mode, and SLAAC prefix processing is controlled separately by the prefix A flag.

## Key takeaways
- Ethernet SLAAC uses /64 prefixes; routing also supports other lengths.
- Router lifetimes, prefix flags and address lifetimes serve different purposes.
- Modified EUI-64 inserts ff:fe and flips the first byte’s U/L bit.
- Stable opaque and temporary identifiers avoid exposing a MAC-derived identifier; DHCPv6 mode support varies.

## Further reading
- [RFC 4862: IPv6 Stateless Address Autoconfiguration](https://www.rfc-editor.org/rfc/rfc4862)
- [RFC 4291: IPv6 Addressing Architecture](https://www.rfc-editor.org/rfc/rfc4291)
- [RFC 7217: Stable opaque interface identifiers](https://www.rfc-editor.org/rfc/rfc7217)
- [RFC 8981: Temporary addresses](https://www.rfc-editor.org/rfc/rfc8981)
