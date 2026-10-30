---
id: app-webrtc-security-and-groups
title: "WebRTC security and group-call bandwidth"
level: advanced
minutes: 3
sourceLesson: app-p2p-webrtc
summary: "WebRTC protects media and data using DTLS-derived keys, SRTP and SCTP channels."
---

After ICE has checked candidates and nominated a path, WebRTC establishes protected media/data transport. The signalling exchange includes DTLS certificate fingerprints; the trustworthiness of that exchange is part of the security model.

### Security: DTLS-SRTP and SCTP

Encryption is **mandatory** in WebRTC:

- After ICE, peers run a **DTLS** handshake (TLS for UDP) over the chosen path. Each checks that the other's certificate matches the `a=fingerprint` received over signalling. So the signalling channel must be trustworthy; whoever controls it can swap fingerprints and sit in the middle.
- Media keys are exported from DTLS into **SRTP** (DTLS-SRTP, RFC 5764).
- **Data channels** run **SCTP over DTLS over UDP** (RFC 8831), giving multiple streams with reliable or unreliable, ordered or unordered delivery per channel.

With BUNDLE and RTP/RTCP multiplexing, several protocols share an ICE transport. First-byte ranges distinguish outer STUN, DTLS and RTP/RTCP packets; SCTP is inside DTLS, not a separate outer packet type. Connectivity-check headers and ordinary RTP headers are not all encrypted. TURN/TCP paths add their own transport framing.

### Group calls

A two-party call is naturally peer-to-peer. With more people:

| Topology | Each client uploads | Server work |
|---|---|---|
| Mesh | One per other participant | No media forwarding if paths are direct |
| SFU | 1 (or a few) | Forward packets |
| MCU | 1 | Decode, mix, encode |

In a mesh, each client sends its own copy of its stream to every other participant, so each extra person adds another full stream to everyone's upload. With five people at 1.5 Mbit/s video, a **full mesh** needs each client to upload four copies, 6 Mbit/s, before protocol overhead; whether an uplink supports this is deployment-specific. An **SFU** (selective forwarding unit) takes one upload per client and forwards copies, and with **simulcast** each client sends, say, three resolutions so the SFU can give each receiver the one that suits its bandwidth. An SFU reduces client upload replication at the cost of server forwarding. With ordinary per-hop DTLS-SRTP, the SFU holds media keys; an additional mechanism such as SFrame is needed to hide media content from it.

## Key takeaways
- WebRTC protects media and data using DTLS-derived keys, SRTP and SCTP channels.
- Mesh upload grows with other participants; SFUs reduce replication but ordinary per-hop media keys expose content.

## Further reading
- [RFC 8827](https://www.rfc-editor.org/rfc/rfc8827)
- [RFC 8831](https://www.rfc-editor.org/rfc/rfc8831)
- [RFC 5764](https://www.rfc-editor.org/rfc/rfc5764)
- [RFC 9605](https://www.rfc-editor.org/rfc/rfc9605)
