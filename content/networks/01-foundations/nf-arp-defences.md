---
id: nf-arp-defences
sourceLesson: nf-arp-switching
title: ARP spoofing and layered defences
level: intermediate
minutes: 3
summary: Assess poisoning evidence and distinguish inspection, isolation and authenticated encryption.
---

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

## Key takeaways
- ARP itself does not authenticate mappings; a duplicate MAC mapping alone is not proof of attack.
- DAI, isolation and authenticated encryption protect different aspects; RA Guard is not general ND inspection.

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
