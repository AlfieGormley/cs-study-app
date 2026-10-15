---
id: nsec-tunnel-byte-budgets
title: Tunnels and inner packet budgets
level: advanced
minutes: 5
summary: Plain encapsulation provides reachability without proving confidentiality or authenticity.
sourceLesson: nsec-vpns
---

A **tunnel** carries packets of one network as the payload of packets on another. Wrap a packet addressed to `10.20.0.5` inside a packet addressed to your office's public IP, send it across the internet, unwrap it at the far end, and the office network sees what looks like a local packet.

Tunnels on their own provide reachability, not security. Here, **VPN** means a cryptographically protected IP tunnel: it authenticates the two ends, and encrypts and integrity-protects what flows between them. The tunnel units cover the plain tunnels (GRE, VXLAN), two examples of protected VPN protocols (IPsec and WireGuard), and the practical problem they all share: overhead and MTU.

## Encapsulation and the MTU tax

Every tunnel adds headers. The physical link's MTU (usually 1,500 bytes for Ethernet) does not change, so the inner packet must shrink:

```
 outer packet on the wire (<= 1500)
+--------+-------+-----+---------------+
| outer  | UDP   | tun | inner packet  |
| IP hdr | (opt) | hdr | (size budget) |
+--------+-------+-----+---------------+
```

Because the outer packet still has to fit the link, the room left for the inner packet is the link MTU minus every header the tunnel adds:

```formula
MTU_inner = MTU_link − H_total
H_total = H_1 + H_2 + … + H_k
where
MTU_inner: the largest inner IP packet that fits without fragmentation, in bytes
MTU_link: the maximum transmission unit (MTU) of the underlying link or path, in bytes; usually 1,500 for Ethernet
H_total: the total overhead the tunnel adds, in bytes
H_1: the size of the first added header, in bytes (for example, an outer IPv4 header, 20 bytes)
H_2: the size of the second added header, in bytes
H_k: the size of the last added header, in bytes
k: the number of headers the tunnel adds
…: and so on, for every header in between
In words: every byte of tunnel header comes straight out of the space available for the packet inside.
```

Applying it to three common tunnels, with the header sizes used in the code below:

```formula
M_GRE = 1500 − (20 + 4) = 1476 B
M_WG = 1500 − (40 + 8 + 32) = 1420 B
M_VX = 1500 − (20 + 8 + 8 + 14)
M_VX = 1500 − 50 = 1450 B
where
M_GRE: inner MTU for GRE over IPv4: a 20-byte outer IPv4 header plus a 4-byte basic GRE header
M_WG: inner MTU for WireGuard over IPv6: a 40-byte outer IPv6 header, an 8-byte UDP header, and 32 bytes of WireGuard data overhead (a 16-byte header plus a 16-byte authentication tag)
M_VX: inner MTU for VXLAN over IPv4: outer IPv4 (20), UDP (8), the VXLAN header (8) and the inner Ethernet header it carries (14)
B: bytes
In words: on a 1,500-byte link, these tunnels leave 1,476, 1,420 and 1,450 bytes for the inner IP packet.
```

The same arithmetic as code, with a header-size table you can extend:

```python
HDR = {"ipv4": 20, "ipv6": 40, "udp": 8,
       "wg": 32, "vxlan": 8, "eth": 14,
       "gre": 4}

def inner_mtu(link_mtu, *layers):
    if type(link_mtu) is not int:
        raise TypeError("integer MTU")
    # Count only the named added layers.
    used = sum(HDR[x] for x in layers)
    if link_mtu <= used:
        raise ValueError("no capacity")
    # Space left for the inner packet.
    return link_mtu - used

# GRE, WireGuard and VXLAN byte budgets.
print(inner_mtu(1500, "ipv4", "gre"))
print(inner_mtu(1500, "ipv6", "udp", "wg"))
print(inner_mtu(1500, "ipv4", "udp",
                "vxlan", "eth"))
```

This prints `1476`, `1420` and `1450`: inner IP size budgets for these exact header assumptions: basic GRE over IPv4, WireGuard over IPv6, and untagged VXLAN over IPv4. They are not universal interface defaults. Options, VLAN tags, extra tunnels and path MTU change the budget; WireGuard padding is bounded so it does not exceed the selected MTU.

## GRE: a plain tunnel

**GRE** (Generic Routing Encapsulation, IP protocol 47) has a 4-byte base header, with optional fields adding overhead, and can encapsulate different payload protocols. It is simple and widely supported by routers, and it gives **no confidentiality or authentication at all**. Anyone on the path can read it, and forged traffic may be accepted if it reaches an endpoint without effective filtering or other validation. GRE is therefore often run *inside* IPsec when routing protocols need a tunnel interface.

## Key takeaways
- Plain encapsulation provides reachability without proving confidentiality or authenticity.
- Subtract every added byte from the underlay IP MTU to obtain the inner budget.
- Header models and padding rules matter more than a memorised tunnel default.

## Further reading
- [RFC 4301: Security Architecture for the Internet Protocol](https://www.rfc-editor.org/rfc/rfc4301)
- [RFC 4303: IP Encapsulating Security Payload (ESP)](https://www.rfc-editor.org/rfc/rfc4303)
- [WireGuard: Next Generation Kernel Network Tunnel (whitepaper)](https://www.wireguard.com/papers/wireguard.pdf)
- [WireGuard: protocol and cryptography](https://www.wireguard.com/protocol/)
- [RFC 7348: Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348)
- [RFC 4459: MTU and Fragmentation Issues with In-the-Network Tunneling](https://www.rfc-editor.org/rfc/rfc4459)
