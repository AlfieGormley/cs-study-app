---
id: tcp-port-numbers
sourceLesson: tcp-udp-ports
title: Ports and ephemeral allocation
level: basic
minutes: 3
summary: Ports and ephemeral allocation, with worked examples and explicit assumptions.
---

IP delivers packets from one **host** to another. But a host can run many programs at once: a browser, a DNS resolver, an SSH session, a game. When a packet arrives, something has to decide which program gets it.

That is the transport layer's most basic job: **multiplexing** (many applications sharing one IP address on the way out) and **demultiplexing** (handing each arriving packet to the right application). The tool for it is the **port number**.

Two widely used Internet transports are TCP and UDP. Base **UDP** offers datagram boundaries, ports and a checksum, with few additional services. **TCP** adds a reliable, ordered byte stream with flow and congestion control. This module starts with UDP as a simple datagram transport; transport protocols need not all use the same multiplexing mechanism.

## Ports

A port is a 16-bit number, so 0 to 65,535. IANA splits the range into three bands:

| Range | Name | Examples |
|---|---|---|
| 0–1023 | System (well-known) | 22 SSH, 53 DNS, 443 HTTPS |
| 1024–49151 | User (registered) | 3306 MySQL, 5432 Postgres |
| 49152–65535 | Dynamic (ephemeral) | Client-side ports |

A server often **binds** to a known service port; discovery mechanisms can also advertise dynamically chosen ports. Port zero is reserved in the IANA registry, and asking a socket API to bind port zero typically requests automatic allocation. A client usually lets the OS pick a temporary **ephemeral port** for its end. Operating systems don't all follow the IANA range: Linux picks ephemeral ports from **32768–60999** by default (`net.ipv4.ip_local_port_range`).

How many ports is that? To count the numbers in a range that includes both ends, subtract the ends and add one (the range 1–3 holds three numbers, not two):

```formula
N = P_high − P_low + 1
N = 60,999 − 32,768 + 1 = 28,232
where
N: how many port numbers the range contains (a plain count)
P_high: the highest port number in the range; 60,999 in Linux's default
P_low: the lowest port number in the range; 32,768 in Linux's default
In words: Linux's default ephemeral range holds 28,232 port numbers; the "+ 1" counts both end points.
```

That is the most a client can draw on before reserved ports, ports already in use and configuration changes are considered.

For a bounded connection-allocation model, fix the protocol (TCP), one source address and one destination address/port. Only the source port then varies between connection tuples. If the model keeps each tuple unavailable for 60 seconds after a negligible-duration connection, the sustainable new-connection rate cannot exceed the available port count divided by that holding time. This is an explicit capacity model, not a promise about every operating system's reuse policy; later units explain TCP tuples and TIME_WAIT in detail.

On Unix, binding to ports below 1024 traditionally needs root, the all-powerful administrator account (on Linux, typically `CAP_NET_BIND_SERVICE`, with the privileged-port threshold configurable per network namespace). That rule is a historical trust signal, not security.

## Key takeaways

- Ports distinguish transport endpoints; IANA service ranges and operating-system allocation policies are different concepts.
- The documented Linux ephemeral range contains 28,232 numbers before reservations and other constraints.

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
