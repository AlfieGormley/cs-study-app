---
id: app-dns-encrypted-transports
title: "Encrypted DNS and the limits of resolver privacy"
level: intermediate
minutes: 3
sourceLesson: app-dns-wire
summary: "DoT, DoH and DoQ protect a client-to-resolver transport rather than independently proving authoritative data."
---

## Encrypted DNS: DoT and DoH

Classic DNS is plaintext. An observer on an unprotected DNS transport can inspect its messages and attempt modification; caches avoid some lookups, and validation can detect tampering. Encrypted transports protect the hop between stub and recursive resolver.

| | DoT | DoH | DoQ |
|---|---|---|---|
| RFC | 7858 | 8484 | 9250 |
| Transport | TLS/TCP | HTTPS | QUIC |
| Port | 853 | 443 | 853 (UDP) |

**DNS over TLS** wraps the normal TCP DNS format (2-byte length, then message) in TLS. Because it has its own port, networks can easily identify and block it. Android supports DoT, and Google announced in July 2022 that updated devices from Android 11 onwards use DoH over HTTP/3 instead for some well-known resolvers that support it. The selected transport depends on version, updates and configuration.

**DNS over HTTPS** sends the same binary message as an HTTP request with media type `application/dns-message`, either POSTed or base64url-encoded in a GET (`/dns-query?dns=...`). Sharing HTTPS transport can make classification less direct than a dedicated port, but resolver addresses, endpoint policy and traffic patterns can still enable blocking. DoH is not guaranteed indistinguishable from other HTTPS. Browsers such as Firefox and Chrome can use it directly.

> [!analogy] Real-world analogy: Sealed questions to a reference librarian
> Instead of shouting your questions across a crowded room, you post them to a reference librarian in sealed envelopes. Nobody handling the post can read them, but the librarian opens every one, and if the librarian is careless or dishonest, the answers can be wrong.
>
> **How it maps:** The sealed envelope is DoT, DoH or DoQ protecting the stub-to-resolver hop. The librarian is the recursive resolver, which still sees every name you ask about. Checking the librarian's answers against the original publisher's signature is DNSSEC validation.
>
> **Where it stops:** The post office still sees which library you write to and when, just as the network sees the resolver's address and traffic timing. And what you do with the answer, such as connecting to the site's IP address, is visible again.

What encrypted DNS does **not** do:

- It does not hide your queries from the **resolver** itself; you have moved trust from your ISP to, say, Cloudflare or Google. Oblivious DoH (RFC 9230) adds a proxy to separate client addressing from query contents under its non-collusion and deployment assumptions. Correlation, colluding parties and identifying query contents remain limits.
- It authenticates and integrity-protects the transport to the selected resolver, but does not independently authenticate authoritative *data*; a malicious or compromised resolver can still lie. That is DNSSEC's job.
- It does not hide the destination entirely: the server's IP address, and often the TLS SNI, still reveal where you went. Encrypted Client Hello ([RFC 9849](https://www.rfc-editor.org/rfc/rfc9849), published in March 2026) can hide the SNI, but only when both the browser and the site support it.

An independently selected DoH resolver can bypass policies implemented only in the network’s default resolver, which is why administrators can disable it by policy and why Firefox checks a "canary" domain (`use-application-dns.net`) before enabling it automatically.

## Key takeaways
- DoT, DoH and DoQ protect a client-to-resolver transport rather than independently proving authoritative data.
- Resolvers still see queries; oblivious designs add assumptions and destination metadata can remain visible.

## Further reading
- [RFC 7858](https://www.rfc-editor.org/rfc/rfc7858)
- [RFC 8484](https://www.rfc-editor.org/rfc/rfc8484)
- [RFC 9250](https://www.rfc-editor.org/rfc/rfc9250)
- [RFC 9230](https://www.rfc-editor.org/rfc/rfc9230)
