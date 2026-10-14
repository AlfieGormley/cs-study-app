---
id: cs2-payment-system-operation-contracts
title: Payment amounts and idempotency
level: advanced
minutes: 5
summary: Represent money exactly and keep one operation identity through every retry boundary.
sourceLesson: cs2-payment-system
---

## API design

This is an illustrative endpoint contract, not a runnable HTTP request. Arrows distinguish responses from submitted fields.

```
POST /v1/payments
  Idempotency-Key: 6f1c...
  { amount: 2350, currency: "GBP",
    customer_id, payment_method_token,
    order_id, capture: "automatic" }
  -> { payment_id, status }

POST /v1/payments/{id}/capture
  Idempotency-Key: ...
POST /v1/payments/{id}/refunds
  Idempotency-Key: ...
  { amount: 500 }

POST /webhooks/psp/{provider}
  (signed by PSP)
GET  /v1/accounts/{id}/balance
```

Three rules:

- **Amounts are integers in minor units** (2,350 pence represents £23.50) with an explicit currency. A minor unit is the currency's smallest subdivision, such as the penny for pounds sterling:

```formula
A_major = A_minor / 10^d
£23.50 = 2,350 / 10^2
where
A_major: the amount in the main currency unit, such as pounds (£)
A_minor: the stored whole number of minor units, such as pence
d: the number of decimal places the currency uses; 2 for GBP (pounds), 0 for JPY (yen), 3 for BHD (Bahraini dinar)
10^d: d copies of 10 multiplied together; 10^2 = 100
£: pounds sterling
In words: store whole pence and divide by 100 only when displaying pounds, so the stored value is always exact.
```

The currency's number of decimal places is defined by the ISO 4217 currency standard, so look it up rather than assuming 2. Avoid binary floating-point for exact money amounts: many decimal fractions are not exactly representable. Exact decimal types are also valid when precision and rounding are specified; IEEE 754 includes decimal formats.
- **`payment_method_token`, never a card number.** The card is collected by the PSP's hosted fields or SDK and swapped for a token, which reduces PCI DSS scope; the merchant still has compliance obligations that depend on the integration.
- **Every mutating call takes an idempotency key.**

## Data model

This is a schema sketch: PK marks the primary key. It omits executable type declarations and migrations.

```
payments(payment_id PK, order_id,
  amount, currency, status, psp,
  psp_payment_ref, version, created_at)

idempotency_keys(key, merchant_id, PK both
  request_hash, status, response,
  locked_until, created_at)

ledger_entries(entry_id PK, txn_id,
  account_id, amount (signed, minor),
  currency, created_at)   -- append-only
ledger_txns(txn_id PK, type,
  ref_id UNIQUE, created_at)

accounts(account_id PK, type, currency,
  balance, version)       -- materialised

psp_events(provider, event_id, PK both
  payload, processed_at)
```

## High-level architecture

Follow the arrows as data paths; the drawing is not a deployment specification.

```
 Client (PSP SDK tokenises card)
        |
        v
+---------------+   +--------------+
| Payments API  |-->| Idempotency  |
+---------------+   | store        |
        |           +--------------+
        v
+---------------+   +--------------+
| Payment       |-->| PSP adapter  |
| orchestrator  |   | (Stripe,     |
| (state mach.) |<--| Adyen, ...)  |
+---------------+   +--------------+
        |   ^  webhooks    |
        v   +--------------+
+---------------+   +--------------+
| Ledger        |   | Reconciler   |
| (double-entry)|<->| (daily files)|
+---------------+   +--------------+
        |
        v
  Payouts -> bank rails
```

## Deep dive 1: idempotency keys

A mobile client sends `POST /payments`, the response is lost to a timeout, and the client retries. Without protection, the customer is charged twice. The fix, popularised by Stripe:

1. The client generates a **unique key per logical operation** (a UUID) and reuses it on every retry of that operation.
2. The server does an `INSERT` into `idempotency_keys` with status `in_progress` and a hash of the request body.
   - If the insert succeeds, process the request.
   - First check merchant/operation scope and request fingerprint; if they match and the key is **completed**, return the stored result.
   - If the key exists and is **in progress**, return `409` (or wait). A concurrent duplicate must not run in parallel.
   - If the key exists with a **different request hash**, return `422`. The same key was reused for a different operation, which is a client bug.
3. On completion, store the response and mark the key completed. Do this in the same transaction as the business state change wherever possible.
4. Expire keys after a window. For Stripe API v1, a key may be pruned once it is at least 24 hours old; reusing a pruned key makes a new request. API v1 replays the first executed status/body, including server errors, while API v2 has different retry semantics. Check the deployed endpoint contract.

The 409 versus 422 split above matches the IETF's Internet-Draft for an `Idempotency-Key` HTTP header. That draft has expired without becoming an RFC, but its status codes are a sensible convention for your own API.

Idempotency has to go **all the way down**. When your orchestrator calls the PSP, pass a deterministic idempotency key derived from your payment id, for example `pay_123:authorise`. If your own retry of the PSP call happens after a crash, the PSP can deduplicate it within its documented endpoint, parameter and retention contract. After key expiry, reconcile rather than blindly resubmitting an unresolved payment. Use a distinct stable operation ID for each capture/refund, including multiple partial refunds.

## Key takeaways
- Use explicit currency and exact minor-unit or decimal arithmetic.
- Atomically claim scoped operation keys and reject mismatched request fingerprints.
- Provider retention and operation scope constrain safe same-key retries.

## Further reading
- [Designing robust and predictable APIs with idempotency (Stripe)](https://stripe.com/blog/idempotency)
- [Idempotent requests (Stripe API docs)](https://docs.stripe.com/api/idempotent_requests)
- [The Payment Intents API (Stripe docs)](https://docs.stripe.com/payments/payment-intents)
- [Stripe currency amount rules](https://docs.stripe.com/currencies)
