---
id: cs2-payment-system
title: Payment system
level: advanced
minutes: 17
summary: Design a payments platform that prevents duplicate postings and detects unresolved money movements, covering payment state machines, idempotency keys, a double-entry ledger, PSP integration with webhooks, and daily reconciliation.
---

Most systems tolerate a little inconsistency. A payment system doesn't. A duplicate charge is a furious customer and a chargeback. A lost capture is lost revenue. A ledger that doesn't balance is a regulatory problem.

The honest framing in an interview is that the network can't give you exactly-once, so you aim for **effectively-once operations within explicit provider contracts** using idempotency keys, state machines, an immutable double-entry ledger, and reconciliation against external truth.

## Requirements

Assume a marketplace (think ride-hailing or e-commerce). Customers pay, the platform takes a fee, and sellers are paid out.

### Functional
- Accept card and wallet payments through one or more **PSPs** (Payment Service Providers such as Stripe, Adyen or Braintree).
- Authorise, capture, refund (full or partial), and handle chargebacks.
- Keep a **ledger** of who owes whom.
- Pay sellers on a schedule (daily payouts to bank accounts).
- Reconcile with PSP settlement reports and bank statements.

### Non-functional
- **Correctness over availability**. It's better to fail a payment cleanly than to double-charge.
- **Idempotency** on every mutating operation, end to end.
- **Auditability**: an immutable history and the ability to explain every penny.
- **Security**: minimise PCI DSS scope (never store raw card numbers).
- Latency target for an uncomplicated card request: 1–3 s as an illustrative product budget. Authentication, asynchronous methods and settlement can take much longer.

## Back-of-the-envelope

```
Payments: 10 M/day
  avg 10e6 / 86,400 = ~115/s
  peak (10x) = ~1,200/s
Ledger entries per payment: ~5
  (charge, fee, PSP fee, payable...)
  peak = ~6,000 entry writes/s
Entry ~200 B:
  10e6 x 5 x 200 B = 10 GB/day
  = ~3.6 TB/year, retained 7+ years
```

The estimate is a starting workload, not proof that any particular database configuration handles it. Benchmark the transaction shape, contention, replication and indexes. What's hard is **correctness under partial failure**: timeouts, retries, crashes between steps, and webhooks arriving out of order. Data volume matters mainly because of retention. Retention depends on jurisdiction and record type. For example, UK limited companies generally retain accounting records for six years from the end of the relevant company financial year, with exceptions requiring longer retention. The seven-year figure above is a scenario assumption. Plan retrieval and retention accordingly.

> **Content gap:** no production capacity benchmark or jurisdiction-complete financial compliance analysis is supplied. The schema, accounting policy and timing targets are illustrative; they are not a complete regulated payments implementation.

## API design

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

- **Amounts are integers in minor units** (2350 = £23.50) with an explicit currency. Never use floats. binary64 arithmetic commonly gives `0.1 + 0.2 != 0.3`. Exact decimal types are also valid when precision and rounding are specified; IEEE 754 includes decimal formats.
- **`payment_method_token`, never a card number.** The card is collected by the PSP's hosted fields or SDK and swapped for a token, which reduces PCI DSS scope; the merchant still has compliance obligations that depend on the integration.
- **Every mutating call takes an idempotency key.**

## Data model

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
4. Expire keys after a window. Stripe, for example, may remove a key once it is at least 24 hours old, so a retry after that is treated as a new request.

The 409 versus 422 split above matches the IETF's Internet-Draft for an `Idempotency-Key` HTTP header. That draft has expired without becoming an RFC, but its status codes are a sensible convention for your own API.

Idempotency has to go **all the way down**. When your orchestrator calls the PSP, pass a deterministic idempotency key derived from your payment id, for example `pay_123:authorise`. If your own retry of the PSP call happens after a crash, the PSP can deduplicate it within its documented endpoint, parameter and retention contract. After key expiry, reconcile rather than blindly resubmitting an unresolved payment. Use a distinct stable operation ID for each capture/refund, including multiple partial refunds.

## Deep dive 2: the payment state machine

```
CREATED -> AUTHORISING -> AUTHORISED
  -> CAPTURING -> CAPTURED -> SETTLED
AUTHORISING -> DECLINED | FAILED
AUTHORISING -> UNKNOWN (timeout)
CAPTURED -> REFUNDING -> (PART)REFUNDED
CAPTURED -> DISPUTED -> WON | LOST
```

