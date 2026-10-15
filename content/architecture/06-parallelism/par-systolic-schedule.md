---
id: par-systolic-schedule
title: Following operands through a systolic array
level: advanced
minutes: 3
sourceLesson: par-accelerators
summary: Row and column delays determine which term pair meets at each processing element.
---

### How a systolic array works

The key idea is to reuse data as it moves through a grid of processing elements (PEs), reducing repeated operand movement. An operand read from a local buffer can serve several operations; a large tiled problem may still require repeated DRAM reads. Each PE multiplies, adds, and passes values to its neighbours, like blood pulsed through the body (hence "systolic").

```
       b-col0  b-col1  b-col2
         v       v       v
a-row0> [PE]--> [PE]--> [PE]
         |       |       |
a-row1> [PE]--> [PE]--> [PE]
         |       |       |
a-row2> [PE]--> [PE]--> [PE]
```

In the *output-stationary* variant, each processing element accumulates one output element. Rows enter from the left and columns from the top, with staggered arrival delays. The next card defines the row, column and cycle indices before using them. So the values meeting at a PE on a given cycle are fixed by the cycle number and the two delays:

```formula
k = t − i − j
C[i][j] ← C[i][j] + A[i][k] × B[k][j]
0 ≤ k ≤ n − 1
where
k: the index of the term being multiplied on this cycle
t: the clock cycle, counting from 0
i: the row of the PE, which is also the row of A and of C it handles
j: the column of the PE, which is also the column of B and of C it handles
A: the left input matrix, entering row by row from the left
B: the right input matrix, entering column by column from the top
C: the output matrix, one element accumulating in each PE
n: the matrix size (all three are n × n)
←: "is updated to": the PE adds the new product to its running total
≤: less than or equal to
In words: on cycle t the PE in row i, column j multiplies the k-th term pair, where k is the cycle number minus both delays, and it works only on cycles where k is a real index from 0 to n − 1.
```

The following ideal output-stationary model assumes one MAC operation per active PE per cycle and square matrices. It is an explanatory schedule, not an implementation of TPU v1’s exact datapath. Python integer inputs give exact integer results; floating-point inputs have Python’s rounding semantics:

```python
def systolic(A, B):
    n = len(A)
    if len(B) != n or any(
        len(row) != n
        for M in (A, B) for row in M
    ):
        raise ValueError("invalid shape")
    # Each PE keeps one accumulating output.
    C = [[0] * n for _ in range(n)]
    pes = [(i, j) for i in range(n)
           for j in range(n)]
    for t in range(3 * n - 2):  # cycles
        for i, j in pes:
            # Match staggered input terms.
            k = t - i - j
            # Fill/drain cycles may be idle.
            if 0 <= k < n:
                C[i][j] += A[i][k] * B[k][j]
    return C

print(systolic([[1, 2], [3, 4]],
               [[5, 6], [7, 8]]))
# [[19, 22], [43, 50]]
```

## Key takeaways
- Row and column delays determine which term pair meets at each processing element.
- The executable output-stationary model illustrates a schedule rather than TPU v1’s exact datapath.

## Further reading
- [Jouppi and colleagues: the first TPU](https://arxiv.org/abs/1704.04760)
- [Cloud TPU bfloat16 conversion](https://docs.cloud.google.com/tpu/docs/bfloat16)
- [AMD configurable logic blocks](https://docs.amd.com/r/en-US/ug474_7Series_CLB/CLB-Overview)
- [AMD high-level synthesis](https://docs.amd.com/r/en-US/ug1399-vitis-hls/Introduction)
- [AMD MicroBlaze soft processor](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/microblaze.html)
