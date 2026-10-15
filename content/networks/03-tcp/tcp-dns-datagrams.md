---
id: tcp-dns-datagrams
sourceLesson: tcp-udp-ports
title: Choosing UDP for DNS
level: basic
minutes: 3
summary: Choosing UDP for DNS, with worked examples and explicit assumptions.
---

## Why would anyone choose UDP?

TCP gives you reliability and ordering, but you pay in **latency** (a normal new-connection handshake and possible waits for retransmissions; extensions and connection reuse change this cost) and **control** (the kernel decides when to send and what to wait for). UDP is right when one of those costs is unacceptable.

## DNS: one question, one answer

A DNS lookup is usually a single small query and a single small response. With UDP the whole exchange takes **one round trip**. A fresh ordinary TCP connection adds a handshake; an already open connection can be reused, and TCP Fast Open can alter setup timing. Total resolution latency also includes DNS processing and any upstream queries.

Reliability is handled by the application: if no reply arrives within a timeout, the resolver asks again or tries another server. If a response is too big for UDP, the server sets the **TC (truncated)** flag and the client retries over TCP. EDNS(0) allows UDP responses bigger than the original 512-byte limit; DNS Flag Day 2020 recommended a 1,232-byte UDP payload limit. The number comes from the smallest packet every IPv6 link must carry:

```formula
P_DNS = MTU_min − H_IPv6 − H_UDP
P_DNS = 1,280 B − 40 B − 8 B = 1,232 B
where
P_DNS: the recommended largest DNS message over UDP, in bytes (B)
MTU_min: the minimum MTU that every IPv6 link must support, 1,280 bytes
H_IPv6: the fixed base IPv6 header, 40 bytes
H_UDP: the UDP header, 8 bytes
B: bytes
In words: a 1,232-byte DNS message plus its base IPv6 and UDP headers exactly fills the smallest packet IPv6 guarantees, so it fits without fragmentation when no extra headers or tunnels are added.
```

This reduces fragmentation risk under those assumptions rather than proving every path can carry it.

## Key takeaways

- A small DNS query/response can use one UDP round trip, with application retry policy supplying recovery.
- A truncated DNS response prompts TCP retry; EDNS advertises a larger UDP capacity.
- The 1,232-byte recommendation follows from minimal IPv6/UDP headers and the 1,280-byte IPv6 minimum MTU, with stated path assumptions.

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
