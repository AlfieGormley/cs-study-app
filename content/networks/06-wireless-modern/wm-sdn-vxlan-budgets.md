---
id: wm-sdn-vxlan-budgets
title: VXLAN overlays and exact MTU budgets
level: intermediate
minutes: 4
summary: Outer addresses move an encapsulated tenant frame through the underlay.
sourceLesson: wm-sdn
---

This unit focuses on VXLAN overlays and exact MTU budgets. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Overlays: virtual networks on a physical fabric

A cloud tenant wants their own private address space (two customers can both use `10.0.0.0/16`), their own subnets and firewall rules, and VMs that move between hosts. An overlay can keep much of this tenant-specific forwarding state out of the transit fabric, though tunnel endpoints and policies still need it.

The answer is an **overlay**: a tunnel endpoint, such as a hypervisor, switch or smart NIC, wraps each tenant packet in an outer packet addressed between physical hosts. The fabric just routes host to host.

**VXLAN** (RFC 7348) is the standard example:

```
| outer Eth | outer IP | UDP | VXLAN | inner
|   14 B    |  20 B    | 8 B |  8 B  | frame
             host A->B  :4789 VNI=24b
```

- The 24-bit **VXLAN Network Identifier** allows about 16 million network segments, against 4,094 usable VLAN IDs (the calculation follows this list).
- RFC 7348 recommends deriving the outer UDP source port from inner headers to add variation for outer-header ECMP. Actual path use depends on the hash, mapping and traffic.
- With outer IPv4 without options, UDP, VXLAN and untagged inner Ethernet without inner FCS, the outer IP packet contains **50 bytes in addition to the inner IP packet**: 20 + 8 + 8 + 14. Thus a 1,500-byte underlay IP MTU permits at most 1,450 inner IP bytes under these assumptions (calculation below). Outer Ethernet is outside that IP MTU; tags, outer IPv6 or other encapsulation alter the budget. A tenant MTU of 1,500 instead needs at least 1,550 underlay IP bytes here, not necessarily a 9,000-byte jumbo frame. Getting this wrong produces the classic "small requests work, big ones hang" bug.

Every extra bit in an identifier field doubles the number of values it can hold:

```formula
N_VNI = 2^24 = 16,777,216
N_VLAN = 2^12 − 2 = 4,094
where
N_VNI: the number of distinct VXLAN segment identifiers; 2^24 means 2 raised to the power 24, that is 24 twos multiplied together, because the field is 24 bits long
N_VLAN: the number of usable VLAN IDs; the 12-bit field has 4,096 values, but 0 and 4,095 are reserved
In words: twelve extra bits multiply the number of isolated network segments by about four thousand.
```

The MTU budget adds up every header that sits inside the outer IP packet:

```formula
H = H_IP + H_UDP + H_VX + H_Eth
H = 20 B + 8 B + 8 B + 14 B = 50 B
X_max = MTU_u − H
X_max = 1,500 B − 50 B = 1,450 B
where
H: the encapsulation overhead counted against the underlay MTU, in bytes (B)
H_IP: the outer IPv4 header, 20 B without options
H_UDP: the outer UDP header, 8 B
H_VX: the VXLAN header, 8 B
H_Eth: the inner Ethernet header, 14 B (untagged, no FCS)
X_max: the largest inner IP packet that fits without fragmentation
MTU_u: the underlay IP MTU, 1,500 B here
B: byte
In words: VXLAN costs 50 bytes inside the outer IP packet, so a 1,500-byte underlay leaves 1,450 bytes for the tenant's IP packet.
```

Something must know which physical host each virtual address lives on. In VXLAN fabrics, BGP EVPN often distributes that mapping. A cloud provider may use a proprietary distributed virtual-network datapath. Do not infer that every provider uses standard VXLAN or the same per-host architecture; AWS’s VPC behaviour below is an API-level example.

## Key takeaways
- Outer addresses move an encapsulated tenant frame through the underlay.
- Count headers inside the actual underlay IP MTU; tags, address versions and extra tunnels change the budget.

## Further reading
- [RFC 7348: Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348)
