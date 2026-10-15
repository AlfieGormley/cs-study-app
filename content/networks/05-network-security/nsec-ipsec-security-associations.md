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

With a 16-byte tag, no extra options or traffic-flow padding, ESP tunnel mode using AES-GCM adds 54 to 57 bytes over IPv4. Padding varies because ESP must make the encrypted part end on a 4-byte boundary:

```formula
O_ESP = H_IP + H_ESP + IV + P + T + ICV
O_min = 20 + 8 + 8 + 0 + 2 + 16 = 54 B
O_max = 20 + 8 + 8 + 3 + 2 + 16 = 57 B
where
O_ESP: the total bytes ESP tunnel mode adds to each packet
O_min: the overhead with no padding needed
O_max: the overhead with the most padding (3 bytes)
H_IP: the new outer IPv4 header, 20 bytes
H_ESP: the ESP header: SPI (4 bytes) and sequence number (4 bytes), 8 bytes
IV: initialisation vector sent with each packet for AES-GCM, 8 bytes
P: padding, 0 to 3 bytes, so the ESP trailer’s final fields meet the required 4-byte alignment
T: the trailer's pad-length and next-header fields, 1 byte each, 2 bytes
ICV: integrity check value: the 16-byte authentication tag
B: bytes
In words: AES-GCM ESP tunnel mode over IPv4 costs between 54 and 57 bytes per packet, depending on how much padding the inner packet needs.
```

### NAT traversal

ESP has no TCP/UDP ports, complicating port-based NAT multiplexing; some devices implement ESP-specific passthrough. When IKE detects a NAT on the path, both peers switch to **NAT-T**: ESP is wrapped in UDP on port 4500, adding another 8 bytes. If a site-to-site VPN negotiates but no traffic flows, check that UDP 500 and 4500 (and protocol 50, if there is no NAT) are allowed.

## Key takeaways
- IKEv2 authenticates peers and negotiates SAs; ESP protects data according to those SAs.
- Confidentiality-enabled tunnel mode encrypts inner addresses; transport mode leaves the original IP header visible.
- NAT-T wraps ESP in UDP and changes the byte budget.

## Further reading
- [RFC 4301: Security Architecture for the Internet Protocol](https://www.rfc-editor.org/rfc/rfc4301)
- [RFC 4303: IP Encapsulating Security Payload (ESP)](https://www.rfc-editor.org/rfc/rfc4303)
- [WireGuard: Next Generation Kernel Network Tunnel (whitepaper)](https://www.wireguard.com/papers/wireguard.pdf)
- [WireGuard: protocol and cryptography](https://www.wireguard.com/protocol/)
- [RFC 7348: Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348)
- [RFC 4459: MTU and Fragmentation Issues with In-the-Network Tunneling](https://www.rfc-editor.org/rfc/rfc4459)
