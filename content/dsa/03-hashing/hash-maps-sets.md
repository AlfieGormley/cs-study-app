---
id: hash-maps-sets
title: Hash maps and sets
level: basic
minutes: 9
summary: What a hash map and a hash set promise, why lookups are O(1) on average but O(n) in the worst case, and when to reach for one.
---

Suppose you have a list of a million customer IDs and you need to check, for each of a million incoming orders, whether the customer exists. Scanning the list each time costs up to a million comparisons per order: around 10¹² operations in total. Sorting the list and binary searching cuts each check to about 20 comparisons.

A **hash table** does better still: on average, each check takes a constant number of steps, no matter how many IDs you store. This makes hash maps and sets useful for many everyday lookup tasks.

## The idea in one picture

A hash table is an array of **buckets** (or slots). To store a key, you run it through a **hash function** that turns it into an integer, then reduce that integer to an array index.

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

Two different keys can land on the same index. That is a **collision**, and every hash table needs a strategy for it (lesson 3). As long as collisions are rare, each bucket holds about one key and operations stay fast.

## The interface

There are two flavours.

A **hash map** (dictionary, associative array) stores key → value pairs:

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
seen.add("alice")
"alice" in seen      # True
seen.discard("bob")  # no error if absent
```

Sets also support union (`a | b`), intersection (`a & b`) and difference (`a - b`). An intersection iterates over the smaller set and probes the larger one, so it costs O(min(len(a), len(b))) on average.

Other languages have the same pair: Java's `HashMap` / `HashSet`, C++'s `std::unordered_map` / `std::unordered_set`, Go's built-in `map`, JavaScript's Map / Set offer similar interfaces, but the specification requires average sublinear access rather than a particular hash-table representation.

## Average case versus worst case

The O(1) figure is an **average**, and it rests on an assumption: the hash function spreads keys roughly evenly across buckets.

If n keys sit in m buckets, the average number of keys per bucket is the **load factor** α = n / m. Tables keep α below a fixed limit (Java uses 0.75, Python's dict about 2/3) by growing the array when it fills up. With α bounded by a constant, the expected work per operation is constant.

The **worst case** is very different. If every key hashes to the same bucket, a list-chained table degenerates into one long chain; an unsuccessful lookup or a hit at the end may scan all n keys:

```
 0     1     2              3
[ ]  [ ]   [k1->k2->...->kn] [ ]
```

That makes a lookup O(n), and inserting n keys O(n²). This happens in practice when:

- the hash function is poor for your data (for example, hashing integers that are all multiples of the table size), or
- an attacker deliberately sends keys that collide, a **hash flooding** attack (lesson 2).

There is also an occasional slow insert: when the table grows, every key is re-inserted into a bigger array, which costs O(n). Spread over all the inserts this averages out to O(1) per insert, which is called **amortised** O(1) (lesson 4).

> [!note] What "O(1) average" really means
> It is the expected cost under a reasonable hash function, ignoring the occasional resize. Hashing the key itself is not free: computing an uncached string hash ordinarily scans O(L) characters. CPython caches string hashes, and identity shortcuts can avoid equality scans; a repeated lookup using the same long string need not rescan it.

## Keys must be hashable

A hash table finds a key by recomputing its hash. If a key's hash could change after insertion, the table would look in the wrong bucket and the entry would be lost. So the contract is:

1. If `a == b`, then `hash(a) == hash(b)`. Equal keys must land in the same bucket.
2. A key's hash and equality-relevant state must stay stable while it is in the table.

The reverse of rule 1 is *not* required: unequal keys may share a hash. That is just a collision.

In Python, immutable built-ins (`int`, `str`, `tuple` of hashables, `frozenset`) are hashable. The built-ins list, dict and set are not hashable. Mutability alone is not the general test: custom mutable objects can use stable identity equality/hashing, and an immutable class can disable hashing:

```python
d = {}
d[(1, 2)] = "ok"     # tuple: fine
d[[1, 2]] = "no"     # TypeError: unhashable
```

> [!warning] Equal keys collapse
> Because `1 == 1.0 == True` in Python, they are the same dict key. `{1: "a", True: "b"}` gives `{1: "b"}`: the second assignment updates the value, keeping the first key object.

If you define `__eq__` on your own class, Python sets `__hash__` to `None`, making instances unhashable, unless you also define `__hash__`. In Java, overriding `equals` without `hashCode` is a classic bug: two equal objects can have different hashes, causing lookup to miss even if bucket reduction happens to coincide.

## When to reach for a hash map or set

Most uses fall into three patterns.

### 1. Lookups by key

Replace a repeated linear search with one O(n) build and O(1) lookups.

```python
users = {u.id: u for u in user_list}
for order in orders:
    user = users.get(order.user_id)
