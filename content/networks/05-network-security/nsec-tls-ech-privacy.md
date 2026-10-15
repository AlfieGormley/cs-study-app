---
id: nsec-tls-ech-privacy
title: ECH and the visible server name
level: intermediate
minutes: 3
summary: ECH encrypts the inner ClientHello, including its real SNI.
sourceLesson: nsec-tls
---

TLS 1.3 encrypts the server certificate in the ordinary full handshake, but its initial ClientHello is normally visible. ECH addresses that remaining name exposure. Distinguish the actual server name from the provider’s visible public name.

For example, when several sites share the public name and externally visible configuration in this unit’s model, an observer can identify the provider without reading the inner SNI. A unique destination IP or a separate plaintext DNS lookup may still reveal which site the user requested.

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

ECH hides the inner ClientHello from passive observers, but the practical anonymity set depends on shared configuration, IP addresses and other metadata; a CDN is not a protocol requirement. Plaintext DNS can independently disclose the requested name. Encrypted DNS protects that hop but does not conceal it from the chosen resolver. For defenders it is a trade-off: firewalls and filters that block by SNI (the detection units) lose that signal.

## Key takeaways
- ECH encrypts the inner ClientHello, including its real SNI.
- A visible public name, server IP and DNS observations can still constrain privacy.
- ECH privacy depends on deployment and anonymity sets, not merely enabling one extension.

## Further reading
- [RFC 9846: TLS 1.3 (2026 revision)](https://www.rfc-editor.org/rfc/rfc9846.html)
- [RFC 8446: original TLS 1.3 specification](https://www.rfc-editor.org/rfc/rfc8446)
- [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/)
- [RFC 9849: TLS Encrypted Client Hello](https://www.rfc-editor.org/rfc/rfc9849.html)
- [Ballot SC081v3: reducing certificate validity periods — CA/Browser Forum](https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/)
- [Certificate Transparency — MDN](https://developer.mozilla.org/en-US/docs/Web/Security/Certificate_Transparency)
- [ssl: TLS/SSL wrapper for socket objects — Python docs](https://docs.python.org/3/library/ssl.html)
