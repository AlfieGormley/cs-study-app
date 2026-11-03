---
id: cs2-payment-system-money-workload
title: Payment workload and correctness boundaries
level: advanced
minutes: 4
summary: Size ledger traffic while distinguishing operational, retention and provider assumptions.
sourceLesson: cs2-payment-system
---

A payment system must distinguish permitted delays in display state from conflicting authoritative money movements. A duplicate charge is a furious customer and a chargeback. A lost capture is lost revenue. A ledger that doesn't balance is a regulatory problem.

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

## Count operations, not only payments

Use ten million daily payments as an illustrative workload, not a provider benchmark. A payment may create several ledger postings, state changes and provider calls. Refunds, disputes and retries add work after the initial checkout, while reconciliation reads old records.

Raw payload estimates exclude indexes, transaction records, replication and backups. The number of entries depends on the accounting policy: a gross revenue posting with a separate provider fee differs from a net presentation. Benchmark the actual transaction shape and hot accounts before inferring a safe payment rate.

## Correctness work survives the busy hour

A timeout can leave an operation unresolved even after the customer has left. Preserve its stable identity, provider reference and recoverable state. More retries do not remove ambiguity, and expired idempotency keys can make a blind resubmission unsafe.

Distinguish accepting an operation from completing it. Cleanly rejecting new work may protect the system; an in-flight UNKNOWN payment still needs reconciliation. Monitor ageing unresolved operations and durable relay backlogs as well as successful requests per second.

## Retention is a separate requirement

An append-only ledger accumulates history. Retention depends on record type, jurisdiction and the product's obligations; this architecture supplies no universal number of years. Specify required retention and retrieval before selecting hot storage, archival partitions and deletion policies. Keep those decisions separate from a chosen daily traffic estimate.

The central engineering difficulty is partial failure: a provider succeeds but its response is lost, an event arrives twice, or two paths try to post the same capture. Atomic local state, provider contracts and external reconciliation address different parts of that problem.

> **Content gap:** no production capacity benchmark or jurisdiction-complete financial compliance analysis is supplied. The schema, accounting policy and timing targets are illustrative; they are not a complete regulated payments implementation.

## Key takeaways
- Payment capacity is a transaction-shape and contention benchmark.
- Retention periods depend on jurisdiction and record type.
- Effectively-once external operations require explicit provider contracts and reconciliation.

## Further reading
- [Designing robust and predictable APIs with idempotency (Stripe)](https://stripe.com/blog/idempotency)
- [Idempotent requests (Stripe API docs)](https://docs.stripe.com/api/idempotent_requests)
- [The Payment Intents API (Stripe docs)](https://docs.stripe.com/payments/payment-intents)
- [Accounting for developers, part I (Modern Treasury)](https://www.moderntreasury.com/journal/accounting-for-developers-part-i)
