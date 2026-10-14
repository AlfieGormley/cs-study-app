---
id: sort-stable-multi-key
title: Stable multi-key sorting and pagination
level: advanced
minutes: 2
sourceLesson: sort-real-world
summary: Sort secondary keys first, then primary keys with a stable algorithm.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Stability in practice

Stability lets you build multi-key sorts from single-key sorts. **Sort by the secondary key first, then by the primary key:**

```python
people = [("ann", 30), ("bob", 25),
          ("cat", 30), ("dan", 25)]
people.sort(key=lambda p: p[0])  # name
people.sort(key=lambda p: p[1])  # age
# [('bob',25), ('dan',25),
#  ('ann',30), ('cat',30)]
```

The second sort orders by age; within equal ages, the stable sort keeps the name order from the first sort. This is exactly how clicking "sort by name" and then "sort by age" behaves in a spreadsheet or UI table: users expect the earlier ordering to survive within ties, and an unstable sort makes rows jump around.

Python's `reverse=True` is also stable: equal elements keep their original order rather than being reversed.

> [!tip] Choosing in practice
> Use your language's default sort with a key function. Reach for a stable sort when the order of ties is visible to users or downstream code. Reach for an unstable one (`sort_unstable`, `std::sort`) only when you have measured that sorting matters and ties are indistinguishable.

JavaScript’s default `Array.sort()` compares string conversions when no comparator is supplied: `[10, 9, 1].sort()` becomes `[1, 10, 9]`. Use a numeric comparator for numeric order. A database pagination query also needs a deterministic tie-breaker such as a unique order ID after its date; a stable in-memory algorithm cannot add a missing SQL ordering key.


## Key takeaways
- Sort secondary keys first, then primary keys with a stable algorithm.
- Pagination additionally needs a deterministic total order, usually a unique tie-breaker.

## Further reading
- [Sorting techniques — Python documentation](https://docs.python.org/3/howto/sorting.html)
- [CPython 3.14.0 list-sort design notes](https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/listsort.txt)
