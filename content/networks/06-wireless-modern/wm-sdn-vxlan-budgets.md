---
id: wm-sdn-vxlan-budgets
title: VXLAN overlays and exact MTU budgets
level: intermediate
minutes: 4
summary: Outer addresses move an encapsulated tenant frame through the underlay.
sourceLesson: wm-sdn
---

Cloud tenants want private networks that behave like their own LAN, while the physical data-centre fabric is a routed network shared by everyone. An overlay bridges the two by wrapping each tenant packet inside another packet. The wrapping costs bytes, and forgetting those bytes causes one of the most recognisable network bugs.

## Overlays: virtual networks on a physical fabric

A cloud tenant wants their own private address space (two customers can both use `10.0.0.0/16`), their own subnets and firewall rules, and VMs that move between hosts. An overlay can keep much of this tenant-specific forwarding state out of the transit fabric, though tunnel endpoints and policies still need it.

The answer is an **overlay**: a tunnel endpoint, such as a hypervisor, switch or smart NIC, wraps each tenant packet in an outer packet addressed between physical hosts. The fabric just routes host to host and never sees tenant addresses.

**VXLAN** (RFC 7348) is the standard example:

```
| outer Eth | outer IP | UDP | VXLAN | inner
|   14 B    |  20 B    | 8 B |  8 B  | frame
             host A->B  :4789 VNI=24b
```

- The 24-bit **VXLAN Network Identifier** (VNI) allows about 16.8 million network segments, against 4,094 usable IDs in a 12-bit VLAN tag: one reason VXLAN suits multi-tenant clouds.
- RFC 7348 recommends deriving the outer UDP source port from inner headers to add variation for outer-header ECMP. Actual path use depends on the hash, mapping and traffic.

> [!analogy] Real-world analogy: Parcels packed into freight crates
> A freight company moves sealed crates between depots, reading only the label on each crate. Inside, each crate holds a customer's parcel addressed in the customer's own private format. Two customers can use identical internal addresses because nobody at the depot reads them. But the crate walls take up space, so a parcel that exactly fitted the old delivery van no longer fits once it is crated.
>
> **How it maps:** The crate label is the outer IP/UDP/VXLAN header addressed between physical hosts, and the parcel is the tenant's Ethernet frame. The depot reading only labels is the fabric routing on outer addresses, the customer code is the VNI, and the crate walls are the 50 bytes of encapsulation that must fit inside the underlay MTU.
>
> **Where it stops:** Unlike sealed crates, VXLAN is not encrypted: anyone on the underlay path can read the inner packet. And the size limit is set by every link on the underlay path, not by one vehicle.

## The MTU budget

The underlay's IP MTU limits the whole outer IP packet, which now has to hold the encapsulation as well as the tenant's packet. With outer IPv4 without options, UDP, VXLAN and untagged inner Ethernet without FCS, the extra bytes inside the outer IP packet are 20 + 8 + 8 + 14 = **50 bytes**. (The outer Ethernet header sits outside the IP MTU; the inner Ethernet header sits inside it.)

So on a 1,500-byte underlay:

- the tenant's IP packets must be at most **1,450 bytes**; or
- to let tenants keep a 1,500-byte MTU, the underlay needs an IP MTU of at least **1,550 bytes**, not necessarily a 9,000-byte jumbo frame.

Tags, outer IPv6 or extra tunnels add more bytes and change the budget. Getting this wrong produces the classic overlay symptom: small packets (pings, logins, short API calls) work, but anything that fills full-size packets (large responses, file transfers, big TLS certificate chains) hangs, especially when the ICMP messages that should report the problem are filtered.

Something must know which physical host each virtual address lives on. In VXLAN fabrics, BGP EVPN often distributes that mapping. A cloud provider may use a proprietary distributed virtual-network datapath. Do not infer that every provider uses standard VXLAN or the same per-host architecture; AWS’s VPC behaviour below is an API-level example.

## Key takeaways
- Outer addresses move an encapsulated tenant frame through the underlay.
- Encapsulation bytes must fit inside the underlay IP MTU; otherwise small packets work and full-size ones fail.

## Further reading
- [RFC 7348: Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348)