- Every transition is a conditional update: `UPDATE payments SET status=:new, version=v+1 WHERE id=:id AND status=:expected AND version=v`. The transition graph, version check and atomic ledger write together prevent invalid regression; conditional updates alone do not define a correct graph. Track authorisation, capture, refund amounts and disputes separately where they overlap.
- Persist **before** calling out (move to AUTHORISING, *then* call the PSP), so after a crash you know a call may have happened.

### The UNKNOWN state
The PSP call times out. Did the charge happen? You **don't know**, and guessing either way is wrong.

- Don't mark it FAILED and let the customer retry with a new key. That's how double charges happen.
- Do mark it UNKNOWN, then **resolve** it: retry within the PSP's documented idempotency contract with the *same* key, or query the PSP for the payment's status, or wait for the webhook. A background resolver sweeps UNKNOWN payments until resolved, escalating unresolved cases for investigation. An authorisation can be declined, cancelled or expire without settling.

## Deep dive 3: the double-entry ledger

Double-entry bookkeeping has been the basis of accounting for over 500 years, and it maps beautifully onto software.

- Each **transaction** consists of two or more **entries**. Each entry debits or credits one account.
- **Entries in a transaction sum to zero** per currency. This is an accounting equality; balancing entries alone does not prove the economic event is valid or that cash is conserved.
- Entries are **immutable and append-only**. Mistakes are fixed by posting a *reversing* transaction, never by an UPDATE. History is the audit trail.
- An account's **balance is the sum of its entries**. You can materialise it for speed, but it must always be derivable.

### Worked example
A customer pays £100 for a ride. The driver gets 80% and the platform keeps 20%, and the PSP charges a £1.50 fee. Once the capture settles, one balanced transaction records it:

| Account | Debit | Credit |
|---|---|---|
| PSP clearing (asset) | 98.50 | |
| PSP fees (expense) | 1.50 | |
| Driver payable (liability) | | 80.00 |
| Platform revenue | | 20.00 |
| **Total** | **100.00** | **100.00** |

In storage, a common convention is signed integers in minor units, with debits positive and credits negative:

```
txn capture:pay_123
  psp_clearing       +9850
  psp_fee_expense     +150
  driver_payable     -8000
  platform_revenue   -2000
                 sum     0
```

When the PSP pays out, a second transaction debits `bank` and credits `psp_clearing` by 9,850. When the driver is paid, `driver_payable` is debited and `bank` credited by 8,000. Each step balances, and every account's balance explains exactly where the money is.

### Making it consistent
- Write the entries for one transaction **atomically**, in one database transaction, together with the payment state change and an outbox row.
- Put a `UNIQUE` constraint on `ledger_txns.ref_id` (for example `capture:pay_123`), so a re-processed event can't post twice.
- To keep a materialised balance, update `accounts.balance` in the same transaction using optimistic concurrency. Enforce account-type-aware balance limits atomically. With debits-positive storage, credit-normal liabilities naturally have negative stored sums; a blanket `balance >= 0` check would be wrong.

### Hot accounts
Every payment touches `platform_revenue`, so updating its balance row 1,200 times a second serialises on one lock. Options:

- Split it into N sub-accounts (`platform_revenue_07`) and sum them on read.
- Don't materialise balances for hot accounts. Compute them from entries plus periodic snapshots.
- Batch postings to hot accounts every few seconds.

Purpose-built ledger databases such as TigerBeetle exist precisely because this workload (tiny, contended, must-be-correct transfers) is awkward for general-purpose databases.

## Deep dive 4: PSP integration and webhooks

PSPs report many outcomes **asynchronously** via webhooks: 3-D Secure completion, captures, refunds, disputes, payouts.

- **Verify using the provider's documented scheme or SDK**. For Stripe this includes the raw body and signed timestamp; check timestamp tolerance and deduplicate event IDs because an authentic event can be replayed within the tolerance.
- **Dedupe by `event_id`**. Insert into `psp_events` with a primary key. If it already exists, return `200` and do nothing. Providers can retry webhook delivery, so duplicates are possible; finite retry windows still permit missed events. Ensure stored but unprocessed events remain discoverable after a crash.
- **Don't trust order.** `charge.refunded` can arrive before `charge.captured`. Either apply events through the state machine, which rejects invalid transitions and retries them later, or treat the webhook as a hint and **fetch the current object** from the PSP API.
- **Acknowledge fast**: write the event durably, return `200`, and process it asynchronously. Slow handlers cause PSP timeouts and redelivery storms.

