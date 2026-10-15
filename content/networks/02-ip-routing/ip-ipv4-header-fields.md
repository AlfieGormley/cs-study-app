---
id: ip-ipv4-header-fields
title: Read the IPv4 header
level: basic
minutes: 5
sourceLesson: ip-ipv4
summary: Read the fields that describe an IPv4 datagram and calculate its header and total-length limits.
---

The **Internet Protocol** (IP) has one job: get a packet from one host to another, across any number of networks, on a best-effort basis. It does not promise delivery, ordering or protection against duplicates. Those are left to the layers above (TCP) or to the application.

That modesty is the point. Because IP asks so little of the networks underneath, it runs over Ethernet, Wi-Fi, 4G, fibre and satellite links alike. Basic forwarding examines the IP header and a forwarding table; real routers also apply validation, queueing and policy.

The unit IP moves is a **datagram** (often just called a packet). Each one carries its own source and destination address and is routed independently. Two packets from the same download can take different paths.

## The IPv4 header

Every IPv4 datagram starts with a header of at least 20 bytes. Here it is, 32 bits per row:

```
0       8       16      24      31
+---+---+-------+---------------+
|Ver|IHL|DSCP|EC|  Total Length |
+---+---+-------+---+-----------+
| Identification    |Flg|FragOff|
+-------+-------+---+-----------+
|  TTL  | Proto |   Checksum    |
+-------+-------+---------------+
|        Source address         |
+-------------------------------+
|      Destination address      |
+-------------------------------+
|   Options (0 to 40 bytes)     |
+-------------------------------+
```

Field by field:

| Field | Bits | Purpose |
|---|---|---|
| Version | 4 | Always 4 |
| IHL | 4 | Header length in 32-bit words |
| DSCP / ECN | 6 / 2 | QoS traffic class, congestion marks |
| Total Length | 16 | Header + data, in bytes |
| Identification | 16 | Groups fragments |
| Flags | 3 | Reserved, DF, MF |
| Fragment Offset | 13 | Position, in 8-byte units |
| TTL | 8 | Hop budget |
| Protocol | 8 | What's inside |
| Header Checksum | 16 | Accidental header-error check |
| Source / Dest | 32 each | Addresses |

A few details worth knowing:

- **IHL** (Internet Header Length) counts 4-byte words, not bytes. Options add header bytes and can encounter filtering or slower processing, depending on the option and equipment.
- The **Total Length field** is 16 bits wide, so it caps the size of a whole datagram. Basic Ethernet commonly carries 1,500-byte IP packets, but other links, jumbo configurations and encapsulations have different MTUs.
- **Protocol** tells the receiver which handler gets the payload: 1 is ICMP, 6 is TCP, 17 is UDP.
- **DSCP** (Differentiated Services Code Point) marks traffic classes, for example "expedited forwarding" for voice. **ECN**, when supported by endpoints and the network, permits congestion marking of eligible packets; it does not eliminate all packet drops.
- The **checksum** covers the header only, not the data. Because every router decrements TTL, a forwarding router must update it, possibly incrementally. IPv6 has no corresponding header checksum.

To turn the IHL field into a header length in bytes, multiply by the size of each 4-byte word:

```formula
L_hdr = IHL × 4 B
L_hdr = 5 × 4 B = 20 B
L_hdr = 15 × 4 B = 60 B
where
L_hdr: the length of the IPv4 header, in bytes (B)
IHL: Internet Header Length, the 4-bit field in the IPv4 header that counts the header in 32-bit (4-byte) words; 5 when there are no options, 15 at most
B: bytes; one byte is 8 bits
In words: multiply the IHL value by 4 to get the header length in bytes. The usual IHL of 5 means a 20-byte header; the largest, 15, means 60 bytes, of which 40 are options.
```

The largest datagram follows from the size of the Total Length field. A field of 16 bits can hold 65,536 different values (2 to the power 16), from 0 up to one less than that:

```formula
L_max = (2^16 − 1) B = 65,535 B
where
L_max: the largest value the 16-bit Total Length field can hold, and so the largest possible IPv4 datagram (header plus data), in bytes (B)
2^16: 16 copies of 2 multiplied together, which is 65,536: the number of different values 16 bits can represent
B: bytes; one byte is 8 bits
In words: Total Length counts from 0, so its largest value is 65,536 − 1 = 65,535 bytes. In practice the link MTU, usually far smaller, is what limits real packets.
```

## Key takeaways
- IPv4 provides best-effort datagrams; each packet carries its own addresses.
- IHL counts four-byte words; Total Length includes header and data.
- The header checksum excludes the payload and must change when TTL changes.

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
