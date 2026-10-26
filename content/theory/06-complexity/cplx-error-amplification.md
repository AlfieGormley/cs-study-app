---
id: cplx-error-amplification
title: "Amplifying one-sided and two-sided decisions"
level: advanced
minutes: 4
summary: "RP uses any-accept; coRP uses all-accept on independent trials."
sourceLesson: cplx-randomised-quantum
---

## Amplification

**One-sided error (RP).** Run the algorithm several times and accept if any run accepts. A no-instance is never accepted; a yes-instance is missed only if every run misses:

```formula reference
ε_k ≤ (1/2)^k = 2^{−k}
where
ε_k: the probability that all k independent runs miss a yes-instance
k: the positive number of independent runs
(1/2)^k: k copies of one-half multiplied together: each run misses with probability at most 1/2, and independent probabilities multiply
≤: is at most
≈: approximately equal to
In words: each fresh independent trial reduces the chance of missing a yes-instance by at least another factor of two. No-instance rejection remains certain.
```

**One-sided error (coRP).** Accept only if all independent trials accept; reject if any rejects. A yes-instance always passes, while a no-instance fools the combined test only when every trial falsely accepts. Miller–Rabin has this direction: declaring prime requires all bases to pass. Repeating an identical random base does not supply independent evidence.

**Two-sided error (BPP).** Run the algorithm an odd number of times and take the **majority vote** answer. The majority is wrong only when at least half of the runs are wrong:

```formula reference
ε_r = Σ C(r, i)p^i (1 − p)^{r−i}
  for (r + 1)/2 ≤ i ≤ r
ε_r ≤ e^{−cr}
where
ε_r: the probability that the majority of r independent runs is wrong
r: the positive odd number of independent runs
i: the number of runs that are wrong; the sum covers every i from (r + 1)/2 up to r
Σ: sum: add up the term after it for every value of i in the stated range
C(r, i): "r choose i", the number of ways to pick which i of the r runs are wrong
p: the error probability of one run; here 1/3
e: Euler's number, about 2.718, the base of natural exponentials
c: a positive constant depending on the fixed error p, which is strictly below one half; here p is one third (Chernoff gives an exponentially shrinking bound)
≈: approximately equal to
≤: is at most
In words: count every outcome with a wrong majority, including cases where only some trials fail. Independent repetitions with a fixed success advantage above one half reduce the majority error exponentially.
```

With three trials, the majority is wrong when either two or all three answers are wrong. Multiplying the probabilities of three wrong answers alone misses the first case. Reusing one random seed to repeat the identical computation provides no independent evidence.

So BPP with error 2 to the power −100 is the same class as BPP with error 1/3. The mathematical error bound assumes independent random choices and correct execution; it is not a hardware-reliability estimate.

Use positive odd trial counts to avoid ties and fresh independent randomness on each run, with a fixed per-run error strictly below one half. Without a success gap above one half, majority voting has no uniform polynomial-repetition guarantee.

## Key takeaways

- RP uses any-accept; coRP uses all-accept on independent trials.
- BPP uses majority voting with a success probability bounded above one half.
- The mathematical error bound assumes independent trials and correct execution.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Randomised complexity — Arora lecture notes](https://users.cs.duke.edu/~reif/courses/complectures/Arora/lec6.pdf)
