---
id: nf-layer-boundaries
sourceLesson: nf-layered-models
title: Where network layers interact
level: basic
minutes: 3
summary: Recognise checksum, NAT, MTU and middlebox interactions across layer boundaries.
---

## Why layering works

- **Independent evolution.** A faster Ethernet link does not inherently require a new TCP wire format. An application protocol can evolve without redesigning link framing.
- **Interchangeable parts.** IP runs over Ethernet, Wi-Fi, 5G, satellite and (famously, in RFC 1149) carrier pigeons. Anything that can carry a packet can be part of the internet.
- **The narrow waist.** Many link technologies below and many applications above all meet at a single network protocol, IP. IP is the common internetworking service in this model; applications normally use higher-level APIs, while lower-layer devices need not implement an IP endpoint.
- **Each device does only what it needs.** Basic bridging uses link-layer information, while IP routing uses network-layer information. Real switches and routers can also inspect higher layers for filtering, load distribution or other functions.

## Where layering leaks

In theory a layer knows nothing about the others. In practice the boundaries leak, and many real problems live in those leaks.

- **TCP checksums cover IP addresses.** The TCP checksum includes a "pseudo-header" of source and destination IP. So address translation must preserve checksum correctness by adjusting or recomputing it; particular changes can cancel numerically.
- **Address/port translation.** A home gateway can use network address and port translation to share a public address. It may preserve a source port when possible or rewrite it when required by its mapping policy.
- **MTU.** The network layer needs the link MTU: the maximum network-layer packet that fits, rather than the whole Ethernet frame including its header and FCS. An oversized packet may be fragmented when permitted, or rejected with an ICMP message. If the required signalling or discovery fails, a path-MTU black hole can make larger traffic fail while smaller packets work.
- **Middleboxes inspect layer 4.** Firewalls and load balancers parse TCP headers and drop what they do not recognise. Such **ossification** can impede new transports and extensions. QUIC uses UDP to improve deployability and protects packet contents and selected header fields to limit unwanted dependencies; some headers remain visible and some networks block UDP or QUIC.
- **Wireless loss looks like congestion.** Loss-based TCP congestion control treats loss as a congestion signal, even when a particular loss comes from corruption rather than queue overflow. Reducing the rate may not address that radio error, and link-layer retransmissions can recover some radio loss before TCP sees it. Wi-Fi retry mechanisms also benefit other traffic; TCP is not their sole reason for existing.
- **Layers that do not fit.** MPLS is often called "layer 2.5". TLS sits between transport and application. Some tunnels, such as VXLAN, carry an inner Ethernet frame inside UDP (without the original FCS); other VPNs tunnel IP packets or application data instead.

> [!note] Layering is a model, not a law
> Treat the layers as a way to reason about responsibilities. Expect real systems to cross them for performance, security or historical reasons, and expect bugs where they do.

## Key takeaways
- Layering allows independent evolution but practical boundaries can interact.
- NAT, MTU discovery, encrypted transports and tunnels need coordinated accounting.

## Further reading
- [RFC 1122: Requirements for Internet Hosts — Communication Layers](https://www.rfc-editor.org/rfc/rfc1122)
- [OSI model — Wikipedia](https://en.wikipedia.org/wiki/OSI_model)
- [Internet protocol suite — Wikipedia](https://en.wikipedia.org/wiki/Internet_protocol_suite)
- [Encapsulation (networking) — Wikipedia](https://en.wikipedia.org/wiki/Encapsulation_(networking))
- [RFC 3439: Some Internet Architectural Guidelines and Philosophy](https://www.rfc-editor.org/rfc/rfc3439)

- [IANA IP protocol number registry](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
- [RFC 9001: QUIC packet and header protection](https://www.rfc-editor.org/rfc/rfc9001)
- [RFC 7348: VXLAN framing](https://www.rfc-editor.org/rfc/rfc7348)
