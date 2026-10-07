---
id: nf-layered-models
title: Layered models and encapsulation
level: basic
minutes: 12
summary: OSI versus TCP/IP, how each layer wraps the one above in its own header, a byte-by-byte packet walk-through, and the places where the neat layering breaks down.
---

Sending a web page from a server in Frankfurt to your phone involves electrical pulses, radio waves, error checks, addresses, routing decisions, retransmissions, encryption and HTTP. Dividing these responsibilities makes the system easier to build and reason about.

Networks tame this by **layering**. In the model, each layer groups related responsibilities, relies on services below, and offers a cleaner service to the layer above. Ethernet does not care whether it carries a web page or a video call. HTTP does not care whether the bits travel over fibre or Wi-Fi.

This lesson sets up the vocabulary used for the rest of the subject.

## The two models

There are two reference models you will meet constantly.

The **OSI reference model** has seven layers. Its *numbering* survived: engineers still say "layer 2 switch" or "layer 7 load balancer".

The **TCP/IP model** (described in RFC 1122) has four layers and describes the protocols the internet actually runs.

| # | OSI layer | TCP/IP layer | Examples |
|---|---|---|---|
| 7 | Application | Application | HTTP, DNS, SMTP |
| 6 | Presentation | Application | TLS, encodings |
| 5 | Session | Application | (rarely distinct) |
| 4 | Transport | Transport | TCP, UDP; QUIC over UDP |
| 3 | Network | Internet | IP, ICMP |
| 2 | Data link | Link | Ethernet, Wi-Fi |
| 1 | Physical | Link | Cables, radio |

Many textbooks (Kurose and Ross, Tanenbaum) teach a hybrid **five-layer** model: physical, link, network, transport, application. That is the model this subject follows.

What each layer is responsible for:

- **Physical**: turn bits into signals on a medium and back again.
- **Link**: move a frame across *one* link or LAN to the next device, using link-specific framing and, on Ethernet or Wi-Fi, MAC addresses.
- **Network**: move a packet from source host to destination host across many links, using IP addresses and routing; not all IP addresses are globally routable or uniquely identify one host.
- **Transport**: deliver data between transport endpoints using ports and addresses. Services vary: TCP offers an ordered reliable byte stream and congestion control; UDP itself does not.
- **Application**: whatever the program needs: fetching pages, resolving names, sending mail.

> [!tip] Hop-by-hop versus end-to-end
> Layers 1 and 2 operate on a single hop. Layer 3 crosses the whole path, but every router along the way inspects it. Layers 4 and up are, in principle, only looked at by the two end hosts. Remembering this explains a lot about which devices touch which headers.

## Encapsulation

On the way down the stack, each layer takes what the layer above handed it, treats it as an opaque **payload**, and prepends its own **header** (and sometimes appends a trailer). On the way up at the receiver, each layer strips its header, acts on it, and passes the payload up.

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

## Worked example: one small HTTP request

A browser sends a 100-byte HTTP request over IPv4 and TCP on wired Ethernet. Assume the complete 100 bytes fit in one TCP segment, no TLS, minimal TCP/IPv4 headers and untagged Ethernet. Ignore ACK traffic, retransmission, PHY coding and other overhead beyond the fields counted below.

| Layer | Adds | Running size |
|---|---|---|
| HTTP | payload | 100 B |
| TCP | 20 B header | 120 B |
| IPv4 | 20 B header | 140 B |
| Ethernet | 14 B header + 4 B FCS | 158 B |

The Ethernet header is destination MAC (6 bytes), source MAC (6) and EtherType (2). The 4-byte **FCS** (frame check sequence) is a CRC-32 trailer covered in lesson 6.

On the wire Ethernet also sends an 8-byte preamble and start delimiter before the frame, and then leaves a nominal 12-byte-time **inter-frame gap** between frames. The PHY may transmit idle signalling during this interval, so it is not necessarily electrically silent. So the link is busy for 178 byte-times to deliver 100 bytes of HTTP: about 56% efficiency.

A full-size segment does far better. With a 1500-byte IP packet, TCP carries 1460 bytes of data, and the wire time is 1500 + 38 = 1538 bytes, so efficiency is 1460 / 1538 ≈ **94.9%**. Lesson 2 uses this figure.

```
 8      14      20   20   1460      4  12
|pre|  eth  | IP |TCP| data ... |FCS|gap|
```

### Parsing headers in code

Many header fields have defined byte layouts; optional and variable-length fields need additional parsing. Python's `struct` module can unpack them (`!` means network byte order, which is big-endian):

```python
import struct

def parse_eth(frame: bytes):
    if len(frame) < 14:
        raise ValueError("short header")
    dst, src, etype = struct.unpack(
        "!6s6sH", frame[:14])
    return (dst.hex(":"), src.hex(":"),
            hex(etype), frame[14:])

frame = bytes.fromhex(
    "ffffffffffff" "3c22fb112233"
    "0806") + b"..."
print(parse_eth(frame)[:3])
# ('ff:ff:ff:ff:ff:ff',
#  '3c:22:fb:11:22:33', '0x806')
```

This is a synthetic header followed by placeholder bytes, not a valid complete ARP frame. Its all-ones destination denotes broadcast and its EtherType selects ARP, which you will meet in lesson 5. This parser demonstrates an untagged Ethernet II header only. It does not handle VLAN tags, 802.3 length/LLC framing, frame length validation or FCS stripping/verification; packet-capture APIs may omit the FCS.

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
- Layering splits networking into independent problems: signals, one-hop delivery, end-to-end delivery, process-to-process delivery, and applications.
- OSI has seven layers and supplies the numbering; TCP/IP has four and describes what the internet runs. This course uses a five-layer teaching model.
- Encapsulation adds a header per layer; fields like EtherType, IP Protocol and ports let the receiver demultiplex.
- Headers cost bandwidth: a 100-byte request uses 178 byte-times on Ethernet, while a full 1460-byte segment is about 95% efficient.
- Layers leak through NAT, checksums, MTU, middleboxes and wireless loss. Many hard network bugs sit at those boundaries.

## Further reading
- [RFC 1122: Requirements for Internet Hosts — Communication Layers](https://www.rfc-editor.org/rfc/rfc1122)
- [OSI model — Wikipedia](https://en.wikipedia.org/wiki/OSI_model)
- [Internet protocol suite — Wikipedia](https://en.wikipedia.org/wiki/Internet_protocol_suite)
- [Encapsulation (networking) — Wikipedia](https://en.wikipedia.org/wiki/Encapsulation_(networking))
- [RFC 3439: Some Internet Architectural Guidelines and Philosophy](https://www.rfc-editor.org/rfc/rfc3439)

- [IANA IP protocol number registry](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
- [RFC 9001: QUIC packet and header protection](https://www.rfc-editor.org/rfc/rfc9001)
- [RFC 7348: VXLAN framing](https://www.rfc-editor.org/rfc/rfc7348)
