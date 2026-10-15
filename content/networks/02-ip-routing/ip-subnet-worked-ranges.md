---
id: ip-subnet-worked-ranges
title: Calculate IPv4 subnet ranges
level: basic
minutes: 5
sourceLesson: ip-subnetting
summary: Find the network, broadcast and conventional host range in both byte-aligned and partial-octet examples.
---

Find the network, broadcast and conventional host range in both byte-aligned and partial-octet examples.

## The recipe

For conventional IPv4 subnets through /30:

1. Find the **interesting octet**: the first mask octet below 255. It can be 0 for a byte-aligned prefix such as /24.
2. **Block size**: 256 minus the mask value in that octet.
3. **Network address**: round the interesting octet down to a multiple of the block size; octets to the right become 0.
4. **Broadcast address**: the network's value in that octet, plus the block size, minus 1; octets to the right become 255.
5. **Usable hosts**: everything strictly between them.

The same steps as arithmetic:

```formula
b = 256 − m
x_net = ⌊x / b⌋ × b
x_bc = x_net + b − 1
H = 2^h − 2
where
b: the block size: how many values one subnet spans in the interesting octet
m: the subnet mask's value in the interesting octet, for example 192 for a /26
x: the address's value in the interesting octet, for example 77 in 192.168.10.77
⌊ ⌋: floor: round down to a whole number, so ⌊77 / 64⌋ = ⌊1.2⌋ = 1
x_net: the network address's value in the interesting octet
x_bc: the broadcast address's value in the interesting octet
H: the number of usable host addresses
h: the number of host bits, 32 minus the prefix length
2^h: h copies of 2 multiplied together: the total number of addresses in the subnet
In words: the mask tells you the block size; the address rounded down to a whole number of blocks is the network; the last value in that block is the broadcast; and the usable hosts are all the addresses minus those two.
```

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

The calculation behind those lines:

```formula
x_net = ⌊77 / 64⌋ × 64 = 1 × 64 = 64
x_bc = 64 + 64 − 1 = 127
h = 32 − 26 = 6
H = 2^6 − 2 = 64 − 2 = 62
where
x_net: the network address's value in the 4th octet
⌊ ⌋: floor: round down to a whole number
x_bc: the broadcast address's value in the 4th octet
h: the number of host bits for a /26
H: the number of usable host addresses
2^6: 6 copies of 2 multiplied together, 64
In words: 77 lies in the second 64-wide block, which runs from 64 to 127. Of its 64 addresses, 62 are usable once the network and broadcast addresses are set aside.
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

```formula
x_net = ⌊45 / 16⌋ × 16 = 2 × 16 = 32
x_bc = 32 + 16 − 1 = 47
h = 32 − 20 = 12
H = 2^12 − 2 = 4,096 − 2 = 4,094
where
x_net: the network address's value in the 3rd (interesting) octet
⌊ ⌋: floor: round down to a whole number
x_bc: the broadcast address's value in the 3rd octet
h: the number of host bits for a /20: the last 4 bits of the 3rd octet plus all 8 of the 4th
H: the number of usable host addresses
2^12: 12 copies of 2 multiplied together, 4,096
In words: 45 lies in the block from 32 to 47 of the third octet. Twelve host bits give 4,096 addresses, 4,094 of them usable.
```

The 4th octet doesn't matter here: it's entirely host bits, so it's 0 in the network and 255 in the broadcast.

## Key takeaways
- Find the first mask octet below 255 and use its block size.
- Round that address octet down to the aligned block start.
- Fill later octets with zero for the network and 255 for the broadcast; /31 and /32 require different treatment.

## Further reading
- [RFC 4632: Classless Inter-domain Routing (CIDR)](https://www.rfc-editor.org/rfc/rfc4632)
- [RFC 1918: Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918)
- [RFC 3021: Using 31-Bit Prefixes on Point-to-Point Links](https://www.rfc-editor.org/rfc/rfc3021)
- [Classless Inter-Domain Routing — Wikipedia](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)
- [Subnet — Wikipedia](https://en.wikipedia.org/wiki/Subnet)
- [ipaddress module — Python docs](https://docs.python.org/3/library/ipaddress.html)

- [RFC 3927: IPv4 link-local addressing](https://www.rfc-editor.org/rfc/rfc3927.html)
- [RFC 6598: Shared address space](https://www.rfc-editor.org/rfc/rfc6598.html)
