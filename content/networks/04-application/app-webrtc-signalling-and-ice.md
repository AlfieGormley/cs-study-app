---
id: app-webrtc-signalling-and-ice
title: "WebRTC signalling, candidate checks and TURN"
level: advanced
minutes: 4
sourceLesson: app-p2p-webrtc
summary: "WebRTC leaves signalling transport to the application while ICE tests candidate-pair reachability."
---

## WebRTC: browsers talking directly

WebRTC lets two browsers exchange audio, video and data directly. The hard part isn't the media; it's getting a packet from one to the other when both are behind NATs.

### Signalling is your problem

WebRTC deliberately **does not specify signalling**. Peers exchange **SDP** offers and answers (session descriptions: codecs, ICE credentials, DTLS fingerprints) through any channel you like, usually a WebSocket to your server. The browser peer-connection API follows JSEP's offer/answer processing. The following fragment is illustrative and wrapped for display: candidate attributes are single lines on the wire, and the fingerprint/password here are abbreviated placeholders.

```
a=ice-ufrag:F7gI
a=ice-pwd:x9cml/YzichV2+XlhiMu8g
a=fingerprint:sha-256 4A:AD:B9:...
a=candidate:1 1 udp 2122260223
  192.168.1.20 54400 typ host
a=candidate:2 1 udp 1686052607
  203.0.113.5 61234 typ srflx
  raddr 192.168.1.20 rport 54400
```

### ICE, STUN and TURN

**ICE** (Interactive Connectivity Establishment, [RFC 8445](https://www.rfc-editor.org/rfc/rfc8445)) gathers **ICE candidates**, addresses where a peer might be reachable:

- **Host candidates**: the device's own interface addresses.
- **Server-reflexive (srflx) candidates**: the externally observed address and port a NAT has mapped, learned by asking a **STUN** server "what address do you see me as?".
- **Relayed candidates**: an address on a **TURN** server that forwards packets for you.

Each side sends its candidates to the other (with **trickle ICE**, as they're found rather than all at once). ICE forms compatible candidate pairs and checks them in a prioritised process using authenticated STUN requests. Type/local preferences and both candidate priorities matter; peer-reflexive candidates may be discovered during checks. The controlling agent nominates a valid pair, rather than every first-success pair being automatically selected.

Why this works through NATs: when A sends a check to B's srflx address, A's NAT creates an outbound mapping. When B's check arrives at A's srflx address, the relevant mapping and filtering state may permit it. Success depends on both NATs' mapping and filtering behaviour; a STUN-observed mapping is not guaranteed to apply to every destination. This is **UDP hole punching**.

> [!analogy] Real-world analogy: Two gated estates arranging a visit
> Two friends live on gated estates whose guards only let in visitors a resident has asked for. They swap notes through a mutual friend: "my gate is on Elm Road, and here is the password my guard will ask for". Each asks a passer-by outside "which gate do you see me at?", and both tell their guards to expect the other at the same time. If the guards still refuse, they meet at a café in town instead.
>
> **How it maps:** The mutual friend is the signalling server carrying SDP. The passer-by is a STUN server revealing your server-reflexive address, and telling the guards to expect the other is the outbound check that opens a NAT mapping, which is hole punching. The guard's password is the ICE username and password that authenticate checks. The café is a TURN relay.
>
> **Where it stops:** Guards are people; NATs are rules about addresses and ports, and some create a different outside mapping for each destination, so the address the passer-by saw may not work for your friend. ICE does not guess: it tests candidate pairs and uses one that actually works.

STUN messages are tiny: a 20-byte header with the **magic cookie** `0x2112A442` and a 96-bit transaction ID, plus attributes. The server reports your address in **XOR-MAPPED-ADDRESS**: it XORs the port with the cookie's top 16 bits and an IPv4 address with the whole cookie, and the client applies the same XOR again to recover them. The point is that the real address never appears literally in the packet, because some NATs "helpfully" rewrote IP addresses they spotted inside packet payloads. For an IPv6 address, the XOR key also includes the message's 96-bit transaction identifier.

Endpoint-dependent NAT mappings (often called **symmetric NAT**) and restrictive filtering can defeat direct UDP hole punching, but NAT labels alone do not prove that every direct path fails. TURN provides a relay path when one is reachable and permitted. A 1 Mbit/s stream relayed once accounts for about 1 Mbit/s ingress and 1 Mbit/s egress, excluding overhead; provider charging varies. Client-to-TURN transport can use TCP or TLS, including a configured port 443, but this does not guarantee firewall traversal. How often calls need TURN depends heavily on the networks involved.

## Key takeaways
- WebRTC leaves signalling transport to the application while ICE tests candidate-pair reachability.
- STUN discovers or checks addresses, and TURN offers a relay when a permitted direct path fails.

## Further reading
- [RFC 8445](https://www.rfc-editor.org/rfc/rfc8445)
- [RFC 8489](https://www.rfc-editor.org/rfc/rfc8489)
- [RFC 8656](https://www.rfc-editor.org/rfc/rfc8656)
- [RFC 9429](https://www.rfc-editor.org/rfc/rfc9429)
