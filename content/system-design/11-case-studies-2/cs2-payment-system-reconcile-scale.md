---
id: cs2-payment-system-reconcile-scale
title: Payment reconciliation and ledger scaling
level: advanced
minutes: 4
summary: Investigate external mismatches and recover cross-shard transfers safely.
sourceLesson: cs2-payment-system
---

## Deep dive 5: reconciliation

Even with perfect code, your view and the outside world's will drift: a webhook never delivered, a manual refund issued in the PSP dashboard, a bank returning a payout. **Reconciliation** is the safety net.

1. Each day, ingest the PSP's **settlement report** (every transaction it settled, its fees and the net payout) and the **bank statement**.
2. **Match** records on references (PSP payment id, payout id) and amounts:
   - internal ledger ↔ PSP report (did every capture we recorded settle, at the amount and fee we expected?)
   - PSP payout ↔ bank deposit (did the money actually arrive?)
3. Unmatched or mismatched items become **reconciliation breaks**: classify them, auto-resolve known patterns (for example, a missed webhook: fetch the object and post the missing transaction), and send the rest to a finance-ops queue.
4. Track reconciliation-break counts and ageing as key health metrics.

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

## Recovering an account-sharded transfer

At larger scale, the two accounts in one transfer may live on different shards. A local commit on the customer shard cannot atomically prove the seller shard accepted the corresponding entry. Persist a unique transfer identity and durable intent with the first balanced clearing transaction. The destination posts its own balanced clearing transaction once under that identity, and a recoverable relay records progress and retries after crashes.

Individual pending transfers need monitoring: opposite in-flight clearing balances can cancel in aggregate while two customers still have unresolved movements. Compensation also needs coordination. Before refunding the first leg, establish a terminal cancellation at the destination that rejects any delayed second-leg attempt. Otherwise a slow delivery can credit the seller after the customer has been refunded. A clearing-account pattern exposes intermediate state; it does not erase distributed failure.

> **Content gap:** no production capacity benchmark or jurisdiction-complete financial compliance analysis is supplied. The schema, accounting policy and timing targets are illustrative; they are not a complete regulated payments implementation.

## Key takeaways
- Match internal entries, provider settlement and bank receipts by references and amounts.
- Split or snapshot hot accounts without losing the ability to derive balances.
- Cross-shard transfers need durable retry progress and terminal cancellation fencing before compensation.

## Further reading
- [Designing robust and predictable APIs with idempotency (Stripe)](https://stripe.com/blog/idempotency)
- [Idempotent requests (Stripe API docs)](https://docs.stripe.com/api/idempotent_requests)
- [The Payment Intents API (Stripe docs)](https://docs.stripe.com/payments/payment-intents)
- [Accounting for developers, part I (Modern Treasury)](https://www.moderntreasury.com/journal/accounting-for-developers-part-i)
- [Two Generals' Problem (Wikipedia)](https://en.wikipedia.org/wiki/Two_Generals%27_Problem)
