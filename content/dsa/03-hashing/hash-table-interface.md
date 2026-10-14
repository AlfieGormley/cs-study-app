---
id: hash-table-interface
title: Hash maps and sets: lookup interfaces
level: basic
minutes: 4
sourceLesson: hash-maps-sets
summary: A map associates a value with a key; a set remembers only whether a key is present.
---

A map associates a value with a key; a set remembers only whether a key is present. Before using either, decide whether the query is exact membership or an ordered search.

Suppose you have a list of a million customer IDs and you need to check, for each of a million incoming orders, whether the customer exists. Scanning the list each time costs up to a million comparisons per order: a million orders times a million comparisons is around 10¹² (a million million) operations in total. Sorting the list and binary searching cuts each check to about 20 comparisons, because each comparison halves the range still to search and 2²⁰ is about a million.

A **hash table** does better still: on average, each check takes a constant number of steps, no matter how many IDs you store. This makes hash maps and sets useful for many everyday lookup tasks.



## The idea in one picture

The full hash in the drawing is illustrative, not a claim about Python’s process-dependent string hash. Its remainder after division by eight is one.

A hash table is an array of **hash buckets** (or slots). To store a key, you run it through a **hash function** that turns it into an integer, then reduce that integer to an array index.

```
key "alice"
   |
   v
hash("alice") = 8,413,776,201
   |
   v  mod 8 (array size)
index 1

 0     1        2     3     4  ...
[ ]  [alice]  [ ]   [bob]  [ ]
```

To look the key up later, you hash it again, jump straight to the same index and check whether it is there. Collision handling can still scan candidates; expected constant work relies on well-distributed hashes, bounded load and constant-cost key operations.

Two different keys can land on the same index. That is a **hash collision**, and every hash table needs a strategy for it (Collision resolution). As long as collisions are rare, each bucket holds about one key and operations stay fast.



## The interface

There are two flavours.

A **hash map** (dictionary, associative array) stores key → value pairs. In the table below, n is the number of keys stored, and O(1) means "a constant number of steps, however large n gets" (Big-O notation, from the Complexity module):

| Operation | Python | Average |
|---|---|---|
| Insert / update | `d[k] = v` | O(1) |
| Look up | `d[k]`, `d.get(k)` | O(1) |
| Membership | `k in d` | O(1) |
| Delete | `del d[k]` | O(1) |
| Iterate | `for k in d` | O(n) for compact state; retained holes can add work |

A **hash set** stores keys only, and answers "have I seen this?":

```python
seen = set()
# Store membership, without a value.
seen.add("alice")
"alice" in seen      # True
seen.discard("bob")  # no error if absent
```

Sets also support set union (`a | b`), set intersection (`a & b`) and set difference (`a - b`). An intersection iterates over the smaller set and probes the larger one, so on average its cost grows with the size of the *smaller* set only: intersecting a 10-item set with a million-item set takes about 10 lookups.

Other languages have the same pair: Java's `HashMap` / `HashSet`, C++'s `std::unordered_map` / `std::unordered_set` and Go's built-in `map`. JavaScript's Map / Set offer similar interfaces, but the ECMAScript specification only requires average sublinear access (faster than scanning everything), not a particular hash-table representation.

> [!tip] Python dicts remember insertion order
> Since Python 3.7, iterating over a dict returns keys in the order they were first inserted. This is a language guarantee, not an accident. Sets make no such promise: their iteration order depends on the hashes.

The constructor dict.fromkeys makes each supplied value a key. Repeated values update an existing entry without moving its original insertion position. Converting the resulting dictionary to a list therefore gives the distinct values in first-appearance order; it does not sort them. This technique is useful when an API requires deduplication while preserving input order.

## Key takeaways
- A map stores key–value pairs; a set stores membership.
- Exact-key access is fast on average under well-distributed hashes and bounded-cost keys.
- Dict iteration preserves insertion order; sets offer no such ordering promise.

## Further reading
- [Time complexity of Python operations — Python wiki](https://wiki.python.org/moin/TimeComplexity)
- [Mapping types: dict — Python docs](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
