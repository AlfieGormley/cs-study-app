---
id: pat-heaps
title: Top-K, k-way merge and two heaps
level: advanced
minutes: 14
summary: Three heap patterns that recur in interviews and production systems, a size-k heap for the k largest, a heap of list heads to merge k sorted inputs, and a pair of heaps to track a running median.
---

A binary heap gives you the minimum (or maximum) of a changing collection in O(1), and inserts or removes the root in O(log(n + 1)) heap comparisons, where n is the number of items in the heap. The log is there because a heap is a balanced tree about log₂ n levels deep, and an insert or removal walks one path from top to bottom; the + 1 just keeps the bound meaningful when n is 0 or 1. Removing an arbitrary item needs a way to locate it. Python list resizing makes individual operations occasionally linear; the standard bound is amortised and assumes constant-cost comparisons. Many problems that look like "sort everything" only need the *best few* items, or the *current* best, and a heap can avoid sorting the entire collection.

This lesson covers three patterns built on that one idea.

```
Top-K        keep a heap of size k
K-way merge  heap holds one head per list
Two heaps    max-heap | min-heap around
             the median
```

## Python's heapq in 60 seconds

`heapq` turns a plain list into a **min-heap**: `h[0]` is always the smallest. In the table, n is the number of items in the heap (or in the input iterable `it`), and k is how many items you ask for.

| Call | Cost |
|---|---|
| `heappush(h, x)` | O(log n) |
| `heappop(h)` | O(log n) |
| `h[0]` (peek) | O(1) |
| `heapreplace(h, x)` | O(log n): pop, then push |
| `heapify(h)` | O(n) |
| `nlargest(k, it)` | O(n log(k + 1)), k from 1 to n |

Python 3.14 provides public max-heap functions such as `heapify_max` and `heappush_max`. The examples use the older-compatible **negation** technique for ordered numeric values: push `-x`, and `-h[0]` is the maximum. NaN values are excluded because they do not provide the required ordering.

Tuples compare element by element, so `(priority, item)` works. If priorities can tie and the items aren't comparable (say, linked-list nodes), add a tie-breaking counter: `(priority, i, item)`.

## Pattern 1: top-K

**Problem.** Find the k largest elements of n (or the k-th largest).

Options:

| Approach | Time | Extra space |
|---|---|---|
| Sort, take last k | O(n log n) | Python sort: O(n) auxiliary, plus output |
| Min-heap of size k | O(n log(k + 1)) | O(k) |
| Max-heapify all, pop k | O(n + k log(n + 1)) | O(n) storage; O(1) heapify auxiliary |
| Randomised quickselect | O(n) expected | O(1) auxiliary with iterative in-place partition |

To see why the size-k heap pays off when k is much smaller than n, compare the dominant terms:

```formula
W_sort ≈ n × log_2(n)
W_heap ≈ n × log_2(k)
W_sort ≈ 10^6 × 20 = 2 × 10^7
W_heap ≈ 10^6 × 3.3 ≈ 3.3 × 10^6
where
W_sort: the rough comparison count for sorting all n items
W_heap: the rough comparison count for streaming n items through a min-heap of size k (the worst case, when every item must be pushed)
n: the number of items; here 10^6
k: how many of the largest items you want; here 10
log_2: the base-2 logarithm, the number of halvings from the argument down to 1; log_2(10^6) ≈ 20 and log_2(10) ≈ 3.3
≈: approximately equal to
In words: each heap operation only climbs a tree log_2(k) levels deep instead of log_2(n), so for the top 10 of a million items the heap does about a sixth of the comparison work and holds only 10 items in memory.
```

These are rough counts that ignore constant factors; the memory saving (k items instead of n) is often the bigger win.

The size-k heap is a standard option. The counter-intuitive part: to keep the k **largest**, use a **min**-heap. Its root is the smallest of your current top k, the "weakest member", which is exactly what a newcomer must beat.

```python
import heapq

def top_k(nums, k):
    if type(k) is not int or k < 0:
        raise ValueError("nonnegative k")
    if k == 0:
        return []
    heap = []
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)
    return heap    # up to k largest values
```

```
nums = [3, 2, 1, 5, 6, 4], k = 2
3  heap [3]
2  heap [2,3]
1  1 < 2: ignore
5  5 > 2: replace -> [3,5]
6  6 > 3: replace -> [5,6]
4  4 < 5: ignore
2nd largest = heap[0] = 5
```

