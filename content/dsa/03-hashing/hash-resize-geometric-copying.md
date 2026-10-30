---
id: hash-resize-geometric-copying
title: Rehashing and geometric growth
level: intermediate
minutes: 4
sourceLesson: hash-resizing
summary: Growing a table re-places every entry because bucket choice depends on size, yet geometric growth keeps the copying to a constant per insert on average.
---

When a table passes its maximum load factor it allocates a bigger array. This lesson covers what moving into that array costs, and why the cost still averages out to a constant per insert.

## Rehashing: why every key moves

You cannot copy the old array across as it is, because a key's bucket depends on the table size: the bucket is the full hash's remainder after dividing by the number of buckets. The full hash never changes, but the divisor does. A key with hash 14 lives in bucket 2 of a 4-bucket table but bucket 6 of an 8-bucket table.

```
old m = 4         new m = 8
hash  idx         hash  idx
  5    1            5    5
  9    1            9    1
 14    2           14    6
```

Doubling the table moves about half the keys under uniform hashing, but the table cannot know which half without looking. Growing therefore means **rehashing**: walking every entry and inserting it into the new array.

Visiting and copying the entries costs O(n) for n entries; placing them by ordinary probing is expected O(n) with well-distributed hashes, and collision-heavy reinsertion can cost more. An implementation can store each entry's full hash so it does not recompute it (which matters for long strings), but every entry must still be visited and placed.

## Amortised analysis: why inserts are still O(1)

One O(n) insert sounds bad. The trick is that, if the table grows by a constant **factor**, expensive inserts become rarer as the table grows.

Picture a table that starts with one slot and doubles when full. The resizes copy 1 key, then 2, then 4, 8, and so on. Each resize copies more than all the earlier ones put together, so the last resize does about half of all the copying ever done. Inserting 1,024 keys this way causes only 1,023 copies in total: about one per insert.

```formula reference
C < 2n
T = C + n < 3n
where
C: the total number of key copies made by all the resizes together
T: the combined copying and placement work, in unit operations
n: the positive number of keys inserted; each initial placement costs one unit in this model
<: is strictly less than
In words: geometric growth copies fewer than two keys per insert overall, so copying plus placing costs fewer than three units per insert on average, for any number of inserts.
```

Thus **resizing overhead** is amortised O(1) per insert, for every sequence of inserts, not just on average over random inputs. The overall cost of a hash-table insert also includes collision work, so the usual statement is *expected* amortised O(1), assuming well-distributed hashes and constant-time key operations. The same doubling argument applies to dynamic arrays (Arrays, Lists, Stacks & Queues).

## Key takeaways
- Changing capacity changes bucket reduction and requires visiting all entries.
- Geometric growth keeps total copying proportional to the insertion count.
- Amortised copying bounds do not prove bounded individual latency or collision cost.

## Further reading
- [Hash table: dynamic resizing — Wikipedia](https://en.wikipedia.org/wiki/Hash_table#Dynamic_resizing)
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
