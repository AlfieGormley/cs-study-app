---
id: tcp-udp-header
sourceLesson: tcp-udp-ports
title: UDP headers, checksums and payload limits
level: basic
minutes: 4
summary: UDP's eight-byte header, what its checksum does and does not protect, and why big datagrams are a bad idea.
---

## The UDP header

UDP ([RFC 768](https://www.rfc-editor.org/rfc/rfc768), 1980) is three pages long. Its header is 8 bytes:

```
 0      7 8     15 16    23 24    31
+--------+--------+--------+--------+
|   Source port   |    Dest port    |
+--------+--------+--------+--------+
|     Length      |    Checksum     |
+--------+--------+--------+--------+
|        data (payload) ...         |
+-----------------------------------+
```

Four 16-bit fields make up the whole base header, so it is always 8 bytes:

- **Source port**: a reply-port hint when supplied; RFC 768 permits zero when unused. Application protocols can impose additional requirements.
- **Destination port**: which socket on the receiver gets this datagram.
- **Length**: header plus data, in bytes; at least 8 for an ordinary datagram. IPv6 jumbograms use the exception described below.
- **Checksum**: the 16-bit one's complement of the one's-complement sum over the header, the data and a **pseudo-header** of source IP, destination IP, protocol number and UDP length. Including addresses helps detect accidental misdelivery, but the checksum does not detect every error and provides no authentication.

The checksum is optional over IPv4 (a value of 0 means "not computed") and normally **required over IPv6**. RFC 6935/6936 permit narrowly constrained zero-checksum tunnel modes; ordinary IPv6 applications cannot simply disable it.

For ordinary UDP, the length field (16 bits) bounds header plus payload at 65,535 bytes. IPv6 jumbograms are a specified exception (RFC 2675), using UDP length zero when required.

Over IPv4 there is a second, tighter limit: the IPv4 header's own 16-bit total-length field counts the whole packet, IP header included. The IP header and the UDP header both come out of the same 65,535 bytes, so with a 20-byte IPv4 header the largest UDP payload is 65,535 − 20 − 8 = 65,507 bytes.

That is a protocol maximum, not a sensible size to send. An IP packet larger than the path MTU may be fragmented where allowed, rejected locally, or dropped with an ICMP error. On Linux (tested on kernel 6.12), a UDP socket's default path-MTU mode fragments an oversized datagram locally; a socket that sets `IP_PMTUDISC_DO` gets `EMSGSIZE` instead. IPv6 routers do not fragment. Reassembly needs all fragments, so UDP applications should manage payload sizes using path and protocol constraints rather than assume one universal safe size.

> [!analogy] Real-world analogy: Postcards
> A postcard carries a destination address, an optional sender's address and the message. The postal service makes no promise that it arrives, arrives once, or arrives before the card you sent the next day, and you are not told if it is lost.
>
> **How it maps:** A UDP datagram is a self-contained postcard: the ports and IP addresses are the addresses, and each `sendto()` produces one card that arrives whole or not at all. There is no conversation to set up first.
>
> **Where it stops:** UDP's checksum lets the receiver detect some corruption and discard the card, which the post office does not do. A postcard has no size limit tied to the road it travels; a large datagram may have to be split into IP fragments, and losing any one of them loses the whole datagram.

> [!note] What UDP does not do
> Base UDP provides no handshake, acknowledgements, retransmission, ordering, flow control or congestion control. Datagrams may be lost, duplicated or reordered. Ordinary datagram socket calls preserve message boundaries; a too-small receive buffer can truncate a message and discard its remainder. A successful send is not proof of remote delivery.

RFC 9868 (October 2025) defines UDP transport options after the user-data area; it does not enlarge the base eight-byte header. This lesson describes ordinary datagrams without those options or socket segmentation/coalescing extensions.

## Key takeaways

- The base UDP header has four 16-bit fields and occupies eight bytes.
- Checksums help detect corruption without authenticating the sender; ordinary IPv6 UDP normally requires one.
- The IPv4 maximum payload is 65,507 bytes with minimal headers; path constraints usually require much smaller datagrams.

## Further reading

- [RFC 768: User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768)
- [User Datagram Protocol — Wikipedia](https://en.wikipedia.org/wiki/User_Datagram_Protocol)
- [RFC 6935: IPv6 UDP checksum exceptions](https://www.rfc-editor.org/rfc/rfc6935)
- [RFC 2675: IPv6 jumbograms](https://www.rfc-editor.org/rfc/rfc2675)
- [RFC 9868: UDP transport options](https://www.rfc-editor.org/rfc/rfc9868)
- [Linux UDP socket semantics](https://man7.org/linux/man-pages/man7/udp.7.html)
