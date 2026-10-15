---
id: nsec-vxlan-isolation
title: VXLAN scale and underlay trust
level: advanced
minutes: 3
summary: A VXLAN VNI names an overlay network; it is not an authentication credential.
sourceLesson: nsec-vpns
---

Cloud overlays need many separate layer 2 networks. VXLAN supplies the identifier space and transport, while operators must supply the security boundary around tunnel endpoints.

## VXLAN and overlays

Data centres and clouds need far more isolated layer 2 segments than VLANs allow. **VXLAN** (RFC 7348) carries whole Ethernet frames in UDP (port 4789), with a 24-bit **VNI** (VXLAN network identifier). The number of network segments an ID field can name doubles with every bit:

```formula
N_VLAN = 2^12 − 2 = 4094
N_VNI = 2^24 = 16777216
where
N_VLAN: usable VLAN IDs: a 12-bit field holds 2^12 (12 copies of 2 multiplied together) = 4,096 values, and IDs 0 and 4095 are reserved
N_VNI: possible VXLAN network identifiers in a 24-bit field: 24 copies of 2 multiplied together
In words: a 12-bit VLAN ID allows about four thousand network segments, while VXLAN's 24-bit VNI allows about 16.8 million.
```

The VXLAN encapsulation looks like this:

```
[outer Eth][outer IP][UDP 4789][VXLAN]
  14         20        8         8
[inner Eth frame ...]
```

For the inner IP budget, subtract outer IPv4 (20), UDP (8), VXLAN (8), and inner Ethernet (14): 50 bytes, leaving a 1,450-byte inner IP budget on this 1,500-byte underlay, as calculated in the earlier tunnel budget unit. The outer Ethernet header shown above is outside the underlay IP MTU. Under these assumptions, either the underlay MTU is raised (data centres often run 9,000-byte jumbo frames) or the overlay MTU drops to 1,450. The devices that wrap and unwrap are **VTEPs**, usually hypervisors or top-of-rack switches. Fabrics can use **BGP EVPN** to distribute MAC address reachability, reducing flood-based learning; broadcast, unknown-unicast and multicast handling may still involve copying packets or flooding. **Geneve** (RFC 8926, UDP 6081) is a more extensible successor, used for example by AWS Gateway Load Balancer.

> [!warning] VXLAN has no security
> VXLAN has no authentication and no encryption; RFC 7348 says so explicitly. An untrusted sender may inject frames if a VTEP accepts its packets and the selected VNI is configured. The VNI alone is not authentication; underlay filtering and endpoint policy can reject the traffic. Keep the underlay private and filtered, never expose VTEPs to the internet, and run VXLAN over IPsec or WireGuard if it must cross untrusted links.

## Key takeaways
- A VXLAN VNI names an overlay network; it is not an authentication credential.
- The untagged IPv4 model costs 50 bytes of the inner IP budget.
- Filtering and protected underlay paths provide security absent from VXLAN itself.

## Further reading
- [RFC 4301: Security Architecture for the Internet Protocol](https://www.rfc-editor.org/rfc/rfc4301)
- [RFC 4303: IP Encapsulating Security Payload (ESP)](https://www.rfc-editor.org/rfc/rfc4303)
- [WireGuard: Next Generation Kernel Network Tunnel (whitepaper)](https://www.wireguard.com/papers/wireguard.pdf)
- [WireGuard: protocol and cryptography](https://www.wireguard.com/protocol/)
- [RFC 7348: Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348)
- [RFC 4459: MTU and Fragmentation Issues with In-the-Network Tunneling](https://www.rfc-editor.org/rfc/rfc4459)
