---
id: ip-subnet-prefix-mask
title: Prefixes, masks and address counts
level: basic
minutes: 4
sourceLesson: ip-subnetting
summary: Translate between a CIDR prefix, a contiguous mask and an IPv4 address count.
---

An IPv4 address is a 32-bit number. We write it as four bytes in decimal, separated by dots: `192.168.10.77` is `11000000.10101000.00001010.01001101`.

An address together with a prefix length divides into a **network prefix** and remaining **host bits**. The address alone does not tell you the split. An interface can have several addresses, and forwarding tables may contain aggregated prefixes or /32 host routes. Aggregation reduces the need for individual-host entries.

Where the split falls is the whole subject of this lesson.

> [!analogy] Real-world analogy: Street name and house number
> A postal address has a street part, which gets the letter to the right road, and a house number, which picks one door on it. Everyone on the same street shares the street part.
>
> **How it maps:** The network prefix is the street: routers use it to deliver to the right network. The host bits are the house number within it. Hosts that share a prefix are on the same "street" and normally deliver to each other directly, without a router.
>
> **Where it stops:** On a letter you can see where the street name ends. In IPv4 the boundary is invisible in the address itself; the prefix length or mask tells you where it falls, and it can sit in the middle of an octet. Moving the boundary by one bit halves or doubles every "street".

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

A contiguous subnet-mask octet can be 0, 128, 192, 224, 240, 248, 252, 254 or 255. Full 255 octets precede at most one partly filled octet; any later octets are 0. You do not need to memorise every row; the pattern matters more. Each step down the table adds one prefix bit and halves the block:

| Prefix | Mask (last octet) | Block size | Usable hosts |
|---|---|---|---|
| /24 | 0 | 256 | 254 |
| /25 | 128 | 128 | 126 |
| /26 | 192 | 64 | 62 |
| /27 | 224 | 32 | 30 |
| /28 | 240 | 16 | 14 |
| /29 | 248 | 8 | 6 |
| /30 | 252 | 4 | 2 |

The **block size** in the interesting octet is 256 minus the mask value. The relationship underneath the whole table is that every host bit doubles the number of addresses, so each extra prefix bit halves the block:

```formula essential
N = 2^(32 − p)
where
N: the number of addresses in the network, including the network and broadcast addresses
p: the prefix length, the number after the slash (/26 means p is 26); a whole number from 0 to 32. The remaining 32 − p bits are host bits, and the power of 2 doubles the count once per host bit
In words: a longer prefix leaves fewer host bits and a smaller block. A /26 has 64 addresses, a /25 twice as many (128), a /27 half as many (32), and a /20 has 4,096.
```

Notice the direction: a **bigger** prefix number means a **smaller** network. A /28 is smaller than a /24, not larger.

For conventional IPv4 subnets through /30, reserve the all-zero host pattern as the network address and the all-one pattern as directed broadcast. Subtracting those two gives the conventional usable-host capacity; special-purpose ranges and provider reservations can reduce assignability further. A /28 therefore has 16 addresses and conventionally 14 usable. Point-to-point /31s and single-address /32s follow different rules, taught in the VLSM unit.

To find the network an address belongs to, a host ANDs the address with the mask. With the same configured mask, equal results identify the same numerical subnet. Actual next-hop selection uses routes and policy; a subnet comparison alone does not prove layer 2 connectivity or exclude a more-specific route.

## Key takeaways
- An address alone does not identify its prefix length.
- CIDR permits any IPv4 prefix length from zero through 32.
- Each added prefix bit halves the address block; conventional host capacity reserves two addresses.

## Further reading
- [RFC 4632: Classless Inter-domain Routing (CIDR)](https://www.rfc-editor.org/rfc/rfc4632)
- [RFC 1918: Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918)
- [RFC 3021: Using 31-Bit Prefixes on Point-to-Point Links](https://www.rfc-editor.org/rfc/rfc3021)
- [Classless Inter-Domain Routing — Wikipedia](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)
- [Subnet — Wikipedia](https://en.wikipedia.org/wiki/Subnet)
- [ipaddress module — Python docs](https://docs.python.org/3/library/ipaddress.html)

- [RFC 3927: IPv4 link-local addressing](https://www.rfc-editor.org/rfc/rfc3927.html)
- [RFC 6598: Shared address space](https://www.rfc-editor.org/rfc/rfc6598.html)
