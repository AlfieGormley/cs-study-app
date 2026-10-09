---
id: sort-merge
title: Merge sort
level: basic
minutes: 13
summary: Divide and conquer, the linear-time merge, why merge sort is stable, the recursion-tree proof of O(n log n), and how external merge sort handles data bigger than memory.
---

The simple sorts are slow because each step makes only a tiny amount of progress: one adjacent swap removes one inversion. Merge sort makes progress in bulk by using **divide and conquer**:

1. **Divide** the array into two halves.
2. **Conquer**: sort each half recursively.
3. **Combine**: merge the two sorted halves into one sorted array.

The magic is that step 3 is cheap. Merging two sorted lists takes linear time, and that is enough to get O(n log n) overall, guaranteed, on every input. Here n is the number of elements, O(...) is Big O notation (how cost grows with n, ignoring constant factors) and log n is the base-2 logarithm of n: how many times n can be halved before reaching 1, about 20 for a million.

## The merge step

Picture two sorted piles of cards face up. Repeatedly take the smaller of the two top cards. When one pile empties, append the rest of the other.

```python
def merge(left, right):
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # stable
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out
```

Each comparison outputs one element, and once one list runs out the rest of the other is copied with no comparisons at all. That gives the cost of a merge:

```formula
C_max = a + b − 1
C_min = min(a, b)
C_max = 3 + 3 − 1 = 5
where
C_max: the most comparisons a merge can need, when both lists are nonempty (it is zero if either is empty)
C_min: the fewest comparisons, reached when every element of the shorter list is smaller than every element of the longer one
a: the number of elements in the left list; here 3
b: the number of elements in the right list; here 3
min: the smaller of its two inputs
In words: a merge never needs more comparisons than one fewer than the total number of elements, and never fewer than the length of the shorter list.
```

```
left  [2, 5, 9]     right [3, 4, 10]
2 vs 3 -> 2        out [2]
5 vs 3 -> 3        out [2, 3]
5 vs 4 -> 4        out [2, 3, 4]
5 vs 10 -> 5       out [2, 3, 4, 5]
9 vs 10 -> 9       out [2, 3, 4, 5, 9]
left empty: append [10]
```

Five comparisons for six elements: 3 + 3 − 1, the maximum.

### Why `<=` makes it stable

When the two front elements are equal, we take the one from the **left** half. Everything in the left half came earlier in the original array, so equal keys keep their original order. Write `<` instead and equal elements from the right half jump ahead: the sort is no longer stable. One character decides it.

## The full sort

```python
def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid])
    right = merge_sort(a[mid:])
    return merge(left, right)
```

```
        [38, 27, 43, 3, 9, 82, 10]
          /                   \
   [38, 27, 43]          [3, 9, 82, 10]
    /       \              /        \
 [38]   [27, 43]       [3, 9]    [82, 10]
         /   \          /  \      /   \
       [27] [43]      [3]  [9]  [82] [10]
 ----------------- merge up ---------------
 [38]   [27, 43]       [3, 9]    [10, 82]
   [27, 38, 43]          [3, 9, 10, 82]
          \                   /
        [3, 9, 10, 27, 38, 43, 82]
```

## Proof of O(n log n): the recursion tree

A **recurrence** describes a cost in terms of the same cost on smaller inputs. Merge sort's running time obeys this one:

```formula
T(n) = 2 × T(n / 2) + c × n
T(1) = c
where
T(n): the running time of merge sort on n elements, in basic steps
n: the number of elements to sort
T(n / 2): the running time of one recursive call on half the elements
T(1): the cost of the base case, a single element
c: a fixed constant: the cost per element of merging
In words: sorting n elements costs two half-size sorts plus a merge that touches every element once.
```

Draw it as a tree. The root does c × n work merging. Its two children each do half that, so that level also totals c × n. Every level works the same way:

```formula
W_k = 2^k × c × (n / 2^k) = c × n
L = log_2(n) + 1
T(n) = c × n × (log_2(n) + 1)
T(n) = Θ(n × log n)
where
W_k: the total work done on level k of the recursion tree
k: the level number, 0 at the root
2^k: 2 multiplied by itself k times: the number of subproblems on level k, which doubles each level
n / 2^k: the size of each subproblem on level k
c: the per-element merging cost
n: the number of elements
L: the number of levels in the tree
log_2(n): the base-2 logarithm of n: how many times n can be halved before reaching 1 (log_2(1024) = 10)
log: the logarithm; inside Big Theta the base does not matter, because changing it only multiplies by a constant
T(n): the total running time
Θ: Big Theta: exactly this growth rate, up to a constant factor
In words: every level of the tree does c × n work in total, and there are log_2(n) + 1 levels, so merge sort costs about n log n.
```

