---
id: ip-subnetting
title: Addressing and subnetting
level: basic
minutes: 15
summary: How IPv4 addresses split into network and host parts, CIDR and subnet masks, calculating network, broadcast and host ranges by hand, private ranges, and route aggregation.
---

An IPv4 address is a 32-bit number. We write it as four bytes in decimal, separated by dots: `192.168.10.77` is `11000000.10101000.00001010.01001101`.

An address together with a prefix length divides into a **network prefix** and remaining **host bits**. The address alone does not tell you the split. An interface can have several addresses, and forwarding tables may contain aggregated prefixes or /32 host routes. Aggregation reduces the need for individual-host entries.

Where the split falls is the whole subject of this lesson.

## From classes to CIDR

Originally the split was fixed by the first bits of the address (**classful** addressing):

| Historical class | First octet bit range | Prefix | Conventional host capacity |
|---|---|---|---|
| A | 0–127 | /8 | 16.7 million |
| B | 128–191 | /16 | 65,534 |
| C | 192–223 | /24 | 254 |

These bit ranges do not make every included network assignable: 0/8 and 127/8 have special meanings. For a single classful network needing 2,000 conventional host addresses, a Class C was insufficient while a Class B left about 97% of its capacity unused. Multiple Class C allocations were another possibility, at the cost of routing entries. CIDR addressed allocation granularity and aggregation.

**Classless Inter-Domain Routing** (CIDR, 1993; now RFC 4632) fixed both problems. The prefix can be **any length** from 0 to 32 bits, written after a slash. `192.168.10.0/26` means "the first 26 bits are the network". Allocations could now match need, and adjacent blocks could be summarised into one route.

## Subnet masks

A **subnet mask** is the same information written as an address: 1-bits for the prefix, 0-bits for the host part.

```
/26 = 11111111.11111111.11111111.11000000
    = 255.255.255.192
```

A contiguous subnet-mask octet can be 0, 128, 192, 224, 240, 248, 252, 254 or 255. Full 255 octets precede at most one partly filled octet; any later octets are 0. Learn this table and subnetting becomes arithmetic:

| Prefix | Mask (last octet) | Block size | Usable hosts |
|---|---|---|---|
| /24 | 0 | 256 | 254 |
| /25 | 128 | 128 | 126 |
| /26 | 192 | 64 | 62 |
| /27 | 224 | 32 | 30 |
| /28 | 240 | 16 | 14 |
| /29 | 248 | 8 | 6 |
| /30 | 252 | 4 | 2 |

The **block size** in the interesting octet is 256 minus the mask value. A /n network contains 2^(32−n) addresses.

To find the network an address belongs to, a host ANDs the address with the mask. With the same configured mask, equal results identify the same numerical subnet. Actual next-hop selection uses routes and policy; a subnet comparison alone does not prove layer 2 connectivity or exclude a more-specific route.

## The recipe

For conventional IPv4 subnets through /30:

1. Find the **interesting octet**: the first mask octet below 255. It can be 0 for a byte-aligned prefix such as /24.
2. **Block size** = 256 − mask value in that octet.
3. **Network address**: round the interesting octet down to a multiple of the block size; octets to the right become 0.
4. **Broadcast address**: network + block size − 1 in that octet; octets to the right become 255.
5. **Usable hosts**: everything strictly between them, so 2^(host bits) − 2.

This conventional capacity excludes all-zero and all-one host fields. /31 point-to-point and /32 uses differ, as explained below. Special address ranges and platform reservations can further reduce assignable addresses; the arithmetic is not an allocation policy.

### Worked example 1: 192.168.10.77/26

- Mask: 255.255.255.192. Interesting octet: the 4th.
- Block size: 256 − 192 = 64. Blocks start at 0, 64, 128, 192.
- 77 falls in the block starting at 64.

```
Network    192.168.10.64
First host 192.168.10.65
Last host  192.168.10.126
Broadcast  192.168.10.127
Hosts      2^6 - 2 = 62
```

### Worked example 2: 172.16.45.200/20

- /20 = 8 + 8 + 4, so the mask is 255.255.240.0. Interesting octet: the 3rd.
- Block size: 256 − 240 = 16. Blocks start at 0, 16, 32, 48 ...
- 45 falls in the block starting at 32 (32 to 47).

```
Network    172.16.32.0
First host 172.16.32.1
Last host  172.16.47.254
Broadcast  172.16.47.255
Hosts      2^12 - 2 = 4,094
```

The 4th octet doesn't matter here: it's entirely host bits, so it's 0 in the network and 255 in the broadcast.

### Worked example 3: are they on the same subnet?

Host A is `10.0.0.130/25` and host B is `10.0.0.120/25`.

- /25 mask: 255.255.255.128, block size 128. Blocks: 0–127 and 128–255.
- A is in 10.0.0.128/25; B is in 10.0.0.0/25.

They are on **different** numerical subnets. With only connected subnet routes and a suitable gateway route, A sends to B via that gateway, even though the addresses look close. A wrong mask can cause partial connectivity, depending on the available routes and next-hop resolution.

### Worked example 4: carving up a /24 (VLSM)

