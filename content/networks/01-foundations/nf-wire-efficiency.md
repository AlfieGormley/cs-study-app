---
id: nf-wire-efficiency
sourceLesson: nf-layered-models
title: Count useful bytes and wire time
level: basic
minutes: 3
summary: Explain why headers and wire overhead affect small requests more than full frames.
---

An application pays for more than its own bytes. Transport, network and link layers add headers, and Ethernet also uses a trailer and time between frames. **Link efficiency** is the share of link occupancy that carries useful data at the boundary you choose.

## A small request and a full frame

Assume a 100-byte HTTP request fits in one TCP segment: no TLS, minimal TCP/IPv4 headers and untagged Ethernet. Ignore acknowledgements, retransmissions and PHY coding.

| Part | Bytes |
|---|---|
| HTTP request | 100 |
| TCP header | 20 |
| IPv4 header | 20 |
| Ethernet header and FCS | 18 |

The resulting frame is 158 bytes from destination MAC to FCS. Ethernet's header contains two 6-byte MAC addresses and a 2-byte EtherType; its **FCS** is a 4-byte CRC trailer.

Wire occupancy also includes an 8-byte preamble/start delimiter and a nominal 12-byte-time **inter-frame gap**. A byte-time is the time to send one byte. The gap is a time allowance, not extra frame payload; the PHY may send idle signalling during it. This request therefore costs 178 byte-times, of which only 100 carry HTTP: about 56% efficiency.

A full 1500-byte IPv4 packet with minimal headers carries 1460 bytes of TCP data and occupies 1538 byte-times under the same accounting. About 95% carries TCP data. The fixed overhead has been spread across much more useful data.

Small messages are still useful: waiting to fill a frame can add latency. The point is to understand the cost, rather than always choose the largest message.

## Count the right boundary

The IP MTU counts the IP packet; Ethernet frame size counts destination MAC through FCS; wire occupancy additionally counts preamble and gap. Confusing these boundaries produces misleading rates.

TCP options use some space inside the same IP MTU, leaving less for data. Tags, encryption and tunnels can add further overhead. A calculated payload ceiling is not a measured application rate: host limits, congestion, acknowledgements and loss can reduce goodput.

## Key takeaways
- Fixed overhead takes a larger share of a small frame's wire time.
- Distinguish useful payload, IP packet size, Ethernet frame size and wire occupancy.

## Further reading
- [RFC 1122: Requirements for Internet Hosts — Communication Layers](https://www.rfc-editor.org/rfc/rfc1122)
- [OSI model — Wikipedia](https://en.wikipedia.org/wiki/OSI_model)
- [Internet protocol suite — Wikipedia](https://en.wikipedia.org/wiki/Internet_protocol_suite)
- [Encapsulation (networking) — Wikipedia](https://en.wikipedia.org/wiki/Encapsulation_(networking))
- [RFC 3439: Some Internet Architectural Guidelines and Philosophy](https://www.rfc-editor.org/rfc/rfc3439)

- [IANA IP protocol number registry](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
- [RFC 9001: QUIC packet and header protection](https://www.rfc-editor.org/rfc/rfc9001)
- [RFC 7348: VXLAN framing](https://www.rfc-editor.org/rfc/rfc7348)
