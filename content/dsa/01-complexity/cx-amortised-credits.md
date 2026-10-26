---
id: cx-amortised-credits
sourceLesson: cx-amortised-analysis
title: Banking credits for expensive steps
level: advanced
minutes: 2
summary: Use the accounting method to save credit during cheap operations.
---

The accounting method explains an amortised bound by saving credit during cheap operations and spending it during expensive ones. Credit is a proof device, measured in counted work units; no actual runtime balance is needed.

## Charge enough to fund later copies

Use the doubling-array model, starting empty with capacity one. Count each copy and new-element write as one unit. Charge three units per append: one pays for the immediate write and two are saved.

Before a resize, saved credit pays to copy all existing elements. After doubling, the appends that fill the new half save enough to pay for the next whole-array copy. The first append also creates enough credit for the first small resize. Inductively, the bank never needs to go below zero.

Why save for older elements too? At the last resize those elements spent their previous copying credit. New appends must rebuild credit for the whole array, not just themselves. Banking two units per new element covers both halves by the next full state.

> [!analogy] Real-world analogy: Saving for an annual bill
> Regular payments can put aside money for an occasional larger bill.
>
> **How it maps:** Cheap appends contribute spare credit; resizing consumes that saved credit. A nonnegative balance proves earlier charges cover the real cost.
>
> **Where it stops:** There is no interest, prediction or random arrival rate. The algorithm proof must cover every allowed sequence from its stated initial state.

## The balance is the proof obligation

If a proposed charge lets the bank become negative, that accounting argument has failed: it is spending work credits never collected. This does not automatically prove the algorithm is slow; it means the proposed charges or invariant are insufficient.

Starting from a pre-populated array requires an initial-credit allowance. Supporting deletion requires a separate argument for the shrinking policy. A proof for append-only sequences does not automatically cover arbitrary updates.

## Key takeaways
- Cheap operations can prepay future expensive work.
- Credits must cover every allowed prefix of the sequence.
- A negative balance invalidates the proposed accounting proof.

## Further reading
- [Erickson: Amortized Analysis](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/09-amortize.pdf)
