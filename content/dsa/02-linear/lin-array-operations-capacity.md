---
id: lin-array-operations-capacity
title: Array operations and spare capacity
level: basic
minutes: 3
sourceLesson: lin-arrays
summary: Interior changes shift elements; position lookup does not.
---

An array gives direct indexed access, but its physical neighbours must move when you open or close an interior gap. In this unit n is the number of live elements and i is the zero-based position being changed.

## Operations and their cost

In this table n is the number of elements in the array and i is the position being read or changed.

| Operation | Cost | Why |
|---|---|---|
| Read/write `a[i]` | O(1) | Address arithmetic |
| Search (unsorted) | O(n) | Check every slot |
| Insert/delete at end | O(1)* | No shifting |
| Insert/delete at `i` | O(n − i + 1) without resizing | Shift the tail; reallocation may add O(n) |

*For a dynamic array, amortised; see below.

Inserting at position `i` means shifting every later element one slot right to make room. Inserting at the front of a million-element array moves a million elements.

```python
a = [10, 20, 30, 40]
a.insert(1, 15)   # shifts 20, 30, 40 right
print(a)          # [10, 15, 20, 30, 40]
```

## Static vs dynamic arrays

A **fixed-size array** has a size chosen when it is created; this is distinct from static storage duration. C's `int a[100]` and Java's `new int[100]` are fixed-size: you cannot append a 101st element.

A **dynamic array** (resizable array) wraps a static array and tracks two numbers:

- **length**: how many elements are in use.
- **capacity**: how many slots the underlying array has.

When the length equals the capacity and you append, it allocates a bigger array, copies everything across, and frees the old one.

```
capacity 4, length 4: full
[ a | b | c | d ]

append e -> allocate 8, copy, add e
[ a | b | c | d | e |   |   |   ]
```

### What the Python operations touch

A CPython list’s contiguous slots hold references to objects. Indexing chooses one slot directly; membership scans values until a match or the end. An unsorted list does not get fast membership merely because its storage supports direct indexing. Equality comparisons can themselves be expensive; the linear scan bound counts comparisons, assuming each has fixed cost.

An append usually writes into spare capacity. Occasionally it reallocates the backing storage, making that individual operation linear in the current length. “Amortised constant time” describes the total cost spread across a sequence, rather than promising identical latency for every append. The next unit proves why geometric growth gives that guarantee.

Negative indices are translated relative to the stored length, so replacing the last item is still direct access. Removing the last item needs no shifting, while removing the first shifts the remaining references. CPython may also shrink its allocation on some pops; its end-pop bound is amortised.

## Key takeaways
- Interior changes shift elements; position lookup does not.
- Length counts live elements, while capacity includes spare slots.

## Further reading
- [Dynamic array — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_array)
- [Array (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Array_(data_structure))
