---
id: nf-stp-root-election
sourceLesson: nf-arp-switching
title: Switch loops and root election
level: intermediate
minutes: 3
summary: Explain broadcast circulation and choose a spanning-tree root using the complete bridge ID.
---

## The loop problem

Engineers like redundancy, so they connect switches in rings or meshes: if one link fails, another takes over. With plain switches this is a disaster.

Consider three switches in a triangle, and a host that sends one broadcast:

```
        S1
       /  \
     S2 -- S3
```

S1 floods it to S2 and S3. S2 floods its copy to S3; S3 floods its copy to S2. Each of those floods it back to S1, which floods again. Copies recirculate; branching topologies can also multiply them.

- Basic Ethernet frames have **no forwarding TTL**. A loop has no hop-count expiry, though congestion, faults or filtering can still discard frames.
- Repeated flooding can consume link capacity and cause a **broadcast storm**; the onset and severity depend on traffic and topology.
- MAC tables can **flap** as the same source arrives on different ports.
- Hosts may spend substantial resources processing unwanted broadcasts.

A single patch cable plugged into two wall ports on the same switch can take down an entire office this way.

## Spanning Tree Protocol

Classic **STP** (historically IEEE 802.1D) lets switches agree on a loop-free **tree** across the physical mesh, and block the remaining links. After a failure, the tree is recomputed; an eligible redundant port can become forwarding if a usable alternate path exists.

Switches exchange **BPDUs** (bridge protocol data units), using a default hello time of 2 seconds and the standard bridge-group multicast MAC `01:80:c2:00:00:00`. Each BPDU says, in effect, "I think the root is X, and my cost to reach it is C".

### Step 1: elect a root bridge

Every bridge has a **bridge ID**, combining a priority/system-ID field and a MAC address. The **lowest** ID wins. With equal priority/system-ID fields, the lowest MAC wins; this does not reliably indicate age or speed. Configure priorities to favour the intended root.

With the extended system ID, configurable priority occupies the upper four bits (steps of 4096, commonly default 32768); the lower 12 bits identify the relevant instance. In per-VLAN STP this is the VLAN ID, but it is not universally a VLAN number.

## Key takeaways
- Basic Ethernet has no forwarding hop count, so switching loops can cause storms.
- The lowest priority/system-ID and MAC combination becomes root.

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
