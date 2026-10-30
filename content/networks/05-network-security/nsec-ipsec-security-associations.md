---
id: nsec-ipsec-security-associations
title: IPsec negotiation, ESP and NAT traversal
level: advanced
minutes: 4
summary: IKEv2 authenticates peers and negotiates SAs; ESP protects data according to those SAs.
sourceLesson: nsec-vpns
---

IPsec separates negotiation from packet protection. Follow both roles before debugging an apparently connected VPN: successful initial IKE messages do not prove that later negotiation and ESP data can pass.

## IPsec

**IPsec** secures IP packets at the network layer, and can protect selected traffic without application changes, according to configured policies. It is the standard for site-to-site VPNs between offices, data centres and cloud VPCs (AWS Site-to-Site VPN, Azure VPN Gateway).

It has two halves:

1. **IKEv2** (UDP 500) is the control plane. The peers authenticate each other (with certificates or a pre-shared key), agree on algorithms and derive keys. IKE establishes a bidirectional IKE SA (with separate 64-bit initiator/responder SPIs) and negotiates Child SAs for data traffic. An ESP Child-SA pair contains unidirectional SAs with 32-bit SPIs.
2. **ESP** (IP protocol 50) is the data plane: it protects the selected data packets using the negotiated SA algorithms. The encrypted-and-authenticated examples here use AEAD; ESP also permits other protection combinations, including integrity without encryption.

There is also **AH** (protocol 51), which authenticates without encrypting. AH also authenticates relevant immutable IP-header fields; mutable fields receive special treatment. Address-rewriting NAT normally conflicts with that authentication.

### Transport and tunnel mode

```
Transport mode:
 [IP][ESP hdr]{TCP|data|trailer}[ICV]

Tunnel mode:
 [new IP][ESP hdr]
   {inner IP|TCP|data|trailer}[ICV]

 {braces} = encrypted portion
```

For these confidentiality-enabled ESP examples, **tunnel mode** encrypts the original IP packet, including its inner addresses, and is suitable for site-to-site VPNs. **Transport mode** leaves the original IP header outside encryption. The ESP trailer is encrypted; the ESP header and authentication tag are not. Actual protection follows the negotiated algorithms.

ESP tunnel mode adds a new outer IP header, the ESP header (SPI and sequence number), a per-packet initialisation vector, a trailer and an integrity tag. For AES-GCM over IPv4 with a 16-byte tag and no extra options, that is 54 to 57 bytes per packet:

```
outer IPv4                20
ESP header (SPI + seq)     8
IV (AES-GCM)               8
padding                  0-3
pad length + next header   2
ICV (integrity tag)       16
total                  54-57
```

The padding varies because ESP must make the encrypted part end on a 4-byte boundary, so the exact overhead depends on the inner packet's length. Other algorithms, IPv6 outer headers and traffic-flow padding change the total.

### NAT traversal

ESP has no TCP/UDP ports, complicating port-based NAT multiplexing; some devices implement ESP-specific passthrough. When IKE detects a NAT on the path, both peers switch to **NAT-T**: ESP is wrapped in UDP on port 4500, adding another 8 bytes per packet, which shrinks the inner packet budget again. If a site-to-site VPN negotiates but no traffic flows, check that UDP 500 and 4500 (and protocol 50, if there is no NAT) are allowed.

> [!analogy] Real-world analogy: agreeing a courier contract, then sending sealed pouches
> Two offices first hold a meeting where each proves who it is and they agree the locks, keys and reference numbers they will use. Afterwards, every package travels in a sealed pouch stamped with the agreed reference number, so the receiving office knows which key opens it.
>
> **How it maps:** The meeting is IKEv2, the control plane that authenticates the peers and negotiates Security Associations. The sealed pouches are ESP packets, the data plane. The reference number on each pouch is the SPI, which tells the receiver which SA (keys and algorithms) to use, and there is a separate agreement for each direction.
>
> **Where it stops:** IKE keeps running after setup, rekeying and checking the peer is alive, and its messages travel over the same network paths as the data. A firewall that lets the meeting happen but blocks the pouches (for example UDP 4500 behind a NAT) leaves a tunnel that looks negotiated but carries nothing.

## Key takeaways
- IKEv2 authenticates peers and negotiates SAs; ESP protects data according to those SAs.
- Confidentiality-enabled tunnel mode encrypts inner addresses; transport mode leaves the original IP header visible.
- NAT-T wraps ESP in UDP and changes the byte budget.

## Further reading
- [RFC 4301: Security Architecture for the Internet Protocol](https://www.rfc-editor.org/rfc/rfc4301)
- [RFC 7296: Internet Key Exchange Protocol Version 2 (IKEv2)](https://www.rfc-editor.org/rfc/rfc7296)
- [RFC 4303: IP Encapsulating Security Payload (ESP)](https://www.rfc-editor.org/rfc/rfc4303)
- [RFC 3948: UDP Encapsulation of IPsec ESP Packets](https://www.rfc-editor.org/rfc/rfc3948)
