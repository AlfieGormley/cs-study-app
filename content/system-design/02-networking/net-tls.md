---
id: net-tls
title: "TLS and HTTPS: handshakes, certificates and termination"
level: intermediate
minutes: 14
summary: What a TLS handshake does and costs, how certificate trust works, where to terminate TLS in your architecture, and how to claw back handshake latency.
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

**A full TLS 1.2 handshake takes two round trips.** In the first, the client offers options and the server replies with its choice, certificate and key-exchange parameters. Only in the second does the client send its key share and both sides exchange Finished. (Extensions like TLS False Start let a TLS 1.2 client send data a round trip early, and a resumed TLS 1.2 session takes one round trip, but a full handshake is two.)

If the server doesn't support the group the TLS 1.3 client guessed, it replies with a **HelloRetryRequest** and the client tries again, costing an extra round trip. Clients offer supported groups such as X25519; the exact preference and use of hybrid post-quantum groups depend on implementation and version.

TLS 1.3 also dropped legacy, insecure options (RSA key exchange, CBC ciphers, SHA-1), and certificate-based handshakes use ephemeral key agreement for **forward secrecy**: later theft of the certificate private key does not decrypt recorded sessions. PSK-only resumption is an exception, and 0-RTT early data lacks forward secrecy against later compromise of its PSK.

## Certificates and the chain of trust

A certificate binds a public key to one or more names, signed by a **certificate authority (CA)**.

```
Root CA  (in OS/browser trust store)
   |
   | signs
   v
Intermediate CA
   |
   | signs
   v
Leaf: shop.example.com
```

The client verifies:

1. The leaf certificate's names (in the **Subject Alternative Name** field) include the hostname. A wildcard `*.example.com` covers `shop.example.com` but not `a.b.example.com` or `example.com`.
2. Each certificate in the chain is signed by the next, ending at a **root** in its trust store.
3. The applicable validity periods and certificate constraints pass validation. Revocation handling depends on client policy; a successful connection does not prove that every certificate was checked online.

The server must send the leaf **and intermediates**. A missing intermediate is a classic bug: it works in desktop browsers (which may cache or fetch intermediates) but fails in mobile apps and `curl`.

### Issuance and automation

**Let's Encrypt** offers free certificates and automated issuance through ACME. Its classic profile is scheduled to move from 90 to 64 days on 10 February 2027, then to 45 days on 16 February 2028; its tlsserver profile moved to 45 days in May 2026. The CA/Browser Forum maximum for publicly trusted TLS certificates becomes 200 days on 15 March 2026, 100 days on 15 March 2027 and 47 days on 15 March 2029. Automate renewal and monitor expiry to make these shorter cycles manageable. These public-trust requirements do not automatically govern a private PKI.

> [!note] Evidence gap
> No comparative outage dataset or reproducible TLS performance benchmark accompanies this lesson. Claims that certificate expiry is a leading outage cause, and universal throughput or signature-speed estimates, are omitted; measure your deployment.

### Revocation and transparency

- **Revocation** (CRLs, OCSP) is unreliable in practice; many clients don't check it strictly, and browsers instead push compressed revocation lists to themselves (Chrome's CRLSets, Firefox's CRLite). **OCSP stapling** lets the server attach a fresh signed status to the handshake, saving the client a lookup, but OCSP is in decline: the CA/Browser Forum made it optional, and Let's Encrypt shut its OCSP service down in 2025 in favour of CRLs. Shorter lifetimes complement revocation by limiting how long an unrevoked certificate can remain valid.
- **Certificate Transparency (CT)** uses public append-only logs; browser CT policies require qualifying publicly trusted certificates to have evidence of logging. Private certificates are not universally subject to CT. You can monitor them for certificates issued for your domains that you didn't request.
- **CAA DNS records** restrict which CAs may issue for your domain.

## Where to terminate TLS

"Termination" is where the encrypted connection ends and traffic is decrypted. You have three main patterns:

| Pattern | Where decrypted | Trade-off |
|---|---|---|
| Edge termination | LB / CDN | Simple; internal hop plaintext |
| Re-encryption | LB, then again at app | Encrypts both hops; adds another TLS connection and requires backend authentication policy |
| Passthrough | App server only | LB can't see HTTP (L4 only) |

```
Edge termination:
Client ==TLS==> LB --HTTP--> App

Re-encryption:
Client ==TLS==> LB ==TLS==> App

Passthrough:
Client ==========TLS========> App
           (LB forwards TCP)
```

**Edge termination** is the common default. The load balancer holds the certificate, offloads crypto from app servers, and can inspect HTTP to route by path, add headers like `X-Forwarded-For` and `X-Forwarded-Proto`, and apply a WAF.

But "plaintext inside the network" is increasingly unacceptable. **Zero-trust** designs and the risk of attackers moving laterally inside networks motivate **re-encryption** or **mutual TLS (mTLS)** between services. Validate backend identities as well as encrypting connections; encryption alone does not establish which service you reached. Service meshes automate mTLS so every service gets a certificate and identity.

