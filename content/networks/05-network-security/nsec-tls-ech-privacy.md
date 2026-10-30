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

> [!analogy] Real-world analogy: a sealed letter inside a mailroom envelope
> To keep the post office from learning which company you are writing to, you seal your letter in an inner envelope that only the building's mailroom can open, and address the outer envelope just to "Mailroom, 1 Big Tower". The mailroom opens it and passes the letter to the right company.
>
> **How it maps:** The outer envelope is the outer ClientHello with the provider's public name, the inner envelope is the encrypted inner ClientHello with the real SNI, the mailroom's lock is the ECH public key published in DNS, and the tower full of companies is the set of sites sharing that configuration.
>
> **Where it stops:** If the building houses only one company, the outer address gives the secret away, just as a unique IP address or a small anonymity set can. The post office can also see where your other letters go, as a plaintext DNS lookup can reveal the name even when the ClientHello hides it.

ECH hides the inner ClientHello from passive observers, but the practical anonymity set depends on shared configuration, IP addresses and other metadata; a CDN is not a protocol requirement. Plaintext DNS can independently disclose the requested name. Encrypted DNS protects that hop but does not conceal it from the chosen resolver. For defenders it is a trade-off: firewalls and filters that block by SNI (the detection units) lose that signal.

## Key takeaways
- ECH encrypts the inner ClientHello, including its real SNI.
- A visible public name, server IP and DNS observations can still constrain privacy.
- ECH privacy depends on deployment and anonymity sets, not merely enabling one extension.

## Further reading
- [RFC 9849: TLS Encrypted Client Hello](https://www.rfc-editor.org/rfc/rfc9849.html)
- [RFC 9846: TLS 1.3 (2026 revision)](https://www.rfc-editor.org/rfc/rfc9846.html)
