---
id: pipe-power-wall-serial-fraction
sourceLesson: pipe-power-wall
title: Calculate Amdahl speedup
level: advanced
minutes: 4
summary: Keep the serial part of a fixed job when dividing its parallel time across equal cores.
---

Multicore can improve throughput for independent jobs. For one fixed-size job, the serial fraction changes the answer: even perfectly balanced parallel work leaves serial work behind. Assume equal core speeds, unchanged time for the one-core component and zero added parallel overhead for every calculation in this unit.

## Amdahl's law

The catch is that most programs are not perfectly parallel. Split a fixed-size job's single-core run time into a serial part, which still runs on one core, and a parallel part, which divides evenly over the cores. Assume unchanged serial time and no communication, scheduling, contention or other parallel overhead:

```formula
S(n) = 1 / ((1 − p) + p / n)
S_max = 1 / (1 − p)   as n → ∞
where
S(n): the speedup on n cores: the original run time divided by the new run time
n: the number of equally fast cores, at least 1
p: the parallel fraction: the share of the original single-core run time that scales perfectly over the cores, between 0 and 1
1 − p: the serial fraction, which no number of cores shortens
S_max: the ceiling the speedup approaches as cores are added, for p below 1
→: approaches, tends towards
∞: infinity: the number of cores growing without limit
In words: the new run time is the serial part plus the parallel part divided among the cores, and however many cores you add, the serial part is still left.
```

For example, with 90% parallel code on 8 cores:

```formula
S(8) = 1 / ((1 − 0.9) + 0.9 / 8)
S(8) = 1 / (0.1 + 0.1125) ≈ 4.71
S_max = 1 / (1 − 0.9) = 10
where
S(8): the speedup on 8 cores
S_max: the ceiling on speedup however many cores are added
≈: approximately equal to (rounded)
In words: the serial 10% plus one-eighth of the parallel 90% is 21.25% of the original time, a speedup of about 4.7; even infinitely many cores leave the 10%, capping the speedup at 10.
```

The same calculation in Python, for several core counts:

```python
def amdahl(p, n):
    if (not 0 <= p <= 1
            or type(n) is not int or n < 1):
        raise ValueError("bad p/n")
    # Divide only the parallel time.
    return 1 / ((1 - p) + p / n)

# Output: core count, then ideal speedup.
for n in (2, 4, 8, 64, 10**9):
    print(n, round(amdahl(0.9, n), 2))
# 2 1.82
# 4 3.08
# 8 4.71
# 64 8.77
# 1000000000 10.0
```

Even with 90% parallel code, 8 cores give only 4.7×, and no number of cores gets past 10×. The serial 10% dominates. This shows why serial performance still matters for this workload. Other workloads can justify many smaller cores; the model does not prescribe one chip organisation. (Gustafson's law gives a more hopeful view when the problem size grows with the machine; that is covered in the parallel hardware module.)

## Key takeaways
- The parallel fraction measures original single-core execution time, not lines of code.
- More equal cores divide only the parallel component in this ideal fixed-work model.
- A nonzero serial fraction sets a finite ceiling; parallel overhead can lower realised gains.

## Further reading
- [MIT: fixed-work parallel speedup](https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/pages/c21/c21s1/)
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)
- [Esmaeilzadeh et al.: dark silicon (original 2011 paper)](https://www.cs.cmu.edu/~18742/papers/Esmaeilzadeh2011.pdf)
