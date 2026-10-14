---
id: cs2-payment-system-balanced-ledger
title: Double-entry ledger invariants
level: advanced
minutes: 4
summary: Post immutable balanced transactions with precise signs and atomic references.
sourceLesson: cs2-payment-system
---

## Deep dive 3: the double-entry ledger

Double-entry bookkeeping has been the basis of accounting for over 500 years, and it maps beautifully onto software.

- Each **transaction** consists of two or more **entries**. Each entry debits or credits one account.
- **Entries in a transaction sum to zero** per currency:

```formula
Σ a_i = 0
where
Σ: sigma, "add up all of": here every entry in one transaction
a_i: the signed amount of entry number i, in minor units; debits positive, credits negative
i: counts through the entries of the transaction (1, 2, 3, ...)
In words: within one transaction, the debits and credits in each currency cancel out exactly.
```

This is an accounting equality; balancing entries alone does not prove the economic event is valid or that cash is conserved.
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

This local calculation checks the illustrative posting; the database must enforce atomicity and the unique capture reference separately.

```python
# Pence: debits positive, credits negative.
entries = {
    "psp_clearing": 9850,
    "psp_fee_expense": 150,
    "driver_payable": -8000,
    "platform_revenue": -2000,
}
# Zero checks only this balance equality.
print(sum(entries.values()))  # 0
```

Checking the sum-to-zero rule for this transaction:

```formula
Σ a_i = 9,850 + 150 − 8,000 − 2,000
Σ a_i = 10,000 − 10,000 = 0
where
Σ: sigma, "add up all of": every entry in the transaction
a_i: the signed amount of entry i, in pence (minor units of GBP); debits positive, credits negative
i: counts through the four entries
In words: £100.00 of debits (10,000 pence) exactly cancels £100.00 of credits, so the transaction balances.
```

When the PSP pays out, a second transaction debits `bank` and credits `psp_clearing` by 9,850. When the driver is paid, `driver_payable` is debited and `bank` credited by 8,000. Each step balances, and every account's balance explains exactly where the money is.

### Making it consistent
- Write the entries for one transaction **atomically**, in one database transaction, together with the payment state change and an outbox row.
- Put a `UNIQUE` constraint on `ledger_txns.ref_id` (for example `capture:pay_123`), so a re-processed event can't post twice.
- To keep a materialised balance, update `accounts.balance` in the same transaction using optimistic concurrency. Enforce account-type-aware balance limits atomically. With debits-positive storage, credit-normal liabilities naturally have negative stored sums; a blanket `balance >= 0` check would be wrong.

### Hot accounts
Every payment touches `platform_revenue`, so updating its balance row 1,200 times a second serialises on one lock. Options:

- Split it into N sub-accounts, where N is however many you need to spread the writes (`platform_revenue_07` is one of them), and sum them on read.
- Don't materialise balances for hot accounts. Compute them from entries plus periodic snapshots.
- Batch ledger entries for hot accounts every few seconds.

Purpose-built ledger databases such as TigerBeetle exist precisely because this workload (tiny, contended, must-be-correct transfers) is awkward for general-purpose databases.

## Key takeaways
- Balance debits and credits separately for each currency.
- Post all entries and business-state changes atomically with unique operation references.
- Corrections append reversing entries rather than editing history.

## Further reading
- [Accounting for developers, part I (Modern Treasury)](https://www.moderntreasury.com/journal/accounting-for-developers-part-i)
- [Double-entry bookkeeping (Wikipedia)](https://en.wikipedia.org/wiki/Double-entry_bookkeeping)
