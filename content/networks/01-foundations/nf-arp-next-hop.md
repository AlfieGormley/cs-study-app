---
id: nf-arp-next-hop
sourceLesson: nf-arp-switching
title: Resolve the IPv4 next hop
level: intermediate
minutes: 3
summary: Choose the next-hop MAC and build the 28-byte Ethernet/IPv4 ARP message.
---

The VLAN and MTU lesson separated link delivery from IP routing. A host now wants to send an IP packet to `192.168.1.1`, but an Ethernet frame needs a destination **MAC** address. Something has to translate one into the other. On IPv4 that is the **Address Resolution Protocol** (ARP, RFC 826, from 1982).

This unit chooses the next hop and constructs the ARP message. Later units cover cache state, spoofing defences and the switching loops that spanning tree prevents.

## Which MAC do I need?

Before sending, a host selects a route. In the simple case with only a connected subnet route and a default route:

- **Same subnet**: it needs the destination host's own MAC.
- **Different subnet**: it needs the MAC of its **default gateway** (router). The IP header still says the final destination; only the frame is addressed to the router.

```
laptop 192.168.1.20/24 -> 93.184.215.14

frame:  dst = router's MAC
packet: dst = 93.184.215.14
```

A prefix length says how many leading address bits identify the network. In the simple IPv4 examples, /24 corresponds to mask `255.255.255.0`, while /16 corresponds to `255.255.0.0`. A mistakenly broad connected prefix can make a host try direct ARP for a destination that actually needs a router. Without proxy ARP or another applicable route, nobody on its VLAN answers for that remote address.

On routed Ethernet hops the link-layer addresses identify the local next hop. Ordinary IP forwarding preserves source and destination IP addresses; NAT changes them, and tunnels add an outer packet. Other link technologies need not use Ethernet MAC addresses.

## How ARP works

1. The host looks in its **ARP cache** (`ip neigh` on Linux, `arp -a` on macOS and Windows).
2. On a miss, it broadcasts an **ARP request** to `ff:ff:ff:ff:ff:ff`: "Who has 192.168.1.1? Tell 192.168.1.20."
3. Hosts in the broadcast domain can receive it, subject to filtering and isolation. Normally the owner of 192.168.1.1 sends a **unicast ARP reply**: "192.168.1.1 is at `a4:91:b1:...`."
4. The asker caches the answer. RFC 826 updates an existing sender mapping before testing the opcode, and adds a new mapping when the receiver is the target. Implementations can impose additional checks; not every receiving host learns from every request.

The packet travels directly in an Ethernet frame with EtherType `0x0806`. It is not an IP packet. For IPv4 over Ethernet it is 28 bytes:

```python
import ipaddress
import struct

def arp_request(src_mac, src_ip, dst_ip):
    if len(src_mac) != 6:
        raise ValueError("need 6 MAC bytes")
    # Pack fields without Ethernet framing.
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

# Group the raw message for visual
# inspection.
for i in range(0, 28, 12):
    print(pkt[i:i + 12].hex(" ", 4))
# 00010800 06040001 3c22fb11
# 2233c0a8 01140000 00000000
# c0a80101
```

`c0a80114` is 192.168.1.20 and `c0a80101` is 192.168.1.1. A reply has the same layout with the OPER (operation) field set to 2 and the target MAC filled in. On basic untagged Ethernet, a 28-byte ARP message needs 18 bytes of padding to form a 64-byte frame including the header and FCS. VLAN tags change the framing calculation; captures may omit padding or FCS.

## Key takeaways
- Routing chooses the next hop before ARP resolves its IPv4 address on Ethernet.
- An initial request is normally broadcast and the owner’s normal reply unicast.

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
