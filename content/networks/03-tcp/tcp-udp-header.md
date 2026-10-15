---
id: tcp-udp-header
sourceLesson: tcp-udp-ports
title: UDP headers, checksums and payload limits
level: basic
minutes: 4
summary: UDP headers, checksums and payload limits, with worked examples and explicit assumptions.
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

Four 16-bit fields make up the whole header:

```formula
H_UDP = 4 × 16 bit = 64 bit
H_UDP = 64 bit × (1 B / (8 bit)) = 8 B
where
H_UDP: the size of the UDP header
bit: binary digit, the smallest unit of data (a 0 or a 1)
B: bytes; one byte is 8 bits
In words: four 16-bit fields (source port, destination port, length, checksum) add up to 64 bits, which is 8 bytes.
```

- **Source port**: a reply-port hint when supplied; RFC 768 permits zero when unused. Application protocols can impose additional requirements.
- **Destination port**: which socket on the receiver gets this datagram.
- **Length**: header plus data, in bytes; at least 8 for an ordinary datagram. IPv6 jumbograms use the exception described below.
- **Checksum**: the 16-bit one's complement of the one's-complement sum over the header, the data and a **pseudo-header** of source IP, destination IP, protocol number and UDP length. Including addresses helps detect accidental misdelivery, but the checksum does not detect every error and provides no authentication.

The checksum is optional over IPv4 (a value of 0 means "not computed") and normally **required over IPv6**. RFC 6935/6936 permit narrowly constrained zero-checksum tunnel modes; ordinary IPv6 applications cannot simply disable it.

For ordinary UDP, the length field (16 bits) bounds header plus payload at 65,535 bytes. IPv6 jumbograms are a specified exception (RFC 2675), using UDP length zero when required.

Over IPv4 there is a second, tighter limit: the IPv4 header's own 16-bit total-length field counts the whole packet, IP header included. So the IP header and the UDP header both come out of the same 65,535 bytes:

```formula
P_max = L_IP − H_IP − H_UDP
P_max = 65,535 B − 20 B − 8 B
P_max = 65,507 B
where
P_max: the largest UDP payload (application data) one IPv4 datagram can carry, in bytes (B)
L_IP: the largest IPv4 total length, 65,535 bytes: the biggest number a 16-bit field can hold
H_IP: the IPv4 header size; 20 bytes when it carries no options (up to 60 bytes with options)
H_UDP: the UDP header size, always 8 bytes
B: bytes; one byte is 8 bits
In words: an IPv4 packet is at most 65,535 bytes, and the IP and UDP headers use 28 of them, leaving at most 65,507 bytes of data.
```

That is a protocol maximum, not a sensible size to send. An IP packet larger than the path MTU may be fragmented where allowed, rejected locally, or dropped with an ICMP error. Linux UDP normally uses PMTU discovery and can return `EMSGSIZE`. IPv6 routers do not fragment. Reassembly needs all fragments, so UDP applications should manage payload sizes using path and protocol constraints rather than assume one universal safe size.

> [!note] What UDP does not do
> Base UDP provides no handshake, acknowledgements, retransmission, ordering, flow control or congestion control. Datagrams may be lost, duplicated or reordered. Ordinary datagram socket calls preserve message boundaries; a too-small receive buffer can truncate a message and discard its remainder. A successful send is not proof of remote delivery.

RFC 9868 (October 2025) defines UDP transport options after the user-data area; it does not enlarge the base eight-byte header. This lesson describes ordinary datagrams without those options or socket segmentation/coalescing extensions.

## Key takeaways

- The base UDP header has four 16-bit fields and occupies eight bytes.
- Checksums help detect corruption without authenticating the sender; ordinary IPv6 UDP normally requires one.
- The IPv4 maximum payload is 65,507 bytes with minimal headers; path constraints usually require much smaller datagrams.

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
