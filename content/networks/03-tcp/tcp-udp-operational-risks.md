---
id: tcp-udp-operational-risks
sourceLesson: tcp-udp-ports
title: Congestion, reflection and UDP deployment
level: basic
minutes: 3
summary: Congestion, reflection and UDP deployment, with worked examples and explicit assumptions.
---

## Pitfalls of UDP

- **You own congestion control.** UDP will happily send faster than the network can carry, hurting everyone. [RFC 8085](https://www.rfc-editor.org/rfc/rfc8085) requires applications to account for congestion and describes suitable control or rate-limiting behaviour for different traffic patterns; low-volume applications are not universally exempt.
- **Amplification attacks.** With no handshake, an attacker can spoof a victim's source address and send small queries to open servers that reply with much bigger responses. Cloudflare documented large amplification from exposed Memcached UDP services in 2018. Amplification depends on the request, stored response and counting of protocol overhead; the attack does not follow merely from choosing UDP.
- **NAT and firewalls.** Idle mapping lifetimes vary. RFC 4787 specifies a normal minimum of two minutes, with a defined exception for some well-known destination ports; actual equipment may differ. Applications needing inbound reachability must account for the relevant timeout and keepalive policy. Some corporate networks block UDP outright, so clients supporting HTTP/2 or HTTP/1.1 can fall back to TCP; a QUIC-only application has no automatic TCP fallback.
- **Fragmentation.** Oversized datagrams may fail locally or require permitted fragmentation. Fragment loss or filtering can prevent reassembly; UDP does not retransmit the missing data.

## Key takeaways

- UDP applications must account for congestion; choosing datagrams does not remove network responsibility.
- Spoofed requests and large open-server replies can create reflection amplification.
- Mapping lifetimes, fragmentation and UDP reachability vary across paths and deployments.

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

> [!note] Scope and omitted evidence
> This lesson does not claim universal game update rates, media packet sizes, NAT timeouts, socket capacity or loss-recovery latency. Those require a specified implementation or measurement. Advanced UDP options and offload APIs are noted but not taught in detail here.
