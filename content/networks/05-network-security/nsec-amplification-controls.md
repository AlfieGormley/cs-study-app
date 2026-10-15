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

**Headers dilute the factor in this unfragmented example.** A UDP datagram carried in one IPv4 packet with no options has 28 bytes of IP and UDP headers (20 for IPv4, 8 for UDP); link-layer overhead is additional. For a 40-byte request and 1,400-byte response, the payload BAF is 35, but counting the IP and UDP headers too gives a lower ratio:

```formula
BAF_IP = (B_resp + H) / (B_req + H)
BAF_IP = (1400 + 28) / (40 + 28)
BAF_IP = 1428 / 68 = 21
where
BAF_IP: the amplification factor counting IP and UDP headers as well as payload, a plain ratio
B_resp: the response payload, in bytes; here 1,400
B_req: the request payload, in bytes; here 40
H: the IPv4 header (20 bytes) plus the UDP header (8 bytes), 28 bytes per packet
In words: adding the same 28 header bytes to both sides shrinks the ratio, and shrinks it most when the request is small: 35 on payload alone becomes 21 at the IP level.
```

A full link-level ratio also needs link-layer framing and packetisation, which dilute it further.

**Packet amplification** matters too. One request producing many response packets multiplies the packets per second, which stresses routers and firewalls as well as links.

### Defending against amplification

- **Do not be a reflector**: close open resolvers, disable NTP `monlist`, never expose memcached (UDP 11211) to the internet. Memcached disabled UDP by default from version 1.5.6 after the 2018 attacks.
- **BCP 38** ingress filtering at ISPs, so spoofed packets never leave the attacker's network.
- **Protocol design**: cap amplification before validating a peer's address. QUIC permits up to three times the received UDP payload bytes before address validation; this bounds amplification rather than eliminating it.
- **Upstream scrubbing and anycast** to spread and absorb the flood.

> [!note] Content omitted after review
> Universal attack-success rates, firewall mistake rankings and provider capacity guarantees are absent: this review has no representative measurement supporting those claims. Historical amplification figures in the preceding unit retain their original measurement scope.

## Key takeaways
- Headers and fragmentation change amplification measured at the IP or link layer.
- Source validation and closing reflectors reduce the available attack paths.
- QUIC bounds pre-validation amplification; it does not eliminate amplification.

## Further reading
- [UDP-Based Amplification Attacks — CISA](https://www.cisa.gov/news-events/alerts/2014/01/17/udp-based-amplification-attacks)
- [RFC 2827 (BCP 38): Network Ingress Filtering](https://www.rfc-editor.org/rfc/rfc2827)
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [Amplification Hell: Revisiting Network Protocols for DDoS Abuse (NDSS 2014)](https://www.ndss-symposium.org/ndss2014/programme/amplification-hell-revisiting-network-protocols-ddos-abuse/)
- [February 28th DDoS incident report — GitHub blog](https://github.blog/news-insights/company-news/ddos-incident-report/)
- [Understanding the Mirai Botnet (USENIX Security 2017)](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/antonakakis)
