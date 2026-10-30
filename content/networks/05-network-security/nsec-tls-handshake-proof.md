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

> [!analogy] Real-world analogy: signed minutes of a meeting
> Two firms negotiate through a courier. At the end, each signs a copy of the full minutes, listing every proposal made and accepted. If the courier quietly struck out the best offer from one side's letter, the two sets of minutes no longer match, and the deal is void.
>
> **How it maps:** The minutes are the handshake transcript, the signatures are CertificateVerify (proof of the certificate's key) and the keyed MACs in the Finished messages (proof that both sides saw the same messages), and the meddling courier is an on-path attacker attempting a downgrade.
>
> **Where it stops:** The checks are cryptographic and immediate, and they protect only what is inside the transcript. They do not stop the courier simply refusing to deliver (a denial of service), and they cannot protect a client that is configured to fall back to an older version after a failure.

### Downgrade protection and ossification

A **downgrade attack** tries to make two parties that both support a strong option agree on a weaker one. It needs three things: an active attacker on the path who can alter or drop handshake messages, a weaker option that both ends still accept, and a way for the tampering to go unnoticed. TLS 1.3 attacks the third requirement. Finished carries a keyed MAC over the whole transcript, so editing the offered cipher suites or groups makes Finished fail. A TLS 1.3 server that ends up negotiating TLS 1.2 also puts a fixed sentinel (`DOWNGRD` plus one byte) in the last 8 bytes of its random value; a TLS 1.3 client that sees it aborts. The sentinel only helps when the TLS 1.2 handshake signs the server random, as ephemeral key exchange does; it gives no protection with static RSA. Disabling old versions entirely removes the second requirement. A correctly configured TLS 1.2 connection is not automatically vulnerable to every historical attack, but it lacks TLS 1.3's protections.

Deployment showed a different problem: **middleboxes** that inspected TLS broke on anything unfamiliar. TLS 1.3 therefore disguises itself. The legacy version field still says 1.2 (`0x0303`), the real version goes in a `supported_versions` extension, and dummy ChangeCipherSpec messages are sent so the handshake looks like a resumed 1.2 session. QUIC reduces exposed protocol details with packet encryption and partial header protection, while fields such as connection IDs and version remain visible.

## Key takeaways
- The illustrated certificate handshake needs one TLS round trip before client application data.
- CertificateVerify binds proof of a private key to the handshake context.
- Finished authenticates the transcript; compatibility fields support older middleboxes.

## Further reading
- [RFC 9846: TLS 1.3 (2026 revision)](https://www.rfc-editor.org/rfc/rfc9846.html)
- [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/)
- [RFC 8446: original TLS 1.3 specification (obsoleted by RFC 9846)](https://www.rfc-editor.org/rfc/rfc8446)
