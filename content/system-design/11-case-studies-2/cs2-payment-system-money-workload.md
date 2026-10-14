---
id: cs2-payment-system-money-workload
title: Payment workload and correctness boundaries
level: advanced
minutes: 4
summary: Size ledger traffic while distinguishing operational, retention and provider assumptions.
sourceLesson: cs2-payment-system
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

Assume 10 M (10 million) payments a day. Divide by the 86,400 seconds in a day for the average rate, then allow a peak of 10 times that (sales, evenings, holidays):

```formula
p_avg = P / 86,400 s
p_avg = 10,000,000 / 86,400 s ≈ 115/s
p_peak = 10 × p_avg ≈ 1,200/s
where
p_avg: average payments per second
P: payments per day; here 10 million
p_peak: payments per second at peak, assumed 10 times the average
86,400 s: the seconds in one day
s: seconds
≈: approximately equal to
In words: 10 million payments a day is about 115 a second on average and about 1,200 a second at a ten-times peak.
```

Each payment writes about 5 ledger entries (the charge, the platform fee, the PSP's fee, the amount payable to the seller, and so on), at about 200 bytes each:

```formula
e_peak = p_peak × n ≈ 1,200/s × 5 ≈ 6,000/s
D = P × n × b
D = 10,000,000 × 5 × 200 B = 10 GB/day
Y = 10 GB/day × 365 days ≈ 3.6 TB/year
where
e_peak: ledger entry writes per second at peak
p_peak: payments per second at peak; about 1,200
n: ledger entries per payment; about 5
D: ledger data written per day
P: payments per day; 10 million
b: bytes per ledger entry (B); about 200
Y: ledger data per year, kept for 7 or more years in this scenario
s: seconds
B: bytes
GB: gigabytes, 1,000,000,000 bytes
TB: terabytes, 1,000 GB
day: one day
days: days
year: one year
≈: approximately equal to
In words: about 6,000 entry writes a second at peak, adding about 10 GB a day, or about 3.6 TB a year.
```

The estimate is a starting workload, not proof that any particular database configuration handles it. Benchmark the transaction shape, contention, replication and indexes. What's hard is **correctness under partial failure**: timeouts, retries, crashes between steps, and webhooks arriving out of order. Data volume matters mainly because of retention. Retention depends on jurisdiction and record type. For example, UK limited companies generally retain accounting records for six years from the end of the relevant company financial year, with exceptions requiring longer retention. The seven-year figure above is a scenario assumption. Plan retrieval and retention accordingly.

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
- [UK company accounting-record retention](https://www.gov.uk/running-a-limited-company/company-and-accounting-records)
