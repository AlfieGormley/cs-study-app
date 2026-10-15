---
id: nf-stp-recovery
sourceLesson: nf-arp-switching
title: STP recovery, guards and alternatives
level: intermediate
minutes: 3
summary: Understand default STP timers, qualified RSTP recovery and safer redundant designs.
---

### STP convergence: the slow part

Classic STP is cautious. A port moving towards forwarding passes through **listening** (15 s) and **learning** (15 s) states, the "forward delay", so the whole network can settle before any data flows. If a failure is detected only by BPDUs stopping, the switch first waits up to the 20-second **max age**. With these default timers, a transition can therefore take **30 to 50 seconds**; actual recovery depends on the failure and topology.

**RSTP** (originally 802.1w, incorporated into 802.1D-2004 and subsequently the combined 802.1Q bridging standard) enables faster transitions. Neighbours negotiate directly with a proposal and agreement handshake, alternate ports are pre-computed as backups, and suitable point-to-point transitions can complete in under a second. Failure detection and legacy neighbours can still introduce delays. **MSTP** (802.1s) runs separate trees for groups of VLANs, so different VLANs can use different links.

### Edge ports and guards

- An **edge port** (Cisco: PortFast) connects to a host, not a switch, so it skips the forward delay. With classic default timers, forwarding can otherwise wait 30 seconds after link-up; DHCP behaviour depends on client retries.
- **BPDU guard** shuts down an edge port that receives a BPDU, protecting the host-port assumption when BPDUs arrive. It is not a detector for every possible loop or silent device.
- **Root guard** stops a port from accepting a better root, so a misconfigured or malicious switch with priority 0 can't hijack the root and drag traffic through itself.

> [!tip] Diagnose before changing topology
> Inspect root IDs, port roles, link status and counters. A unidirectional link can require loop guard or an appropriate link-detection mechanism; the applicable feature depends on the failure and equipment.

## Beyond spanning tree

A spanning tree leaves some redundant paths unavailable for data within that instance; the unused fraction depends on topology. Alternatives can make more paths available:

- **Link aggregation** (LACP, 802.1AX) bundles parallel links into one logical link that STP sees as a single port, so eligible members can share flows. Hashing and the workload determine utilisation; one flow normally stays on one member.
- **MLAG** coordinates a link aggregation across two switches; details and failure behaviour are implementation-dependent.
- **Routed leaf-spine designs** can use ECMP across multiple equal-cost paths. IP TTL bounds a packet's lifetime in a forwarding loop; ECMP does not guarantee equal utilisation or that every link is busy. Layer 2 services may be extended over VXLAN.

## Key takeaways
- Classic default timers can introduce 30–50-second transitions.
- RSTP, edge-port guards, aggregation and routed multipath need their own failure and configuration assumptions.

## Further reading
- [RFC 826: An Ethernet Address Resolution Protocol](https://www.rfc-editor.org/rfc/rfc826)
- [RFC 5227: IPv4 Address Conflict Detection](https://www.rfc-editor.org/rfc/rfc5227)
- [Address Resolution Protocol — Wikipedia](https://en.wikipedia.org/wiki/Address_Resolution_Protocol)
- [ARP spoofing — Wikipedia](https://en.wikipedia.org/wiki/ARP_spoofing)
- [Spanning Tree Protocol — Wikipedia](https://en.wikipedia.org/wiki/Spanning_Tree_Protocol)
- [Broadcast storm — Wikipedia](https://en.wikipedia.org/wiki/Broadcast_storm)

- [Linux ARP implementation and neighbour parameters](https://man7.org/linux/man-pages/man7/arp.7.html)
- [RFC 9568: VRRP version 3](https://www.rfc-editor.org/rfc/rfc9568.html)
- [Cisco: Understand RSTP](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/24062-146.html)
- [IEEE: 802.1D consolidation into 802.1Q](https://www.ieee802.org/1/files/public/docs2021/maint-parsons-802.1D_withdrawal_status-0321-v1.pdf)
