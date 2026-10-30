---
id: nsec-packet-identities
title: Privacy and forged packet identities
level: basic
minutes: 4
summary: An address in a packet is a claim, not cryptographic proof of the sender.
sourceLesson: nsec-threats
---

Basic IPv4, ARP, UDP and traditional DNS do not by themselves cryptographically authenticate every sender or encrypt application data. Checksums detect some accidental corruption, but do not prove identity. Security extensions and deployment controls can add protections.

Missing authentication and encryption enable several important network attacks. These threat units sort attacks into five families. For each one, ask two questions: **what security property does it break**, and **what is the standard defence**?

The classic properties are often summarised as **CIA**:

| Property | Meaning | Broken by |
|---|---|---|
| Confidentiality | Only the intended party reads it | Eavesdropping |
| Integrity | Nobody alters it undetected | MITM, injection |
| Authenticity | It came from who it claims | Spoofing, replay |
| Availability | The service stays up | DoS / DDoS |

(Strictly, CIA is confidentiality, integrity and availability; authenticity is usually grouped with integrity. It is listed separately here because so many network attacks target it.)

## Eavesdropping

**Eavesdropping** (passive sniffing) means reading traffic you were not meant to see. The attacker changes nothing, which makes it very hard to detect.

Where can an attacker listen?

- **Shared media.** Wi-Fi is radio: a nearby receiver may capture frames on a monitored channel, subject to signal, interference and radio capabilities. An Ethernet repeater hub repeated received signals onto its other ports, subject to physical-layer error and collision handling.
- **Switched LANs.** A switch normally forwards known unicasts toward the learned destination port, while broadcasts and some unknown traffic are flooded. Exhausting the switch's MAC address table, or ARP poisoning, may expose additional traffic, depending on switch protections and topology.
- **On the path.** Any ISP, transit provider, café router or compromised router between you and the server sees your packets.

Even when the payload is encrypted, **metadata** leaks: source and destination addresses, packet sizes, timing, and often the server's hostname (in DNS queries and the TLS SNI field, covered in the TLS units).

The defence is **encryption in transit**: TLS for application traffic, VPNs for whole networks, WPA2/WPA3 for Wi-Fi. The maths behind the ciphers is covered in the Security & Cryptography subject; here we care about where encryption sits and what it leaves exposed.

## Spoofing

**Spoofing** means forging an identifier. Many packet fields can be written by a sender. Whether a forgery is accepted depends on filtering, cryptographic validation and protocol state.

| What is forged | How | Classic use |
|---|---|---|
| Source IP | Write any value in the header | Reflection DDoS |
| MAC address | Change the NIC setting | Bypass MAC filters |
| ARP reply | Send unsolicited replies | LAN MITM |
| DNS answer | Race the real reply | Redirect a domain |
| Email sender | Set the From header | Phishing |

**IP spoofing** has a catch for the attacker: replies go to the forged address, not to them. So it is mostly useful for one-way attacks where the attacker does not need the answer. That is exactly what reflection attacks need, as covered in the later amplification units.

An off-path attacker who cannot observe replies has an additional obstacle when forging a TCP handshake: the acknowledgment must match the server's initial sequence number plus one in the ordinary no-data handshake. With an unpredictable 32-bit initial sequence number, one blind guess is right only about once in 4.3 billion tries. Predictable sequence numbers once made blind spoofing practical, which is why RFC 6528 recommends unpredictable generation.

> [!analogy] Real-world analogy: a forged sender's name on a letter
> Anyone can write any name in the sender's corner of a letter and post it. The post office delivers it without checking, and any reply goes to the name and address written there, not to the person who really sent it.
>
> **How it maps:** The source address in an IP packet is the written sender's name. Routers forward on the destination and do not prove the source, so replies go to the forged address. That is why spoofing suits one-way floods and reflection, and why a blind attacker cannot see a server's reply.
>
> **Where it stops:** Networks can check sources in ways the post office does not: BCP 38 filtering drops packets whose source is outside the customer's permitted prefixes, and protocols such as TCP and TLS add state or cryptographic proof that a forger must also defeat.

> [!tip] BCP 38: stop spoofing at the source
> RFC 2827 (BCP 38) recommends filtering customer traffic against permitted source prefixes. This blocks spoofing outside those prefixes, but does not by itself stop one host impersonating another inside an allowed prefix. More granular source validation and reflector controls are also useful.

## Key takeaways
- An address in a packet is a claim, not cryptographic proof of the sender.
- Encryption hides protected content but leaves observable metadata.
- BCP 38 filters unauthorised source prefixes; it does not identify every individual sender.

## Further reading
- [RFC 2827 (BCP 38): Network Ingress Filtering](https://www.rfc-editor.org/rfc/rfc2827)
- [RFC 6528: Defending against Sequence Number Attacks](https://www.rfc-editor.org/rfc/rfc6528)
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [Man-in-the-middle attack — Wikipedia](https://en.wikipedia.org/wiki/Man-in-the-middle_attack)
