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

With independent promotions, search crosses only an expected constant number of links per level, over logarithmically many levels. Search, insertion and deletion therefore have expected O(log n) cost for n keys when the level capacity is sufficient.

Lower promotion probability makes tall towers rarer and reduces pointer memory. It also changes search constants: fewer levels are offset by more horizontal work at each level. It does not guarantee a faster search.

For an uncapped list, expected forward-pointer memory is useful sizing reference:

```formula reference
N_ptr = n / (1 − p)
where
N_ptr: expected forward pointers across all key nodes, excluding the head
n: number of keys
p: independent promotion probability, strictly between zero and one
In words: less frequent promotion uses fewer pointers per key; with fair coins the average is two forward links per key, while quarter-probability promotion averages four thirds.
```

The teaching code caps each tower at 32 levels. A cap bounds allocation, but if the input keeps growing indefinitely, the top level eventually becomes crowded and searching it becomes expensive. An asymptotic logarithmic guarantee for unbounded input needs a cap that grows with the logarithm of the key count. Choose a fixed cap for an intended capacity, not as a universal guarantee.

### Where skip lists are used

- **Redis sorted sets** (Redis 8.2 implementation) (`ZADD`, `ZRANGE`, leaderboards) pair a hash table with a skip list, using a promotion probability of 1/4 and a cap of 32 levels. Each forward pointer also stores a **skip-list span**, so rank queries (`ZRANK`) are O(log n) too, where n is the number of members in the set. Small sorted sets use a compact listpack instead.
- **LevelDB** uses a skip-list memtable. **RocksDB** uses a skip list by default and also offers other memtable representations.
- **Java's `ConcurrentSkipListMap`** is a sorted concurrent map. Its Java SE 21 API documents safe concurrent access and expected average logarithmic lookup and updates. That public contract does not promise lock-free progress; the teaching skip-list implementation is not a concurrent implementation.

## Key takeaways

- Promotion probability trades pointer memory against search constants.
- A fixed level cap is a practical capacity choice, not an unbounded logarithmic guarantee.

## Further reading
- [Skip Lists — William Pugh](https://drum.lib.umd.edu/bitstreams/17176ef8-8330-4a6c-8b75-4cd18c570bec/download)
- [Redis 8.2 skip-list constants](https://raw.githubusercontent.com/redis/redis/8.2/src/server.h)
- [Java ConcurrentSkipListMap contract](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentSkipListMap.html)
