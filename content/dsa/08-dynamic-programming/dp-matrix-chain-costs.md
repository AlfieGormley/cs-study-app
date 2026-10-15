---
id: dp-matrix-chain-costs
title: Why matrix multiplication order matters
level: advanced
minutes: 2
summary: Exact matrix multiplication is associative, but evaluation costs differ.
sourceLesson: dp-interval-tree
---

## Matrix chain multiplication

With the classical dense algorithm, multiplying a matrix with p rows and q columns by one with q rows and r columns has the following scalar-multiplication count (multiplications of single numbers):

```formula
cost = pqr
cost = 10 × 30 × 5 = 1,500
where
cost: the number of scalar multiplications
p: the number of rows of the first matrix
q: the number of columns of the first matrix, which must equal the number of rows of the second
r: the number of columns of the second matrix
In words: the result has p × r entries and each one is a sum of q products.
```

Matrix multiplication is associative in exact arithmetic, so for a chain A·B·C you can choose the bracketing, and the costs can differ wildly.

With A: 10 × 30, B: 30 × 5, C: 5 × 60:

For the two bracketings:

```formula
C_left = 10 × 30 × 5 + 10 × 5 × 60
C_left = 1,500 + 3,000 = 4,500
C_right = 30 × 5 × 60 + 10 × 30 × 60
C_right = 9,000 + 18,000 = 27,000
where
C_left: scalar multiplications when A and B are multiplied first
C_right: scalar multiplications when B and C are multiplied first
In words: Multiplying the small inner dimensions first cuts this classical multiplication count by a factor of six.
```

Six times as many scalar multiplications in this cost model, just from the brackets. The number of possible bracketings of a chain of n matrices is the (n − 1)th Catalan number, which grows exponentially (about 4ⁿ, divided by a polynomial in n): 1, 1, 2, 5, 14, 42, ... for chain lengths one, two, three and onwards, and 1,430 already for 9 matrices. So trying them all is out.

## Key takeaways
- Exact matrix multiplication is associative, but evaluation costs differ.
- The classical dense model counts multiplications of individual numbers.
- Choose brackets without changing the exact result.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Matrix chain multiplication](https://en.wikipedia.org/wiki/Matrix_chain_multiplication)
