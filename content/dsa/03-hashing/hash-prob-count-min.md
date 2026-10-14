---
id: hash-prob-count-min
title: Count-Min counters and stream-relative error
level: advanced
minutes: 5
sourceLesson: hash-probabilistic
summary: Count-Min estimates frequency rather than membership.
---

Count-Min estimates frequency rather than membership. Its guarantee is an additive error relative to the total update weight, not a percentage of each item’s own count.

## Count-Min Sketch

A **Count-Min Sketch** (Cormode and Muthukrishnan, 2005) estimates how often each item appears in a stream. It is a grid of d rows by w counters, with one hash function per row.

- **Add x**: in each row, increment the counter that row's hash function picks for x.
- **Query x**: return the **minimum** of x's d counters.

```
w = 8, d = 3 (counts after a stream)

row 0: 0 5 0 2 0 9 0 1
row 1: 3 0 0 7 1 0 0 6
row 2: 0 0 4 0 8 0 2 3

x hashes to row0[5], row1[3], row2[4]
counters: 9, 7, 8  -> estimate 7
```

Every counter x touches includes x's true count plus whatever else collided there. Collisions can only *add*, so every counter is an overestimate (with non-negative updates), and the minimum is the least polluted one.

```python
class CountMin:
    def __init__(self, w, d):
        if type(w) is not int or w <= 0:
            raise ValueError("positive w")
        if type(d) is not int or d <= 0:
            raise ValueError("positive d")
        self.w, self.d = w, d
        self.t = [[0] * w for _ in range(d)]

    def _col(self, item, i):
        return hash((i, item)) % self.w

    def add(self, item, n=1):
        if type(n) is not int or n < 0:
            raise ValueError("negative n")
        for i in range(self.d):
            c = self._col(item, i)
            # Collisions can only add
            # pollution.
            self.t[i][c] += n

    def count(self, item):
        # Choose the least polluted row.
        return min(
            self.t[i][self._col(item, i)]
            for i in range(self.d))
```

This fragment demonstrates the counter/minimum mechanism. Python hash((i, item)) is not an independently sampled universal family, so the formal error bound below is not established for this sample. It still never undercounts under its enforced nonnegative updates, provided keys retain stable hashes.

### Error guarantee

You size a Count-Min Sketch from two numbers: how big an error you accept, as a fraction of the whole stream, and how often you allow that limit to be broken. Assume a stream fixed independently of the hash choices, independent rows using suitable universal hashes (Hash flooding and runtime randomisation), nonnegative updates and counters that never overflow. Then choose:

```formula
w = ⌈e / ε⌉
d = ⌈ln(1 / δ)⌉
w = ⌈e / 0.001⌉ = 2719
d = ⌈ln(100)⌉ = ⌈4.61⌉ = 5
where
w: the width, the number of counters in each row
d: the depth, the number of rows (and of hash functions)
ε: epsilon, the allowed error as a fraction of the stream total, here 0.001 (0.1%)
δ: delta, the allowed probability of exceeding that error, here 0.01 (1%)
e: Euler's number, about 2.718
ln: the natural logarithm (base e); ln(100) ≈ 4.61
⌈ ⌉: ceiling, round up to the next whole number
In words: the width sets how big the error can be and the depth sets how rarely it is exceeded; for 0.1% error with 99% confidence you need 5 rows of 2,719 counters, about 13,600 counters in all.
```

With those sizes, the guarantee for any single item, fixed before the hash functions are chosen, is:

```formula
c_est ≤ c_true + ε N
c_est ≤ c_true + 0.001 × 100,000,000
c_est ≤ c_true + 100,000
where
c_est: the count the sketch reports for the item
c_true: the item's real count in the stream
ε: epsilon, the error fraction the sketch was sized for, here 0.001
N: the total of all counts in the stream, here 100 million events
δ: the allowed probability that the upper error bound fails, here 0.01
≤: "is at most"; the bound holds with probability at least 1 − δ (here 99%)
In words: the estimate never undercounts, and with 99% probability it overcounts by at most 0.1% of the whole stream: 100,000 for a 100-million-event stream, however many distinct items there are.
```

This is not a simultaneous guarantee for all items at once, nor for queries chosen after seeing the hash functions.

That error is relative to the *total* N, not to the item's own count, so the sketch is accurate for **heavy hitters** (frequent items) and nearly useless for rare ones: an item seen 10 times may be reported as tens of thousands. Tracking top items also requires a candidate-tracking algorithm, since the sketch cannot enumerate keys; a heap can form part of that design.

Count-Min Sketches appear in network monitoring (top talkers by IP), trending-topic detection, and caches: the Caffeine library's W-TinyLFU policy keeps approximate access frequencies in a Count-Min-style sketch of 4-bit counters to decide which items deserve a place in the cache.

## Key takeaways
- Query the minimum counter to reduce collision overcount.
- Nonnegative updates and no overflow prevent undercounting.
- The formal upper error bound needs suitable independent universal rows and concerns one fixed query.

## Further reading
- [Count–min sketch — Wikipedia](https://en.wikipedia.org/wiki/Count%E2%80%93min_sketch)
- [Count-Min Sketch original paper](https://people.cs.umass.edu/~mcgregor/711S18/countmin.pdf)
