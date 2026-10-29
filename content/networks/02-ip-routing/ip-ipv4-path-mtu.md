---
id: ip-ipv4-path-mtu
title: Path MTU and stalled transfers
level: basic
minutes: 4
sourceLesson: ip-ipv4
summary: Trace MTU feedback, recognise a possible black hole and choose a TCP MSS clamp that fits a tunnel.
---

Because fragmentation is fragile, modern senders try not to need it.

## Path MTU Discovery

The better approach is for the sender to learn the smallest MTU on the path (the **path MTU**) and send datagrams that fit. That is **Path MTU Discovery** (PMTUD, RFC 1191):

1. The sender sets **DF** on every packet and starts with its own link MTU.
2. A router that cannot forward a packet drops it and returns ICMP type 3, code 4 ("Fragmentation Needed and DF set"), which an RFC 1191 router fills with the next-hop MTU. Older messages may report zero and require fallback estimation.
3. The sender lowers its path estimate; retransmission or repacketisation depends on the transport/application. IP itself does not promise to resend.

```
Host        R1          R2        Server
 |  1500,DF  |           |           |
 |---------->|  1500,DF  |           |
 |           |---------->| MTU 1400! |
 |           |  ICMP 3/4 |           |
 |<----------------------| mtu=1400  |
 |  1400,DF  |           |           |
 |---------------------------------->|
```

IPv6 does the same with ICMPv6 **Packet Too Big**.

> [!analogy] Real-world analogy: A lorry and a low bridge
> A haulier sends tall lorries along a route it has never driven. At a low bridge the lorry cannot pass, so the bridge keeper stops it there and sends a note to the depot: "maximum height 4 m on this road". The depot sends a fresh copy of that cargo in a lower lorry and uses lower lorries from then on.
>
> **How it maps:** The lorry height is the packet size, the low bridge is the smallest-MTU link, "stop, do not split the load" is the DF flag, and the note is the ICMP Fragmentation Needed or Packet Too Big message carrying the next-hop MTU. The stopped lorry is a dropped packet: nothing is sent back except the note, so any resending is done by the sender's transport, such as TCP, from its own copy.
>
> **Where it stops:** If the depot's post room bins the notes (a firewall blocking ICMP), the depot never learns and keeps sending tall lorries that silently disappear. Real networks can also recover without the note by probing with gradually larger packets, which has no tidy road equivalent.

### The PMTUD black hole

Classic ICMP-based PMTUD depends on error feedback reaching the sender. If that feedback is blocked and no effective probing/fallback recovers, a **black hole** can result: the TCP handshake works (small packets), but as soon as full-size data packets are sent, they vanish silently. Users see web pages that start loading and then hang.

Common fixes:

- **Permit necessary ICMP errors.** IPv4 type 3/code 4 and ICMPv6 type 2 carry MTU feedback. ICMPv6 also supports essential functions such as neighbour discovery; treat message types appropriately rather than applying a blanket rule.
- **MSS clamping.** Routers on tunnels or PPPoE links rewrite the TCP **MSS** (maximum segment size) option in SYN packets to limit what the receiving peer sends. Bidirectional coverage requires handling MSS advertisements in both directions; MSS is not one jointly negotiated value. MSS does not constrain UDP; senders must also account for any options when forming packets (RFC 6691).
- **Packetization Layer PMTUD** (RFC 4821, and RFC 8899 for datagram protocols like QUIC) probes with progressively larger packets and watches for loss, without relying on ICMP.

The MSS counts only TCP data, so the right clamp value is the MTU minus both the IP and TCP headers. For IPv4 and TCP without options that is 40 bytes: a 1,500-byte Ethernet MTU gives the familiar 1,460, and a 1,492-byte PPPoE link gives 1,452. A common mistake is to clamp to the link or tunnel MTU itself, which still lets full-size segments exceed it by 40 bytes.

IP or TCP options reduce the payload a sender can place in a packet of that MTU. RFC 6691 says the advertised MSS is calculated using the fixed headers, excluding options; the sender separately reduces actual payload to allow for the options it sends. Do not confuse that per-packet adjustment with changing the peer’s MSS advertisement.

## Key takeaways
- Classic PMTUD relies on permitted MTU feedback; symptoms alone do not prove an MTU fault.
- MSS advertisements limit TCP data in one direction and exclude IP/TCP headers.
- Encapsulation consumes packet room; PLPMTUD provides probing rather than depending on ICMP alone.

## Further reading
- [RFC 1191: Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc1191)
- [RFC 4821: Packetization Layer Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc4821)
- [RFC 6691: TCP options and MSS](https://www.rfc-editor.org/rfc/rfc6691.html)
- [RFC 4638: Larger PPPoE MTUs](https://www.rfc-editor.org/rfc/rfc4638.html)
- [RFC 792: Internet Control Message Protocol](https://www.rfc-editor.org/rfc/rfc792)
