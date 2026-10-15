---
id: par-roofline-traffic
title: Counting streaming and matrix traffic
level: advanced
minutes: 3
sourceLesson: par-measuring
summary: Count read-for-ownership and eventual writeback when the streaming model requires them.
---

### Worked example

Take the same machine: a 1,000 GFLOP/s peak and 100 GB/s of bandwidth, so the ridge is at 10 FLOP/byte. Consider three compute kernels on 8-byte doubles:

Use a cold streaming model with disjoint arrays, 8-byte doubles, write-back caches with write-allocate, full-line utilisation and eventual dirty-line writeback. Exclude non-temporal stores and traffic-elimination optimisations unless stated.

- **Vector add** `c[i] = a[i] + b[i]`: one FLOP per element. It reads 16 input bytes, plus 8 bytes of output read-for-ownership (the cache fetches the output line before writing it) and 8 bytes of eventual output writeback: 32 bytes per element.
- **DAXPY** (double-precision a times x plus y) `y[i] = a * x[i] + y[i]`: count two FLOPs per multiply-add. Reading x and y plus writing y back moves 24 bytes per element in this model.
- **Matrix multiply** of two square matrices: conventionally count two FLOPs per MAC operation. Idealised traffic is one read each of the two inputs and one write of the output. This deliberately excludes write allocation and assumes enough reuse; it is not achievable for arbitrary sizes with fixed cache capacity.

```formula
AI_add = 1 / 32 ≈ 0.031 FLOP/byte
AI_ax = 2 / 24 ≈ 0.083 FLOP/byte
F_mm = 2 × n^3
D_mm = 3 × 8 × n^2 = 24 × n^2
AI_mm = (2n^3) / (24n^2) = n / 12
where
AI_add: the intensity of vector add: 1 FLOP per 32 bytes
AI_ax: the intensity of DAXPY: 2 FLOPs per 24 bytes
F_mm: the FLOPs in an n × n matrix multiply: n^3 multiply-adds, each counted as two
D_mm: the ideal matrix-multiply traffic in bytes: three n × n matrices of 8-byte doubles, each moved once
AI_mm: the ideal matrix-multiply intensity, in FLOP/byte
n: the matrix size (rows = columns)
FLOP: one floating-point operation
byte: 8 bits
≈: approximately equal to
In words: streaming compute kernels do well under one FLOP per byte, while matrix multiply's ideal intensity grows with the matrix size, about 83 FLOP/byte for 1,000 × 1,000.
```

```python
def attainable(ai, peak, bw):
    """GFLOP/s bound; nonnegative inputs."""
    # Use consistent rate/byte units.
    return min(peak, ai * bw)

PEAK, BW = 1000, 100  # GFLOP/s, GB/s
RIDGE = PEAK / BW     # 10 FLOP/B
kernels = {"vec add": 1 / 32,
           "daxpy": 2 / 24,
           "matmul": 1000 / 12}
# Report a model bound, not a measurement.
for k, ai in kernels.items():
    g = attainable(ai, PEAK, BW)
    kind = ("bw roof" if ai < RIDGE
            else "compute roof")
    print(f"{k:8}{ai:6.2f}{g:7.1f}", kind)
```

```
vec add   0.03    3.1 bw roof
daxpy     0.08    8.3 bw roof
matmul   83.33 1000.0 compute roof
```

The vector-add bound is about 0.3125% of the assumed compute peak under this traffic model. Matrix multiplication’s ideal intensity permits a compute ceiling, but does not guarantee reaching it. A naive loop may repeatedly fetch data if it exceeds cache capacity; small matrices may remain cached. Blocking can improve reuse, although real traffic need not equal the ideal three-matrix estimate.

## Key takeaways
- Count read-for-ownership and eventual writeback when the streaming model requires them.
- Ideal matrix reuse is a traffic model, not a guarantee for arbitrary sizes.

## Further reading
- [The original Roofline paper](https://people.eecs.berkeley.edu/~kubitron/cs252/handouts/papers/RooflineVyNoYellow.pdf)
- [Python timeit measurement contract](https://docs.python.org/3/library/timeit.html)
- [Linux perf stat reference](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-stat.txt)
- [Linux perf record reference](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-record.txt)
- [Flame graphs from their creator](https://www.brendangregg.com/flamegraphs.html)
- [STREAM traffic conventions](https://www.cs.virginia.edu/stream/ref.html)
- [Python Linux perf integration](https://docs.python.org/3/howto/perf_profiling.html)
