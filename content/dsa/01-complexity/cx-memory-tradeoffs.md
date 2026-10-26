---
id: cx-memory-tradeoffs
sourceLesson: cx-space-complexity
title: Memory trade-offs and real storage
level: intermediate
minutes: 2
summary: Choose a representation and balance extra memory against speed.
---

A faster algorithm may need more storage. A smaller representation may let the same algorithm handle a much larger input. Here n is the number of input items.

## Spend memory where it removes repeated work

Checking duplicates with a hash set uses expected linear time and linear extra storage under suitable hashing assumptions. Sorting in place and comparing neighbours trades more computation for less extra storage, but changes input order. A strict constant-space claim needs a suitable sort, such as heapsort.

For a pair-sum problem on a reorderable array, sorting followed by two positions moving inward avoids keeping a hash set. When the current sum is too small, advance the lower end; when too large, retreat the upper end. The ordering makes those decisions safe.

**Precomputation** is another trade-off. Prefix sums store the total before each position. A range total is then the prefix at the end minus the prefix at the start. Building the prefixes costs linear work and storage, while each query uses one subtraction for fixed-size values. Updates can invalidate later prefixes, so the benefit depends on the workload.

## A growth class is not a byte budget

A Python list stores references to objects. A packed numeric array stores fixed-width values directly. Both have linear storage growth, but their per-item sizes differ.

For a hypothetical representation with eight-byte entries, ten million entries need an 80 MB data buffer, using decimal megabytes. A list of separately allocated Python integers also needs object headers, references and possible spare capacity. `sys.getsizeof` reports the immediate object size, not recursively all objects it references.

Use the actual build and value range when budgeting. The standard `array` module exposes `itemsize`; its type widths depend on the C implementation. A signed 64-bit representation cannot hold arbitrary-size Python integers. Leave room for runtime state and temporary buffers during construction or conversion.

## Key takeaways
- Compare time, extra storage and permission to mutate together.
- Precomputed answers help repeated queries but introduce storage and update costs.
- Measure representation overhead and peak construction memory, not just asymptotic space.

## Further reading
- [Python packed arrays](https://docs.python.org/3.14/library/array.html)
- [Python object-size measurement](https://docs.python.org/3.14/library/sys.html)
