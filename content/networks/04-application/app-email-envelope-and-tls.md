---
id: app-email-envelope-and-tls
title: "SMTP envelopes versus message headers"
level: intermediate
minutes: 3
sourceLesson: app-email
summary: "SMTP envelope recipients and bounce addresses are separate from visible message headers."
---

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
    # Trust configured CAs and check names.
    tls = ssl.create_default_context()
    with smtplib.SMTP(
            host, 587, timeout=10) as s:
        # Encrypt before credentials.
        s.starttls(context=tls)
        s.login(user, password)
        # Set the separate SMTP envelope.
        return s.send_message(
            msg,
            from_addr=(
                "bounces@alice.example"),
            to_addrs=["bob@bob.example"])
```

Notice that `from_addr` and `to_addrs` are passed separately from the message headers. That is the next idea.

### Envelope versus header

There are **two** sets of addresses:

- The **SMTP envelope**: `MAIL FROM` (the *return path*, where bounces go) and `RCPT TO` (who actually receives it). These are SMTP commands.
- The **message header**: the `From:`, `To:` and `Cc:` lines inside the message ([RFC 5322](https://www.rfc-editor.org/rfc/rfc5322)). These are what your mail client displays.

They need not match. In a common Bcc implementation, the recipient appears in `RCPT TO` while the Bcc header is removed before delivery. RFC 5322 also permits other Bcc-header handling for separate copies. Mailing lists set the envelope sender to the list's bounce address. And a spammer can put *anything* in `From:`, which is the core spoofing problem email SPF, DKIM and DMARC address.

> [!analogy] Real-world analogy: The envelope and the letterhead
> The post office delivers a letter using only what is written on the envelope. The letter inside can carry any letterhead, any "To" line and any signature, and the post office never reads them.
>
> **How it maps:** The envelope is `MAIL FROM` and `RCPT TO`: they decide where the message goes and where failures return. The letter's own headers, `From:`, `To:` and `Cc:`, are what the recipient sees. A Bcc copy is like an extra envelope addressed to Carol containing the same letter, which does not mention her.
>
> **Where it stops:** Envelopes are thrown away on arrival but SMTP keeps a trace: the receiver records the envelope sender in a `Return-Path:` header. And because anyone can print any letterhead, receivers need email SPF, DKIM and DMARC to judge whether a visible `From:` is genuine.

Bounces are sent with an empty envelope sender, `MAIL FROM:<>`, so conforming servers do not generate another delivery failure notification in response.

## Key takeaways
- SMTP envelope recipients and reverse paths are independent of visible message headers.
- Submit credentials only after establishing authenticated TLS; message headers do not determine envelope delivery.

## Further reading
- [RFC 5321](https://www.rfc-editor.org/rfc/rfc5321)
- [RFC 5322](https://www.rfc-editor.org/rfc/rfc5322)
- [Python smtplib](https://docs.python.org/3/library/smtplib.html)
