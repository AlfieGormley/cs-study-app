---
id: ip-subnet-vlsm-plan
title: Plan VLSM and point-to-point links
level: basic
minutes: 4
sourceLesson: ip-subnetting
summary: Compare configured subnets, allocate aligned blocks and check /31 and /32 exceptions in Python.
---

Compare configured subnets, allocate aligned blocks and check /31 and /32 exceptions in Python.

### Worked example 3: are they on the same subnet?

Host A is `10.0.0.130/25` and host B is `10.0.0.120/25`.

- /25 mask: 255.255.255.128, block size 128. Blocks: 0–127 and 128–255.
- A is in 10.0.0.128/25; B is in 10.0.0.0/25.

They are on **different** numerical subnets. With only connected subnet routes and a suitable gateway route, A sends to B via that gateway, even though the addresses look close. A wrong mask can cause partial connectivity, depending on the available routes and next-hop resolution.

### Worked example 4: carving up a /24 (VLSM)

You have `192.168.1.0/24` and need subnets for 100 hosts, 50 hosts, 20 hosts and two point-to-point router links. **Variable-length subnet masking** (VLSM) gives each subnet the smallest address block (longest prefix) that fits.

To size one subnet, find the fewest host bits whose usable capacity covers the need:

```formula
2^h − 2 ≥ n
2^6 − 2 = 62 < 100
2^7 − 2 = 126 ≥ 100
p = 32 − h = 32 − 7 = 25
where
h: the number of host bits; try 1, 2, 3 … and keep the first that fits
n: the number of hosts the subnet must hold, here 100
2^h: h copies of 2 multiplied together: the number of addresses with h host bits
≥: is at least (greater than or equal to)
<: is less than, so 6 host bits are too few
p: the resulting prefix length
In words: keep adding host bits until the usable addresses (all addresses minus network and broadcast) reach the number you need; the prefix is whatever is left of the 32 bits.
```

Doing that for each need, and starting at the aligned beginning of this unused /24, allocate largest first at the lowest available address:

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
    # Keep the prefix; clear the host bits.
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

`ip.IPv4Interface` accepts an interface address with host bits. By contrast, `ip.ip_network` defaults to strict network parsing: passing `192.168.1.77/26` raises `ValueError`, because the supplied address is not the network start. Use an interface when describing a host, or explicitly pass `strict=False` when clearing host bits is your intent.


## Key takeaways
- Numerically close addresses can belong to different configured subnets.
- Choose the smallest block that meets each conventional host requirement.
- Allocate descending sizes from an unused aligned start to avoid unnecessary alignment gaps.
- An RFC 3021 /31 uses both addresses as endpoints; Python strict network parsing rejects host bits.

## Further reading
- [RFC 4632: Classless Inter-domain Routing (CIDR)](https://www.rfc-editor.org/rfc/rfc4632)
- [RFC 1918: Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918)
- [RFC 3021: Using 31-Bit Prefixes on Point-to-Point Links](https://www.rfc-editor.org/rfc/rfc3021)
- [Classless Inter-Domain Routing — Wikipedia](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)
- [Subnet — Wikipedia](https://en.wikipedia.org/wiki/Subnet)
- [ipaddress module — Python docs](https://docs.python.org/3/library/ipaddress.html)

- [RFC 3927: IPv4 link-local addressing](https://www.rfc-editor.org/rfc/rfc3927.html)
- [RFC 6598: Shared address space](https://www.rfc-editor.org/rfc/rfc6598.html)
