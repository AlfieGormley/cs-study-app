---
id: app-email-dmarc-alignment
title: "DMARC alignment, forwarding and rollout"
level: intermediate
minutes: 4
sourceLesson: app-email
summary: "One aligned email SPF or DKIM pass can satisfy DMARC; unaligned authentication does not."
---

Email SPF authenticates the connecting source for an envelope domain. DKIM authenticates selected signed content under its d= signing domain. DMARC connects those results to the domain in the message header that users see.

### DMARC: tie it to the visible From

Neither email SPF nor DKIM on its own protects the `From:` header the user sees. **DMARC** ([RFC 9989](https://www.rfc-editor.org/rfc/rfc9989), published in May 2026 and replacing RFC 7489) adds **alignment**: a message passes DMARC if

- Email SPF passes **and** the envelope domain aligns with the `From:` domain, **or**
- DKIM passes **and** the `d=` domain aligns with the `From:` domain.

One aligned pass is enough, and an unaligned pass counts for nothing: a phisher's server can pass email SPF for `phish.example`, but that cannot produce a DMARC pass for a message showing `From: it@alice.example`.

"Aligned" by default (relaxed mode) means the same organisational domain, so `mail.alice.example` aligns with `alice.example` when both have organisational domain `alice.example`. RFC 9989 discovers that boundary through DNS tree walks; do not assume every two-label suffix is an organisation. Strict alignment (`aspf=s`, `adkim=s`) requires an exact match.

The policy is a TXT record at `_dmarc`:

```
_dmarc.alice.example. TXT
  "v=DMARC1; p=reject;
   rua=mailto:dmarc@alice.example"
```

- `p=none` requests no DMARC-specific enforcement; `quarantine` requests suspicious treatment and `reject` requests rejection. Receivers retain local discretion: RFC 9989 tells fully participating receivers not to reject a message solely because the policy says `reject`, but to weigh other evidence, for example about mailing lists.
- RFC 9989 drops the old `pct=` percentage tag. A domain trying out a stricter policy can add `t=y` (test mode), which asks receivers to apply one level less than the stated policy, so `reject` is treated as `quarantine`. Guides written for RFC 7489 can be out of date.
- `rua=` requests aggregate reports about observed sources and authentication results. Reporting is not guaranteed; current report formats are in RFC 9990.

A staged rollout inventories legitimate senders, monitors reports with `p=none`, fixes authentication and alignment, then considers enforcement. A fixed number of weeks cannot guarantee that every infrequent sender has appeared.

The receiver’s pass rule and the domain owner’s conformance requirements are different. For full participation, RFC 9989 section 8 requires domain owners to send with **both aligned email SPF and aligned DKIM**, publish the required policies, and collect and analyse aggregate reports. It explicitly forbids relying solely on email SPF when the Author Domain policy is `p=reject`. One aligned pass still suffices for a receiver’s message result; that does not make a sender’s email SPF-only deployment fully conformant.

> [!example] A spoof that DMARC catches
> A phisher sends from their own server with `MAIL FROM:<x@phish.example>` and `From: <it@alice.example>`. Email SPF passes for phish.example, but it does not align with alice.example. There is no valid alice.example DKIM signature. DMARC fails. A receiver applying the requested `p=reject` policy without a local override refuses it.

Since February 2024, Google's published sender rules (unchanged when checked in October 2026) require senders of 5,000 or more messages a day to personal Gmail accounts to use email SPF, DKIM and DMARC. One-click unsubscribe applies to marketing and subscribed messages. Yahoo also has bulk-sender requirements, but the Gmail numeric threshold should not be assumed to define Yahoo's classification. Consult each provider's current policy.

> [!analogy] Real-world analogy: Checking the seal matches the letterhead
> A letter arrives on Alice Ltd letterhead. It came by an approved courier and carries an intact wax seal, but both belong to Phish Ltd. Each check passed, yet neither shows that Alice Ltd sent it.
>
> **How it maps:** The letterhead is the visible `From:` domain. The courier and seal are the email SPF and DKIM results, each tied to its own domain. DMARC asks whether at least one passing check belongs to the same organisation as the letterhead (relaxed alignment) or to exactly the same domain (strict), and the letterhead's owner publishes what to do when none does.
>
> **Where it stops:** A receptionist can phone Alice Ltd to ask; a receiver cannot, so it relies on the published policy and its own judgement. Forwarders and mailing lists also change couriers or contents in transit, which can break both checks even for genuine mail.

**ARC** (RFC 8617) helps forwarders and mailing lists: each intermediary records the authentication results it saw and signs them, so the final receiver can choose to trust a known forwarder's verdict even though email SPF and DKIM now fail.

## Pitfalls

- **Forgotten senders.** Moving to `p=reject` before every SaaS tool signs with your domain can cause legitimate invoices and password resets to be rejected when they lack any aligned authentication pass.
- **Email SPF lookup limit.** Evaluated nested terms can exceed the ten-term budget and produce permerror.
- **Short DKIM keys.** RFC 8301 requires RSA signing keys of at least 1024 bits and recommends at least 2048; key rotation and supported algorithms need an operational policy.
- **Plaintext relay.** Opportunistic relay without an effective authenticated-TLS requirement is vulnerable to downgrade; local mandatory-TLS policies are another possible protection.

## Key takeaways
- One aligned email SPF or DKIM pass can satisfy DMARC; unaligned authentication does not.
- Enforcement rollout must include every legitimate sender and account for forwarding or content changes.

## Further reading
- [RFC 9989](https://www.rfc-editor.org/rfc/rfc9989)
- [RFC 9990](https://www.rfc-editor.org/rfc/rfc9990)
- [RFC 8617](https://www.rfc-editor.org/rfc/rfc8617)
- [Google sender policy](https://support.google.com/a/answer/81126)
