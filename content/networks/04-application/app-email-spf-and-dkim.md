---
id: app-email-spf-and-dkim
title: "Email SPF envelope checks and DKIM content signatures"
level: intermediate
minutes: 3
sourceLesson: app-email
summary: "Email SPF checks a connecting sender against an envelope-domain policy; it does not authenticate the visible From."
---

## Authentication: email SPF, DKIM and DMARC

Nothing in SMTP stops a server from claiming `MAIL FROM:<ceo@yourbank.example>` and `From: CEO <ceo@yourbank.example>`. Three DNS-published mechanisms let receivers check.

### email SPF: which IPs may send for this domain?

Email SPF ([RFC 7208](https://www.rfc-editor.org/rfc/rfc7208)) is a TXT record listing the servers allowed to send mail for a domain:

```
alice.example. TXT "v=spf1
  ip4:192.0.2.0/24
  include:_spf.google.com
  -all"
```

(Shown wrapped for readability; publish one TXT record whose concatenated strings contain the policy with spaces between terms.) The receiver checks the **connecting IP** against the email SPF record of the **envelope sender's** domain (`MAIL FROM`, or the HELO name for bounces). The final `all` sets the default: `-all` fail, `~all` softfail, `?all` neutral.

Email SPF's limits:

- It checks the **SMTP envelope**, not the visible `From:` header. A spammer can pass email SPF for their own domain while showing your domain in `From:`.
- It **can fail on forwarding**: when `bob@uni.example` forwards to Gmail, Gmail sees the university's IP, which may not be authorised by alice.example's record.
- Evaluation permits at most **10 evaluated DNS-query-causing terms** across the recursive check: `include`, `a`, `mx`, `ptr`, `exists` and `redirect`. Exceeding that limit gives *permerror*. This is not a cap of ten individual DNS packets: some terms cause several queries, and additional per-mechanism and void-lookup limits apply. Evaluation stops when a mechanism matches.

### DKIM: a signature over the message

DKIM ([RFC 6376](https://www.rfc-editor.org/rfc/rfc6376)) has the sending server sign selected headers and the body, and add the result as a header:

```
DKIM-Signature: v=1; a=rsa-sha256;
  c=relaxed/relaxed; d=alice.example;
  s=mail2026; h=from:to:subject:date;
  bh=2jUSOH9NhtVGCQWNr9BrIAPreKQjO6Sn...;
  b=AuUoFEfDxTDkHlLXSZEpZj79LICEps6e...
```

- `d=` is the signing domain and `s=` the **DKIM selector**. The receiver fetches the public key from `mail2026._domainkey.alice.example` (TXT).
- `bh=` hashes the canonicalised body (or the prefix selected by optional `l=`); `b=` signs the selected canonicalised headers and the DKIM-Signature field with its `b=` value empty.
- `c=relaxed/relaxed` canonicalisation normalises specified whitespace and header **field-name** case. It does not make arbitrary changes to header values or body text harmless.

> [!analogy] Real-world analogy: An approved-courier list and a wax seal
> A company publishes a list of couriers allowed to deliver on its behalf, and it also seals each letter with its own wax seal. A receptionist can check the courier at the door against the list, or check the seal on the letter.
>
> **How it maps:** The courier list is email SPF: it checks the connecting server's IP against the envelope domain's published policy. The wax seal is DKIM: a signature over the message that anyone can verify with the public key published under `d=` and the selector.
>
> **Where it stops:** Neither check says the company named on the letterhead, the visible `From:`, is the one whose list or seal was checked; DMARC adds that link. A DKIM signature also fails if covered content changes beyond what its canonicalisation tolerates, not only when something is opened. A forwarded message arrives with a different courier, so email SPF often fails while the seal survives.

DKIM selectors let a domain have several keys at once: one per provider, and new ones for rotation. DKIM can survive forwarding when the signed content remains valid and the key/signature remains usable. A change to a signed subject or covered body content invalidates it; an unsigned header or content outside an `l=` prefix is a different case.

## Key takeaways
- Email SPF checks a connecting sender against an envelope-domain policy; it does not authenticate the visible From.
- DKIM binds selected canonicalised headers and body content to a signing domain.

## Further reading
- [RFC 7208](https://www.rfc-editor.org/rfc/rfc7208)
- [RFC 6376](https://www.rfc-editor.org/rfc/rfc6376)
- [RFC 8301](https://www.rfc-editor.org/rfc/rfc8301)