The size-k heap works on a **stream of already scored items**: keeping the 100 largest numeric observations needs O(100) stored items. Exact top-100 query *frequencies* are different: frequencies must first be counted, which can require memory proportional to the number of distinct queries or external/distributed storage.

**Top-K frequent elements**: count with a `Counter` (expected O(n), O(u) entries for u distinct values), then take the top k by count with `heapq.nlargest(k, counts, key=counts.get)`. Since counts are bounded by n, a **bucket sort** (a list of buckets indexed by frequency) gets O(n) total.

> [!note] Quickselect
> Quickselect partitions like quicksort but recurses into only the side containing the k-th position: expected O(n) with independent random pivots, O(n²) worst case for ordinary quickselect. It is a useful option for a one-off order statistic, but universal speed claims require benchmarks. The usual in-place implementation needs the array resident and reorders it.

## Pattern 2: k-way merge

**Problem.** Merge k sorted lists (total N elements) into one sorted list.

At every step, the next output element is the smallest among the k list **heads**. A heap of those heads finds it in O(log k), not O(k).

```python
import heapq

def merge_k(lists):
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            heap.append((lst[0], i, 0))
    heapq.heapify(heap)
    out = []
    while heap:
        val, i, j = heapq.heappop(heap)
        out.append(val)
        if j + 1 < len(lists[i]):
            item = (lists[i][j+1], i, j + 1)
            heapq.heappush(heap, item)
    return out
```

```
lists: [1,4,5] [1,3,4] [2,6]
heap heads: (1,L0) (1,L1) (2,L2)
pop 1 (L0) push 4   out [1]
pop 1 (L1) push 3   out [1,1]
pop 2 (L2) push 6   out [1,1,2]
pop 3 (L1) push 4   ...
final: [1,1,2,3,4,4,5,6]
```

Let h be the number of nonempty lists. Inspecting all k inputs and heapifying their heads costs O(k); each of the N outputs then costs one pop and at most one push on a heap of at most h heads:

```formula
T = O(k + N × log(h + 1))
N × log_2(h) ≈ 10^6 × 6.6 ≈ 6.6 × 10^6
N × k = 10^6 × 100 = 10^8
where
T: the total running time of the heap merge
O(…): Big-O, the growth rate of the cost, ignoring constant factors
k: the number of input lists; here 100
h: the number of nonempty input lists, at most k; here 100
N: the total number of elements across all lists; here 10^6
log: logarithm; its base doesn't matter inside Big-O
log_2: the base-2 logarithm; log_2(100) ≈ 6.6
≈: approximately equal to
In words: merging a million elements from 100 lists costs on the order of 7 million heap steps (each pop or push climbs a tree about 7 levels deep), against about 100 million if you scanned all 100 heads for every output element.
```

So total time is O(k + N log(h + 1)), with O(h) heap space plus O(N) returned output. Concatenating and a generic comparison sort has an O(N log N) bound, but adaptive sorting can exploit the k existing runs. Sequentially merging into a growing result has O(Nk) worst-case movement.

The list index `i` in the tuple breaks ties and tells us which list to advance. Python ships this as `heapq.merge(*lists)`, which is lazy.

> [!example] Where this runs in production
> External sorting (sorting files bigger than RAM) sorts chunks that fit in memory, writes them as sorted "runs", then k-way merges the runs. LSM-tree databases such as RocksDB and Cassandra do the same during **compaction**, merging sorted SSTable streams, often writing multiple output SSTables and applying version/tombstone rules.

