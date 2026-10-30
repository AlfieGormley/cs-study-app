---
id: nsec-tunnel-byte-budgets
title: Tunnels and inner packet budgets
level: advanced
minutes: 4
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

Because the outer packet still has to fit the link, every byte the tunnel adds comes out of the room left for the packet inside:

```formula essential
MTU_inner = MTU_link − H_total
where
MTU_inner: the largest inner IP packet that fits without fragmentation, in bytes
MTU_link: the maximum transmission unit (MTU) of the underlying link or path, in bytes; usually 1,500 for Ethernet
H_total: the total of every header and trailer the tunnel adds, in bytes
In words: whatever the tunnel adds is subtracted from the space available for the packet inside.
```

For three common tunnels on a 1,500-byte link, with the header sizes listed:

| Tunnel | Added bytes | Inner budget |
|---|---|---|
| GRE over IPv4 | IPv4 20 + GRE 4 = 24 | 1,476 |
| WireGuard over IPv6 | IPv6 40 + UDP 8 + WireGuard 32 = 80 | 1,420 |
| VXLAN over IPv4 | IPv4 20 + UDP 8 + VXLAN 8 + inner Ethernet 14 = 50 | 1,450 |

WireGuard's 32 bytes are a 16-byte data header and a 16-byte authentication tag. VXLAN counts the inner Ethernet header because it carries whole Ethernet frames. These are inner IP budgets for these exact header assumptions (basic GRE, no options, untagged VXLAN), not universal interface defaults. Options, VLAN tags, extra tunnels and a smaller path MTU all shrink the budget; WireGuard's padding is bounded so it does not exceed the selected MTU.

What goes wrong when the budget is ignored? Hosts inside keep sending 1,500-byte packets, which no longer fit once wrapped. Depending on the tunnel and the Don't Fragment setting, they are fragmented (slower and fragile) or dropped with an error that must reach the sender. The next unit diagnoses that failure.

## GRE: a plain tunnel

**GRE** (Generic Routing Encapsulation, IP protocol 47) has a 4-byte base header, with optional fields adding overhead, and can encapsulate different payload protocols. It is simple and widely supported by routers, and it gives **no confidentiality or authentication at all**. Anyone on the path can read it, and forged traffic may be accepted if it reaches an endpoint without effective filtering or other validation. GRE is therefore often run *inside* IPsec when routing protocols need a tunnel interface.

## Key takeaways
- Plain encapsulation provides reachability without proving confidentiality or authenticity.
- Every byte a tunnel adds comes out of the inner packet budget.
- Header models and padding rules matter more than a memorised tunnel default.

## Further reading
- [RFC 4459: MTU and Fragmentation Issues with In-the-Network Tunneling](https://www.rfc-editor.org/rfc/rfc4459)
- [RFC 2784: Generic Routing Encapsulation (GRE)](https://www.rfc-editor.org/rfc/rfc2784)
- [WireGuard: protocol and cryptography](https://www.wireguard.com/protocol/)
- [RFC 7348: Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348)
