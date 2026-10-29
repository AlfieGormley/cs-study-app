---
id: ip-ipv4-fragment-risks
title: Why fragmentation is fragile
level: basic
minutes: 3
sourceLesson: ip-ipv4
summary: Explain fragment loss, reassembly state and Identification wrap-around, then contrast IPv6.
---

Fragmentation lets an oversized IPv4 datagram cross a small-MTU link, but it creates problems that make networks and hosts avoid it where they can.

### Why fragmentation is avoided

Fragmentation works, but it is bad news in practice:

- **Loss amplification.** Lose any one fragment and the whole datagram is useless. IP itself has no fragment retransmission. Higher-layer or link-layer recovery is a separate mechanism.
- **The first fragment starts with the transport header.** A tiny first IPv4 fragment need not hold the complete TCP header. Later fragments normally lack ports, complicating stateless classification; stateful devices can associate fragments, while some policies drop them.
- **Reassembly costs memory** at the receiver and is a classic denial-of-service target (overlapping-fragment attacks, fragment floods).
- **ID wrap-around.** At high speeds the 16-bit Identification wraps quickly, risking fragments from different datagrams being stitched together.

How quickly? The field has 65,536 possible values. If a sender takes one per datagram to the same destination with the same protocol, the time before values repeat is simply 65,536 divided by the sending rate. At about 15,000 datagrams a second (roughly 8 KB datagrams at 1 Gbit/s) the counter wraps in about 4 seconds.

That is far shorter than reassembly state can last at a receiver (often tens of seconds). If a fragment of an old datagram is still waiting when a new datagram reuses its Identification value, the receiver can stitch pieces of two different datagrams together. The IPv4 header checksum does not cover the payload, and a transport checksum may not catch every such corruption.

IPv6 takes the lesson to heart: routers **never** fragment. Only the sending host may, using an extension header, and every IPv6 link must present an MTU of at least 1,280 bytes to IPv6, using fragmentation below IPv6 if the physical link needs it.

## Key takeaways
- Losing any fragment prevents reassembly of that datagram.
- Fragment handling consumes state and complicates filtering.
- A sequential Identification counter can repeat while old reassembly state remains; the rate and context matter.
- IPv6 routers do not fragment packets.

## Further reading
- [RFC 791: Internet Protocol](https://www.rfc-editor.org/rfc/rfc791)
- [RFC 8900: IP Fragmentation Considered Fragile](https://www.rfc-editor.org/rfc/rfc8900.html)
- [RFC 6864: IPv4 Identification field](https://www.rfc-editor.org/rfc/rfc6864)
- [RFC 8200: IPv6 Specification](https://www.rfc-editor.org/rfc/rfc8200)
