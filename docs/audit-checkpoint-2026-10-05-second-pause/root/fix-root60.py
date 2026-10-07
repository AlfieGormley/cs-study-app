from pathlib import Path
import json
p=Path('content/networks/01-foundations/nf-arp-switching.md');s=p.read_text()
def r(a,b):
 global s
 assert a in s,a[:80]
 s=s.replace(a,b)
r('Before sending, a host checks whether the destination IP is on its own subnet (using its address and mask).','Before sending, a host selects a route. In the simple case with only a connected subnet route and a default route:')
r('This is the key idea of layering at work: MAC addresses change on every hop, while the IP addresses stay end to end. Every router strips the old frame and builds a new one for the next link.','On routed Ethernet hops the link-layer addresses identify the local next hop. Ordinary IP forwarding preserves source and destination IP addresses; NAT changes them, and tunnels add an outer packet. Other link technologies need not use Ethernet MAC addresses.')
r('Every host on the LAN receives it. The owner','Hosts in the broadcast domain can receive it, subject to filtering and isolation. Normally the owner')
r("Most implementations also cache the *requester's* mapping, since a reply is likely to follow.","RFC 826 updates an existing sender mapping before testing the opcode, and adds a new mapping when the receiver is the target. Implementations can impose additional checks; not every listener learns every request.")
r('import socket','import ipaddress')
r('    return struct.pack(','    if len(src_mac) != 6:\n        raise ValueError("MAC must be 6 bytes")\n    return struct.pack(')
r('src_mac, socket.inet_aton(src_ip),','src_mac, ipaddress.IPv4Address(src_ip).packed,')
r('socket.inet_aton(dst_ip))','ipaddress.IPv4Address(dst_ip).packed)')
r("Because 28 bytes is below Ethernet's 46-byte minimum payload, every ARP frame is padded to 64 bytes.","On basic untagged Ethernet, a 28-byte ARP message needs 18 bytes of padding to form a 64-byte frame including the header and FCS. VLAN tags change the framing calculation; captures may omit padding or FCS.")
a=s.index('Entries expire so');b=s.index('\n### Gratuitous',a)
s=s[:a]+"Cache lifetime and reachability are separate. Linux's default 30-second base reachable time is randomised to 15–45 seconds. Becoming **stale** does not immediately delete an entry or require resolution before the next packet: Linux can send using it, then seek confirmation. Other systems and configurations differ. A stale mapping can disrupt delivery until it is updated or resolved again.\n"+s[b:]
r('If anyone answers, the address is taken. This is duplicate address detection.','A conflicting request or reply, or another host probing the same target address, can reveal a conflict. It is not enough to check replies alone.')
r('broadcast "my IP is at my MAC" so everyone updates their caches.','broadcast an ARP request with both sender and target IP set to the announced address, allowing listeners to refresh applicable mappings.')
a=s.index('Announcements are how');b=s.index('\n## ARP spoofing',a)
s=s[:a]+"Announcements can help move a virtual IP during failover. With different physical MAC addresses, neighbours need the new mapping. VRRP uses a shared virtual MAC; then switch forwarding tables must learn its new location. Failure detection, filtering and implementation affect recovery time.\n\n> [!note] Content omitted after review\n> A universal millisecond failover time and cross-product ARP-cache defaults are omitted because they depend on versions, configuration and measurements not established here.\n"+s[b:]
r('Any host can send a reply claiming any IP, and most stacks will update an existing cache entry from an ARP message they never asked for.','A host with access to the link can claim a false mapping. Without defensive checks, receivers may update existing entries from unsolicited messages.')
r("It can't read properly verified TLS, but it can try downgrade tricks against anything that isn't strictly HTTPS.","Properly authenticated TLS protects application contents, but does not hide all metadata or prevent the intermediary from dropping traffic. The attack alone does not defeat TLS authentication.")
r('Anyone on the same layer 2 segment can do this with freely available tools: coffee-shop Wi-Fi, a hotel network, a flat office LAN. It is one of the main reasons "encrypt everything, even inside the network" became standard advice.','A shared layer 2 network can expose peers to forged ARP messages unless isolation or inspection blocks them. The network location alone does not establish that an attack is possible or occurring.')
r('Interception yields only ciphertext','Authenticated encryption protects contents and integrity, not availability or all metadata')
r('Switch drops ARP that contradicts DHCP records','Configured switches validate ARP against trusted bindings or ARP ACLs')
r("Unspoofable, but don't scale","Can prevent dynamic replacement of that mapping; do not prevent MAC impersonation or other attacks")
r('**Dynamic ARP Inspection** (DAI) is the usual enterprise answer.','**Dynamic ARP Inspection** (DAI) is one switch defence.')
r('It then checks every ARP message on untrusted ports against that table and drops liars.','DAI checks ARP on configured untrusted ports against bindings; static-address hosts may require ARP ACLs. Trusted ports and incorrect bindings need care.')
r('IPv6 replaces ARP with **Neighbor Discovery** (ICMPv6 neighbour solicitations sent to a multicast address rather than a broadcast). It has the same trust problem; the counterpart defences are RA Guard and ND inspection, plus the rarely deployed SEND.','IPv6 uses **Neighbor Discovery**: initial address resolution uses ICMPv6 neighbour solicitations to a solicited-node multicast address; reachability probes can be unicast. Unauthenticated ND also has spoofing risks. ND inspection and SEND address aspects of this problem. RA Guard filters router advertisements; it is not a general defence against forged neighbour advertisements.')
r('The copies multiply.','Copies recirculate; branching topologies can also multiply them.')
a=s.index('- Ethernet frames have **no TTL**');b=s.index('\nA single patch',a)
s=s[:a]+'''- Basic Ethernet frames have **no forwarding TTL**. A loop has no hop-count expiry, though congestion, faults or filtering can still discard frames.
- Repeated flooding can consume link capacity and cause a **broadcast storm**; the onset and severity depend on traffic and topology.
- MAC tables can **flap** as the same source arrives on different ports.
- Hosts may spend substantial resources processing unwanted broadcasts.
'''+s[b:]
r('**STP** (IEEE 802.1D, designed by Radia Perlman in 1985)','Classic **STP** (historically IEEE 802.1D)')
r('sent every 2 seconds to the multicast MAC','using a default hello interval of 2 seconds and the standard bridge-group multicast MAC')
r('Every switch has a **bridge ID**: a priority (default 32768) followed by its MAC address. The **lowest** bridge ID wins. Out of the box, with equal priorities, the switch with the lowest MAC becomes root, which is often the oldest, slowest box in the building. So you always set the priority deliberately on the core switch.','Every bridge has a **bridge ID**, combining a priority/system-ID field and a MAC address. The **lowest** ID wins. With equal priority/system-ID fields, the lowest MAC wins; this does not reliably indicate age or speed. Configure priorities to favour the intended root.')
r('On modern switches the priority field also embeds the VLAN number (the "extended system ID"), so priority can only be set in steps of 4096.','With the extended system ID, configurable priority occupies the upper four bits (steps of 4096, commonly default 32768); the lower 12 bits identify the relevant instance. In per-VLAN STP this is the VLAN ID, but it is not universally a VLAN number.')
r('in the original 802.1D table','in the commonly used short path-cost table')
r('Ties are broken by the lowest neighbouring bridge ID, then the lowest port ID.','After equal root IDs and path costs, ties use the sender bridge ID, sender port ID, and finally local port ID. Costs may be configured; long path-cost values differ.')
r('Every port on the root bridge is designated.','In the simple point-to-point topology below, the root ends of inter-switch links are designated. Shared segments and multiple ports attached to one segment need the full port-role rules.')
r('all priorities are 32768, and S1 has the lowest MAC.','all priority/system-ID fields are equal, and the MAC ordering is S1 < S2 < S3.')
r("That's **30 to 50 seconds** of outage.","With these default timers, a transition can therefore take **30 to 50 seconds**; actual recovery depends on the failure and topology.")
r('**RSTP** (Rapid STP, 802.1w, now folded into 802.1D) fixes this.','**RSTP** (originally 802.1w, incorporated into 802.1D-2004 and subsequently the combined 802.1Q bridging standard) enables faster transitions.')
r('failover on point-to-point links typically takes well under a second.','suitable point-to-point transitions can complete in under a second. Failure detection and legacy neighbours can still introduce delays.')
r("Without it, a laptop would wait 30 seconds for its link, long enough for DHCP to time out.","With classic default timers, forwarding can otherwise wait 30 seconds after link-up; DHCP behaviour depends on client retries.")
r('catching someone plugging a switch (or a loop) into a desk port.','protecting the host-port assumption when BPDUs arrive. It is not a detector for every possible loop or silent device.')
a=s.index('> [!tip] Where STP');b=s.index('\n## Beyond',a)
s=s[:a]+"> [!tip] Diagnose before changing topology\n> Inspect root IDs, port roles, link status and counters. A unidirectional link can require loop guard or an appropriate link-detection mechanism; the applicable feature depends on the failure and equipment.\n"+s[b:]
r("STP's weakness is waste: blocked links carry nothing, so half of your redundant capacity sits idle. Modern designs avoid large layer 2 domains:","A spanning tree leaves some redundant paths unavailable for data within that instance; the unused fraction depends on topology. Alternatives can make more paths available:")
r('so both members carry traffic.','so eligible members can share flows. Hashing and the workload determine utilisation; one flow normally stays on one member.')
r('**MLAG** lets a server attach to two switches that pretend to be one.','**MLAG** coordinates a link aggregation across two switches; details and failure behaviour are implementation-dependent.')
r('**Leaf-spine data centres** route at layer 3 between every switch. IP has a TTL and routing protocols use all equal-cost paths (ECMP), so loops are bounded and no links sit idle. Layer 2 is kept within a rack, or emulated over IP with VXLAN.','**Routed leaf-spine designs** can use ECMP across multiple equal-cost paths. IP TTL bounds a packet\'s lifetime in a forwarding loop; ECMP does not guarantee equal utilisation or that every link is busy. Layer 2 services may be extended over VXLAN.')
a=s.index('## Key takeaways');b=s.index('## Further reading',a)
s=s[:a]+'''## Key takeaways
- Routing selects the next hop; ARP resolves that IPv4 next hop on Ethernet.
- An initial ARP lookup normally uses a broadcast request and unicast reply. Ethernet/IPv4 ARP messages occupy 28 bytes before link framing.
- Probes detect address conflicts; announcements help refresh mappings. Shared virtual MACs also require switch relearning during failover.
- ARP lacks authentication. Inspection, isolation and authenticated encryption address different parts of the risk.
- Ethernet has no hop-count expiry. Spanning tree selects forwarding paths that remove switching loops.
- Classic default STP transitions can take 30–50 seconds. RSTP permits faster transitions but does not guarantee a universal recovery time.

'''+s[b:]
s+='\n- [Linux ARP implementation and neighbour parameters](https://man7.org/linux/man-pages/man7/arp.7.html)\n- [RFC 9568: VRRP version 3](https://www.rfc-editor.org/rfc/rfc9568.html)\n- [Cisco: Understand RSTP](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/24062-146.html)\n- [IEEE: 802.1D consolidation into 802.1Q](https://www.ieee802.org/1/files/public/docs2021/maint-parsons-802.1D_withdrawal_status-0321-v1.pdf)\n'
p.write_text(s)
