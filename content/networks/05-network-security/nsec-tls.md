---
id: nsec-tls
title: TLS 1.3, certificates, ECH and mTLS
level: intermediate
minutes: 15
summary: What happens in a TLS 1.3 handshake and why each message is there, how certificate chains are validated and revoked, what Encrypted Client Hello hides, and how mutual TLS authenticates both ends.
---

TLS (Transport Layer Security) is the protocol behind the padlock: HTTPS and configured secure SMTP/IMAP use TLS. QUIC version 1 uses the TLS 1.3 handshake for authentication and key establishment, while QUIC applies its own packet protection. Lesson 1 showed that encryption alone does not stop a man-in-the-middle; you also need to know *who* you are talking to. Correctly configured TLS can provide both; peer verification and the negotiated authentication mode matter.

This lesson takes the network engineer's view: what is on the wire, what each message proves, and what goes wrong in production. How the ciphers and key exchanges work mathematically is covered in the Security & Cryptography subject.

## What TLS does and does not protect

TLS gives a connection three properties:

- **Confidentiality**: only the two endpoints can read the data.
- **Integrity**: protected records reject unauthorised changes under the cryptographic assumptions; this does not prevent packet loss, delay or all denial of service.
- **Authentication**: in the certificate-based mode below, the client validates the server identity and proof of its private key. PSK modes use a different credential. Client certificate authentication is optional (mTLS, below).

It does **not** hide:

- IP addresses and ports (they are in the IP and TCP headers).
- Sizes and timing of records, which can leak which page you visited.
- Traditionally, the hostname, sent in clear in the **SNI** (Server Name Indication) extension so a server hosting many sites knows which certificate to present. ECH fixes this (below).

## Why TLS 1.3 was needed

The pre-TLS-1.3 ecosystem retained legacy protocol versions, cipher suites and implementations with weaknesses. TLS 1.2 CBC suites were exposed to timing and padding-oracle implementation attacks; original POODLE targeted SSL 3.0. RSA key transport also lacks forward secrecy: later compromise of its decryption key can expose recorded handshakes using that key. A conventional full TLS 1.2 handshake takes two TLS round trips before client application data, excluding TCP setup and False Start.

TLS 1.3 (RFC 8446, 2018) took a hard line:

| Removed | Why |
|---|---|
| RSA key transport, static DH | No forward secrecy |
| CBC modes, RC4 | Padding and bias attacks |
| SHA-1, MD5 in signatures | Collisions |
| Compression | CRIME attack |
| Renegotiation | Complex, attacked |

What is left is small. RFC 8446 originally defines five cipher suites, all **AEAD** (authenticated encryption), the common ones being `TLS_AES_128_GCM_SHA256`, `TLS_AES_256_GCM_SHA384` and `TLS_CHACHA20_POLY1305_SHA256`. Certificate-authenticated TLS 1.3 uses ephemeral key establishment. RFC 8446 also permits PSK-only `psk_ke`, which lacks forward secrecy against later PSK compromise; PSK with ephemeral DH can provide it for post-handshake traffic. Early data has separate limitations below. Secure erasure of ephemeral/session secrets is part of the model.

## The 1-RTT handshake

This diagram shows a full certificate-authenticated handshake without HelloRetryRequest, client certificates or early data. It excludes TCP setup; implementation scheduling and transport loss can add delay.

```
Client                       Server
ClientHello
 key_share, SNI, ALPN  ------>
                        ServerHello
                         key_share
             {EncryptedExtensions}
                     {Certificate}
               {CertificateVerify}
                        {Finished}
                     <------
{Finished}             ------>
[app data]   <------>  [app data]

{ } = encrypted with handshake keys
[ ] = encrypted with traffic keys
```

Step by step:

1. **ClientHello.** The client lists versions, cipher suites and signature algorithms, and, crucially, sends a **key share** straight away. It guesses which group the server will accept (for example, X25519 when supported). It also sends SNI and ALPN (for example `h2` for HTTP/2).
2. **ServerHello.** The server picks the options and sends its own key share. Both sides can now compute a shared secret, and subsequent handshake messages in this flow are encrypted; record headers and optional compatibility ChangeCipherSpec records are exceptions.
3. **EncryptedExtensions**: the rest of the server's choices, such as the agreed ALPN.
4. **Certificate**: the server's certificate chain. In TLS 1.2 this went in clear; now a passive observer cannot see which certificate was presented.
5. **CertificateVerify**: a signature using the certificate's private key over a context-bound transcript value (including a fixed prefix, role-specific context string and transcript hash). This proves the server holds the key *right now*, and binds the key exchange to that identity, which is what defeats a man-in-the-middle.
6. **Finished**: a MAC over the whole transcript. If an attacker altered any earlier message (say, deleted the strongest cipher suites to force a weak one), the transcripts differ and Finished fails.

