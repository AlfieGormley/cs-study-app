---
id: ip-ipv4-fragment-risks
title: Why fragmentation is fragile
level: basic
minutes: 3
sourceLesson: ip-ipv4
summary: Explain fragment loss, reassembly state and Identification wrap-around, then contrast IPv6.
---

Explain fragment loss, reassembly state and Identification wrap-around, then contrast IPv6.

### Why fragmentation is avoided

Fragmentation works, but it is bad news in practice:

- **Loss amplification.** Lose any one fragment and the whole datagram is useless. IP itself has no fragment retransmission. Higher-layer or link-layer recovery is a separate mechanism.
- **The first fragment starts with the transport header.** A tiny first IPv4 fragment need not hold the complete TCP header. Later fragments normally lack ports, complicating stateless classification; stateful devices can associate fragments, while some policies drop them.
- **Reassembly costs memory** at the receiver and is a classic denial-of-service target (overlapping-fragment attacks, fragment floods).
- **ID wrap-around.** At high speeds the 16-bit Identification wraps quickly, risking fragments from different datagrams being stitched together.

How quickly? A 16-bit counter has 65,536 values, so if a sender uses one per datagram:

```formula
t_wrap = 2^16 / r
t_wrap = 65,536 / (15,000 / s)
t_wrap ≈ 4.4 s
where
t_wrap: the time before the Identification counter repeats a value, in seconds (s)
2^16: 16 copies of 2 multiplied together, 65,536: the number of different values the 16-bit Identification field can hold
r: the rate at which the sender sends datagrams to the same destination with the same protocol, in datagrams per second; about 15,000 for 8 KB datagrams at 1 Gbit/s
≈: approximately equal to (the result is rounded)
s: seconds
In words: the faster the sender, the sooner Identification values repeat. If reassembly state lasts longer than this (often tens of seconds), an old fragment can be mistaken for part of a new datagram.
```

IPv6 takes the lesson to heart: routers **never** fragment. Only the sending host may, using an extension header, and every IPv6 link must present an MTU of at least 1,280 bytes to IPv6, using fragmentation below IPv6 if the physical link needs it.

## Key takeaways
- Losing any fragment prevents reassembly of that datagram.
- Fragment handling consumes state and complicates filtering.
- A sequential Identification counter can repeat while old reassembly state remains; the rate and context matter.
- IPv6 routers do not fragment packets.

## Further reading
- [RFC 791: Internet Protocol](https://www.rfc-editor.org/rfc/rfc791)
- [RFC 792: Internet Control Message Protocol](https://www.rfc-editor.org/rfc/rfc792)
- [RFC 1191: Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc1191)
- [RFC 4821: Packetization Layer Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc4821)
- [IP fragmentation — Wikipedia](https://en.wikipedia.org/wiki/IP_fragmentation)
- [Traceroute — Wikipedia](https://en.wikipedia.org/wiki/Traceroute)

- [RFC 8900: IP Fragmentation Considered Fragile](https://www.rfc-editor.org/rfc/rfc8900.html)
- [RFC 6864: IPv4 Identification field](https://www.rfc-editor.org/rfc/rfc6864)
- [RFC 4638: Larger PPPoE MTUs](https://www.rfc-editor.org/rfc/rfc4638.html)
- [RFC 6691: TCP options and MSS](https://www.rfc-editor.org/rfc/rfc6691.html)
- [RFC 1812: IPv4 router requirements](https://www.rfc-editor.org/rfc/rfc1812.html)
