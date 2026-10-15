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

STUN messages are tiny: a 20-byte header with the **magic cookie** `0x2112A442` and a 96-bit transaction ID, plus attributes. The server reports your address in **XOR-MAPPED-ADDRESS**, with the port XORed against the cookie's high 16 bits and IPv4 address against the cookie:

```formula
X_port = p ⊕ 0x2112
X_addr = A ⊕ 0x2112A442
where
X_port: the port value as it appears in the attribute
p: your actual mapped port
X_addr: the IPv4 address value as it appears in the attribute
A: your actual mapped IPv4 address, read as one 32-bit number
⊕: XOR (exclusive or), applied bit by bit; applying the same XOR again restores the original
In words: the server scrambles the address with the fixed magic cookie, and the client unscrambles it with the same XOR, so the real address never appears literally in the packet.
```

IPv6 additionally uses the STUN transaction ID, because some NATs "helpfully" rewrote IP addresses they spotted inside packet payloads.

Endpoint-dependent NAT mappings (often called **symmetric NAT**) and restrictive filtering can defeat direct UDP hole punching, but NAT labels alone do not prove that every direct path fails. TURN provides a relay path when one is reachable and permitted. A 1 Mbit/s stream relayed once accounts for about 1 Mbit/s ingress and 1 Mbit/s egress, excluding overhead; provider charging varies. Client-to-TURN transport can use TCP or TLS, including a configured port 443, but this does not guarantee firewall traversal. A universal percentage of calls requiring TURN is absent because no reliable representative measurement was established.

## Key takeaways
- WebRTC leaves signalling transport to the application while ICE tests candidate-pair reachability.
- STUN discovers or checks addresses, and TURN offers a relay when a permitted direct path fails.

## Further reading
- [RFC 8445](https://www.rfc-editor.org/rfc/rfc8445)
- [RFC 8489](https://www.rfc-editor.org/rfc/rfc8489)
- [RFC 8656](https://www.rfc-editor.org/rfc/rfc8656)
- [RFC 9429](https://www.rfc-editor.org/rfc/rfc9429)