The client sends its own Finished and can send application data immediately in this successful flow: one TLS round trip versus two for the conventional full TLS 1.2 flow.

If the client guessed the wrong group, the server replies with a **HelloRetryRequest** naming one it supports, costing an extra round trip.

### Downgrade protection and ossification

A downgrade can expose older protocol choices or weaker permitted configurations; a correctly configured TLS 1.2 connection is not automatically vulnerable to every historical attack. So a TLS 1.3 server that ends up negotiating 1.2 puts a fixed sentinel (`DOWNGRD` plus one byte) in the last 8 bytes of its random value, which 1.3 clients check.

Deployment showed a different problem: **middleboxes** that inspected TLS broke on anything unfamiliar. TLS 1.3 therefore disguises itself. The legacy version field still says 1.2 (`0x0303`), the real version goes in a `supported_versions` extension, and dummy ChangeCipherSpec messages are sent so the handshake looks like a resumed 1.2 session. QUIC reduces exposed protocol details with packet encryption and partial header protection, while fields such as connection IDs and version remain visible.

## Resumption and 0-RTT

After a handshake, the server can issue a **session ticket**: an opaque identity associated with a resumption PSK. The client derives that PSK from resumption secrets and the ticket nonce; the ticket is not simply the raw key. A resumed handshake skips the certificate.

With a ticket, the client may also send **0-RTT early data** in its very first flight, encrypted with a key derived from the PSK. The catch is serious:

> [!warning] 0-RTT data can be replayed
> An attacker can capture the first flight and send it again. TLS does not inherently guarantee non-replay of early data. Servers can implement anti-replay state, but applications must account for the remaining risk across instances and retries. Early data lacks forward secrecy against later compromise of its PSK. Permit only requests whose actual semantics tolerate replay; an HTTP method label or idempotence alone is not a complete safety argument. A server can answer HTTP `425 Too Early` to make the client retry after the full handshake.

This is lesson 1's replay attack again, accepted deliberately in exchange for speed.

## Certificate chains

A certificate binds a public key to names, and is signed by a **certificate authority** (CA). Clients use configured **trust anchors**, often from a browser, operating system or application root store. Store membership varies. Root private keys can be kept offline while intermediate CAs perform routine issuance; this is an operational design, not a property of every CA.

The following chain-shaped example illustrates a leaf, intermediate and cross-signed root. It is not a live assertion of what `www.rfc-editor.org` currently serves:

```
0 leaf:  CN=rfc-editor.org
         issued by WE1
1 inter: WE1 (Google Trust Services)
         issued by GTS Root R4
2 cross: GTS Root R4
         issued by GlobalSign Root CA
```

The server sends its leaf and needed intermediates. A client must independently trust a suitable anchor. Item 2 illustrates a **cross-signed certificate** for the same subject/key, with a different issuer and potentially different constraints, enabling an alternate path where supported.

Certificate validation includes the following checks (this is not an exhaustive validation algorithm; path-length/name constraints and unsupported critical extensions also matter):

1. Each signature verifies with the issuer's public key, up to a root it trusts.
2. The leaf and intermediate certificates in the validation path are within their validity dates; trust-anchor handling is a separate client-policy input.
3. The leaf's **Subject Alternative Name** matches the hostname. (Browsers ignore the old Common Name field.)
4. Intermediates are marked as CAs (`basicConstraints CA:TRUE`) and allowed to issue.
5. The leaf is allowed for server authentication (extended key usage).
6. Applicable browser policies require **Certificate Transparency** evidence for publicly trusted certificates. A signed certificate timestamp is a log's promise to include the certificate, not itself an inclusion proof; SCTs need not be embedded in the certificate. Monitoring helps detect misissuance.

> [!example] "It works in Chrome but not in curl"
> The server sends only its leaf, not the intermediate. Desktop browsers often cope, because they cache intermediates or fetch them from a URL in the certificate. Other clients may fail with "unable to get local issuer certificate"; fetching and caching depend on the TLS backend, trust store and configuration, not just the application name. The fix is on the server: serve the full chain (leaf plus intermediates).

### Revocation and short lifetimes

If a private key leaks, the certificate must be **revoked**. The two classic mechanisms are **CRLs** (lists of revoked serial numbers) and **OCSP** (ask the CA about one certificate). Direct OCSP requests can reveal certificate lookups to the responder. Some clients **soft-fail** when status cannot be retrieved; others use different revocation mechanisms or policies. Blocking a responder can therefore undermine a soft-fail check. **OCSP stapling** lets the server attach a recent signed OCSP response itself.

The industry's answer has shifted to **short-lived certificates**. Let's Encrypt shut down its OCSP service in 2025 in favour of CRLs. The CA/Browser Forum has cut the maximum lifetime of public certificates from 398 days to 200 days (from March 2026), falling to 100 days in 2027 and 47 days in 2029. Short lifetimes limit the damage of an unrevoked key, and make reliable renewal and monitoring more demanding. **Automated renewal** (for example ACME) is a practical approach, not a mathematical requirement imposed by the lifetime alone.

