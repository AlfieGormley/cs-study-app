---
id: tcp-port-numbers
sourceLesson: tcp-udp-ports
title: Ports and ephemeral allocation
level: basic
minutes: 3
summary: How port numbers let many programs share one IP address, and why a client's ephemeral port pool can run dry.
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

That default range holds 28,232 port numbers (both end points count). It is the most a client can draw on before reserved ports, ports already in use and configuration changes are considered.

> [!analogy] Real-world analogy: Flat numbers in a block of flats
> A block of flats has one street address, but post is delivered to individual flats by number. A resident who sends a letter writes their own flat number on the envelope as the address for replies, so the answer comes back to the right door.
>
> **How it maps:** The IP address is the street address of the host; the port number is the flat number that picks one program on it. A server's well-known port is like a flat whose number is published; a client's ephemeral port is a temporary reply flat number the operating system picks for one conversation.
>
> **Where it stops:** Real flat numbers are permanent, whereas ephemeral ports are borrowed and later reused. The kernel also identifies a TCP conversation by both ends' addresses and ports together, not by the local port alone.

Why can the pool run dry? Picture a proxy that keeps opening short TCP connections from one source address to one backend address and port. Only its source port differs between those connections. If each used port stays unavailable for a while after the connection closes (later units explain why TCP holds it), the sustainable rate of new connections is at most the number of usable ports divided by that holding time. With the full Linux default range and a 60-second hold, that is roughly 470 new connections a second to that one backend. This is an explicit capacity model, not a promise about every operating system's reuse policy.

On Unix, binding to ports below 1024 traditionally needs root, the all-powerful administrator account (on Linux, typically `CAP_NET_BIND_SERVICE`, with the privileged-port threshold configurable per network namespace). That rule is a historical trust signal, not security.

## Key takeaways

- Ports distinguish transport endpoints; IANA service ranges and operating-system allocation policies are different concepts.
- The documented Linux ephemeral range contains 28,232 numbers before reservations and other constraints.
- Repeated short connections to one destination are limited by usable source ports divided by how long each port is held after closing.

## Further reading

- [RFC 6335: IANA port number procedures](https://www.rfc-editor.org/rfc/rfc6335)
- [Ephemeral port — Wikipedia](https://en.wikipedia.org/wiki/Ephemeral_port)
- [Linux IP sysctl defaults](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
- [RFC 768: User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768)
