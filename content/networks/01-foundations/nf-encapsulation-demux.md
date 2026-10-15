---
id: nf-encapsulation-demux
sourceLesson: nf-layered-models
title: Encapsulation and protocol selection
level: basic
minutes: 3
summary: Follow a payload through headers and learn how receivers select the next protocol.
---

## Encapsulation

On the way down the stack, each layer takes what the layer above handed it, treats it as an opaque **payload**, and adds its own **header** in front (and sometimes appends a trailer). On the way up at the receiver, each layer strips its header, acts on it, and passes the payload up.

Each layer's unit has a name, the **PDU** (protocol data unit):

| Layer | PDU name |
|---|---|
| Application | Message |
| Transport | Segment (TCP) / datagram (UDP) |
| Network | Packet (or datagram) |
| Link | Frame |
| Physical | Bits / symbols |

```diagram
App            [   HTTP data   ]
Transport  [TCP][   HTTP data   ]
Network [IP][TCP][   HTTP data   ]
Link [Eth][IP][TCP][ HTTP data ][FCS]
```

### How the receiver knows what is inside

Several headers and endpoint identifiers allow **demultiplexing**, selecting the next protocol or recipient. Not every protocol header contains an explicit next-protocol field:

- Ethernet's **EtherType** field: `0x0800` means IPv4, `0x86DD` IPv6, `0x0806` ARP.
- IPv4's **Protocol** field (IPv6 calls it Next Header): `6` is TCP, `17` UDP, `1` ICMPv4 and `58` ICMPv6. IPv6 Next Header can also identify an extension header.
- TCP and UDP **port numbers**, together with addresses and other socket context, select transport endpoints. Port 443 conventionally serves HTTPS and 53 serves DNS; port numbers alone do not prove the application protocol or uniquely identify one process.

Without these fields a receiver would see an undifferentiated stream of bytes.

For ordinary forwarding without NAT or a tunnel, each router replaces the incoming link-layer frame for the next link while preserving the source and destination IP addresses. It decrements IPv4 TTL (or IPv6 Hop Limit); an IPv4 router also updates the IPv4 header checksum. These changes do not normally change the transport ports. A basic bridge forwarding within one VLAN instead looks up the destination MAC address.

## Key takeaways
- EtherType and IP protocol fields identify payload protocols.
- Each routed Ethernet hop needs its own local frame; end hosts interpret transport endpoints.

## Further reading
- [RFC 1122: Requirements for Internet Hosts — Communication Layers](https://www.rfc-editor.org/rfc/rfc1122)
- [OSI model — Wikipedia](https://en.wikipedia.org/wiki/OSI_model)
- [Internet protocol suite — Wikipedia](https://en.wikipedia.org/wiki/Internet_protocol_suite)
- [Encapsulation (networking) — Wikipedia](https://en.wikipedia.org/wiki/Encapsulation_(networking))
- [RFC 3439: Some Internet Architectural Guidelines and Philosophy](https://www.rfc-editor.org/rfc/rfc3439)

- [IANA IP protocol number registry](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
- [RFC 9001: QUIC packet and header protection](https://www.rfc-editor.org/rfc/rfc9001)
- [RFC 7348: VXLAN framing](https://www.rfc-editor.org/rfc/rfc7348)
