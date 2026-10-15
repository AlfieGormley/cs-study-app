---
id: crypto-forward-secrecy
sourceLesson: crypto-key-exchange
title: Ephemeral keys, erasure and future compromise
level: advanced
minutes: 3
summary: Fresh erased ephemeral secrets protect recorded sessions against later long-term-key compromise.
---

## Ephemeral keys and forward secrecy

Compare two historical TLS handshake families (this table omits PSK and resumption modes):

| Approach | If server key leaks later |
|---|---|
| RSA key transport | All recorded sessions exposed |
| Ephemeral (EC)DHE | Past sessions stay safe |

With **RSA key transport** (TLS 1.2 and earlier), the client encrypts a premaster secret to the server's long-term RSA key; the protocol derives traffic keys from it. A passive recording containing the required handshake and traffic can then be decrypted if that RSA private key is later compromised.

With **ephemeral** Diffie–Hellman (DHE or ECDHE), both sides generate a fresh key pair for every connection and delete it afterwards. The long-term key only *signs* the exchange. Stealing it later lets an attacker impersonate the server in future, but past session keys are gone. This property is **forward secrecy** (or perfect forward secrecy). TLS 1.3 made ephemeral key exchange mandatory for certificate-based handshakes and removed RSA key transport.

The Signal Protocol's Double Ratchet evolves message keys and periodically incorporates fresh DH material. Erasure protects older keys; recovery after compromise requires fresh secret contributions no longer visible to the attacker. Continuous endpoint access or retained keys can prevent recovery, so there is no guaranteed short exposure window.

## Beyond classical DH

Shor's algorithm on a large quantum computer would solve discrete logs and break DH and ECDH. Because recorded traffic could be decrypted later, browsers and CDNs have already deployed **hybrid** key exchange, X25519 combined with ML-KEM-768, so a correctly constructed and authenticated hybrid can retain key-establishment secrecy if one component remains secure under its assumptions. This does not protect compromised endpoints or broken authentication.

## Key takeaways
- Fresh erased ephemeral secrets protect recorded sessions against later long-term-key compromise.
- Quantum-resistant hybrid exchange and endpoint security address different risks.

## Further reading
- [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [NIST FIPS 203: ML-KEM](https://csrc.nist.gov/pubs/fips/203/final)
