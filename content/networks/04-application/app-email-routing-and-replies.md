---
id: app-email-routing-and-replies
title: "Email delivery, MX selection and SMTP replies"
level: intermediate
minutes: 4
sourceLesson: app-email
summary: "Clients submit mail to a provider; MTAs relay to MX destinations and retrieval uses separate protocols."
---

SMTP began as a mail-transfer protocol without built-in encryption or sender-domain authentication. Submission authentication, transport security and DNS-based authentication mechanisms address different parts of the problem.

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
- **Mail submission** (port **587** with STARTTLS, or **465** with implicit TLS) is where your client hands mail to your provider, after authenticating. [RFC 8314](https://www.rfc-editor.org/rfc/rfc8314) now recommends implicit TLS on 465.
- **Relay** between providers uses port **25**. Some access networks restrict outbound port 25 to reduce abuse; availability depends on the provider.
- The receiving server stores the message, and Bob's client fetches it with **IMAP** or **POP3**. SMTP is push-only; retrieval is a separate protocol.

> [!analogy] Real-world analogy: Posting a parcel through two depots
> You hand a parcel to your local depot after showing ID. Your depot looks up which depot serves the recipient's town and drives it there. The recipient later collects it from their own locker.
>
> **How it maps:** Handing it over with ID is authenticated submission on port 587 or 465. The depot-to-depot drive is relay over port 25, and looking up the destination depot is the MX lookup. Collecting from the locker is IMAP or POP3, a separate protocol from the one that delivered it.
>
> **Where it stops:** A real depot can usually confirm who sent a parcel. Plain SMTP relay cannot; that is the job of the email SPF, DKIM and DMARC checks covered later. Mail can also wait in queues and be retried for days, which parcel services rarely do.

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
| 3xx | Positive intermediate reply | Continue as requested (354 asks for the message text after the DATA command) |
| 4xx | Temporary failure | Retry the affected delivery later |
| 5xx | Permanent failure | Do not repeat the unchanged failed request |

A transient recipient failure such as `451` leaves that delivery eligible for retry. RFC 5321 recommends a give-up time generally at least 4–5 days, with retry spacing; local policy and failure conditions matter. A permanent delivery failure, or expiration after temporary failures, can produce a delivery-status notification for previously accepted mail. No such notification is sent to a null reverse path. **Greylisting** temporarily rejects unfamiliar deliveries to distinguish senders that retry; it does not reliably separate all legitimate messages from spam.

## Key takeaways
- Clients submit mail to a provider; MTAs relay to MX destinations and retrieval uses separate protocols.
- SMTP 4xx permits later retry, while an unchanged failed 5xx request should not be repeated.

## Further reading
- [RFC 5321](https://www.rfc-editor.org/rfc/rfc5321)
- [RFC 8314](https://www.rfc-editor.org/rfc/rfc8314)
- [RFC 7505](https://www.rfc-editor.org/rfc/rfc7505)
