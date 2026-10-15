---
id: cplx-freivalds-checking
title: "Checking a matrix product with randomness"
level: advanced
minutes: 3
summary: "Freivalds compares three matrix–vector products using exact arithmetic."
sourceLesson: cplx-randomised-quantum
---

## Randomness in action

### Freivalds: checking a matrix product

Multiplying two n × n matrices naively costs about n³ multiplications; subcubic algorithms also exist. The comparison below is with naive multiplication, not a claim about the current best exponent. Checking a claimed product is cheaper: using exact integer arithmetic or arithmetic in a field, pick a random vector of 0s and 1s and multiply it through both sides.

```formula
A × (B × r) = C × r
cost = 3 × n^2
cost = 3 × 1000^2 = 3 × 10^6
where
A, B: the two n × n input matrices
C: the claimed product of A and B, an n × n matrix
r: a random column vector of n entries, each 0 or 1 with probability 1/2
B × r: a matrix–vector product: n^2 multiplications, giving a vector of n numbers
n: the number of rows (and columns) of each matrix; 1000 in the last line
cost: the number of multiplications in one trial (three matrix–vector products)
In words: if C really is A times B, both sides agree for every r. Each trial costs three matrix–vector products, about 3 million multiplications for 1000 × 1000 matrices, against about 10^9 to redo the product naively.
```

If C is wrong, a single trial exposes it with probability at least 1/2, so the chance that t independent trials all miss is at most 2 to the power −t (about one in a million for t = 20).

```python
import random

def freivalds(A, B, C, trials=20):
    n = len(A)
    def mul(M, x):
        return [sum(M[i][j] * x[j]
                    for j in range(n))
                for i in range(n)]
    # All trials must pass to accept the
    # product.
    for _ in range(trials):
        r = [random.randint(0, 1)
             for _ in range(n)]
        if mul(A, mul(B, r)) != mul(C, r):
            return False  # surely wrong
    return True  # wrong w.p. <= 2**-trials

A = [[1, 2], [3, 4]]
B = [[5, 6], [7, 8]]
good = [[19, 22], [43, 50]]
bad = [[19, 22], [43, 51]]
print(freivalds(A, B, good))  # True
print(freivalds(A, B, bad))
# Usually False; True with chance 2**-20.
```

For `bad`, the only wrong entry is at row 1, column 1 (0-indexed), so a trial catches it exactly when the random vector's entry `r[1]` is 1, with probability exactly 1/2.

> [!note] Content gap: empirical measurement
> The previous measured detection-rate claim has been omitted because no reproducible run record was available to verify it. The probability calculation above follows directly from the two equally likely values of `r[1]`. With 20 trials, `bad` slips through with probability 2 to the power −20, about one in a million.

These are arithmetic-operation counts, not a claim that unbounded integer multiplication costs one bit operation. Intermediate integer lengths and input encoding matter for bit complexity. Floating-point rounding can also invalidate the exact one-sided guarantee. Python’s random module illustrates ideal independent draws in the mathematical model; a finite pseudorandom generator is not itself a proof of independent randomness.

## Key takeaways

- Freivalds compares three matrix–vector products using exact arithmetic.
- Correct products always pass; incorrect products pass a trial with probability at most one half.
- Independent trials that all accept multiply false-positive bounds.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Randomised complexity — Arora lecture notes](https://users.cs.duke.edu/~reif/courses/complectures/Arora/lec6.pdf)
