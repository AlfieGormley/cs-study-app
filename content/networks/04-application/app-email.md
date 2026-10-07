---
id: app-email
title: "Email: SMTP, IMAP, SPF, DKIM and DMARC"
level: intermediate
minutes: 16
summary: How a message travels from submission to mailbox, a real SMTP session line by line, envelope versus header, IMAP's model of mailboxes and UIDs, and how SPF, DKIM and DMARC combine to stop spoofing.
---

Email is one of the oldest application protocols still in heavy use, and it shows. SMTP was designed in 1982 for a small network of trusted machines, with no authentication and no encryption. Almost everything since has been bolted on: TLS, submission authentication, and three separate DNS-based mechanisms to answer one question: *was this message really sent by the domain it claims?*

## The path of a message

```
 Alice's client (MUA)
   | SMTP submission, port 587/465
   v
 Alice's provider (MSA/MTA)
   | DNS: MX for bob.example?
   | SMTP relay, port 25
   v
 Bob's provider (MTA -> MDA)
   | stores in mailbox
   v
 Bob's client  <-- IMAP 993 / POP3 995
```

- A **mail user agent** (MUA) is the client: Outlook, Apple Mail, Thunderbird.
- **Submission** (port **587** with STARTTLS, or **465** with implicit TLS) is where your client hands mail to your provider, after authenticating. [RFC 8314](https://www.rfc-editor.org/rfc/rfc8314) now recommends implicit TLS on 465.
- **Relay** between providers uses port **25**. Some access networks restrict outbound port 25 to reduce abuse; availability depends on the provider.
- The receiving server stores the message, and Bob's client fetches it with **IMAP** or **POP3**. SMTP is push-only; retrieval is a separate protocol.

### Finding the destination: MX records

To deliver to `bob@bob.example`, the sending MTA looks up `MX` records for `bob.example`:

```
bob.example.  MX 10 mx1.bob.example.
bob.example.  MX 20 mx2.bob.example.
```

The **lower** preference number wins. A sender randomises equal-preference destinations unless it has a reason to favour one. Connection failures can lead it to try another destination; a permanent rejection of a recipient is not an instruction to bypass that rejection at a backup server. If there is no MX at all, the sender falls back to the domain's A/AAAA record (the "implicit MX"). A domain that never receives mail should publish a **null MX** (`MX 0 .`, RFC 7505) so senders fail fast.

## An SMTP session

SMTP ([RFC 5321](https://www.rfc-editor.org/rfc/rfc5321)) is a line-based text protocol. The client sends commands; the server answers with 3-digit codes. `C:` is the client, `S:` the server:

```
S: 220 mx1.bob.example ESMTP
C: EHLO mail.alice.example
S: 250-mx1.bob.example
S: 250-SIZE 52428800
S: 250-STARTTLS
S: 250 8BITMIME
C: STARTTLS
S: 220 Ready to start TLS
   ...TLS handshake, then EHLO again...
C: MAIL FROM:<alice@alice.example>
S: 250 OK
C: RCPT TO:<bob@bob.example>
S: 250 OK
C: DATA
S: 354 End data with <CRLF>.<CRLF>
C: From: Alice <alice@alice.example>
C: To: Bob <bob@bob.example>
C: Subject: Lunch?
C: Date: Mon, 5 Oct 2026 12:00:00 +0100
C:
C: Thursday at 1?
C: .
S: 250 OK queued as 7F3A2
C: QUIT
S: 221 Bye
```

The multi-line `250-` replies list **extensions** the server supports. A line `250 ` with a space marks the last one.

The first digit of each reply code is what matters:

| Code | Meaning | Sender should |
|---|---|---|
| 2xx | Success | Carry on |
| 3xx | Positive intermediate reply | Continue as requested (354 requests DATA) |
| 4xx | Temporary failure | Retry the affected delivery later |
| 5xx | Permanent failure | Do not repeat the unchanged failed request |

A transient recipient failure such as `451` leaves that delivery eligible for retry. RFC 5321 recommends a give-up time generally at least 4–5 days, with retry spacing; local policy and failure conditions matter. A permanent delivery failure, or expiration after temporary failures, can produce a delivery-status notification for previously accepted mail. No such notification is sent to a null reverse path. **Greylisting** temporarily rejects unfamiliar deliveries to distinguish senders that retry; it does not reliably separate all legitimate mail from spam.

Python's `smtplib` drives the same dialogue. This function submits through a configured provider, explicitly verifies the TLS certificate and hostname, and fails if STARTTLS is unavailable. Supply credentials separately; debug logging can expose authentication data and message contents. The example is not executed against a real provider here.

```python
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formatdate

msg = EmailMessage()
msg["From"] = "alice@alice.example"
msg["To"] = "bob@bob.example"
msg["Subject"] = "Lunch?"
msg["Date"] = formatdate(localtime=True)
msg.set_content("Thursday at 1?")

def submit(host, user, password):
    tls = ssl.create_default_context()
    with smtplib.SMTP(
            host, 587, timeout=10) as s:
        s.starttls(context=tls)
        s.login(user, password)
        return s.send_message(
            msg,
            from_addr=(
                "bounces@alice.example"),
            to_addrs=["bob@bob.example"])
```

Notice that `from_addr` and `to_addrs` are passed separately from the message headers. That is the next idea.

### Envelope versus header

There are **two** sets of addresses:

- The **envelope**: `MAIL FROM` (the *return path*, where bounces go) and `RCPT TO` (who actually receives it). These are SMTP commands.
- The **header**: the `From:`, `To:` and `Cc:` lines inside the message ([RFC 5322](https://www.rfc-editor.org/rfc/rfc5322)). These are what your mail client displays.

They need not match. In a common Bcc implementation, the recipient appears in `RCPT TO` while the Bcc header is removed before delivery. RFC 5322 also permits other Bcc-header handling for separate copies. Mailing lists set the envelope sender to the list's bounce address. And a spammer can put *anything* in `From:`, which is the core spoofing problem SPF, DKIM and DMARC address.

Bounces are sent with an empty envelope sender, `MAIL FROM:<>`, so conforming servers do not generate another delivery failure notification in response.

### Dot-stuffing and SMTP smuggling

The message ends with a line containing just `.`. A body line that starts with `.` is sent with an extra dot (`..`), which the receiver strips. That is **dot-stuffing**.

In 2023, researchers showed **SMTP smuggling**: some servers accepted a bare `\n.\n` as end of data while others required `\r\n.\r\n`. An attacker could hide a second, forged message inside the first, which the receiving server then treated as a separate message from the sending provider. Same lesson as HTTP request smuggling: when two parsers disagree on framing, attackers live in the gap.

### TLS between servers

With **opportunistic** STARTTLS on port 25 and no policy requiring authenticated TLS, stripping the offer can induce plaintext delivery. Enforcing senders instead defer or fail delivery. Two policy mechanisms are:

- **MTA-STS** (RFC 8461): an HTTPS policy in `enforce` mode requires authenticated TLS to approved MX hosts. Cached policies protect against stripping; initial DNS policy discovery can still be suppressed before a sender has a policy.
- **DANE** (RFC 7672): DNSSEC-authenticated TLSA records bind acceptable certificates or keys, including supported trust-anchor forms, to the SMTP service.

## Retrieval: IMAP and POP3

**POP3** (port 110, or 995 with implicit TLS) retrieves messages and supports deletion; clients can also leave messages on the server. It lacks IMAP's richer server-side mailbox and flag model.

**IMAP** (port 143, or **993** with TLS; current version IMAP4rev2, [RFC 9051](https://www.rfc-editor.org/rfc/rfc9051)) keeps mail **on the server** and lets many clients view and modify it. Folders, read and flagged states, and moves all sync between devices.

IMAP commands use client-chosen **tags** to match responses. Some commands can be outstanding concurrently, subject to protocol ordering rules. This abbreviated transcript assumes TLS is already established; the FETCH response body and other required SELECT responses are omitted:

```
C: a1 LOGIN bob secret
S: a1 OK LOGIN completed
C: a2 SELECT INBOX
S: * 172 EXISTS
S: * OK [UIDVALIDITY 3857529045]
S: a2 OK [READ-WRITE] SELECT done
C: a3 UID FETCH 4827 (FLAGS BODY[])
S: * 172 FETCH (UID 4827 FLAGS ...
S: a3 OK FETCH completed
```

Lines starting with `*` are **untagged** responses: data or notifications. Key ideas:

- **Sequence numbers** (1 to 172 here) are positions in the mailbox and shift when earlier messages are **expunged**, not merely marked `\Deleted`.
- **UIDs** increase with message assignment and remain stable within a mailbox's UIDVALIDITY generation. A cache identity includes the server/account, mailbox, UIDVALIDITY and UID; mutable flags still need synchronisation.
- **UIDVALIDITY** says whether cached UIDs are still meaningful. If it changes (the mailbox was rebuilt), the client must invalidate the old UID mappings and resynchronise, rather than assume a reused number identifies the same message.
- **Flags** such as `\Seen`, `\Flagged`, `\Deleted` record state. Deleting is two steps: set `\Deleted`, then `EXPUNGE`.
- **IDLE** lets the server send mailbox updates while the client waits. Connections can time out; the client terminates and reissues IDLE periodically and reconnects when needed.

Applications can also use provider APIs or JMAP (RFC 8620), a JSON-based synchronisation framework over HTTP; JMAP Mail is specified separately in RFC 8621. Deployment prevalence is omitted because this review did not establish a reliable measurement.

## Authentication: SPF, DKIM and DMARC

Nothing in SMTP stops a server from claiming `MAIL FROM:<ceo@yourbank.example>` and `From: CEO <ceo@yourbank.example>`. Three DNS-published mechanisms let receivers check.

### SPF: which IPs may send for this domain?

SPF ([RFC 7208](https://www.rfc-editor.org/rfc/rfc7208)) is a TXT record listing the servers allowed to send mail for a domain:

```
alice.example. TXT "v=spf1
  ip4:192.0.2.0/24
  include:_spf.google.com
  -all"
```

(Shown wrapped for readability; publish one TXT record whose concatenated strings contain the policy with spaces between terms.) The receiver checks the **connecting IP** against the SPF record of the **envelope sender's** domain (`MAIL FROM`, or the HELO name for bounces). The final `all` sets the default: `-all` fail, `~all` softfail, `?all` neutral.

SPF's limits:

- It checks the **envelope**, not the visible `From:` header. A spammer can pass SPF for their own domain while showing your domain in `From:`.
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

- `d=` is the signing domain and `s=` the **selector**. The receiver fetches the public key from `mail2026._domainkey.alice.example` (TXT).
- `bh=` hashes the canonicalised body (or the prefix selected by optional `l=`); `b=` signs the selected canonicalised headers and the DKIM-Signature field with its `b=` value empty.
- `c=relaxed/relaxed` canonicalisation normalises specified whitespace and header **field-name** case. It does not make arbitrary changes to header values or body text harmless.

Selectors let a domain have several keys at once: one per provider, and new ones for rotation. DKIM can survive forwarding when the signed content remains valid and the key/signature remains usable. A change to a signed subject or covered body content invalidates it; an unsigned header or content outside an `l=` prefix is a different case.

### DMARC: tie it to the visible From

Neither SPF nor DKIM on its own protects the `From:` header the user sees. **DMARC** ([RFC 9989](https://www.rfc-editor.org/rfc/rfc9989), published in May 2026 and replacing RFC 7489) adds **alignment**: a message passes DMARC if

- SPF passes **and** the envelope domain aligns with the `From:` domain, **or**
- DKIM passes **and** the `d=` domain aligns with the `From:` domain.

"Aligned" by default (relaxed mode) means the same organisational domain, so `mail.alice.example` aligns with `alice.example` when both have organisational domain `alice.example`. RFC 9989 discovers that boundary through DNS tree walks; do not assume every two-label suffix is an organisation. Strict mode (`aspf=s`, `adkim=s`) requires an exact match.

The policy is a TXT record at `_dmarc`:

```
_dmarc.alice.example. TXT
  "v=DMARC1; p=reject;
   rua=mailto:dmarc@alice.example"
```

- `p=none` requests no DMARC-specific enforcement; `quarantine` requests suspicious treatment and `reject` requests rejection. Receivers retain local discretion.
- `rua=` requests aggregate reports about observed sources and authentication results. Reporting is not guaranteed; current report formats are in RFC 9990.

A staged rollout inventories legitimate senders, monitors reports with `p=none`, fixes authentication and alignment, then considers enforcement. A fixed number of weeks cannot guarantee that every infrequent sender has appeared.

> [!example] A spoof that DMARC catches
> A phisher sends from their own server with `MAIL FROM:<x@phish.example>` and `From: <it@alice.example>`. SPF passes for phish.example, but it does not align with alice.example. There is no valid alice.example DKIM signature. DMARC fails. A receiver applying the requested `p=reject` policy without a local override refuses it.

Google's published bulk-sender rules for personal Gmail accounts require SPF, DKIM and DMARC around the 5,000-messages-per-day threshold. One-click unsubscribe applies to marketing and subscribed messages. Yahoo also has bulk-sender requirements, but the Gmail numeric threshold should not be assumed to define Yahoo's classification. Consult each provider's current policy.

**ARC** (RFC 8617) helps forwarders and mailing lists: each intermediary records the authentication results it saw and signs them, so the final receiver can choose to trust a known forwarder's verdict even though SPF and DKIM now fail.

## Pitfalls

- **Forgotten senders.** Moving to `p=reject` before every SaaS tool signs with your domain can cause legitimate invoices and password resets to be rejected when they lack any aligned authentication pass.
- **SPF lookup limit.** Evaluated nested terms can exceed the ten-term budget and produce permerror.
- **Short DKIM keys.** RFC 8301 requires RSA signing keys of at least 1024 bits and recommends at least 2048; key rotation and supported algorithms need an operational policy.
- **Plaintext relay.** Opportunistic relay without an effective authenticated-TLS requirement is vulnerable to downgrade; local mandatory-TLS policies are another possible protection.

## Key takeaways
- Clients submit on 587/465 with authentication; servers relay on 25 to the lowest-preference MX; clients retrieve with IMAP (993) or POP3.
- SMTP replies: 4xx indicates a temporary failure; 5xx means the failed request should not be repeated unchanged. Delivery notifications depend on the transaction and reverse path. Queued retries for days make email resilient.
- The envelope (`MAIL FROM`, `RCPT TO`) and header (`From:`, `To:`) are separate, which enables Bcc, lists and spoofing.
- IMAP keeps state on the server; UIDs plus UIDVALIDITY let clients cache safely.
- SPF authorises IPs for the envelope domain, DKIM signs the content, and DMARC requires one of them to pass and align with the visible From.

## Further reading
- [RFC 5321: Simple Mail Transfer Protocol — IETF](https://www.rfc-editor.org/rfc/rfc5321)
- [RFC 9051: IMAP4rev2 — IETF](https://www.rfc-editor.org/rfc/rfc9051)
- [DMARC overview — dmarc.org](https://dmarc.org/overview/)
- [Email sender guidelines — Google Workspace Admin Help](https://support.google.com/a/answer/81126)
- [SMTP smuggling: spoofing e-mails worldwide — SEC Consult](https://sec-consult.com/blog/detail/smtp-smuggling-spoofing-e-mails-worldwide/)
- [DMARC — Wikipedia](https://en.wikipedia.org/wiki/DMARC)
