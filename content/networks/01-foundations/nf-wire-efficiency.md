---
id: nf-wire-efficiency
sourceLesson: nf-layered-models
title: Count useful bytes and wire time
level: basic
minutes: 4
summary: Calculate Ethernet overhead and compare small-request and full-frame efficiency.
---

## Worked example: one small HTTP request

A browser sends a 100-byte HTTP request over IPv4 and TCP on wired Ethernet. Assume the complete 100 bytes fit in one TCP segment, no TLS, minimal TCP/IPv4 headers and untagged Ethernet. Ignore ACK traffic, retransmission, PHY coding and other overhead beyond the fields counted below.

| Layer | Adds | Running size |
|---|---|---|
| HTTP | payload | 100 B |
| TCP | 20 B header | 120 B |
| IPv4 | 20 B header | 140 B |
| Ethernet | 14 B header + 4 B FCS | 158 B |

The Ethernet header is destination MAC (6 bytes), source MAC (6) and EtherType (2). The 4-byte **FCS** (frame check sequence) is a CRC-32 trailer covered in the error-control units.

On the wire Ethernet also sends an 8-byte preamble and start delimiter before the frame, and then leaves a nominal 12-byte-time **inter-frame gap** between frames. The PHY may transmit idle signalling during this interval, so it is not necessarily electrically silent. So the link is busy for 158 + 8 + 12 = 178 byte-times (a byte-time is how long the link takes to send one byte) to deliver 100 bytes of HTTP.

**Efficiency** answers "what share of the link's busy time carried data the application actually wanted?" Divide the useful bytes by everything the frame cost on the wire:

```formula
η = D / W
η = 100 B / 178 B ≈ 0.56
where
η: eta, the efficiency: the fraction of the link's busy time that carries useful data, from 0 to 1 (0.56 = 56%)
D: the useful application data in the frame, in bytes (B); here the 100-byte HTTP request
W: the wire time the frame occupies, counted in byte-times: the data plus every header, trailer, preamble and gap; here 178
B: bytes; one byte is 8 bits
≈: approximately equal to (the result is rounded)
In words: only 100 of every 178 byte-times carry the request, so the link spends about 56% of its time on useful data and 44% on overhead.
```

A full-size segment does far better, because the same fixed overhead is spread over much more data. With a 1500-byte IP packet, TCP carries 1460 bytes of data (1500 minus 20 bytes of IPv4 header and 20 of TCP header). The Ethernet costs on top are 14 (header) + 4 (FCS) + 8 (preamble and start delimiter) + 12 (gap) = 38 byte-times:

```formula
W = 1500 B + 38 B = 1538 B
η = D / W
η = 1460 B / 1538 B ≈ 0.949
where
W: the wire time of one full-size frame, in byte-times: the 1500-byte IP packet plus 38 bytes of Ethernet header, FCS, preamble and gap
η: eta, the efficiency: the fraction of wire time carrying TCP data (0.949 = 94.9%)
D: the TCP data carried per frame, in bytes; here 1460
B: bytes; one byte is 8 bits
≈: approximately equal to (rounded)
In words: a full-size frame spends about 95% of its wire time on data, because 78 bytes of overhead are now spread over 1460 bytes of data instead of 100.
```

The model assumes minimal headers (no TCP or IP options, no VLAN tag) and counts only the fields listed. Options, tags, encryption or tunnelling add bytes and lower the efficiency. The delay and bandwidth-delay-product units use the 94.9% figure.

```
 8      14      20   20   1460      4  12
|pre|  eth  | IP |TCP| data ... |FCS|gap|
```

## Key takeaways
- Count headers, FCS, preamble and nominal gap consistently.
- A full frame spreads fixed overhead across more useful data.

## Further reading
- [RFC 1122: Requirements for Internet Hosts — Communication Layers](https://www.rfc-editor.org/rfc/rfc1122)
- [OSI model — Wikipedia](https://en.wikipedia.org/wiki/OSI_model)
- [Internet protocol suite — Wikipedia](https://en.wikipedia.org/wiki/Internet_protocol_suite)
- [Encapsulation (networking) — Wikipedia](https://en.wikipedia.org/wiki/Encapsulation_(networking))
- [RFC 3439: Some Internet Architectural Guidelines and Philosophy](https://www.rfc-editor.org/rfc/rfc3439)

- [IANA IP protocol number registry](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
- [RFC 9001: QUIC packet and header protection](https://www.rfc-editor.org/rfc/rfc9001)
- [RFC 7348: VXLAN framing](https://www.rfc-editor.org/rfc/rfc7348)
