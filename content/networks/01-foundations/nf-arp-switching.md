---
id: nf-arp-switching
title: ARP, spoofing and spanning tree
level: intermediate
minutes: 14
summary: How a host finds the MAC address for an IP address, why ARP is trivially spoofable and how networks defend against it, and how spanning tree stops switch loops from melting a LAN.
---

The previous lesson ended with a gap. A host wants to send an IP packet to `192.168.1.1`, but an Ethernet frame needs a destination **MAC** address. Something has to translate one into the other. On IPv4 that is the **Address Resolution Protocol** (ARP, RFC 826, from 1982).

This lesson covers ARP, the attacks its simplicity invites, and a second problem that appears as soon as you join switches together: loops. The fix for loops, **spanning tree**, is one of the most consequential protocols most engineers never think about.

## Which MAC do I need?

Before sending, a host selects a route. In the simple case with only a connected subnet route and a default route:

- **Same subnet**: it needs the destination host's own MAC.
- **Different subnet**: it needs the MAC of its **default gateway** (router). The IP header still says the final destination; only the frame is addressed to the router.

```
laptop 192.168.1.20/24 -> 93.184.215.14

frame:  dst = router's MAC
packet: dst = 93.184.215.14
```

On routed Ethernet hops the link-layer addresses identify the local next hop. Ordinary IP forwarding preserves source and destination IP addresses; NAT changes them, and tunnels add an outer packet. Other link technologies need not use Ethernet MAC addresses.

## How ARP works

1. The host looks in its **ARP cache** (`ip neigh` on Linux, `arp -a` on macOS and Windows).
2. On a miss, it broadcasts an **ARP request** to `ff:ff:ff:ff:ff:ff`: "Who has 192.168.1.1? Tell 192.168.1.20."
3. Hosts in the broadcast domain can receive it, subject to filtering and isolation. Normally the owner of 192.168.1.1 sends a **unicast ARP reply**: "192.168.1.1 is at `a4:91:b1:...`."
4. The asker caches the answer. RFC 826 updates an existing sender mapping before testing the opcode, and adds a new mapping when the receiver is the target. Implementations can impose additional checks; not every listener learns every request.

The packet travels directly in an Ethernet frame with EtherType `0x0806`. It is not an IP packet. For IPv4 over Ethernet it is 28 bytes:

```python
import ipaddress
import struct

def arp_request(src_mac, src_ip, dst_ip):
    if len(src_mac) != 6:
        raise ValueError("need 6 MAC bytes")
    return struct.pack(
        "!HHBBH6s4s6s4s",
        1,          # HTYPE: Ethernet
        0x0800,     # PTYPE: IPv4
        6, 4,       # HLEN, PLEN
        1,          # OPER: 1 = request
        src_mac,
        ipaddress.IPv4Address(
            src_ip).packed,
        bytes(6),   # target MAC: unknown
        ipaddress.IPv4Address(
            dst_ip).packed)

pkt = arp_request(
    bytes.fromhex("3c22fb112233"),
    "192.168.1.20", "192.168.1.1")
print(len(pkt))  # 28
for i in range(0, 28, 12):
    print(pkt[i:i + 12].hex(" ", 4))
# 00010800 06040001 3c22fb11
# 2233c0a8 01140000 00000000
# c0a80101
```

`c0a80114` is 192.168.1.20 and `c0a80101` is 192.168.1.1. A reply has the same layout with OPER = 2 and the target MAC filled in. On basic untagged Ethernet, a 28-byte ARP message needs 18 bytes of padding to form a 64-byte frame including the header and FCS. VLAN tags change the framing calculation; captures may omit padding or FCS.

### The cache

Cache lifetime and reachability are separate. Linux's default 30-second base reachable time is randomised to 15–45 seconds. Becoming **stale** does not immediately delete an entry or require resolution before the next packet: Linux can send using it, then seek confirmation. Other systems and configurations differ. A stale mapping can disrupt delivery until it is updated or resolved again.

### Gratuitous ARP

An unsolicited ARP announcement advertises a host’s own address; it is commonly called **gratuitous ARP**. Address-conflict detection also uses a distinct probe before claiming an address. RFC 5227 specifies both:

- **Probe**: before using an address, send a request for it with sender IP 0.0.0.0. A conflicting request or reply, or another host probing the same target address, can reveal a conflict. It is not enough to check replies alone.
- **Announcement**: broadcast an ARP request with both sender and target IP set to the announced address, allowing listeners to refresh applicable mappings.

Announcements can help move a virtual IP during failover. With different physical MAC addresses, neighbours need the new mapping. VRRP uses a shared virtual MAC; then switch forwarding tables must learn its new location. Failure detection, filtering and implementation affect recovery time.

> [!note] Content omitted after review
> A universal millisecond failover time and cross-product ARP-cache defaults are omitted because they depend on versions, configuration and measurements not established here.

## ARP spoofing

ARP has no authentication at all. A host with access to the link can claim a false mapping. Without defensive checks, receivers may update existing entries from unsolicited messages. That is what makes gratuitous ARP failover work, and it is also the attack.

**ARP spoofing** (or ARP cache poisoning) goes like this:

