exec(open('/tmp/network04-helper.py').read())
n='app-email'
def m(a,b,why='Correct protocol scope and avoid an unsupported universal claim.'): md(n,a,b,why)
m('Residential ISPs usually block outbound 25 to stop infected machines sending spam directly.','Some access networks restrict outbound port 25 to reduce abuse; availability depends on the provider.')
m('Servers with equal preference share load. If the preferred server fails, the sender tries the next.','A sender randomises equal-preference destinations unless it has a reason to favour one. Connection failures can lead it to try another destination; a permanent rejection of a recipient is not an instruction to bypass that rejection at a backup server.')
m('C: Subject: Lunch?','C: Subject: Lunch?\nC: Date: Mon, 5 Oct 2026 12:00:00 +0100','RFC 5322 requires an origination Date field.')
m('| 3xx | Send more | Send the data |\n| 4xx | Temporary failure | Retry later |\n| 5xx | Permanent failure | Bounce |','| 3xx | Positive intermediate reply | Continue as requested (354 requests DATA) |\n| 4xx | Temporary failure | Retry the affected delivery later |\n| 5xx | Permanent failure | Do not repeat the unchanged failed request |')
m('The 4xx/5xx distinction is the backbone of reliability. A `451` (try again later) keeps the message in the sender\'s queue, typically retried for several days before giving up and sending a bounce. **Greylisting** exploits this: the receiver deliberately answers `451` to unknown senders on the first attempt, because legitimate MTAs retry while much spam software does not.','A transient recipient failure such as `451` leaves that delivery eligible for retry. RFC 5321 recommends a give-up time generally at least 4–5 days, with retry spacing; local policy and failure conditions matter. A permanent delivery failure, or expiration after temporary failures, can produce a delivery-status notification for previously accepted mail. No such notification is sent to a null reverse path. **Greylisting** temporarily rejects unfamiliar deliveries to distinguish senders that retry; it does not reliably separate all legitimate mail from spam.')
m("Python's `smtplib` drives the same dialogue. `set_debuglevel(1)` prints every command and reply:","Python's `smtplib` drives the same dialogue. This function submits through a configured provider, explicitly verifies the TLS certificate and hostname, and fails if STARTTLS is unavailable. Supply credentials separately; debug logging can expose authentication data and message contents. The example is not executed against a real provider here.")
a='''import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg["From"] = "alice@alice.example"
msg["To"] = "bob@bob.example"
msg["Subject"] = "Lunch?"
msg.set_content("Thursday at 1?")

with smtplib.SMTP("smtp.alice.example",
                  587) as s:
    s.set_debuglevel(1)
    s.starttls()
    s.login("alice", "app-password")
    s.send_message(
        msg,
        from_addr="bounces@alice.example",
        to_addrs=["bob@bob.example"])'''
b='''import smtplib
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
            from_addr="bounces@alice.example",
            to_addrs=["bob@bob.example"])'''
