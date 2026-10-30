---
id: crypto-dh-authentication
sourceLesson: crypto-key-exchange
title: Stop a man in the middle with authenticated keys
level: advanced
minutes: 4
summary: An active attacker can substitute DH shares and establish separate secrets with each victim.
---

In the toy DH exchange, Alice’s secret exponent is 6, Bob’s is 15 and their public values are 8 and 19, modulo 23 with generator 5. Mallory can replace the values in transit.

## Man in the middle: why DH must be authenticated

Plain DH protects against a **passive** eavesdropper. It does nothing against an **active** attacker who can change messages. Mallory sits in the middle and runs a separate exchange with each side, using her own secret exponent, 3:

```
Alice ---8--->  Mallory  ---10--> Bob
Alice <--10---  Mallory  <--19--- Bob

Mallory's public value: 10

Alice and Mallory share: 6
Bob and Mallory share:   5
```

Each victim performs a perfectly normal exchange, just with Mallory instead of the other victim. Mallory knows her own secret exponent and has seen both victims' public values, so she can compute both resulting keys: 6 with Alice and 5 with Bob.

Alice thinks she shares key 6 with Bob; she actually shares it with Mallory. Bob shares key 5 with Mallory. Mallory decrypts each message, reads or alters it, and re-encrypts it for the other side. Neither notices.

> [!analogy] Real-world analogy: A switchboard operator you never chose
> Alice asks the operator to connect her to Bob. The operator instead answers Alice personally, places a separate call to Bob, and relays every sentence between the two lines, reading and editing as they go. Each call is private between its two ends, yet neither end is talking to whom they think.
>
> **How it maps:** Each phone line is a separate DH exchange, and the operator is Mallory. Both victims get a working encrypted channel, but the other end of each channel is the attacker. Encryption works perfectly; identity is what is missing.
>
> **Where it stops:** On the phone you might recognise a voice. A DH public value carries no identity at all, so recognition has to be added deliberately, by signing the exchange with a key the other side already trusts (a certificate, a pinned host key or a pre-configured static public key).

DH tells you "I share a key with whoever sent this number". It doesn't tell you *who* sent it. Every real protocol therefore **authenticates** the exchange:

- **Certificate-authenticated TLS 1.3**: `CertificateVerify` signs a context string and the transcript hash up to that point. The client verifies the signature, certificate chain and intended server identity. PSK modes authenticate differently.
- **SSH**: the server signs the exchange with its host key; a correctly configured client verifies a trusted host key, often stored in `known_hosts`, and rejects unexpected changes. Accepting an unverified first key can pin an attacker.
- **Signal Protocol**: long-term identity keys are mixed into the exchange, and users can compare "safety numbers" out of band.
- **WireGuard**: each peer is configured with the other's static public key in advance.

> [!warning] Unauthenticated DH is a classic home-made protocol bug
> "We do Diffie–Hellman, so it's secure" is not true. Without authentication, a MITM is trivial. This is one of many reasons to use TLS or a Noise-based library rather than designing a protocol.

## Key takeaways
- An active attacker can substitute DH shares and establish separate secrets with each victim.
- Authenticate the exchange and intended peer using the protocol’s specified trust mechanism.

## Further reading
- [Diffie and Hellman: New Directions in Cryptography](https://ee.stanford.edu/~hellman/publications/24.pdf)
- [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [RFC 7748: X25519 and X448](https://www.rfc-editor.org/rfc/rfc7748)
