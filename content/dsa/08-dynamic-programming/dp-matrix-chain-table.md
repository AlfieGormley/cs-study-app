---
id: dp-matrix-chain-table
title: Build the matrix-chain cost table
level: advanced
minutes: 4
summary: The final multiplication defines two independent subchains.
sourceLesson: dp-interval-tree
---

The previous unit counted the scalar multiplications for a particular bracketing. Now minimise that count across every bracketing without enumerating them all.

Represent the chain by a dimension list `p`: each matrix’s row count is its entry in the list, and its column count is the following entry. Neighbouring matrices therefore share their inner dimension.

**State**: `C[i][j]` records minimum cost to multiply matrices i through j.

**Recurrence**: the **last** multiplication splits the chain into `(i..k)` and `(k+1..j)`. The left product’s rows come from the first matrix and its columns from the split. The right product shares that inner dimension and ends with the final matrix’s column count. The final cost is their three dimensions multiplied together:

```formula
C[i][j] = min(C[i][k] + C[k + 1][j]
  + p_i p_{k+1} p_{j+1})   for i ≤ k < j
C[i][i] = 0
where
C[i][j]: the fewest scalar multiplications needed to multiply matrices i to j (counting from 0)
i, j: the first and last matrix in the sub-chain
k: the split point: the last multiplication joins product i..k with product k+1..j
p_i: the number of rows of matrix i (p[i] in the code); matrix i is p_i × p_{i+1}
p_{k+1}: the columns of matrix k, which equal the rows of matrix k + 1
p_{j+1}: the number of columns of matrix j
min: the smallest value over every split point k
In words: try every place for the last multiplication, add the best costs of the two halves to the cost of that final multiply, and keep the cheapest.
```

A single matrix needs no multiplications. For the dimensions `[10, 30, 5, 60]`, try the two final splits:

```formula
C[0][2] = min(27,000, 4,500) = 4,500
where
C[i][j]: the minimum scalar multiplication count for matrices i through j
i, j: zero-based first and last matrix positions
min: the smallest candidate cost
In words: The split after the second matrix produces the cheaper final multiplication.
```

```python
def matrix_chain(p):
    p = tuple(p)
    if not p or any(type(x) is not int
                    or x <= 0 for x in p):
        raise ValueError("positive dims")
    n = len(p) - 1
    # An empty chain needs no products.
    if n == 0:
        return 0
    C = [[0] * n for _ in range(n)]
    # Shorter subchains are complete first.
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            # Try every position of the
            # final split.
            C[i][j] = min(
                C[i][k] + C[k+1][j]
                + p[i] * p[k+1] * p[j+1]
                for k in range(i, j))
    return C[0][n - 1]
```

`matrix_chain([10, 30, 5, 60])` returns 4,500. For `[40, 20, 30, 10, 30]` (four matrices) it returns 26,000, via `((A(BC))D)`. Store the best k in a parallel `split` table to print the bracketing recursively.

The table fills diagonal by diagonal:

```
         j=0   j=1   j=2
 i=0      0   1500  4500
 i=1            0   9000
 i=2                  0
```

> [!note] Where this matters
> Numerical libraries face this directly: `numpy.linalg.multi_dot` chooses the multiplication order for a chain of arrays using this DP, and `numpy.einsum` with `optimize=True` uses its greedy contraction-order search, which need not find the global optimum. Database query optimisers solve a harder cousin when ordering joins.

## Key takeaways
- The final multiplication defines two independent subchains.
- Keep the cheapest split and optionally store it for reconstruction.
- A single matrix has zero multiplication cost.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Matrix chain multiplication](https://en.wikipedia.org/wiki/Matrix_chain_multiplication)
- [NumPy multi_dot](https://numpy.org/doc/stable/reference/generated/numpy.linalg.multi_dot.html)
- [NumPy einsum](https://numpy.org/doc/stable/reference/generated/numpy.einsum.html)