m(a,b,'Observed CPython starttls default uses the legacy stdlib SSL context; supply a verifying context and avoid credential debug output.')
m('Bcc works because the Bcc recipient is in `RCPT TO` but not in the headers.','In a common Bcc implementation, the recipient appears in `RCPT TO` while the Bcc header is removed before delivery. RFC 5322 also permits other Bcc-header handling for separate copies.')
m('so that a bounce can never cause another bounce in a loop.','so conforming servers do not generate another delivery failure notification in response.')
m('`STARTTLS` on port 25 is **opportunistic**: if the server doesn\'t offer it, or an attacker strips the `250-STARTTLS` line, most senders deliver in plaintext. Two standards make it enforceable:','With **opportunistic** STARTTLS on port 25 and no policy requiring authenticated TLS, stripping the offer can induce plaintext delivery. Enforcing senders instead defer or fail delivery. Two policy mechanisms are:')
m('- **MTA-STS** (RFC 8461): the domain publishes, over HTTPS, a policy saying "always use TLS with a valid certificate for these MX hosts".\n- **DANE** (RFC 7672): pins the MX server\'s certificate in DNS with TLSA records, relying on DNSSEC.','- **MTA-STS** (RFC 8461): an HTTPS policy in `enforce` mode requires authenticated TLS to approved MX hosts. Cached policies protect against stripping; initial DNS policy discovery can still be suppressed before a sender has a policy.\n- **DANE** (RFC 7672): DNSSEC-authenticated TLSA records bind acceptable certificates or keys, including supported trust-anchor forms, to the SMTP service.')
m('**POP3** (port 110, or 995 with TLS) is simple: download messages and usually delete them from the server. It suits one device and is now mostly legacy.','**POP3** (port 110, or 995 with implicit TLS) retrieves messages and supports deletion; clients can also leave messages on the server. It lacks IMAP\'s richer server-side mailbox and flag model.')
m('IMAP commands are prefixed with a client-chosen **tag**, so several can be outstanding and responses matched up:','IMAP commands use client-chosen **tags** to match responses. Some commands can be outstanding concurrently, subject to protocol ordering rules. This abbreviated transcript assumes TLS is already established; the FETCH response body and other required SELECT responses are omitted:')
m('shift when messages are deleted.','shift when earlier messages are **expunged**, not merely marked `\\Deleted`.')
m('**UIDs** are stable per mailbox and strictly increasing. Clients cache by UID.','**UIDs** increase with message assignment and remain stable within a mailbox\'s UIDVALIDITY generation. A cache identity includes the server/account, mailbox, UIDVALIDITY and UID; mutable flags still need synchronisation.')
m('the client must discard its cache and resync.','the client must invalidate the old UID mappings and resynchronise, rather than assume a reused number identifies the same message.')
m('**IDLE** keeps the connection open so the server can push "new mail" notifications instead of the client polling.','**IDLE** lets the server send mailbox updates while the client waits. Connections can time out; the client terminates and reissues IDLE periodically and reconnects when needed.')
m('Modern webmail and mobile apps often use proprietary APIs (Gmail API, Microsoft Graph) or JMAP (RFC 8620), a JSON-over-HTTP replacement for IMAP.','Applications can also use provider APIs or JMAP (RFC 8620), a JSON-based synchronisation framework over HTTP; JMAP Mail is specified separately in RFC 8621. Deployment prevalence is omitted because this review did not establish a reliable measurement.')
m('(One string on the wire.)','(Shown wrapped for readability; publish one TXT record whose concatenated strings contain the policy with spaces between terms.)')
m('It **breaks on forwarding**:','It **can fail on forwarding**:')
m('which is not in alice.example\'s record.','which may not be authorised by alice.example\'s record.')
m('Evaluation may take at most **10 DNS lookups** (each `include`, `a`, `mx` counts). Exceed it and SPF returns a *permerror*, a common failure for companies that include many SaaS senders.','Evaluation permits at most **10 evaluated DNS-query-causing terms** across the recursive check: `include`, `a`, `mx`, `ptr`, `exists` and `redirect`. Exceeding that limit gives *permerror*. This is not a cap of ten individual DNS packets: some terms cause several queries, and additional per-mechanism and void-lookup limits apply. Evaluation stops when a mechanism matches.')
m('`bh=` is a hash of the body; `b=` is the signature over the listed headers (`h=`) and the DKIM header itself.','`bh=` hashes the canonicalised body (or the prefix selected by optional `l=`); `b=` signs the selected canonicalised headers and the DKIM-Signature field with its `b=` value empty.')
m('canonicalisation tolerates harmless changes such as whitespace and header case.','canonicalisation normalises specified whitespace and header **field-name** case. It does not make arbitrary changes to header values or body text harmless.')
m("DKIM **survives forwarding** as long as the signed parts aren't altered. Mailing lists that add `[list]` to the subject or a footer to the body break it.","DKIM can survive forwarding when the signed content remains valid and the key/signature remains usable. A change to a signed subject or covered body content invalidates it; an unsigned header or content outside an `l=` prefix is a different case.")
m('[RFC 7489](https://www.rfc-editor.org/rfc/rfc7489)','[RFC 9989](https://www.rfc-editor.org/rfc/rfc9989), published in May 2026 and replacing RFC 7489','The current standard superseded RFC 7489 in May 2026.')
m('so `mail.alice.example` aligns with `alice.example`.','so `mail.alice.example` aligns with `alice.example` when both have organisational domain `alice.example`. RFC 9989 discovers that boundary through DNS tree walks; do not assume every two-label suffix is an organisation.')
m('- `p=none` monitor only, `p=quarantine` send to spam, `p=reject` refuse at SMTP time.\n- `rua=` asks receivers to send daily aggregate XML reports listing which IPs sent mail claiming your domain and whether they passed.','- `p=none` requests no DMARC-specific enforcement; `quarantine` requests suspicious treatment and `reject` requests rejection. Receivers retain local discretion.\n- `rua=` requests aggregate reports about observed sources and authentication results. Reporting is not guaranteed; current report formats are in RFC 9990.')
m('The usual rollout: publish `p=none`, read reports for weeks to find every legitimate sender (the CRM, the invoicing system, the marketing platform), fix their SPF or DKIM, then move to `quarantine` and `reject`.','A staged rollout inventories legitimate senders, monitors reports with `p=none`, fixes authentication and alignment, then considers enforcement. A fixed number of weeks cannot guarantee that every infrequent sender has appeared.')
m('DMARC fails, and with `p=reject` the message is refused.','DMARC fails. A receiver applying the requested `p=reject` policy without a local override refuses it.')
m('Since 2024 Gmail and Yahoo have required bulk senders (around 5,000+ messages a day to their users) to have SPF, DKIM and a DMARC record, plus one-click unsubscribe, so DMARC moved from best practice to necessity.','Google\'s published bulk-sender rules for personal Gmail accounts require SPF, DKIM and DMARC around the 5,000-messages-per-day threshold. One-click unsubscribe applies to marketing and subscribed messages. Yahoo also has bulk-sender requirements, but the Gmail numeric threshold should not be assumed to define Yahoo\'s classification. Consult each provider\'s current policy.')
m('silently drops invoices and password resets.','can cause legitimate invoices and password resets to be rejected when they lack any aligned authentication pass.')
m('Many `include:`s quietly push you over 10 lookups and into permerror.','Evaluated nested terms can exceed the ten-term budget and produce permerror.')
m('1024-bit RSA keys are weak by modern standards; use 2048-bit and rotate selectors.','RFC 8301 requires RSA signing keys of at least 1024 bits and recommends at least 2048; key rotation and supported algorithms need an operational policy.')
m('Without MTA-STS or DANE, server-to-server TLS can be stripped.','Opportunistic relay without an effective authenticated-TLS requirement is vulnerable to downgrade; local mandatory-TLS policies are another possible protection.')
m('4xx means retry later, 5xx means bounce.','4xx indicates a temporary failure; 5xx means the failed request should not be repeated unchanged. Delivery notifications depend on the transaction and reverse path.')