Multi-PSP setups add **routing**: choose a provider by cost, region, card type and live health, with a circuit breaker for new, unattempted operations. Do not reroute an ambiguous in-flight charge to another PSP: keys are not shared across providers, and the first may already have charged. Resolve its outcome first. Each adapter normalises provider-specific states into your state machine.

## Deep dive 5: reconciliation

Even with perfect code, your view and the outside world's will drift: a webhook never delivered, a manual refund issued in the PSP dashboard, a bank returning a payout. **Reconciliation** is the safety net.

1. Each day, ingest the PSP's **settlement report** (every transaction it settled, its fees and the net payout) and the **bank statement**.
2. **Match** records on references (PSP payment id, payout id) and amounts:
   - internal ledger ↔ PSP report (did every capture we recorded settle, at the amount and fee we expected?)
   - PSP payout ↔ bank deposit (did the money actually arrive?)
3. Unmatched or mismatched items become **breaks**: classify them, auto-resolve known patterns (for example, a missed webhook: fetch the object and post the missing transaction), and send the rest to a finance-ops queue.
4. Track break counts and ageing as key health metrics.

Reconciliation checks agreement with the external records available at a point in time. Missing reports, settlement timing and source errors still require investigation; agreement is evidence, not a proof that every economic event is correct.

## Bottlenecks and trade-offs

- **Synchronous vs asynchronous capture**: auth-and-capture in one call is simpler. Separate capture (capture at fulfilment, like a ride ending) reduces refunds but adds a state and an expiry. Online card authorisations typically lapse after about 7 days, and sooner for some networks and in-person payments (Stripe lists 2–5 days for several cases), so a delayed capture needs a deadline and an alert.
- **Strong consistency** requires a protocol that orders conflicting operations; one home write region per account is one design, not a requirement. Cross-region consensus is another, with latency and availability trade-offs.
- **Hot accounts** need splitting or batching, as above.
- **Retention vs cost**: keep years of entries online but tiered (hot recent partitions, cold older ones), and archive to immutable object storage.

## Evolving at 10x

- **12,000 payments/s peak**: shard the ledger by account id. Cross-shard transactions (customer on shard A, seller on shard B) become two-phase transfers via a clearing account, or a saga with compensating entries.
- **Event-sourced core**: ledger entries *are* the events. Balances, reports and analytics are projections built by streaming the entries through Kafka.
- **More rails**: bank transfers, open banking and local payment methods each get an adapter into the same state machine and ledger.
- **Risk and fraud** scoring inline before authorisation, using models on device, velocity and history, within a strict latency budget.

## Key takeaways
- Duplicate-resistant money movement combines: client idempotency keys, deterministic idempotency keys to the PSP, conditional state-machine transitions and unique ledger references.
- Persist intent before calling out. Treat a timeout as UNKNOWN and resolve it with the same key or a status query, never by assuming failure.
- Use an append-only double-entry ledger with integer minor units, where every transaction sums to zero and corrections are reversing entries.
- Webhooks may be duplicated, reordered or ultimately missed. Verify signatures, dedupe on event id, acknowledge fast, and apply them through the state machine or re-fetch the current state.
- Reconcile daily against PSP settlement files and bank statements. Breaks are inevitable, so detect and resolve them systematically.

## Further reading
- [Designing robust and predictable APIs with idempotency (Stripe)](https://stripe.com/blog/idempotency)
- [Idempotent requests (Stripe API docs)](https://docs.stripe.com/api/idempotent_requests)
- [The Payment Intents API (Stripe docs)](https://docs.stripe.com/payments/payment-intents)
- [Accounting for developers, part I (Modern Treasury)](https://www.moderntreasury.com/journal/accounting-for-developers-part-i)
- [Double-entry bookkeeping (Wikipedia)](https://en.wikipedia.org/wiki/Double-entry_bookkeeping)
- [Two Generals' Problem (Wikipedia)](https://en.wikipedia.org/wiki/Two_Generals%27_Problem)