You have `192.168.1.0/24` and need subnets for 100 hosts, 50 hosts, 20 hosts and two point-to-point router links. **Variable-length subnet masking** gives each subnet the smallest address block (longest prefix) that fits. Starting at the aligned beginning of this unused /24, allocate largest first at the lowest available address:

| Need | Prefix | Range |
|---|---|---|
| 100 hosts | /25 (126) | .0 – .127 |
| 50 hosts | /26 (62) | .128 – .191 |
| 20 hosts | /27 (30) | .192 – .223 |
| link | /30 (2) | .224 – .227 |
| link | /30 (2) | .228 – .231 |

That leaves .232 – .255 free for later. Placing small subnets first can leave alignment gaps before later large blocks; the exact result depends on placement.

> [!tip] /31 and /32
> A /30 wastes half its four addresses on network and broadcast. On point-to-point links, RFC 3021 allows a **/31**: both addresses are endpoint addresses, with no directed broadcast. Limited broadcast (255.255.255.255) remains available. A **/32** names a single host and is used for loopback addresses and host routes.

### Let Python check you

```python
import ipaddress as ip

def describe(cidr):
    net = ip.IPv4Interface(cidr).network
    count = net.num_addresses
    usable = count
    if net.prefixlen < 31:
        usable -= 2
    return (net, net.netmask,
            net.broadcast_address,
            usable)

print(describe("172.16.45.200/20"))
# (IPv4Network('172.16.32.0/20'),
#  IPv4Address('255.255.240.0'),
#  IPv4Address('172.16.47.255'), 4094)
```

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

## Supernetting and route aggregation

CIDR's other half is **aggregation** (also called **supernetting** or **summarisation**): advertising several contiguous networks as one shorter prefix.

Suppose an ISP has customers on `200.10.0.0/24`, `200.10.1.0/24`, `200.10.2.0/24` and `200.10.3.0/24`. Write the third octets in binary:

```
0 = 000000|00
1 = 000000|01
2 = 000000|10
3 = 000000|11
```

The first 22 bits match (16 from the first two octets, 6 here), so the ISP advertises one route: **200.10.0.0/22**. The rest of the Internet needs one entry instead of four.

Aggregation requires **alignment**. The block must start on a multiple of its size. `200.10.1.0` to `200.10.4.0` is also four /24s, but no single /22 covers exactly them. The best summary is `200.10.1.0/24`, `200.10.2.0/23` and `200.10.4.0/24`:

```python
nets = [ip.ip_network(f"200.10.{i}.0/24")
        for i in range(1, 5)]
print(list(ip.collapse_addresses(nets)))
# [200.10.1.0/24, 200.10.2.0/23,
#  200.10.4.0/24]  (reprs shortened)
```

Aggregation reduces entries advertised to other networks, saving routing/forwarding state. How a router stores control-plane and forwarding tables is implementation-dependent. A maintained aggregate can hide a component route's changes from upstream peers, depending on advertisement policy.

The catch is that a summary can attract traffic for addresses that don't exist, or that live elsewhere. A more-specific route wins by **longest-prefix match**, but only if it exists. An aggregate can still attract traffic for unavailable destinations. The advertising router needs appropriate component routes and discard handling for unmatched portions to avoid forwarding loops.

## Address exhaustion

IPv4 has 2³² possible address values, and special-purpose ranges reduce the pool available for globally unique assignments. Address sharing, transfers and allocation policies address scarcity in different ways; IPv6 provides a much larger address space.

> [!note] Content omitted after review
> Current global route counts, address-market prices and a regional exhaustion/allocation timeline are absent because they require dated measurements and registry-policy evidence not established in this lesson. No universal purchase price or route-memory design is assumed.

## Key takeaways
- An IPv4 address is a 32-bit number split into a network prefix and a host part; CIDR lets that split fall at any bit.
- Block size = 256 − mask value in the interesting octet; round down to find the network, add block − 1 for the broadcast.
- Usable hosts = 2^(host bits) − 2, except /31 links (2 usable) and /32 host routes.
- For an initially empty aligned block, allocating descending block sizes from its start is a straightforward way to preserve alignment.
- RFC 1918 space is private; 100.64/10 is distinct shared space for CGN; 169.254/16 is link-local and does not itself diagnose DHCP failure.
- Aggregation merges aligned, contiguous prefixes into one shorter route, keeping routing tables small.

## Further reading
- [RFC 4632: Classless Inter-domain Routing (CIDR)](https://www.rfc-editor.org/rfc/rfc4632)
- [RFC 1918: Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918)
- [RFC 3021: Using 31-Bit Prefixes on Point-to-Point Links](https://www.rfc-editor.org/rfc/rfc3021)
- [Classless Inter-Domain Routing — Wikipedia](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)
- [Subnet — Wikipedia](https://en.wikipedia.org/wiki/Subnet)
- [ipaddress module — Python docs](https://docs.python.org/3/library/ipaddress.html)

- [RFC 3927: IPv4 link-local addressing](https://www.rfc-editor.org/rfc/rfc3927.html)
- [RFC 6598: Shared address space](https://www.rfc-editor.org/rfc/rfc6598.html)
