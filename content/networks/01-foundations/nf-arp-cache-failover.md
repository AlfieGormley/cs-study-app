---
id: nf-arp-cache-failover
sourceLesson: nf-arp-switching
title: ARP cache state and announcements
level: intermediate
minutes: 3
summary: Distinguish stale reachability state, address probes and failover announcements.
---

### The cache

Cache lifetime and reachability are separate. Linux's default 30-second base reachable time is randomised to 15–45 seconds. Becoming **stale** does not immediately delete an entry or require resolution before the next packet: Linux can send using it, then seek confirmation. Other systems and configurations differ. A stale mapping can disrupt delivery until it is updated or resolved again.

### Gratuitous ARP

An unsolicited ARP announcement advertises a host’s own address; it is commonly called **gratuitous ARP**. Address-conflict detection also uses a distinct probe before claiming an address. RFC 5227 specifies both:

- **ARP probe**: before using an address, send a request for it with sender IP 0.0.0.0. A conflicting request or reply, or another host probing the same target address, can reveal a conflict. It is not enough to check replies alone.
- **ARP announcement**: broadcast an ARP request with both sender and target IP set to the announced address, allowing receiving hosts to refresh applicable mappings.

Announcements can help move a virtual IP during failover. With different physical MAC addresses, neighbours need the new mapping. VRRP uses a shared virtual MAC; then switch forwarding tables must learn its new location. Failure detection, filtering and implementation affect recovery time.

> [!note] Content omitted after review
> A universal millisecond failover time and cross-product ARP-cache defaults are omitted because they depend on versions, configuration and measurements not established here.

## Key takeaways
- Stale does not mean an entry is immediately deleted or unusable.
- Probes detect conflicts; announcements refresh mappings, while a shared virtual MAC also needs switch relearning.

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
