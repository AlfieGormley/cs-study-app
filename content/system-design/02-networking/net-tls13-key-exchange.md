---
id: net-tls13-key-exchange
title: "TLS 1.3 key exchange and identity"
level: intermediate
minutes: 3
summary: "Follow the encrypted handshake and distinguish certificate authentication from ephemeral key agreement."
sourceLesson: net-tls
---
TLS (Transport Layer Security) is what puts the S in HTTPS. It gives a connection three properties:

- **Confidentiality:** nobody on the path can read the traffic.
- **Integrity:** nobody can modify it undetected.
- **Authentication:** the client knows it's talking to the real `bank.example.com`, not an impostor.

For system design, TLS matters because of its **latency cost** (extra round trips), its **CPU cost** (key exchange) and the architectural question of **where you terminate it**.

## The TLS 1.3 handshake

A normal certificate-authenticated TLS 1.3 handshake (RFC 8446, 2018), without retry or early data, needs one round trip before the client sends application data:

```
Client                       Server
  |-- ClientHello ------------>|
  |   versions, ciphers,       |
  |   key share, SNI, ALPN     |
  |                            |
  |<-- ServerHello ------------|
  |    key share               |
  |    {EncryptedExtensions}   |
  |    {Certificate}           |
  |    {CertificateVerify}     |
  |    {Finished}              |
  |                            |
  |-- {Finished} + {GET /} --->|
  |<-- {200 OK} ---------------|
```

Step by step:

1. **ClientHello.** The client lists supported versions and cipher suites, and *guesses* a key-exchange group, sending its public key share up front. It includes **SNI** (the hostname) and **ALPN** (which protocols it speaks, e.g. `h2`, `http/1.1`).
2. **ServerHello.** The server picks parameters, sends its own key share, and both sides now derive the same secret via (EC)DHE key exchange. Everything after this is encrypted, including the certificate.
3. **Certificate + CertificateVerify.** The server proves it owns the private key matching its certificate by signing the handshake transcript.
4. **Finished.** Both sides confirm the handshake wasn't tampered with. The client can send its HTTP request immediately alongside its Finished message.

> [!analogy] Real-world analogy: Mixing paint in public
> Two people openly agree on a common base colour. Each secretly picks a colour of their own, mixes it into the base and hands the mixture over in public. Each then adds their own secret colour to the mixture they received, and both end up with the same final colour. An onlooker saw the base and both mixtures but cannot practically un-mix them to find either secret.
>
> **How it maps:** the base colour is the agreed key-exchange group, each secret colour is an ephemeral private key and each public mixture is a key share sent in the ClientHello or ServerHello. The final colour is the secret both endpoints derive, from which the session keys come. Because the secret colours are fresh for every connection, stealing the certificate key later does not reveal them: that is forward secrecy.
>
> **Where it stops:** mixing paint does not tell you who you are mixing with; an attacker in the middle could mix separately with each side. That is why the server also signs the handshake with its certificate key (CertificateVerify). The real protection rests on mathematical problems that are hard to reverse, not on colours being hard to separate.

**A full TLS 1.2 handshake takes two round trips.** In the first, the client offers options and the server replies with its choice, certificate and key-exchange parameters. Only in the second does the client send its key share and both sides exchange Finished. (Extensions like TLS False Start let a TLS 1.2 client send data a round trip early, and a resumed TLS 1.2 session takes one round trip, but a full handshake is two.)

If the server doesn't support the group the TLS 1.3 client guessed, it replies with a **HelloRetryRequest** and the client tries again, costing an extra round trip. Clients offer supported groups such as X25519; the exact preference and use of hybrid post-quantum groups depend on implementation and version.

TLS 1.3 also dropped legacy, insecure options (RSA key exchange, CBC ciphers, SHA-1), and certificate-based handshakes use ephemeral key agreement for **forward secrecy**: later theft of the certificate private key does not decrypt recorded sessions. PSK-only resumption is an exception, and 0-RTT early data lacks forward secrecy against later compromise of its PSK.

## Key takeaways

- ClientHello carries a key share; the server’s response lets both endpoints derive secrets in one round trip.
- CertificateVerify proves possession of the certificate private key; (EC)DHE supplies ephemeral agreement.
- HelloRetryRequest adds a trip, and early data or PSK-only resumption has different forward-secrecy guarantees.

## Further reading

- [TLS 1.3 (RFC 8446)](https://www.rfc-editor.org/rfc/rfc8446)
- [TLS (High Performance Browser Networking)](https://hpbn.co/transport-layer-security-tls/)
