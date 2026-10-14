---
id: cx-amortised-credits
sourceLesson: cx-amortised-analysis
title: Banking credits for expensive steps
level: advanced
minutes: 3
summary: Use the accounting method to save credit during cheap operations.
---

The aggregate proof bounded all appends together. The accounting method instead assigns credit to elements so that each future copy has already been paid for.

## Method 2: the accounting method

Charge each operation a fixed **amortised cost**, which may be more than it really costs. The overcharge is stored on elements of the structure as **amortised credit**, and expensive operations pay for themselves out of saved credit. The rule: **credit must never go negative**.

For the dynamic array, charge **3 units** per append:

1. 1 unit pays for writing the new element now.
2. 1 unit is stored on the new element, to pay for copying it at the next resize.
3. 1 unit is stored on an element from the *older half* of the array, which already spent its credit in the previous resize.

Why it works: look at the append that triggers a resize from capacity k to 2k, plus the k − 1 appends after it that fill the new array. Those k appends each bank 2 units:

```formula
banked = k × 2 = 2 × k
needed = 2 × k
banked − needed = 0 ≥ 0
where
banked: the credit saved by the k appends between two resizes, in units
needed: the cost of copying all 2k elements at the next resize, in units
k: the capacity before the earlier resize; the new capacity is 2 × k
≥: greater than or equal to
In words: the appends that fill the new half save exactly enough credit to copy the whole array next time, so the credit never goes negative.
```

```
resize 4 -> 8, then write e:
  [o o o o e _ _ _]   e banks 2
3 more appends (f, g, h):
  [o o o o e f g h]   8 banked
append i: copy 8, spending all 8
```

Since the bank never goes negative, the real total cost is at most the total charged: **3n**.

## Key takeaways
- An accounting proof charges cheap operations more than their immediate cost.
- Saved credit pays for later expensive operations.
- The credit must not go negative if the charges are to bound actual cost.

## Further reading
- [Accounting method — Wikipedia](https://en.wikipedia.org/wiki/Accounting_method_(computer_science))
- [Erickson: Amortized Analysis](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/09-amortize.pdf)