**Passthrough** is used when the app must hold the key (end-to-end requirements) or needs the raw TLS session (e.g. for client certificates). The load balancer can still route by **SNI**, which is visible in the ClientHello, but can't see paths or headers. **Encrypted Client Hello (ECH)** hides the real SNI inside an encrypted inner ClientHello; an SNI-routing balancer then sees only the outer, public name unless it holds the ECH keys itself.

> [!note] Keys at the edge
> Edge termination on a CDN means a third party holds your private key or terminates on your behalf. For highly sensitive keys, options include short-lived delegated credentials or "keyless" setups where the CDN calls back to your own key server for the signing step.

## The latency cost, and how to reduce it

In the simplified model with no DNS delay, TCP Fast Open, handshake retry, loss or processing delay, a new HTTPS connection over TCP costs **TCP (1 RTT) + TLS 1.3 (1 RTT)** before the request goes out. At 100 ms RTT, that's 200 ms of pure setup. Ways to cut it:

1. **Use TLS 1.3.** Saves a full RTT over TLS 1.2.
2. **Session resumption.** The server hands the client a *session ticket*; next time, the handshake skips certificate exchange and verification (less CPU and fewer bytes).
3. **0-RTT (early data).** With a ticket, TLS 1.3 lets the client send its request *in the first flight*. Setup cost on resumption drops to just the TCP handshake (or nothing extra with QUIC).

Putting the round trips together, before the first request byte can leave the client:

| Setup | New | Resumed |
|---|---|---|
| TCP + TLS 1.2 | 3 RTT | 2 RTT |
| TCP + TLS 1.3 | 2 RTT | 2 (1 with 0-RTT) |
| QUIC | 1 RTT | 1 (0 with 0-RTT) |

Note that plain TLS 1.3 resumption *without* early data saves CPU and bytes, not round trips: it still takes a full round trip before the request goes out.
4. **Terminate close to the user.** Handshakes at a CDN edge 10 ms away cost 20 ms, not 200 ms. The edge keeps warm, long-lived connections to the origin.
5. **Reuse connections.** The best handshake is the one you don't do.
6. **Keep certificate chains small.** For comparable certificate fields, ECDSA P-256 uses smaller keys and signatures than RSA-2048; actual certificate size and signing time depend on the chain and implementation. Oversized chains can overflow TCP's initial window and add an RTT.

> [!warning] 0-RTT replay
> Early data has no protection against replay across connections: an attacker who captures the first flight can resend it. Servers must assess **replay safety**, not merely idempotency. RFC 8470 permits clients, absent other information, to send only safe HTTP methods in early data. Even a nominal `GET` requires care if its implementation has sensitive side effects. When Cloudflare launched 0-RTT in 2017, it answered only `GET` requests without query parameters in early data, and tagged them with a header so the origin could spot replays. RFC 8470 standardises this pattern: a proxy adds `Early-Data: 1`, and an origin that won't risk it replies `425 Too Early`, making the client retry after the handshake completes.

### CPU cost

TLS CPU cost includes bulk encryption, handshake signatures and key exchange. Their relative cost depends on hardware, cryptographic library, algorithms, record sizes and connection reuse. Benchmark representative traffic before sizing load balancers; resumption and connection reuse can reduce handshake work.

## mTLS: when the client authenticates too

In normal TLS only the server presents a certificate. In **mutual TLS**, the client does too. That's common for:

- Service-to-service traffic in a mesh (Istio, Linkerd issue a certificate per workload).
- B2B APIs and payment networks.
- IoT devices with a certificate burned in at manufacture.

The hard part isn't the protocol but **certificate lifecycle**: issuing, rotating (at a configured lifetime and renewal interval) and revoking at scale. That's what mesh control planes and tools like SPIFFE/SPIRE automate.

## Key takeaways

- TLS provides confidentiality, integrity and server authentication; TLS 1.3 needs 1 RTT, TLS 1.2 needed 2.
- Trust flows from a root CA through intermediates to the leaf; always serve the full chain.
- Automate certificate renewal and monitor expiry to prevent avoidable outages.
- Terminate at the edge for simplicity, re-encrypt or use mTLS when the internal network isn't trusted.
- Cut handshake latency with TLS 1.3, resumption, edge termination and connection reuse; accept 0-RTT only when the application can safely tolerate replay.

## Further reading

- [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [High Performance Browser Networking: TLS](https://hpbn.co/transport-layer-security-tls/)
- [How Let's Encrypt works](https://letsencrypt.org/how-it-works/)
- [Certificate Transparency (Wikipedia)](https://en.wikipedia.org/wiki/Certificate_Transparency)
- [Introducing 0-RTT (Cloudflare blog)](https://blog.cloudflare.com/introducing-0-rtt/)