Related problems: "k-th smallest element in a sorted matrix" (rows are sorted lists; pop k times), "smallest range covering one element from each of k lists" (track the max of the heads alongside the heap's min).

## Pattern 3: two heaps for a running median

**Problem.** Numbers arrive one at a time. After each, report the median.

Re-sorting each time is O(n log n) per query. Instead, split the numbers into two halves:

- `lo`: a **max-heap** of the smaller half (its top is the largest small number);
- `hi`: a **min-heap** of the larger half (its top is the smallest large number).

Keep every element of `lo` no larger than every element of `hi`, and keep the sizes balanced: `len(lo)` equals `len(hi)` or exceeds it by one. Then the median sits at the tops:

```formula
m = a   if |lo| > |hi|
m = (a + b) / 2   if |lo| = |hi|
m = (3 + 5) / 2 = 4
where
m: the median of all numbers seen so far
a: the top of lo, the largest number in the smaller half
b: the top of hi, the smallest number in the larger half
|lo|: the number of items in the max-heap lo
|hi|: the number of items in the min-heap hi
In words: with an odd count, lo holds the extra item and its top is the middle value; with an even count, the median is the average of the two middle values, here 3 and 5 after adding 5, 15, 1 and 3.
```

```
  lo (max-heap)      hi (min-heap)
  [1, 3, 5]  top 5 | top 8  [8, 15]
  median = 5 (lo is bigger)
```

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.lo = []   # max-heap (negated)
        self.hi = []   # min-heap

    def add(self, x):
        heapq.heappush(self.lo, -x)
        # move lo's largest across to hi
        top = -heapq.heappop(self.lo)
        heapq.heappush(self.hi, top)
        # rebalance: lo may be one bigger
        if len(self.hi) > len(self.lo):
            top = heapq.heappop(self.hi)
            heapq.heappush(self.lo, -top)

    def median(self):
        if not self.lo and not self.hi:
            raise ValueError("empty stream")
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        a, b = -self.lo[0], self.hi[0]
        return (a + b) / 2
```

Pushing through `lo` and then moving its top to `hi` guarantees the ordering invariant without any comparisons of our own; the rebalance step fixes the sizes.

```
add  lo        hi        median
5    [5]       []        5
15   [5]       [15]      10.0
1    [1,5]     [15]      5
3    [1,3]     [5,15]    4.0
8    [1,3,5]   [8,15]    5
```

Each `add` takes O(log(n + 1)) amortised heap work; `median` reads O(1) heap entries, and the two heaps together store O(n) values. The numeric example returns a floating-point mean for even sizes: very large integers can lose precision or overflow conversion, and finite floats can overflow their sum. For exact integer medians, replace `(a + b) / 2` with `Fraction(a + b, 2)` from `fractions`, accounting for integer bit costs.

The two-heaps shape also solves **IPO / maximise capital** (a min-heap of projects by cost, a max-heap of affordable profits) and, with deletion support, **sliding window median**. Naive lazy heaps may accumulate stale entries; O(k) storage and O(n log(k + 1)) total time require bounded heaps, rebuilding or indexed deletion.

## Recognising the pattern

| Cue | Pattern |
|---|---|
| "k largest/smallest/closest" | Size-k heap |
| "k-th largest in a stream" | Size-k min-heap |
| "top k frequent" | Counter + heap/buckets |
| "merge k sorted" | Heap of heads |
| "k-th smallest in sorted matrix" | K-way merge |
| "median of a stream" | Two heaps |
| Repeatedly take the best option | Heap (greedy) |

## Pitfalls

- **Wrong heap direction.** k largest → min-heap of size k; k smallest → max-heap of size k.
- **Comparing uncomparable items.** `(5, node_a)` vs `(5, node_b)` raises `TypeError` when the priorities tie; add an index.
- **Forgetting to negate back** when using `-x` for a max-heap.
- **Assuming the heap list is sorted.** Only `h[0]` is guaranteed; the rest is in heap order.
- **Integer vs float medians.** The even case returns an average, which may need to be a float.

## Key takeaways
- A size-k min-heap keeps the k largest of n items in O(n log(k + 1)) time and O(k) space (for k from 1 to n), and works on streams.
- K-way merge holds one head per list in a heap: O(k + N log(h + 1)) for h nonempty inputs, a technique behind external sorting and LSM compaction.
- Two heaps (max-heap of the low half, min-heap of the high half) give a running median with O(log n) inserts.
- Python's `heapq` is a min-heap; negate for max, and use tie-breakers in tuples.
- Quickselect finds a one-off k-th element in O(n) average when all data is in memory.

## Further reading
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [Heap cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/heap/)
- [Heap (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Heap_(data_structure))
- [K-way merge algorithm — Wikipedia](https://en.wikipedia.org/wiki/K-way_merge_algorithm)
- [Quickselect — Wikipedia](https://en.wikipedia.org/wiki/Quickselect)
