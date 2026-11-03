---
id: dp-matrix-chain-costs
title: Why matrix multiplication order matters
level: advanced
minutes: 2
summary: Exact matrix multiplication is associative, but evaluation costs differ.
sourceLesson: dp-interval-tree
---

## Matrix chain multiplication

With the classical dense algorithm, multiplying a matrix with 10 rows and 30 columns by one with 30 rows and 5 columns takes 10 × 30 × 5 = 1,500 scalar multiplications (multiplications of single numbers): the result has 10 × 5 entries, and each is a sum of 30 products. In general the cost is the three dimensions multiplied together: rows of the first, the shared inner dimension, and columns of the second.

```formula reference
cost = pqr
where
cost: the number of scalar multiplications
p: the number of rows of the first matrix
q: the number of columns of the first matrix, which must equal the number of rows of the second
r: the number of columns of the second matrix
In words: the cost is the first matrix's row count × the shared inner dimension × the second matrix's column count, because the result has one entry per row–column pair and each entry is a sum of one product per position along the shared dimension.
```

Matrix multiplication is associative in exact arithmetic, so for a chain A·B·C you can choose the bracketing, and the costs can differ wildly.

With A: 10 × 30, B: 30 × 5, C: 5 × 60:

- **(AB)C**: AB costs 1,500 and leaves a small 10 × 5 matrix; multiplying that by C costs 3,000. Total 4,500.
- **A(BC)**: BC costs 9,000 and leaves a bigger 30 × 60 matrix; multiplying A by it costs 18,000. Total 27,000.

Same answer, six times as many scalar multiplications in this cost model, just from the brackets. The difference comes from the sizes of the intermediate results: a bracketing that creates a large intermediate matrix pays for it twice, once to build it and again to use it. "Associative" means the result doesn't depend on the brackets; it says nothing about the cost. The number of possible bracketings of a chain of n matrices is the (n − 1)th Catalan number, which grows exponentially (about 4ⁿ, divided by a polynomial in n): 1, 1, 2, 5, 14, 42, ... for chain lengths one, two, three and onwards, and 1,430 already for 9 matrices. So trying them all is out.

## Key takeaways
- Exact matrix multiplication is associative, but evaluation costs differ.
- The classical dense model counts multiplications of individual numbers.
- Choose brackets without changing the exact result.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Matrix chain multiplication](https://en.wikipedia.org/wiki/Matrix_chain_multiplication)
