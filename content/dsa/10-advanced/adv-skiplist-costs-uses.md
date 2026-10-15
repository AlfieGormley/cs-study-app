---
id: adv-skiplist-costs-uses
title: Skip-list pointer costs, caps and uses
level: advanced
minutes: 4
summary: Promotion probability trades pointer memory against search constants.
sourceLesson: adv-randomised-structures
---

Here n is the number of keys or stream items, and k is the requested sample size when sampling. Random draws are assumed independent and uniform under the stated model.

### Cost

Read the search path backwards: from the found node, each step either goes up (if that node was promoted, which happens with the promotion probability) or left. Pugh's analysis turns that into an expected step count:

```formula
C ≈ (1 / p) × log_{1/p}(n)
C ≈ 2 × log_2(1,000,000) ≈ 2 × 20 = 40
C ≈ 4 × log_4(1,000,000) ≈ 4 × 10 = 40
where
C: the expected number of pointer steps in one search
p: the promotion probability, strictly between zero and one (1/2 in the second line, 1/4 in the third)
1 / p: the expected number of steps spent on each level before the path climbs
n: the number of keys, a million here
log_{1/p}(n): the logarithm of n to base 1/p, about the number of levels
log_2, log_4: logarithms to base 2 and base 4
≈: approximately equal to
In words: about 1/p steps per level times about log_{1/p}(n) levels, so search, insert and delete are expected O(log n).
```

O(log n) means the cost grows in proportion to the logarithm of n. Lower p means fewer, longer hops per level but fewer levels, so at a million keys both settings take about 40 steps. Pugh's full formula adds a small constant; the estimate ignores it.

The memory cost is the number of forward pointers, one per level each node occupies (not counting the head):

```formula
N_ptr = n / (1 − p)
N_ptr = n / (1 − 1/2) = 2n
N_ptr = n / (1 − 1/4) ≈ 1.33 × n
N_cap = n(1 − p^L) / (1 − p)
where
N_ptr: the expected total number of forward pointers when levels are not capped
N_cap: the expected total when no node may exceed L levels
n: the number of keys
p: the promotion probability, strictly between zero and one
L: the level cap (32 in the code above)
p^L: L copies of p multiplied together
≈: approximately equal to
In words: each key holds on average 1/(1 − p) pointers, so 2 per key at p = 1/2 and about 1.33 per key at p = 1/4; a cap trims a tiny amount off that.
```

A million keys therefore cost about 2 million pointers with fair coins and about 1.33 million with a promotion probability of 1/4. Lower p saves pointers; search constants and variance also depend on the workload and implementation.

The code caps levels at 32 for a bounded practical capacity. The number of nodes expected to reach the cap shows when that stops being enough:

```formula
N_top = np^{L − 1}
N_top = n(1/4)^31 ≈ n / (4.6 × 10^18)
where
N_top: the expected number of nodes that would want to reach the top (capped) level
n: the number of keys
p: the promotion probability, strictly between zero and one; 1/4 in the second line
L: the level cap, 32 in the second line
p^{L − 1}: L − 1 copies of p multiplied together
≈: approximately equal to
In words: with 32 levels at p = 1/4, you would need billions of billions of keys before the top level gets crowded.
```

Well below that scale the capped top level has a small expected population. This is a probabilistic practical estimate, not a guarantee that the cap never affects a particular run. An asymptotic O(log n) guarantee for unbounded n requires a cap that grows with log n; a fixed cap eventually leaves too many nodes on its top level.

### Where skip lists are used

- **Redis sorted sets** (Redis 8.2 implementation) (`ZADD`, `ZRANGE`, leaderboards) pair a hash table with a skip list, using a promotion probability of 1/4 and a cap of 32 levels. Each forward pointer also stores a **skip-list span**, so rank queries (`ZRANK`) are O(log n) too, where n is the number of members in the set. Small sorted sets use a compact listpack instead.
- **LevelDB** uses a skip-list memtable. **RocksDB** uses a skip list by default and also offers other memtable representations.
- **Java's `ConcurrentSkipListMap`** is a sorted concurrent map. Its Java SE 21 API documents safe concurrent access and expected average logarithmic lookup and updates. That public contract does not promise lock-free progress; the hand-written example above is not a concurrent implementation.

## Key takeaways

- Promotion probability trades pointer memory against search constants.
- A fixed level cap is a practical capacity choice, not an unbounded logarithmic guarantee.

## Further reading
- [Skip list — Wikipedia](https://en.wikipedia.org/wiki/Skip_list)
- [Treap — Wikipedia](https://en.wikipedia.org/wiki/Treap)
- [Treap (Cartesian tree) — cp-algorithms](https://cp-algorithms.com/data_structures/treap.html)
- [Reservoir sampling — Wikipedia](https://en.wikipedia.org/wiki/Reservoir_sampling)
- [Fisher–Yates shuffle — Wikipedia](https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle)
