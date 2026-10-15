---
id: nf-model-responsibilities
sourceLesson: nf-layered-models
title: What each network layer does
level: basic
minutes: 3
summary: Distinguish the OSI, TCP/IP and five-layer models and identify each layer’s responsibility.
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

A basic Ethernet bridge doing ordinary layer-2 forwarding within one VLAN looks up the destination MAC address. It does not need an IP destination or an application header for that lookup.

What each layer is responsible for:

- **Physical**: turn bits into signals on a medium and back again.
- **Link**: move a frame across *one* link or LAN to the next device, using link-specific framing and, on Ethernet or Wi-Fi, MAC addresses.
- **Network**: move a packet from source host to destination host across many links, using IP addresses and routing; not all IP addresses are globally routable or uniquely identify one host.
- **Transport**: deliver data between transport endpoints using ports and addresses. Services vary: TCP offers an ordered reliable byte stream and congestion control; UDP itself does not.
- **Application**: whatever the program needs: fetching pages, resolving names, sending mail.

> [!tip] Hop-by-hop versus end-to-end
> Layers 1 and 2 operate on a single hop. Layer 3 crosses the whole path, but every router along the way inspects it. Layers 4 and up are, in principle, only looked at by the two end hosts. Remembering this explains a lot about which devices touch which headers.

## Key takeaways
- The OSI numbering describes seven responsibilities; this course uses the five-layer teaching model.
- Link delivery is local to a hop or LAN; network routing crosses links.

## Further reading
- [RFC 1122: Requirements for Internet Hosts — Communication Layers](https://www.rfc-editor.org/rfc/rfc1122)
- [OSI model — Wikipedia](https://en.wikipedia.org/wiki/OSI_model)
- [Internet protocol suite — Wikipedia](https://en.wikipedia.org/wiki/Internet_protocol_suite)
- [Encapsulation (networking) — Wikipedia](https://en.wikipedia.org/wiki/Encapsulation_(networking))
- [RFC 3439: Some Internet Architectural Guidelines and Philosophy](https://www.rfc-editor.org/rfc/rfc3439)

- [IANA IP protocol number registry](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
- [RFC 9001: QUIC packet and header protection](https://www.rfc-editor.org/rfc/rfc9001)
- [RFC 7348: VXLAN framing](https://www.rfc-editor.org/rfc/rfc7348)
