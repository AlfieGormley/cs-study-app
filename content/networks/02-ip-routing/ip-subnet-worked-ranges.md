---
id: ip-subnet-worked-ranges
title: Recognise IPv4 subnet boundaries
level: basic
minutes: 4
sourceLesson: ip-subnetting
summary: Find where a subnet starts and ends, and use those boundaries to predict which addresses are on-link or reserved.
---

Knowing where a subnet starts and ends lets you predict whether two hosts can talk directly, and spot an address that should never be assigned. A calculator or Python's `ipaddress` module will do the arithmetic; the point here is to recognise the boundaries.

## The recipe

For conventional IPv4 subnets through /30:

1. Find the **interesting octet**: the first mask octet below 255. It can be 0 for a byte-aligned prefix such as /24.
2. **Block size**: 256 minus the mask value in that octet.
3. **Network address**: round the interesting octet down to a multiple of the block size; octets to the right become 0.
4. **Broadcast address**: the network's value in that octet, plus the block size, minus 1; octets to the right become 255.
5. **Usable hosts**: everything strictly between them.

Subnets of one size tile the address space in aligned blocks, like rulers laid end to end: a /26 block always starts at .0, .64, .128 or .192, never at .50.

This conventional capacity excludes all-zero and all-one host fields. On an RFC 3021 point-to-point /31, both addresses are endpoints; a /32 names one address. The next unit examines those exceptions. Special address ranges and platform reservations can further reduce assignable addresses; the arithmetic is not an allocation policy.

### Worked example 1: 192.168.10.77/26

- Mask: 255.255.255.192. Interesting octet: the 4th.
- Block size: 256 − 192 = 64. Blocks start at 0, 64, 128, 192.
- 77 falls in the block starting at 64.

```
Network    192.168.10.64
First host 192.168.10.65
Last host  192.168.10.126
Broadcast  192.168.10.127
Hosts      62
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
Hosts      4,094
```

The 4th octet doesn't matter here: it's entirely host bits, so it's 0 in the network and 255 in the broadcast.

That has a practical consequence. Inside this /20, addresses such as 172.16.33.0 and 172.16.40.255 are ordinary host addresses: they end in .0 or .255, but they are neither the first nor the last address of the block. Only 172.16.32.0 and 172.16.47.255 are reserved.

## Using the boundaries

- **Same subnet or not?** Two hosts with the same mask are on the same subnet only if both fall inside one block. 192.168.10.77/26 and 192.168.10.130/26 look close but sit in different blocks (.64–.127 and .128–.191), so with only connected routes and a default gateway, each sends to its gateway rather than directly.
- **Assignable or not?** Within a conventional subnet up to /30, only the first (network) and last (broadcast) addresses are reserved. An address outside the block cannot be used on that subnet at all.

## Key takeaways
- Find the first mask octet below 255 and use its block size.
- Round that address octet down to the aligned block start.
- Fill later octets with zero for the network and 255 for the broadcast; /31 and /32 require different treatment.
- In blocks larger than /24, addresses ending .0 or .255 can be ordinary hosts; only the block's first and last addresses are reserved.

## Further reading
- [RFC 4632: Classless Inter-domain Routing (CIDR)](https://www.rfc-editor.org/rfc/rfc4632)
- [RFC 3021: Using 31-Bit Prefixes on Point-to-Point Links](https://www.rfc-editor.org/rfc/rfc3021)
- [Subnet — Wikipedia](https://en.wikipedia.org/wiki/Subnet)
- [ipaddress module — Python docs](https://docs.python.org/3/library/ipaddress.html)
