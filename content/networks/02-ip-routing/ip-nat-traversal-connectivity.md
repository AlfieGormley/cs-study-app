---
id: ip-nat-traversal-connectivity
title: NAT reachability and ICE traversal
level: intermediate
minutes: 4
sourceLesson: ip-nat-ipv6
summary: Explain NAT constraints and follow STUN, TURN and ICE through a connection attempt.
---

Explain NAT constraints and follow STUN, TURN and ICE through a connection attempt.

## Why NAT breaks end-to-end connectivity

IP was designed so any host could send a packet to any other. NAT breaks that:

- **Inbound reachability needs a usable mapping and permitted traffic.** Static forwarding, mapping-control protocols, traversal or relays can provide it; a previously unused private endpoint is not automatically reachable through dynamic NAPT. Running a server, a game host or a video call at home becomes awkward.
- **Addresses in payloads break.** Protocols that carry IP addresses inside the data (FTP's active mode, SIP for VoIP) send the private address, which is useless outside. Some devices provide **ALGs** (application-level gateways) that rewrite protocol fields. Application-aware traversal and relays are alternatives; encryption or protocol differences can prevent an ALG from doing the required rewrite.
- **State in the middle.** Losing an active dynamic mapping can interrupt a connection. Replicated or recoverable state and static mappings change failure behaviour; not every NAT deployment is a single unrecoverable point of failure.
- **Carrier-grade NAT** shares public IPv4 addresses among subscribers. It can add another translation layer beyond a home NAT, and RFC 6598 provides 100.64.0.0/10 for shared internal addressing. Sharing ratios vary. IP-based bans can affect unrelated subscribers; attribution needs sufficiently detailed mapping records, including protocol, ports and time. A subscriber mapping is not proof of an individual person's identity.

> [!note] NAT is not a firewall
> Translation does not define a complete security policy. Missing mappings can prevent delivery, while filtering determines which traffic may use existing mappings. IPv6 can apply stateful firewall rules without network address translation.

## Application NAT traversal: STUN, TURN and ICE

Video calls, WebRTC, games and VPN meshes (Tailscale, for example) want direct peer-to-peer paths. Three protocols, used together, make that work:

**STUN** (RFC 8489): a client sends a request to a public STUN server, which replies "I saw you as 203.0.113.7:40000". The client now knows its **server-reflexive** address. Endpoint-independent mapping can make that address reusable with other peers, but filtering, mapping lifetime and path reachability still determine whether traffic works.

**UDP hole punching**: both peers learn their reflexive addresses via STUN, swap them through a signalling server, then send connectivity probes towards one another. This can create mappings and filtering state that permit replies. Exact simultaneity is unnecessary, and NAT/filter behaviour can still prevent success.

**TURN** (RFC 8656): when direct connectivity checks fail, a peer can allocate a reachable **relay** address; one or both peers may use relayed candidates. It can provide connectivity when direct paths fail, but the relay must be reachable and have capacity and valid credentials. Firewalls and network failures can still block it. Relaying costs bandwidth and can add latency.

**ICE** (RFC 8445) is the procedure that ties them together:

1. **Gather candidates**: host addresses (local interfaces), server-reflexive (from STUN) and relayed (from TURN).
2. **Exchange** candidates through signalling. WebRTC can include candidates in SDP descriptions and convey additional candidates later using Trickle ICE.
3. **Connectivity checks**: try candidate pairs in priority order with STUN requests.
4. **Nominate** a valid pair under ICE priorities and application policy. A direct pair is commonly preferred, but relays can be deliberately preferred and nomination does not benchmark every path for optimal performance.

> [!analogy] Real-world analogy: Two callers behind switchboards
> Two people each sit behind an office switchboard and want to talk directly. Each first rings a friend outside and asks "what number did my call come from?", then they swap those numbers through a mutual contact and both dial at about the same time, so each receptionist sees the other's call as expected. If the switchboards still refuse, they both dial into a conference bridge instead.
>
> **How it maps:** Asking the outside friend is a STUN request revealing the server-reflexive address; the mutual contact is the signalling server; dialling at once is hole punching through connectivity checks; the conference bridge is a TURN relay; working through the options in order and settling on one that connects is ICE.
>
> **Where it stops:** A switchboard that gives each outside call a different line (destination-dependent mapping) makes the number your friend saw useless to anyone else, which phone systems rarely do. And ICE works through many candidate pairs in priority order, with several checks in flight, rather than strictly one call at a time.

```
         signalling server
          /             \
   Peer A ---- direct? ---- Peer B
     |   (hole punched)     |
     +------ TURN relay ----+
```

## Key takeaways
- NAT translation and firewall policy are different functions.
- Payload addresses, lost mapping state and shared addresses complicate applications and attribution.
- STUN discovers an observed mapping; it does not prove peer reachability.
- ICE checks candidate pairs and may use a TURN relay when direct checks fail.

## Further reading
- [RFC 4787: NAT Behavioral Requirements for Unicast UDP](https://www.rfc-editor.org/rfc/rfc4787)
- [RFC 8445: Interactive Connectivity Establishment (ICE)](https://www.rfc-editor.org/rfc/rfc8445)
- [RFC 8200: IPv6 Specification](https://www.rfc-editor.org/rfc/rfc8200)
- [RFC 4862: IPv6 Stateless Address Autoconfiguration](https://www.rfc-editor.org/rfc/rfc4862)
- [RFC 8305: Happy Eyeballs Version 2](https://www.rfc-editor.org/rfc/rfc8305)
- [Network address translation — Wikipedia](https://en.wikipedia.org/wiki/Network_address_translation)
- [IPv6 adoption statistics — Google](https://www.google.com/intl/en/ipv6/statistics.html)
