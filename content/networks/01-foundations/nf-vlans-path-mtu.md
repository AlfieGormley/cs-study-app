---
id: nf-vlans-path-mtu
sourceLesson: nf-ethernet
title: VLAN tags and path MTU
level: intermediate
minutes: 3
summary: Separate VLAN broadcast domains and diagnose size-dependent failures after encapsulation.
---

## VLANs

A basic single-VLAN bridge joins eligible ports into one broadcast domain; port isolation and filtering can further restrict connectivity. A **VLAN** (virtual LAN) splits one physical switch, or a set of switches, into several isolated LANs. Typical uses: separate staff, guest Wi-Fi, phones and servers without separate hardware.

IEEE **802.1Q** inserts a 4-byte **VLAN tag** after the source MAC:

| Field | Bits | Purpose |
|---|---|---|
| TPID | 16 | `0x8100`: "tagged" |
| PCP | 3 | Priority (QoS) |
| DEI | 1 | Drop eligible |
| VID | 12 | VLAN ID |

- The 12-bit VID allows 4096 values; 0 indicates priority tagging without a VLAN identifier and 4095 is reserved, leaving **4094 assignable VLAN IDs**. Equipment may support fewer active VLANs.
- Adding one tag to a maximum-size basic 1518-byte frame produces 1522 bytes; additional encapsulation has its own limits.
- An ordinary **access port** presents one untagged data VLAN to a host; voice VLANs, priority tags and vendor-specific configurations are exceptions.
- A **trunk port** carries many VLANs between switches (or to a router or hypervisor), usually with tags distinguishing VLANs. Depending on configuration, untagged traffic may use a native VLAN or be rejected; a native VLAN can also be tagged.
- Hosts in different VLANs cannot talk at layer 2 at all. Traffic between them must go through a **router** (or a layer 3 switch), where it can be filtered.

Large providers outgrew 4094. **802.1ad** ("QinQ") stacks a second tag (TPID `0x88A8`), and data centres use **VXLAN**, which carries Ethernet frames inside UDP with a 24-bit segment ID, allowing about 16 million.

## MTU

The **MTU** (maximum transmission unit) is the largest payload a link can carry in one frame. For standard Ethernet it is **1500 bytes**: the IP packet, not counting Ethernet's own 18 bytes of header and FCS.

- **Jumbo frames** raise the MTU, typically to about 9000 bytes. Fewer, larger frames can reduce per-packet work (interrupt moderation and offloads mean interrupts are not necessarily one per frame), and slightly less header overhead, so storage networks and data-centre fabrics often use them. They are not part of the IEEE standard, and every traversed link/interface must support the sizes actually sent, or the sender must adapt to a smaller path MTU; configured MTUs need not all be identical.
- An **MTU mismatch** can produce a black-hole failure if fragmentation or path-MTU adaptation does not resolve it: small packets (pings, TCP handshakes, short requests) work, but full-size packets are dropped. Connections open and then hang as soon as real data flows. Tunnels (VPNs, VXLAN) cause the same thing by quietly shrinking the effective MTU.

The IP module covers how hosts discover the path MTU and what happens when that discovery fails.

## Key takeaways
- VLAN tags distinguish logical link-layer domains; routing connects them.
- Tunnels add overhead, so unresolved path-MTU constraints can break large packets.

## Further reading
- [Ethernet frame — Wikipedia](https://en.wikipedia.org/wiki/Ethernet_frame)
- [MAC address — Wikipedia](https://en.wikipedia.org/wiki/MAC_address)
- [Carrier-sense multiple access with collision detection — Wikipedia](https://en.wikipedia.org/wiki/Carrier-sense_multiple_access_with_collision_detection)
- [IEEE 802.1Q — Wikipedia](https://en.wikipedia.org/wiki/IEEE_802.1Q)
- [Network switch — Wikipedia](https://en.wikipedia.org/wiki/Network_switch)
- [Jumbo frame — Wikipedia](https://en.wikipedia.org/wiki/Jumbo_frame)

- [IEEE address-allocation guidelines](https://standards-support.ieee.org/hc/en-us/articles/4888705676564-Guidelines-for-Use-of-Extended-Unique-Identifier-EUI-Organizationally-Unique-Identifier-OUI-and-Company-ID-CID)
- [Cisco auto-negotiation and duplex guidance](https://www.cisco.com/c/en/us/support/docs/lan-switching/ethernet/10561-3.html)
- [Cisco unicast flooding behaviour](https://www.cisco.com/c/en/us/support/docs/switches/catalyst-6000-series-switches/23563-143.html)
- [Apple private Wi-Fi address modes](https://support.apple.com/en-ie/102509)