1. The attacker, on the same LAN, sends the victim repeated replies: "192.168.1.1 is at *attacker's MAC*".
2. It sends the router: "192.168.1.20 is at *attacker's MAC*".
3. Both now send their frames to the attacker, which forwards them on so nothing appears broken.

```
before:  victim ---------> router
after:   victim -> ATTACKER -> router
```

The attacker is now a **man in the middle**. It can read unencrypted traffic, modify it, or drop it (a denial of service). Properly authenticated TLS protects application contents, but does not hide all metadata or prevent the intermediary from dropping traffic. The attack alone does not defeat TLS authentication.

> [!warning] Why this matters on shared networks
> A shared layer 2 network can expose peers to forged ARP messages unless isolation or inspection blocks them. The network location alone does not establish that an attack is possible or occurring.

### Defences

| Defence | How it helps |
|---|---|
| Encryption (TLS, SSH, VPN) | Authenticated encryption protects contents and integrity, not availability or all metadata |
| Dynamic ARP Inspection | Configured switches validate ARP against trusted bindings or ARP ACLs |
| Static ARP entries | Can prevent dynamic replacement of that mapping; do not prevent MAC impersonation or other attacks |
| Client isolation, small VLANs | Fewer hosts can reach you at layer 2 |

**Dynamic ARP Inspection** (DAI) is one switch defence. With **DHCP snooping**, the switch watches DHCP and records which IP was leased to which MAC on which port. DAI checks ARP on configured untrusted ports against bindings; static-address hosts may require ARP ACLs. Trusted ports and incorrect bindings need care. Monitoring tools such as arpwatch alert when a mapping changes.

IPv6 uses **Neighbor Discovery**: initial address resolution uses ICMPv6 neighbour solicitations to a solicited-node multicast address; reachability probes can be unicast. Unauthenticated ND also has spoofing risks. ND inspection and SEND address aspects of this problem. RA Guard filters router advertisements; it is not a general defence against forged neighbour advertisements.

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

Classic **STP** (historically IEEE 802.1D) lets switches agree on a loop-free **tree** across the physical mesh, and block the remaining links. If an active link fails, a blocked one is unblocked.

Switches exchange **BPDUs** (bridge protocol data units), using a default hello interval of 2 seconds and the standard bridge-group multicast MAC `01:80:c2:00:00:00`. Each BPDU says, in effect, "I think the root is X, and my cost to reach it is C".

### Step 1: elect a root bridge

Every bridge has a **bridge ID**, combining a priority/system-ID field and a MAC address. The **lowest** ID wins. With equal priority/system-ID fields, the lowest MAC wins; this does not reliably indicate age or speed. Configure priorities to favour the intended root.

With the extended system ID, configurable priority occupies the upper four bits (steps of 4096, commonly default 32768); the lower 12 bits identify the relevant instance. In per-VLAN STP this is the VLAN ID, but it is not universally a VLAN number.

### Step 2: each switch picks a root port

Every non-root switch chooses one **root port**: its port with the lowest total **path cost** to the root. Costs come from link speed; in the commonly used short path-cost table, 100 Mbit/s costs 19, 1 Gbit/s costs 4 and 10 Gbit/s costs 2. After equal root IDs and path costs, ties use the sender bridge ID, sender port ID, and finally local port ID. Costs may be configured; long path-cost values differ.

### Step 3: each link picks a designated port

On every link, the end with the lowest cost to the root becomes the **designated port** and forwards for that link (ties again go to the lower bridge ID). In the simple point-to-point topology below, the root ends of inter-switch links are designated. Shared segments and multiple ports attached to one segment need the full port-role rules.

Any port that is neither root nor designated is **blocked**: it still listens to BPDUs but forwards no data.

### The triangle, worked

All three links are 1 Gbit/s (cost 4), all priority/system-ID fields are equal, and the MAC ordering is S1 < S2 < S3.

| Switch | Cost to root | Root port |
|---|---|---|
| S1 | 0 (root) | none |
| S2 | 4 | to S1 |
| S3 | 4 | to S1 |

The S2–S3 link: both ends have cost 4, so the tie goes to the lower bridge ID, S2. S2's end is designated; S3's end is neither root nor designated, so it **blocks**.

```
        S1 (root)
       /  \
      R    R
     S2 -D-X- S3
 R = root port   D = designated
 X = blocked
```

If the S1–S3 link fails, S3 stops receiving BPDUs from S1, its blocked port becomes its new root port, and traffic flows via S2.

### Convergence: the slow part

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
- Routing selects the next hop; ARP resolves that IPv4 next hop on Ethernet.
- An initial ARP lookup normally uses a broadcast request and unicast reply. Ethernet/IPv4 ARP messages occupy 28 bytes before link framing.
- Probes detect address conflicts; announcements help refresh mappings. Shared virtual MACs also require switch relearning during failover.
- ARP lacks authentication. Inspection, isolation and authenticated encryption address different parts of the risk.
- Ethernet has no hop-count expiry. Spanning tree selects forwarding paths that remove switching loops.
- Classic default STP transitions can take 30–50 seconds. RSTP permits faster transitions but does not guarantee a universal recovery time.

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
