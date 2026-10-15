---
id: tcp-real-time-transport
sourceLesson: tcp-udp-ports
title: Real-time updates and transport over UDP
level: basic
minutes: 3
summary: Real-time updates and transport over UDP, with worked examples and explicit assumptions.
---

## Live games and voice: old data is useless

Consider a game sending independent full-state position snapshots at 60 Hz. The gap between snapshots is one divided by the rate:

```formula
T = 1 / f
T = 1 / (60 Hz) ≈ 0.0167 s ≈ 16.7 ms
where
T: the time between two snapshots, in seconds (s) or milliseconds (ms)
f: how many snapshots are sent each second, in hertz (Hz)
Hz: hertz, the unit for "times per second"; 60 Hz is 60 times a second
s: seconds
ms: milliseconds, thousandths of a second
≈: approximately equal to (the result is rounded)
In words: sending 60 updates a second leaves about 16.7 ms between them, so a 100 ms stall spans about six updates.
```

A new snapshot can supersede a lost one; delta updates and important game events can have different reliability requirements. TCP would **hold back** every later update until the lost one was retransmitted, delaying delivery of later bytes until the gap is repaired. The delay depends on detection, retransmission and buffering; the whole game loop need not freeze. That is **head-of-line blocking**, and independent deadline-sensitive updates can prefer skipping out-of-date data to waiting for that gap.

Voice and video calls (RTP over UDP) work the same way: a late frame may be concealed or discarded, but timely retransmission and forward error correction can also help. RFC 4588 specifies RTP retransmission; media deadlines determine its usefulness.

## QUIC: build your own transport

QUIC ([RFC 9000](https://www.rfc-editor.org/rfc/rfc9000)), the transport under HTTP/3, uses UDP; HTTP/3 commonly uses **port 443**, but QUIC is not restricted to that port. QUIC provides its own loss recovery, stream reliability, congestion control and protected transport, and can be implemented in user space. UDP is used not because QUIC wants unreliability, but because using existing UDP socket support can ease endpoint and middlebox deployment. UDP is neither the only permitted non-TCP transport nor guaranteed to pass every path. The transport-performance units cover why.

## Others

Examples using UDP include DHCPv4 initial discovery, conventional NTP/SNMP exchanges, UDP syslog, multicast media and WireGuard. Several of these application families also define other transports; “syslog” alone does not imply UDP.

## Key takeaways

- Independent state updates can supersede old data, while important events may need separate reliability.
- TCP delivery gaps can delay later stream bytes; this need not freeze an entire game loop.
- QUIC builds protected, congestion-controlled transport services above UDP rather than relying on base UDP for reliability.

## Further reading

- [RFC 768: User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768)
- [RFC 8085: UDP Usage Guidelines](https://www.rfc-editor.org/rfc/rfc8085)
- [User Datagram Protocol — Wikipedia](https://en.wikipedia.org/wiki/User_Datagram_Protocol)
- [Ephemeral port — Wikipedia](https://en.wikipedia.org/wiki/Ephemeral_port)
- [RFC 6335: IANA port number procedures](https://www.rfc-editor.org/rfc/rfc6335)
- [Memcrashed: amplification attacks from port 11211 — Cloudflare blog](https://blog.cloudflare.com/memcrashed-major-amplification-attacks-from-port-11211/)
- [Linux UDP socket semantics](https://man7.org/linux/man-pages/man7/udp.7.html)
- [Linux IP sysctl defaults](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
- [RFC 6935: IPv6 UDP checksum exceptions](https://www.rfc-editor.org/rfc/rfc6935)
- [RFC 2675: IPv6 jumbograms](https://www.rfc-editor.org/rfc/rfc2675)
- [RFC 9868: UDP transport options](https://www.rfc-editor.org/rfc/rfc9868)
- [RFC 4588: RTP retransmission](https://www.rfc-editor.org/rfc/rfc4588)
- [DNS Flag Day 2020 guidance](https://www.dnsflagday.net/2020/)
