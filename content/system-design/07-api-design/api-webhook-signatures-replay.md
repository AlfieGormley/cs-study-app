---
id: api-webhook-signatures-replay
title: Webhook signatures and replay defences
level: advanced
minutes: 5
summary: Authenticate raw delivery bytes, rotate secrets safely and reject stale or repeated signed payloads.
sourceLesson: api-webhooks-gateways
---

The previous lesson covered pushing data to *browsers*. Webhooks push data to *other servers*: Stripe tells your backend a payment succeeded, GitHub tells your CI that code was pushed, Shopify tells your app an order was placed.

Later units cover delivery, ordering and the gateways and backends-for-frontends that sit in front of APIs.

## Webhooks: reverse APIs

A webhook is an HTTP `POST` that **the provider** sends to a URL **the consumer** registered. It's an API call in the opposite direction.

```
Provider            Your server
(Stripe)            /webhooks/stripe
   |                     |
   | payment succeeded   |
   |--- POST event ----->|
   |                     | verify sig
   |                     | enqueue
   |<----- 200 OK -------|
   |                     | process async
```

A typical delivery:

```
POST /webhooks/stripe HTTP/1.1
Content-Type: application/json
Stripe-Signature: t=1767225600,
  v1=5257a869e7ecebeda32a...

{"id": "evt_1Nq...",
 "type": "payment_intent.succeeded",
 "created": 1767225600,
 "data": {"object": {...}}}
```

The alternative is the consumer polling `GET /events?since=...`. Webhooks are more efficient and faster, but they shift a lot of reliability problems onto both sides.

## Problem 1: authenticity

Your webhook URL is public. Anyone who discovers it can `POST` a fake "payment succeeded" event and get free goods. You must verify that each request genuinely came from the provider.

A common technique is an **HMAC signature** (a shared-secret message authentication code). Follow the provider-specific signing protocol; asymmetric signatures are another option. Provider and consumer share a secret (`whsec_...`). The provider computes (this is Stripe's scheme):

```formula
m = t + "." + b
sig = HMAC(k, m)
where
m: the signed message: the bytes the signature covers
t: the timestamp of the delivery, as a Unix timestamp in seconds
b: the raw request body, exactly the bytes sent
+: joined end to end (concatenation), not addition
k: the shared webhook secret
HMAC: HMAC-SHA256, a keyed hash that only someone holding k can compute; it outputs 32 bytes, sent as 64 hex characters
sig: the signature
In words: glue the timestamp, a dot and the raw body together, then hash that with the shared secret.
```

and sends `t=<timestamp>,v1=<sig>` in a header. For the delivery above, the signed message is `1767225600.` followed by the exact body bytes. The consumer recomputes the HMAC and compares. In Python:

```python
import hashlib, hmac

def sign(secret, t, raw_body):
    # Bind the timestamp to exact body
    # bytes.
    msg = t.encode() + b"." + raw_body
    # Hex is the signature header value.
    return hmac.new(secret, msg,
        hashlib.sha256).hexdigest()
```

Details that matter:

- **Use the raw body bytes.** If your framework parses and re-serialises the JSON first, whitespace or key order changes and the signature won't match.
- **Compare in constant time** (`hmac.compare_digest`, `crypto.timingSafeEqual`). Ordinary equality checks are not guaranteed constant-time and can expose timing differences; use a vetted constant-time comparison for appropriately validated equal-length inputs.
- **Support multiple secrets during rotation.** Stripe and the Standard Webhooks spec allow several signatures in one header so old and new secrets both verify during the changeover.

GitHub uses `X-Hub-Signature-256: sha256=<hmac>`, computed over the body alone, with no timestamp. The **Standard Webhooks** specification (backed by Svix, Zapier, Twilio and others) standardises `webhook-id`, `webhook-timestamp` and `webhook-signature` headers, and signs `id.timestamp.body`, so the message id and timestamp are both covered.

## Problem 2: replay attacks

An attacker who captures one genuine, correctly signed webhook (from a log, a misconfigured proxy) can resend it later. The signature is still valid.

Defences:

- **Sign the timestamp** along with the body (as above), and **reject events whose timestamp is too old**. Stripe's libraries default to a 5-minute tolerance. The check is shown below this list.
- **Deduplicate by event id.** Store processed `evt_...` ids and ignore repeats. You need this anyway for retries (below). For GitHub, `X-GitHub-Delivery` is useful for ordinary redelivery deduplication, but it is not included in the body HMAC: someone replaying a captured body can change that header. Use authenticated payload identity or a retained digest of the verified raw body where appropriate, make business effects idempotent, and reconcile current provider state. Without signed freshness or retained identity, the signature alone cannot reject an old valid payload.

The following one-sided age check rejects old deliveries after signature verification. Follow the provider SDK's clock-skew policy as well; this inequality alone does not reject future timestamps.

```formula
T_now − t ≤ τ
T_now − t = 1,767,226,500 − 1,767,225,600
T_now − t = 900 s
where
T_now: the receiver's current time, as a Unix timestamp in seconds
t: the signed timestamp from the header
τ: tau, the tolerance, here 300 s (5 minutes)
≤: less than or equal to; the event is accepted only when this holds
s: seconds
In words: accept the event only if it was signed within the tolerance; a delivery signed 900 s (15 minutes) ago fails the 300 s check, so it is refused even though its signature is genuine.
```

> [!warning] Why the timestamp must be inside the signature
> If the timestamp were sent separately and unsigned, an attacker could replay an old body with a fresh timestamp. Including it in the signed string means changing it breaks the signature.

## Key takeaways
- A webhook is a provider-to-consumer HTTP notification whose public endpoint must authenticate each request.
- Sign the provider-defined raw bytes and compare with a vetted constant-time function.
- Signed freshness and retained authenticated identity solve different replay cases.
- Use overlapping signatures during supported secret rotation; unsigned delivery identifiers cannot prove freshness.

## Further reading
- [Stripe docs: Verify webhook signatures](https://docs.stripe.com/webhooks/signature)
- [GitHub docs: Validating webhook deliveries](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)
- [Standard Webhooks specification](https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md)
