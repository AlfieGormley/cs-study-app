---
id: nsec-amplification-controls
title: Headers and amplification controls
level: basic
minutes: 3
summary: Headers and fragmentation change amplification measured at the IP or link layer.
sourceLesson: nsec-threats
---

The previous unit counted response payload bytes per request payload byte. This unit compares that number with the IP-packet ratio, then identifies controls at senders, reflectors and the victim’s upstream network.

Two subtleties:

**Headers dilute the factor.** A UDP datagram carried in one IPv4 packet with no options has 28 bytes of IP and UDP headers (20 for IPv4, 8 for UDP); link-layer overhead is additional. The same 28 bytes are added to both the request and the response, but they are a much bigger share of a small request. So the ratio measured on whole IP packets is lower than the payload ratio, and falls most when the request is tiny. For a 40-byte request and 1,400-byte response, the payload BAF of 35 becomes about 21 at the IP-packet level:

```formula reference
BAF_IP = (B_resp + H) / (B_req + H)
where
BAF_IP: the amplification factor counting IP and UDP headers as well as payload, a plain ratio
B_resp: the response payload, in bytes
B_req: the request payload, in bytes
H: the IPv4 header (20 bytes) plus the UDP header (8 bytes), 28 bytes per packet in this unfragmented model
In words: adding the same header bytes to both sides shrinks the ratio, and shrinks it most when the request is small.
```

A full link-level ratio also needs link-layer framing and packetisation, which dilute it further.

**Packet amplification** matters too. One request producing many response packets multiplies the packets per second, which stresses routers and firewalls as well as links.

### Defending against amplification

- **Do not be a reflector**: close open resolvers, disable NTP `monlist`, never expose memcached (UDP 11211) to the internet. Memcached disabled UDP by default from version 1.5.6 after the 2018 attacks.
- **BCP 38** ingress filtering at ISPs, so spoofed packets never leave the attacker's network.
- **Protocol design**: cap amplification before validating a peer's address. QUIC permits up to three times the received UDP payload bytes before address validation; this bounds amplification rather than eliminating it.
- **Upstream scrubbing and anycast** to spread and absorb the flood.

QUIC's rule shows how protocol design can bound amplification: until a server has confirmed the client can receive at its claimed address, it may send at most three times the bytes it has received. Clients must pad UDP datagrams that carry Initial packets to at least 1,200 bytes of payload, so even the first flight gives the server some room. If the server's handshake (for example a long certificate chain) needs more, it must wait for more client bytes or validate the address first, for example with a Retry token.

## Key takeaways
- Headers and fragmentation change amplification measured at the IP or link layer.
- Source validation and closing reflectors reduce the available attack paths.
- QUIC bounds pre-validation amplification; it does not eliminate amplification.

## Further reading
- [RFC 2827 (BCP 38): Network Ingress Filtering](https://www.rfc-editor.org/rfc/rfc2827)
- [RFC 9000: QUIC, section 8 (address validation)](https://www.rfc-editor.org/rfc/rfc9000#section-8)
- [UDP-Based Amplification Attacks — CISA](https://www.cisa.gov/news-events/alerts/2014/01/17/udp-based-amplification-attacks)