```
level 0:   n                  = n
level 1:   n/2  n/2           = n
level 2:   n/4 n/4 n/4 n/4    = n
  ...
level lg n: 1 1 1 ... 1 (n)   = n
```

Subproblem sizes halve each level, so they reach 1 after log₂ n levels. That gives log₂ n + 1 levels, each costing c × n. For 1,024 elements that is 11 levels. The proof assumes n is a power of 2; for other sizes the halves differ by at most one element and the result is the same.

The **master theorem**, a general recipe for divide-and-conquer recurrences, gives the same result:

```formula
T(n) = a × T(n / b) + f(n)
a = 2,  b = 2,  f(n) = Θ(n)
T(n) = Θ(n × log n)
where
T(n): the running time on n elements
n: the number of elements
a: the number of recursive calls each call makes; 2 for merge sort
b: the factor each call shrinks the input by; 2, because each half has n / 2 elements
f(n): the work done outside the recursive calls; here the merge, which is linear in n
Θ: Big Theta: exactly this growth rate, up to a constant factor
log: the logarithm (base 2 here; the base only changes a constant)
In words: merge sort is the master theorem's "balanced" case, where the work outside the calls matches the work on every level of the tree.
```

The theorem gives the answer, but the tree shows *why*: every level touches every element exactly once.

Concrete numbers for a million elements:

```formula
n × log_2(n) ≈ 10^6 × 20 = 2 × 10^7
n^2 / 4 = 10^12 / 4 = 2.5 × 10^11
where
n: the number of elements, here 1,000,000 (10^6)
log_2(n): the base-2 logarithm of n; log_2(10^6) ≈ 19.9, rounded to 20
n^2: n squared, n × n
10^6: ten to the power 6, a million (similarly 10^7, 10^11, 10^12)
≈: approximately equal to
In words: merge sort needs about 20 million comparisons in the worst case, while insertion sort on shuffled input needs about 250 billion steps, one per inversion.
```

The operation counts differ greatly. **Content gap:** absolute runtimes are omitted because no benchmark environment or implementation was verified.

> [!note] Worst, best and average are all n log n
> Merge sort always splits in the middle and always merges everything, so its cost hardly depends on the input. Plain merge sort is not adaptive: a sorted input still costs Θ(n log n). Timsort (lesson 6) fixes that.

The exact worst-case comparison count for top-down merge sort is known, and it is very close to the theoretical minimum (lesson 4):

```formula
C_w = n × ⌈log_2(n)⌉ − 2^{⌈log_2(n)⌉} + 1
C_w = 5 × 3 − 2^3 + 1 = 8
where
C_w: the most comparisons top-down merge sort makes on any input of n elements
n: the number of elements; here 5
log_2(n): the base-2 logarithm of n; log_2(5) ≈ 2.32
⌈ ⌉: the ceiling: round up to the next whole number, so ⌈2.32⌉ = 3
2^{⌈log_2(n)⌉}: 2 raised to that rounded-up power: the smallest power of 2 that is at least n (8 for n = 5)
In words: the worst case is roughly n log_2(n) comparisons, minus a correction for n not being a power of 2.
```

For five elements that is 8 comparisons, one more than the minimum of 7 that lesson 4 derives.

## Space: the real cost

The array version needs an O(n) auxiliary buffer for merging. You can allocate it once and reuse it, rather than slicing like the teaching code above (which allocates a lot of small lists). The recursion stack adds O(log n).

In-place merge algorithms exist, but they are complicated and slower in practice. This is merge sort's main trade-off against quicksort with smaller-side recursion and heapsort, which need O(log n) and O(1) extra space respectively. Naive quicksort can use O(n) stack space.

**Linked lists** are the exception. Merging two linked lists just re-links nodes, so merge sort on a list needs no buffer, and it does not need random access. It is the standard way to sort a linked list.

## Bottom-up merge sort

You can skip recursion entirely. Treat the array as n runs of length 1, merge neighbouring pairs into runs of length 2, then 4, 8 and so on.

```
width 1: [38][27] [43][3] [9][82] [10]
width 2: [27 38]  [3 43]  [9 82]  [10]
width 4: [3 27 38 43]     [9 10 82]
width 8: [3 9 10 27 38 43 82]
```

Same O(n log n), no recursion stack, and the access pattern is simple sequential passes. It is also the idea behind external sorting.

