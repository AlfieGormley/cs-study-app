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

```formula essential
A × (B × r) = C × r
where
A, B: the two n × n input matrices
C: the claimed product of A and B, an n × n matrix
r: a random column vector of n independently sampled entries, each uniformly 0 or 1
B × r: a matrix–vector product: n^2 multiplications, giving a vector of n numbers
n: the number of rows and columns of each square matrix
In words: multiply the random vector by the second matrix, then the first, and compare with multiplying it by the claimed product. Correct products agree for every vector; each trial needs only three matrix–vector products.
```

Each trial uses quadratically many arithmetic operations in the matrix side length, instead of the cubic work of naive full multiplication.

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

For any incorrect product, choose a nonzero row of the difference from the true product and a nonzero coefficient in that row. Hold all other random-vector entries fixed. At most one of the two choices for this coefficient’s entry can make the row’s dot product zero. Thus at least half the vectors detect an error, without needing an empirical benchmark.

These are arithmetic-operation counts, not a claim that unbounded integer multiplication costs one bit operation. Intermediate integer lengths and input encoding matter for bit complexity. Floating-point rounding can also invalidate the exact one-sided guarantee. Python’s random module illustrates ideal independent draws in the mathematical model; a finite pseudorandom generator is not itself a proof of independent randomness.

## Key takeaways

- Freivalds compares three matrix–vector products using exact arithmetic.
- Correct products always pass; incorrect products pass a trial with probability at most one half.
- Independent trials that all accept multiply false-positive bounds.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Randomised complexity — Arora lecture notes](https://users.cs.duke.edu/~reif/courses/complectures/Arora/lec6.pdf)
