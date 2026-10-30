---
id: hash-table-cost-model
title: Hash-table average and worst cases
level: basic
minutes: 4
sourceLesson: hash-maps-sets
summary: Average O(1) depends on the load factor and an even hash spread; colliding keys make lookups linear and bulk inserts quadratic.
---

A hash table's "O(1)" is a conditional promise, not a latency guarantee. Keep three costs apart: hashing and comparing a key, the collision work inside the table, and the occasional resize.

## Average case versus worst case

The O(1) figure is an **average**, and it rests on an assumption: the hash function spreads keys roughly evenly across buckets.

How full a table is matters more than how big it is. The **load factor** measures that fullness: the average number of keys per bucket.

```formula essential
α = n / m
where
α: alpha, the load factor: the average number of keys per bucket, a plain number with no unit (0.75 means three keys for every four buckets)
n: the number of keys currently stored in the table
m: the number of buckets (slots) in the table's array
In words: the load factor is keys divided by buckets. Twelve keys in sixteen buckets is 0.75: the table is three-quarters full, whatever its absolute size.
```

Tables keep α below a fixed limit (Java's `HashMap` uses 0.75, Python's dict about 2/3) by growing the array when it fills up. With α held below a constant, the expected work per operation is constant, whether the table holds ten keys or ten million. This relies on the hash function spreading keys evenly; it says nothing about a bad hash or a deliberate attack.

The **worst case** is very different. If every key hashes to the same bucket, a list-chained table degenerates into one long chain; an unsuccessful lookup or a hit at the end may scan all n keys:

```
 0     1     2              3
[ ]  [ ]   [k1->k2->...->kn] [ ]
```

That makes a lookup O(n). Inserting n keys is worse, because each new key is first compared with every key already in the chain (to check it is not a duplicate). The first key is compared with nothing, the second with one key, the third with two, and so on.

```formula reference
C = n (n − 1) / 2
where
C: the total number of key comparisons needed to insert n distinct keys into one shared chain
n: the number of keys inserted
In words: the comparisons add up to roughly half of n squared, so doubling the number of colliding keys roughly quadruples the total work. That growth is written O(n²).
```

For 1,000 colliding keys that is about half a million comparisons, where a good hash needs about 1,000 steps. This happens in practice when:

- the hash function is poor for your data (for example, hashing integers that are all multiples of the table size), or
- an attacker deliberately sends keys that collide, a **hash flooding** attack (Hash flooding and runtime randomisation).

There is also an occasional slow insert: when the table grows, every key is re-inserted into a bigger array, which costs O(n). Spread over all the inserts this averages out to O(1) per insert, which is called **amortised** O(1) (Rehashing and geometric growth).

> [!note] What "O(1) average" really means
> It is the expected cost under a reasonable hash function, ignoring the occasional resize. Hashing the key itself is not free: computing an uncached hash of a string of L characters ordinarily scans all L of them, so it costs O(L). CPython caches string hashes, and identity shortcuts can avoid equality scans; a repeated lookup using the same long string need not rescan it.

## Key takeaways
- Load factor measures keys per bucket rather than total table size.
- Colliding chains can make each operation linear and a sequence of inserts quadratic.
- Hash computation, equality and resizing are separate parts of the cost model.

## Further reading
- [Hash table — Wikipedia](https://en.wikipedia.org/wiki/Hash_table)
- [Time complexity of Python operations — Python wiki](https://wiki.python.org/moin/TimeComplexity)
