---
id: hash-resize-geometric-copying
title: Rehashing and geometric growth
level: intermediate
minutes: 4
sourceLesson: hash-resizing
summary: Resizing changes bucket selection, so it visits all entries even if their full hashes are cached.
---

Resizing changes bucket selection, so it visits all entries even if their full hashes are cached. We count this copying work separately from collisions and allocation costs.

## Rehashing: why every key moves

When the table grows, you cannot copy the old array across as it is, because a key's bucket depends on the table size:

```formula
b = H mod m
b = 14 mod 4 = 2     (m = 4)
b = 14 mod 8 = 6     (m = 8)
where
b: the bucket index the key is stored in, from 0 to m − 1
H: the key's full hash value, which never changes; here 14
m: the number of buckets, 4 before growing and 8 after
mod: "modulo", the remainder after whole-number division
In words: the bucket is the hash's remainder after dividing by the table size, so changing the size moves the key; hash 14 lives in bucket 2 of 4 but bucket 6 of 8.
```

Doubling the table moves about half the keys under uniform hashing. Growing therefore means **rehashing**: walking every entry and inserting it into the new array.

```
old m = 4         new m = 8
hash  idx         hash  idx
  5    1            5    5
  9    1            9    1
 14    2           14    6
```

Visiting/copying entries costs O(n); placing them by ordinary probing assumes well-distributed hashes for expected O(n), and collision-heavy reinsertion can cost more. An implementation can retain the full hash in the entry or key object so it does not have to recompute it (which matters for long strings), but every entry still has to be visited and placed.



## Amortised analysis: why inserts are still O(1)

One O(n) insert sounds bad. The trick is that, if the table grows by a constant **factor**, expensive inserts become rarer as the table grows.

Count the copying work for n inserts into a table that starts with one slot and doubles when full. Each resize copies every key present. First assume n is a power of two:

```formula
C = 1 + 2 + 4 + … + n / 2
C = n − 1 < n
C = 1 + 2 + 4 + … + 512 = 1023
where
C: the total number of key copies made by all the resizes together
n: the number of keys inserted, a power of two; here 1,024
…: "and so on", each term double the one before
<: "is less than"
In words: the resizes copy 1, then 2, then 4 keys and so on, and this doubling series always adds up to one less than n; inserting 1,024 keys causes only 1,023 copies in total, about one per insert.
```

The sum works because each term is bigger than all the earlier terms put together: the last resize does about half the total work. For powers of two the preceding exact sum applies. For an arbitrary positive insertion count, the last copied capacity may exceed half that count, but the following bounds still hold:

```formula
C < 2n
T = C + n < 3n
where
C: total entries copied while growing, in copy operations
T: combined copying and placement work, in unit operations
n: positive number of inserted entries; each placement costs one unit in this model
<: strictly less than
In words: Geometric growth copies fewer than twice the inserted entries; adding their initial placements still uses fewer than three units per insert on average.
```
 Thus **resizing overhead** is amortised O(1) per insert for every sequence. Overall hash-table insertion also depends on collision costs: the usual bound is expected amortised O(1), assuming well-distributed hashes and constant-time key operations.

## Key takeaways
- Changing capacity changes bucket reduction and requires visiting all entries.
- Geometric growth keeps total copying proportional to the insertion count.
- Amortised copying bounds do not prove bounded individual latency or collision cost.

## Further reading
- [Hash table: dynamic resizing — Wikipedia](https://en.wikipedia.org/wiki/Hash_table#Dynamic_resizing)
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
