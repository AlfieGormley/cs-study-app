---
id: hash-prob-count-min
title: Count-Min counters and stream-relative error
level: advanced
minutes: 5
sourceLesson: hash-probabilistic
summary: A Count-Min Sketch estimates how often an item appears, never undercounting, with an error measured against the whole stream rather than the item.
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

> [!analogy] Real-world analogy: several shared tally sheets
> A survey team keeps three tally sheets with only a few columns each, and every answer gets a mark in one column on each sheet, chosen by a different rule per sheet. Unrelated answers share columns, so every column over-counts. To estimate one answer, read its column on each sheet and trust the smallest.
>
> **How it maps:** the sheets are the sketch's rows, the columns are counters, each sheet's rule is that row's hash function, and taking the smallest reading is the minimum query.
>
> **Where it stops:** a tally sheet could list which answers share a column; a sketch keeps only the numbers, so it cannot name its frequent items. And the error bound comes from the rows' hash functions behaving independently, which tally-sheet rules need not.

### Error guarantee

You size a Count-Min Sketch from two choices: how big an error you accept, as a fraction of the *whole stream's* total, and how often you allow that limit to be broken. Wider rows make collisions in each row rarer, so the error is smaller; more rows make it less likely that *every* row is badly polluted at once. The guarantee assumes a stream fixed independently of the hash choices, independent rows using suitable universal hashes (Universal hashing and adversary assumptions), nonnegative updates and counters that never overflow. With high probability the estimate is then at most the true count plus the chosen error fraction of the whole stream total:

```formula reference
c_est ≤ c_true + εN
where
c_est: the count the sketch reports for the item
c_true: the item's real count in the stream (the sketch never reports less than this)
ε: epsilon, the allowed error as a fraction of the stream total, chosen when sizing the sketch
N: the total of all counts in the stream
≤: "is at most"; this upper bound holds with probability at least 1 − δ, where δ (delta) is the allowed failure probability chosen when sizing
In words: the estimate never undercounts, and with high probability it overcounts by at most a fixed fraction of the *whole stream*, however many distinct items there are. With an error fraction of 0.1% and a 100-million-event stream, that is at most 100,000 too high.
```

```formula reference
w = ⌈e / ε⌉
d = ⌈ln(1 / δ)⌉
where
w: the width, the number of counters in each row
d: the depth, the number of rows (and of hash functions)
ε: epsilon, the allowed error as a fraction of the stream total
δ: delta, the allowed probability of exceeding that error
e: Euler's number, about 2.718
ln: the natural logarithm (base e)
⌈ ⌉: ceiling, round up to the next whole number
In words: the width grows in proportion to how small an error you want, while the depth grows only with the logarithm of how rarely you allow failure. For 0.1% error with 99% confidence: 5 rows of 2,719 counters, about 13,600 counters in all.
```

The guarantee is for one item fixed before the hash functions are chosen. It is not a simultaneous guarantee for all items at once, nor for queries chosen after seeing the hash functions.

Because the error is relative to the stream total, not to the item's own count, the sketch is accurate for **heavy hitters** (frequent items) and nearly useless for rare ones: an item seen 10 times may be reported as tens of thousands. Tracking the top items also needs a separate way to remember candidate keys, since the sketch cannot list them; a heap can form part of that design.

Count-Min Sketches appear in network monitoring (top talkers by IP), trending-topic detection, and caches: the Caffeine library's W-TinyLFU policy keeps approximate access frequencies in a Count-Min-style sketch of 4-bit counters to decide which items deserve a place in the cache.

## Key takeaways
- Query the minimum counter to reduce collision overcount.
- Nonnegative updates and no overflow prevent undercounting.
- The formal upper error bound needs suitable independent universal rows and concerns one fixed query.

## Further reading
- [Count–min sketch — Wikipedia](https://en.wikipedia.org/wiki/Count%E2%80%93min_sketch)
- [Count-Min Sketch original paper](https://people.cs.umass.edu/~mcgregor/711S18/countmin.pdf)
