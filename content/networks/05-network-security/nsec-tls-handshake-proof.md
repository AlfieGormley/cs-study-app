---
id: nsec-tls-handshake-proof
title: What the TLS 1.3 handshake proves
level: intermediate
minutes: 3
summary: The illustrated certificate handshake needs one TLS round trip before client application data.
sourceLesson: nsec-tls
---

This unit follows a full certificate-authenticated TLS 1.3 connection. Its message order explains both the latency improvement and how authentication binds the agreed keys to the intended peer.

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
5. **CertificateVerify**: a signature using the certificate's private key over a context-bound transcript value (including a fixed prefix, role-specific context string and transcript hash). This proves the server holds the key *right now*, and ties the key exchange to that identity, which is what defeats a man-in-the-middle.
6. **Finished message**: a keyed message authentication code over the whole transcript, computed with a key derived from the handshake. If an attacker altered any earlier message (say, deleted the strongest cipher suites to force a weak one), the transcripts differ and Finished fails.

The client sends its own Finished and can send application data immediately in this successful flow: one TLS round trip versus two for the conventional full TLS 1.2 flow.

If the client guessed the wrong group, the server can send a **HelloRetryRequest** naming a supported group. A retry can also request a cookie. The revised ClientHello costs an extra round trip.

### Downgrade protection and ossification

A downgrade can expose older protocol choices or weaker permitted configurations; a correctly configured TLS 1.2 connection is not automatically vulnerable to every historical attack. So a TLS 1.3 server that ends up negotiating 1.2 puts a fixed sentinel (`DOWNGRD` plus one byte) in the last 8 bytes of its random value, which 1.3 clients check.

Deployment showed a different problem: **middleboxes** that inspected TLS broke on anything unfamiliar. TLS 1.3 therefore disguises itself. The legacy version field still says 1.2 (`0x0303`), the real version goes in a `supported_versions` extension, and dummy ChangeCipherSpec messages are sent so the handshake looks like a resumed 1.2 session. QUIC reduces exposed protocol details with packet encryption and partial header protection, while fields such as connection IDs and version remain visible.

## Key takeaways
- The illustrated certificate handshake needs one TLS round trip before client application data.
- CertificateVerify binds proof of a private key to the handshake context.
- Finished authenticates the transcript; compatibility fields support older middleboxes.

## Further reading
- [RFC 9846: TLS 1.3 (2026 revision)](https://www.rfc-editor.org/rfc/rfc9846.html)
- [RFC 8446: original TLS 1.3 specification](https://www.rfc-editor.org/rfc/rfc8446)
- [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/)
- [RFC 9849: TLS Encrypted Client Hello](https://www.rfc-editor.org/rfc/rfc9849.html)
- [Ballot SC081v3: reducing certificate validity periods — CA/Browser Forum](https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/)
- [Certificate Transparency — MDN](https://developer.mozilla.org/en-US/docs/Web/Security/Certificate_Transparency)
- [ssl: TLS/SSL wrapper for socket objects — Python docs](https://docs.python.org/3/library/ssl.html)