## A bonus: counting inversions

While merging, whenever you take an element from the right half, it is smaller than every element still waiting in the left half. Each of those is an inversion. Adding `len(left) - i` at that moment counts all inversions in O(n log n), instead of O(n²) by checking every pair. This is used to measure how similar two rankings are (Kendall tau distance).

## External sorting: data bigger than memory

Suppose you must sort 100 GB of records on a machine with 1 GB of RAM. You cannot load it all, and random access to disk is slow. Merge sort's sequential access pattern makes it the natural fit.

**Phase 1: run generation.** For a simplified example, reserve 1 GB for sortable records with additional memory available for overhead, sort each chunk, and write it as a sorted **run**. That gives 100 runs. On a machine with only 1 GB total, choose smaller chunks and expect more runs.

**Phase 2: k-way merge.** Open all 100 runs at once. Give each a small input buffer (say 8 MB each, reserving the remaining memory for output, heap and process overhead) and repeatedly output the smallest front element. With k runs (here k = 100), finding the smallest of the k fronts efficiently uses a **min-heap** of size k (covered in the trees module), costing O(log k) per element.

```
run 1 [buffer] \
run 2 [buffer]  \
  ...            > min-heap -> output
run 100 [buffer]/
```

The arithmetic of the plan:

```formula
r = D / M = 100 GB / 1 GB = 100
B = r × 8 MB = 800 MB
where
r: the number of sorted runs phase 1 produces
D: the total size of the data, here 100 gigabytes
M: the memory used to sort each chunk, here 1 gigabyte
B: the total memory phase 2 spends on input buffers, one per run
GB: gigabyte, 1,000,000,000 bytes
MB: megabyte, 1,000,000 bytes
In words: 100 GB sorted 1 GB at a time gives 100 runs, and 100 input buffers of 8 MB need 800 MB in the merge phase.
```

Total: every record is read and written twice (once per phase), all sequentially. If there are too many runs to merge in one go, you merge in several passes, each multiplying run length by k.

> [!example] PostgreSQL does exactly this
> When a sort needs more memory than `work_mem` (default 4 MB), PostgreSQL switches to an external merge sort using temporary files. `EXPLAIN ANALYZE` shows `Sort Method: external merge  Disk: ...` instead of `quicksort  Memory: ...`. Raising `work_mem` for a big reporting query can keep the sort in memory.

The same pattern appears in big-data systems: MapReduce and Spark sort map output into spill files and merge them, and LSM-tree databases (RocksDB, Cassandra) merge sorted files during compaction.

## Trade-offs and pitfalls

| Property | Merge sort |
|---|---|
| Time (all cases) | Θ(n log n) |
| Extra space | O(n) for arrays |
| Stable | Yes, with `<=` |
| Adaptive | No (plain version) |

- **Use it when** you need guaranteed n log n, stability, a linked list, or data on disk or arriving as sorted streams.
- **Small sub-arrays.** Recursing down to size 1 wastes time. Real implementations switch to insertion sort below roughly 16 to 32 elements.
- **Skip merges that are not needed.** If `left[-1] <= right[0]`, the halves are already in order and the merge can be skipped. For an index-range implementation that returns without copying an already ordered range, this makes sorted-input time linear. In the slicing example, creating and concatenating halves still costs Θ(n log n), even if comparisons become linear.
- **Midpoint overflow.** In languages with fixed-width integers, `(lo + hi) / 2` can overflow on huge arrays. Use `lo + (hi - lo) / 2`. This bug sat in Java's library for years (see lesson 7).

## Key takeaways
- Merge sort divides in half, sorts each half recursively and merges in linear time.
- The recursion tree has about log₂ n levels, each doing n work, so it is Θ(n log n) on every input.
- It is stable when ties are taken from the left half (`<=`).
- Its cost is O(n) extra memory for arrays; linked-list merging needs no element buffer, while recursive sorting still uses O(log n) stack space (bottom-up variants can use O(1)).
- External merge sort (sorted runs plus a k-way heap merge) is how databases and big-data systems sort data larger than RAM.

## Further reading
- [Mergesort — Algorithms, 4th ed. (Sedgewick and Wayne)](https://algs4.cs.princeton.edu/22mergesort/)
- [Merge sort — Wikipedia](https://en.wikipedia.org/wiki/Merge_sort)
- [External sorting — Wikipedia](https://en.wikipedia.org/wiki/External_sorting)
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [PostgreSQL resource consumption settings (work_mem)](https://www.postgresql.org/docs/current/runtime-config-resource.html)
