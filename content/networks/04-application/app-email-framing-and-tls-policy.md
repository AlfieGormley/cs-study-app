---
id: app-email-framing-and-tls-policy
title: SMTP parser agreement and enforced relay TLS
level: intermediate
minutes: 3
sourceLesson: app-email
summary: Relay security depends on both consistent framing and an effective authenticated-TLS policy.
---

An SMTP sender transmits an envelope followed by message headers and body. email SPF authenticates a connecting IP for an envelope domain; DKIM binds covered content to a signing domain, and DMARC checks alignment with the visible From. Those authentication results do not replace safe SMTP framing or confidential, authenticated transport.

## Dot-stuffing and SMTP smuggling

The message ends with a line containing just `.`. A body line that starts with `.` is sent with an extra `.` (as `..`), which the receiver strips. That is **dot-stuffing**.

In 2023, researchers showed **SMTP smuggling**: some servers accepted a bare `\n.\n` as end of data while others required `\r\n.\r\n`. An attacker could hide a second, forged message inside the first, which the receiving server then treated as a separate message from the sending provider. Same lesson as HTTP request smuggling: when two parsers disagree on framing, attackers live in the gap.

### TLS between servers

With **opportunistic STARTTLS** on port 25 and no policy requiring authenticated TLS, stripping the offer can induce plaintext delivery. Enforcing senders instead defer or fail delivery. Two policy mechanisms are:

- **MTA-STS** (RFC 8461): an HTTPS policy in `enforce` mode requires authenticated TLS to approved MX hosts. Cached policies protect against stripping; initial DNS policy discovery can still be suppressed before a sender has a policy.
- **DANE** (RFC 7672): DNSSEC-authenticated TLSA records associate acceptable certificates or keys, including supported trust-anchor forms, to the SMTP service.

## Key takeaways
- Dot-stuffing preserves message boundaries only when both hops apply compatible end-of-data parsing.
- Opportunistic STARTTLS and enforced authenticated TLS have different downgrade guarantees.
- MTA-STS and SMTP DANE constrain relay security under different discovery and trust assumptions.

## Further reading
- [RFC 5321](https://www.rfc-editor.org/rfc/rfc5321)
- [RFC 8461: MTA-STS](https://www.rfc-editor.org/rfc/rfc8461)
- [RFC 7672: SMTP DANE](https://www.rfc-editor.org/rfc/rfc7672)
- [SMTP smuggling original research](https://sec-consult.com/blog/detail/smtp-smuggling-spoofing-e-mails-worldwide/)
