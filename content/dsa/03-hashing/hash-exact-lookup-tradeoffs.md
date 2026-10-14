---
id: hash-exact-lookup-tradeoffs
title: Lookup, deduplication and representation
level: basic
minutes: 3
sourceLesson: hash-maps-sets
summary: Once key equality is sound, choose a representation from the actual query.
---

Once key equality is sound, choose a representation from the actual query. A prebuilt membership index can save repeated scans, while range queries and small dense integer domains often need a different structure.

## When to reach for a hash map or set

Most uses fall into three patterns.

### 1. Lookups by key

Replace a repeated linear search with one O(n) build (n being the number of items you index) and O(1) average lookups.

```python
# Partial example: supplied user objects.
# Build once, then probe for each order.
users = {u.id: u for u in user_list}
for order in orders:
    user = users.get(order.user_id)
```

For m orders and n users (here m counts orders, not buckets) this is O(n + m), instead of O(n × m) with a nested loop. With 10,000 users and 10,000 orders that is about 20,000 steps instead of 100 million.

### 2. Deduplication and "seen before?"

```python
def first_repeat(items):
    seen = set()
    for x in items:
        # Return the first value seen twice.
        if x in seen:
            return x
        seen.add(x)
    return None

first_repeat([3, 1, 4, 1, 5])  # 1
```

Checking `x in some_list` inside a loop is a common hidden O(n²): for n items, each of the n checks can scan up to n list entries. Changing the list to a set is often the single biggest speed-up available in a slow script.

### 3. Counting

```python
from collections import Counter

words = "the cat and the hat".split()
# Count token appearances, not positions.
counts = Counter(words)
counts["the"]          # 2
counts.most_common(1)  # [('the', 2)]
```

`Counter` is a dict subclass. The hand-written version is `counts[w] = counts.get(w, 0) + 1`. A related tool, `defaultdict(list)`, groups items by key without checking whether the key exists first.



## When not to use one

Hash tables are fast at exact-match lookups and nothing else. Reach for something different when:

- **You need order or ranges.** "All keys between 100 and 200", "the smallest key" or "the next key after x" need a sorted structure: a balanced binary search tree (Java's `TreeMap`, O(log n) per operation for n keys, about 20 steps for a million keys), a B-tree in a database, or a sorted array with binary search. A hash table would have to scan everything.
- **Keys are small dense integers.** If keys are 0 to 999, a plain array avoids hashing and often reduces overhead; actual performance depends on representation and workload.
- **Memory is tight.** Hash tables keep spare empty slots and per-entry overhead. For example, on a 64-bit CPython 3.14 build, sys.getsizeof(list(range(1_000_000))) is about 8 MB and sys.getsizeof(set(range(1_000_000))) about 33.6 MB, excluding integer objects. These sizes are build- and construction-dependent.
- **You need guaranteed worst-case latency.** A resize or a burst of collisions can make one operation take far longer than usual.

| Need | Use |
|---|---|
| Exact lookup, membership | Hash map / set |
| Sorted order, range query | Balanced BST, B-tree |
| Keys are 0..n | Plain array |
| Min or max repeatedly | Heap |



## Key takeaways
- Build a membership index once to avoid repeated list scans.
- Use sorted structures for ordered range queries and direct arrays for dense integer domains.
- Account for spare slots, representation overhead and latency spikes when choosing a table.

## Further reading
- [Time complexity of Python operations — Python wiki](https://wiki.python.org/moin/TimeComplexity)
- [collections: Counter and defaultdict — Python docs](https://docs.python.org/3/library/collections.html)
