from pathlib import Path
import json
p=Path('content/networks/02-ip-routing/ip-ipv4.md');s=p.read_text()
def r(a,b):
 global s
 assert a in s,a[:70]
 s=s.replace(a,b)
r('Every router only has to read a small header, pick the next hop and pass the packet on.','Basic forwarding examines the IP header and a forwarding table; real routers also apply validation, queueing and policy.')
r('Options are rare today and many networks drop packets that carry them.','Options add header bytes and can encounter filtering or slower processing, depending on the option and equipment.')
r('In practice almost all are 1,500 bytes or less, because that is Ethernet\'s MTU.','Basic Ethernet commonly carries 1,500-byte IP packets, but other links, jumbo configurations and encapsulations have different MTUs.')
r('**ECN** lets routers signal congestion by marking packets instead of dropping them.','**ECN**, when supported by endpoints and the network, permits congestion marking of eligible packets; it does not eliminate all packet drops.')
r('every router must recompute it. IPv6 dropped the header checksum entirely for this reason.','a forwarding router must update it, possibly incrementally. IPv6 has no corresponding header checksum.')
r('def parse_ipv4(pkt):','def parse_ipv4(pkt):\n    # Parse a captured header, not its payload.\n    if len(pkt) < 20:\n        raise ValueError("short IPv4 header")\n    version, ihl = pkt[0] >> 4, pkt[0] & 15\n    if version != 4 or ihl < 5:\n        raise ValueError("bad version/IHL")\n    if len(pkt) < ihl * 4:\n        raise ValueError("missing options")')
r('    return {','    if total < ihl * 4:\n        raise ValueError("bad total length")\n    return {')
r('That is exactly what a Linux `ping 8.8.8.8` sends: a 20-byte IP header, an 8-byte ICMP header and 56 bytes of data.','This is a synthetic header illustrating a packet with an 8-byte ICMP header and 56 data bytes. Source address, identification, TTL and options depend on configuration; it is not a capture of a universal `ping` default. This parser extracts fields and validates basic lengths, but does not validate the checksum, option contents or complete payload.')
r('Each router subtracts 1. If the result is 0, the router discards the packet and sends an ICMP **Time Exceeded** message back to the source.','A forwarding router decrements TTL by at least one. If it expires, the router discards the packet and normally sends ICMP **Time Exceeded**, subject to the rules suppressing errors for certain packets and to rate limiting.')
r('Without TTL, a looping packet would circulate for ever and loops would melt links. With TTL, a looping packet dies after at most 255 hops.','Without TTL, forwarding has no hop-count expiry, though congestion or faults can still drop packets. With initial TTL at most 255 and compliant forwarding, an ordinary datagram cannot be forwarded indefinitely. Tunnel encapsulation uses its own outer TTL and needs separate consideration.')
r('Operating systems pick the starting value. Linux and macOS use 64; Windows uses 128. So if you receive a packet with TTL 52, it probably came from a Linux box about 12 hops away.','The sender chooses the initial TTL. If it is known to be 64 and each router subtracts exactly one without rewriting or encapsulation, arrival at 52 means 12 forwarding hops. An observed TTL alone does not establish the starting value or identify an operating system.\n\n> [!note] Content omitted after review\n> A universal OS-default table and Internet hop-count range are omitted because they depend on platform versions, configuration and measurements not established here.')
r("Every link has a **maximum transmission unit** (MTU): the largest IP datagram it can carry in one frame. Ethernet's is 1,500 bytes. PPPoE broadband links lose 8 bytes to their own header and have 1,492. Tunnels (VPNs, GRE, VXLAN) shave off more.","An IP interface's **maximum transmission unit** (MTU) is the largest IP packet it supports without IP fragmentation. Link-specific mechanisms may fragment below IP. Basic Ethernet commonly uses 1,500 bytes. PPPoE plus PPP consumes 8 bytes within its Ethernet payload, giving 1,492 unless larger payload support is negotiated as in RFC 4638. Encapsulation reduces the inner MTU for a fixed outer path MTU.")
r('Fragments are reassembled only at the **destination**, never by routers along the way. Each fragment is a full IP datagram with a copy of the header, the same **Identification**, an **offset** (in 8-byte units) and the **MF** (More Fragments) flag set on all but the last.','In ordinary IP forwarding, reassembly is performed at the **destination**, not as a normal transit-router step. Firewalls/NATs may track or reassemble fragments for their separate functions, and a tunnel endpoint is the destination of the outer packet. Each fragment has its own IP header; option-copy rules mean not every option appears in every fragment. Fragments share **Identification**, carry an **offset** in 8-byte units and have **MF** set unless they contain the end of the original payload.')
a=s.index('def fragment(data_len, mtu, hdr=20):');b=s.index('\nfor f in fragment',a)
s=s[:a]+'''def fragment(data_len, mtu, hdr=20):
    # Model one unfragmented, DF-clear packet.
    # Equal header sizes; no option-copy logic.
    if not all(isinstance(v, int)
               for v in (data_len, mtu, hdr)):
        raise ValueError("integers required")
    if (hdr < 20 or hdr > 60 or hdr % 4
            or data_len < 0
            or data_len + hdr > 65535
            or mtu < hdr):
        raise ValueError("invalid sizes")
    capacity = mtu - hdr
    if data_len <= capacity:
        yield 0, data_len, False
        return
    per = capacity // 8 * 8
    if per == 0:
        raise ValueError("MTU too small")
    off = 0
    while off < data_len:
        left = data_len - off
        size = left if left <= capacity else per
        mf = off + size < data_len
        yield off // 8, size, mf
        off += size
'''+s[b:]
r('There is no retransmission of single fragments.','IP itself has no fragment retransmission. Higher-layer or link-layer recovery is a separate mechanism.')
r('**Only the first fragment has the TCP/UDP header.** Firewalls and load balancers that look at ports cannot classify later fragments, and many simply drop them.','**The first fragment starts with the transport header.** A tiny first IPv4 fragment need not hold the complete TCP header. Later fragments normally lack ports, complicating stateless classification; stateful devices can associate fragments, while some policies drop them.')
r('every IPv6 link must support an MTU of at least 1,280 bytes.','every IPv6 link must present an MTU of at least 1,280 bytes to IPv6, using fragmentation below IPv6 if the physical link needs it.')
r('which includes the next link\'s MTU.','which an RFC 1191 router fills with the next-hop MTU. Older messages may report zero and require fallback estimation.')
r('The sender lowers its estimate for that destination and resends.','The sender lowers its path estimate; retransmission or repacketisation depends on the transport/application. IP itself does not promise to resend.')
r('PMTUD depends on ICMP getting back to the sender. Many firewalls block all ICMP "for security". The result is a **black hole**:','Classic ICMP-based PMTUD depends on error feedback reaching the sender. If that feedback is blocked and no effective probing/fallback recovers, a **black hole** can result:')
r("**Don't block ICMP type 3 / ICMPv6 type 2.** Filter echo if you must, but let error messages through.","**Permit necessary ICMP errors.** IPv4 type 3/code 4 and ICMPv6 type 2 carry MTU feedback. ICMPv6 also supports essential functions such as neighbour discovery; treat message types appropriately rather than applying a blanket rule.")
r('so both ends agree to send smaller segments.','to limit what the receiving peer sends. Bidirectional coverage requires handling MSS advertisements in both directions; MSS is not one jointly negotiated value.')
r('On a 1,492-byte PPPoE link the MSS is clamped to 1,452 (1,492 − 20 IP − 20 TCP).','For inner IPv4 with fixed 20-byte IP/TCP headers, a 1,492-byte IP MTU gives MSS 1,452. MSS does not constrain UDP; senders must also account for any options when forming packets (RFC 6691).')
r('Error messages include the IP header and at least the first 8 bytes of the offending datagram,','The IPv4 errors discussed here quote the offending IP header and at least the first 8 bytes of its payload,')
r('(those 8 bytes contain the TCP or UDP ports).','(for a first fragment carrying TCP or UDP, these include the ports). The returned data cannot exceed what was actually available.')
r('Time Exceeded | TTL hit 0','Time Exceeded | TTL expiry or reassembly timeout')
r('`ping` sends ICMP Echo Requests and times the Echo Replies. It tells you whether a host is reachable and gives the **round-trip time**.','`ping` sends ICMP Echo Requests and measures reply **round-trip time**. A reply establishes that this probe/response exchange worked; it does not establish application service health.')
r('Both send three probes per hop by default.','Probe counts, starting ports and stopping rules depend on the implementation and options.')
r('```\n$ traceroute example.net','Illustrative output, not a live measurement:\n\n```\n$ traceroute example.net')
a=s.index('> [!warning] Reading traceroute honestly');b=s.index('\n## Key takeaways',a)
s=s[:a]+'''> [!warning] Reading traceroute honestly
> - `*` means no matching reply arrived before the timeout. The probe or reply may have been lost, filtered or rate-limited. Later replies show some probes got further, not that every packet took the same path or that forwarding is faultless.
> - Each displayed time is a round trip to the responding interface, including reply generation and the return path. Differences between hops do not isolate one link's delay.
> - Flow-preserving probes, such as Paris traceroute, reduce artefacts from per-flow load balancing. They cannot guarantee a fixed path through per-packet balancing or routing changes.
'''+s[b:]
r('every router decrements it and sends ICMP Time Exceeded when it hits 0.','forwarding routers decrement it and normally report expiry through ICMP, subject to suppression and rate limits.')
r('Fragmentation splits datagrams into 8-byte-aligned pieces reassembled only at the destination, but it hurts performance and breaks middleboxes, so senders use DF and Path MTU Discovery.','IPv4 non-final fragments carry multiples of 8 data bytes; the final fragment need not. Ordinary forwarding leaves reassembly to the destination. Fragmentation creates loss, state and middlebox complications.')
r('Blocking all ICMP creates PMTUD black holes; MSS clamping and PLPMTUD are the workarounds.','Blocking MTU feedback can cause PMTUD black holes. Permit necessary feedback; TCP MSS adjustment and PLPMTUD address different parts of the problem.')
s+='\n- [RFC 8900: IP Fragmentation Considered Fragile](https://www.rfc-editor.org/rfc/rfc8900.html)\n- [RFC 6864: IPv4 Identification field](https://www.rfc-editor.org/rfc/rfc6864)\n- [RFC 4638: Larger PPPoE MTUs](https://www.rfc-editor.org/rfc/rfc4638.html)\n- [RFC 6691: TCP options and MSS](https://www.rfc-editor.org/rfc/rfc6691.html)\n- [RFC 1812: IPv4 router requirements](https://www.rfc-editor.org/rfc/rfc1812.html)\n'
p.write_text(s)