```

For m orders and n users this is O(n + m), instead of O(n × m) with a nested loop.

### 2. Deduplication and "seen before?"

```python
def first_repeat(items):
    seen = set()
    for x in items:
        if x in seen:
            return x
        seen.add(x)
    return None

first_repeat([3, 1, 4, 1, 5])  # 1
```

Checking `x in some_list` inside a loop is a common hidden O(n²). Changing the list to a set is often the single biggest speed-up available in a slow script.

### 3. Counting

```python
from collections import Counter

words = "the cat and the hat".split()
counts = Counter(words)
counts["the"]          # 2
counts.most_common(1)  # [('the', 2)]
```

`Counter` is a dict subclass. The hand-written version is `counts[w] = counts.get(w, 0) + 1`. A related tool, `defaultdict(list)`, groups items by key without checking whether the key exists first.

## When not to use one

Hash tables are fast at exact-match lookups and nothing else. Reach for something different when:

- **You need order or ranges.** "All keys between 100 and 200", "the smallest key" or "the next key after x" need a sorted structure: a balanced binary search tree (Java's `TreeMap`, O(log n) per operation), a B-tree in a database, or a sorted array with binary search. A hash table would have to scan everything.
- **Keys are small dense integers.** If keys are 0 to 999, a plain array avoids hashing and often reduces overhead; actual performance depends on representation and workload.
- **Memory is tight.** Hash tables keep spare empty slots and per-entry overhead. For example, on a 64-bit CPython 3.14 build, sys.getsizeof(list(range(1_000_000))) is about 8 MB and sys.getsizeof(set(range(1_000_000))) about 33.6 MB, excluding integer objects. These sizes are build- and construction-dependent.
- **You need guaranteed worst-case latency.** A resize or a burst of collisions can make one operation take far longer than usual.

| Need | Use |
|---|---|
| Exact lookup, membership | Hash map / set |
| Sorted order, range query | Balanced BST, B-tree |
| Keys are 0..n | Plain array |
| Min or max repeatedly | Heap |

> [!tip] Python dicts remember insertion order
> Since Python 3.7, iterating over a dict returns keys in the order they were first inserted. This is a language guarantee, not an accident. Sets make no such promise: their iteration order depends on the hashes.

## Key takeaways
- A hash table hashes a key to an array index, so lookup, insert and delete are O(1) on average, independent of size.
- The worst case is O(n) per operation, when many keys collide; good hash functions and resizing keep it rare.
- Keys must be hashable: equal keys need equal hashes, and the hash must not change while the key is stored.
- Reach for a map or set for lookups by key, deduplication and counting; replacing `x in list` with `x in set` removes a hidden O(n²).
- Use a sorted structure instead when you need ordering, ranges, or min and max.

## Further reading
- [Hash table — Wikipedia](https://en.wikipedia.org/wiki/Hash_table)
- [Time complexity of Python operations — Python wiki](https://wiki.python.org/moin/TimeComplexity)
- [Mapping types: dict — Python docs](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
- [collections: Counter and defaultdict — Python docs](https://docs.python.org/3/library/collections.html)
- [Associative array — Wikipedia](https://en.wikipedia.org/wiki/Associative_array)
