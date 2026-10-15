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

```formula
ε_k ≤ (1/2)^k = 2^{−k}
ε_20 ≤ 2^{−20} ≈ 9.5 × 10^{−7}
where
ε_k, ε_20: the probability that all k (or 20) independent runs miss a yes-instance (the error after k runs)
k: the number of independent runs; 20 in the second line
(1/2)^k: k copies of one-half multiplied together: each run misses with probability at most 1/2, and independent probabilities multiply
≤: is at most
≈: approximately equal to
In words: every extra run halves the chance of missing a yes-instance. Twenty runs bring it below one in a million, and no-instances are never wrongly accepted.
```

**One-sided error (coRP).** Accept only if all independent trials accept; reject if any rejects. A yes-instance always passes, while a no-instance fools the combined test only when every trial falsely accepts. Miller–Rabin has this direction: declaring prime requires all bases to pass. Repeating an identical random base does not supply independent evidence.

**Two-sided error (BPP).** Run the algorithm an odd number of times and take the **majority vote** answer. The majority is wrong only when at least half of the runs are wrong:

```formula
ε_r = Σ C(r, i)p^i (1 − p)^{r−i}
  for (r + 1)/2 ≤ i ≤ r
ε_3 = 3 × (1/3)^2 × (2/3) + (1/3)^3
ε_3 = 6/27 + 1/27 = 7/27 ≈ 0.26
ε_r ≤ e^{−cr}
where
ε_r, ε_3: the probability that the majority of r (or 3) runs is wrong
r: the number of independent runs, an odd whole number; 3 in the worked lines
i: the number of runs that are wrong; the sum covers every i from (r + 1)/2 up to r
Σ: sum: add up the term after it for every value of i in the stated range
C(r, i): "r choose i", the number of ways to pick which i of the r runs are wrong
p: the error probability of one run; here 1/3
e: Euler's number, about 2.718, the base of natural exponentials
c: a positive constant depending on the fixed error p, which is strictly below one half; here p is one third (Chernoff gives an exponentially shrinking bound)
≈: approximately equal to
≤: is at most
In words: add up the chances of every outcome where wrong runs make up more than half of the runs. With error 1/3, three runs give 7/27, about 0.26; the Chernoff bound guarantees the error then shrinks exponentially as r grows.
```

The code below evaluates the same sum, starting from error 1/3:

```python
from math import comb

def majority_error(r, p=1/3):
    # P(at least half of r runs wrong)
    # Count every majority-wrong outcome
    # once.
    return sum(comb(r, i) * p**i
               * (1 - p)**(r - i)
               for i in range((r + 1) // 2,
                              r + 1))

for r in (1, 11, 31, 101):
    print(r, f"{majority_error(r):.2g}")
# 1 0.33
# 11 0.12
# 31 0.027
# 101 0.00027
```

So BPP with error 2 to the power −100 is the same class as BPP with error 1/3. The mathematical error bound assumes independent random choices and correct execution; it is not a hardware-reliability estimate.

The demonstration function is used only with positive odd trial counts and a fixed per-run error strictly below one half. Without a success gap above one half, majority voting has no uniform polynomial-repetition guarantee.

## Key takeaways

- RP uses any-accept; coRP uses all-accept on independent trials.
- BPP uses majority voting with a success probability bounded above one half.
- The mathematical error bound assumes independent trials and correct execution.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Randomised complexity — Arora lecture notes](https://users.cs.duke.edu/~reif/courses/complectures/Arora/lec6.pdf)