Checking a server by hand:

```python
import socket, ssl

host = "www.rfc-editor.org"
ctx = ssl.create_default_context()

with socket.create_connection(
        (host, 443), timeout=10) as raw:
    with ctx.wrap_socket(
            raw,
            server_hostname=host) as tls:
        print(tls.version())
        print(tls.cipher()[0])
        cert = tls.getpeercert()
        subject = dict(
            x[0] for x in cert["subject"])
        print(subject)
```

The negotiated version, cipher and certificate subject depend on the live endpoint and local TLS stack; no fixed output is guaranteed. `create_default_context()` turns on chain and hostname verification; passing `server_hostname` sets SNI and the name to check. Code that sets `verify=False` (in `requests`) or `CERT_NONE` throws all of that away and is open to any MITM.

## Encrypted Client Hello

Even with TLS 1.3, the ClientHello is sent in clear, so the SNI reveals the site to anyone on the path, and is widely used for censorship and filtering. **Encrypted Client Hello** (ECH, RFC 9849, 2026) closes that gap:

```
ClientHelloOuter (clear)
  SNI = cloudflare-ech.com  <- public
  ech = HPKE(ClientHelloInner)
ClientHelloInner (encrypted)
  SNI = secret-site.example
```

1. The client looks up the site's DNS **HTTPS record**, which carries an `ECHConfig`: a public key and a **public name** for the provider's client-facing server.
2. It encrypts the real ClientHello with that key and wraps it in an outer ClientHello naming only the public name.
3. The provider decrypts the inner hello and completes the handshake for the real site.

ECH hides the inner ClientHello from passive observers, but the practical anonymity set depends on shared configuration, IP addresses and other metadata; a CDN is not a protocol requirement. Plaintext DNS can independently disclose the requested name. Encrypted DNS protects that hop but does not conceal it from the chosen resolver. For defenders it is a trade-off: firewalls and filters that block by SNI (lesson 6) lose that signal.

## Mutual TLS

In a full server-certificate TLS handshake, the client need not supply a certificate and may authenticate at the application layer later. For certificate-based **mutual TLS (mTLS)**, the server requests a client certificate and the client supplies Certificate and CertificateVerify when authenticating. PSK resumption does not repeat these certificate messages.

```
Server: {CertificateRequest} ...
Client: {Certificate}
        {CertificateVerify}
        {Finished}
```

Where it is used:

- **Service-to-service** traffic in zero trust designs (lesson 2). Configured service meshes can issue workload certificates and apply mTLS. For example, Istio uses SPIFFE-style identities and separate authentication/authorisation policies; permissive modes and unenrolled workloads require attention.
- **APIs** for banks and payment networks, IoT devices and internal admin tools.

Trade-offs and pitfalls:

- You usually run a **private CA**, and must issue, rotate and revoke certificates for every client. Automation is the whole game.
- A certificate proves **who** the caller is, not **what** they may do. You still need authorisation: "service `checkout` may call `POST /charge`".
- TLS terminated at a load balancer ends the mTLS there; the backend must trust the balancer to pass on the verified identity, usually in a header that clients must not be able to set themselves.

> [!note] Content omitted after review
> A universal trusted-root count, live endpoint chain/output, certificate-outage frequency and current key-exchange adoption percentages are not asserted: no reproducible dated measurements were available for those claims in this review. The handshake and chain examples are explanatory models.

## Key takeaways
- The illustrated TLS 1.3 certificate handshake provides confidentiality, integrity and authentication in one TLS round trip. Forward secrecy depends on the negotiated mode and secret handling; PSK-only and early data are important exceptions.
- CertificateVerify binds proof of the private key to the transcript. Finished authenticates the negotiated transcript, and downgrade sentinels protect relevant cross-version cases.
- 0-RTT early data is replayable; require application-specific replay-safe semantics and correct intermediary handling.
- Clients validate the chain up to a trusted root, check names and dates, and need the server to send its intermediates; revocation behavior varies, and the public Web PKI lifetime schedule reaches 47 days in 2029.
- ECH encrypts the ClientHello, hiding SNI behind a provider's public name; mTLS authenticates clients with certificates and underpins service-to-service zero trust.

## Further reading
- [RFC 8446: The Transport Layer Security (TLS) Protocol Version 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/)
- [RFC 9849: TLS Encrypted Client Hello](https://www.rfc-editor.org/rfc/rfc9849.html)
- [Ballot SC081v3: reducing certificate validity periods — CA/Browser Forum](https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/)
- [Certificate Transparency — MDN](https://developer.mozilla.org/en-US/docs/Web/Security/Certificate_Transparency)
- [ssl: TLS/SSL wrapper for socket objects — Python docs](https://docs.python.org/3/library/ssl.html)
