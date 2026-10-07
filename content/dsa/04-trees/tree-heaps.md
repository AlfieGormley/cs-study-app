---
id: tree-heaps
title: Heaps and priority queues
level: intermediate
minutes: 14
summary: The binary heap's array layout, sift up and sift down, why heapify is O(n), Python's heapq, and the top-k and k-way merge patterns.
---

Many problems only ever need the **smallest** (or largest) item: the next job to run, the nearest unvisited city in Dijkstra's algorithm, the earliest timer to fire, the next event in a simulation. A BST can do that, but it keeps far more order than you need.

A **priority queue** is the abstract data type for this job: `push(item)`, `pop_min()` and `peek()`. The standard implementation is the **binary heap**, which gives O(log n) push and pop and O(1) peek, stored with implicit parent/child indices rather than tree-link pointers. Python lists still store references to their elements. Costs assume constant-time comparisons; dynamic-array resizing makes push/pop bounds amortized when allocation costs are included.

## The heap property

A binary **min-heap** is a binary tree with two rules:

1. **Shape:** it is a **complete** binary tree (every level full except possibly the last, which fills from the left).
2. **Order:** every parent is **less than or equal to** its children.

So the minimum is always at the root. A **max-heap** flips the order rule.

```
          1
        /   \
       3     2
      / \   / \
     4   8 7   6
    /
   9
```

Notice how much weaker this is than a BST. Siblings are unordered (3 is left of 2), and 4 sits deep on the left while 2 is near the top on the right. The heap only promises that every path from the root downward is sorted. That weaker promise is what makes it cheap to maintain.

## The array layout

Because the tree is complete, it packs into an array in level order with no gaps (lesson 1):

```
idx:  0  1  2  3  4  5  6  7
val: [1, 3, 2, 4, 8, 7, 6, 9]

parent(i) = (i - 1) // 2
left(i)   = 2*i + 1
right(i)  = 2*i + 2
```

Avoiding explicit tree links saves their storage. The array of slots is contiguous, though referenced payload objects need not be; actual cache behavior depends on layout and access patterns. In a heap of n items, the **leaves** are exactly the indices n // 2 to n − 1, so there are ceil(n/2) leaves for n > 0.

## Sift up: push

To push, append the new item at the end (the next free slot in the last level, which keeps the shape) and then **sift up**: while it is smaller than its parent, swap them.

```python
def sift_up(a, i):
    while i > 0:
        p = (i - 1) // 2
        if a[p] <= a[i]:
            break
        a[p], a[i] = a[i], a[p]
        i = p

def push(a, x):
    a.append(x)
    sift_up(a, len(a) - 1)
```

Pushing 0 into the heap above: it lands at index 8 (child of 4), swaps with 4, then 3, then 1, and becomes the new root. At most one swap per level: **O(log n)**.

## Sift down: pop

To pop the minimum, you cannot just remove the root: that would leave a hole at the top. Instead, move the **last** item into the root (keeping the shape), shrink the array, and **sift down**: swap it with its **smaller** child until it is no larger than both children.

```python
def sift_down(a, i, n):
    while True:
        best = i
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and a[l] < a[best]:
            best = l
        if r < n and a[r] < a[best]:
            best = r
        if best == i:
            return
        a[i], a[best] = a[best], a[i]
        i = best

def pop(a):
    a[0], a[-1] = a[-1], a[0]
    top = a.pop()
    if a:
        sift_down(a, 0, len(a))
    return top
```

Swapping with the **smaller** child matters: that child becomes the parent of the other, so it must be the smaller of the two. Pop is also **O(log n)**.

> [!warning] Heaps are not sorted
> Only `a[0]` is guaranteed to be the minimum. `a[1]` is not necessarily the second smallest (in the example it is 3, but 2 is smaller), and iterating over a heap list does not give sorted order. Popping repeatedly does.

## Heapify in O(n)

Given n unsorted items, you could push them one at a time: n × O(log n) = O(n log n). There is a faster way. Treat the array as a complete tree already, and sift down every **non-leaf** from the bottom up:

```python
def heapify(a):
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
```

Trace on `[9, 4, 7, 1, 8, 2, 6, 3]` (n = 8, so start at index 3):

```
i=3 (1): children 3      no swap
i=2 (7): children 2, 6   swap with 2
i=1 (4): children 1, 8   swap with 1,
         then 4 vs 3     swap with 3
i=0 (9): children 1, 2   swap with 1,
         9 vs 3, 8       swap with 3,
         9 vs 4          swap with 4

result: [1, 3, 2, 4, 8, 7, 6, 9]
```

### Why is that O(n)?

The cost of sifting down a node is at most its **height**, and most nodes have tiny heights. A rigorous bound counts nodes able to move down at least j levels: at most floor(n / 2^j). Summing those possible levels gives:

```
swaps ≤ floor(n/2) + floor(n/4) + ...
      < n
```

For the shown sift-down algorithm, this bounds swaps by n and key comparisons by 2n; loop and index checks are additional constant work per step. Pushing one at a time is slower because new items arrive at the *bottom*, the level with the most nodes, and each may climb the full height.

The intuition: sift-down costs are cheap where nodes are plentiful (the bottom) and expensive only where they are rare (the top). Sift-up is the reverse.

### Heapsort

Heapify, then repeatedly swap the root with the last item and sift down over a shrinking prefix. That is **heapsort**: O(n log n) worst case, O(1) extra memory, but not stable and with poor cache locality (it jumps between i and 2i), which can affect practical performance. One use is the worst-case fallback inside **introsort** (the usual implementation of C++ `std::sort`), which switches to heapsort if quicksort recurses too deeply.

## heapq in Python

Python's `heapq` module implements a **min-heap on a plain list**. There is no heap class.

| Function | Cost |
|---|---|
| `heappush(h, x)` | O(log n) |
| `heappop(h)` | O(log n) |
| `h[0]` (peek) | O(1) |
| `heapify(h)` | O(n), in place |
| `heapreplace(h, x)` | pop then push, O(log n) |
| `heappushpop(h, x)` | push then pop, O(log n) |
| `nlargest(k, it)` | O(n log(k + 1)) for 1 ≤ k ≤ n; implementation may choose max or sorting |

Practical details:

- **Max-heaps**: before Python 3.14, negate the keys (`heappush(h, -x)`). Python 3.14 added `heapify_max`, `heappush_max`, `heappop_max` and friends.
- **Priorities with payloads**: push tuples `(priority, item)`. If two priorities tie, Python compares the items, which fails for objects that don't support `<`. Add a counter: `(priority, next(counter), item)`. This also makes ties first-in-first-out.
- **Changing a priority** ("decrease-key") is not supported. The usual trick is **lazy deletion**: push a new entry and mark the old one as removed, skipping stale entries when they are popped. Dijkstra's algorithm in Python is normally written this way.

## Pattern: top-k

"Find the k largest of n items" (top 10 search results, the 100 busiest IPs in a log). Sorting is O(n log n). Better: keep a **min-heap of size k** holding the best k seen so far. Its root is the *weakest* of the current top k, so each new item only needs comparing with the root.

```python
import heapq

def top_k(nums, k):
    if not isinstance(k, int) or k < 0:
        raise ValueError("k must be >= 0")
    if k == 0:
        return []
    h = []
    for x in nums:
        if len(h) < k:
            heapq.heappush(h, x)
        elif x > h[0]:
            heapq.heapreplace(h, x)
    return sorted(h, reverse=True)

top_k([5, 1, 9, 3, 7, 9, 2, 8], 3)
# [9, 9, 8]
```

For 1 ≤ k ≤ n, cost is O(n log(k + 1)) time including final sorting, and O(k) memory. Larger k returns all n items; k = 0 returns immediately. With n = 10⁹ log lines and k = 100, that is about 7 heap levels per item instead of 30, and it works on a stream that never fits in memory. `heapq.nlargest` does this for you.

> [!tip] Min-heap for the largest, max-heap for the smallest
> It feels backwards, but for the k **largest** you want quick access to the **smallest** of your keepers, because that is the one a newcomer must beat.

If all the data is in memory and you only need the k-th element, **quickselect** finds it in expected O(n), but it does not stream and reorders the array.

## Pattern: k-way merge

Merge k sorted lists (sorted runs from an external sort, per-shard query results, SSTables in LSM-tree compaction). Put the head of each list in a min-heap; repeatedly pop the smallest and push the next item from the same list.

```python
def merge_k(lists):
    h = []
    for i, lst in enumerate(lists):
        if lst:
            h.append((lst[0], i, 0))
    heapq.heapify(h)
    out = []
    while h:
        val, i, j = heapq.heappop(h)
        out.append(val)
        j += 1
        if j < len(lists[i]):
            nxt = (lists[i][j], i, j)
            heapq.heappush(h, nxt)
    return out

merge_k([[1, 4, 9], [2, 3, 10], [5]])
# [1, 2, 3, 4, 5, 9, 10]
```

The heap never holds more than k items, so with N items in total the cost is O(k + N log(k + 1)), including scanning empty input lists, with O(k) heap space plus O(N) returned output. Merging the lists pairwise one after another would cost up to O(N·k). `heapq.merge` is a lazy version of this.

## Beyond binary heaps

- **d-ary heaps** (4-ary is common) are shallower, which makes push cheaper and improves cache use, at the cost of more comparisons per sift-down level.
- Fibonacci heaps support amortized O(1) decrease-key and O(log n) delete-min, giving O(E + V log V) for Dijkstra with suitable handles and nonnegative edge weights. Ordinary pairing heaps do not share this combined constant-amortized decrease-key guarantee; their analysis is different. Benchmark concrete implementations before choosing.
- Real uses: OS timer queues, Go's `container/heap`, Java's `PriorityQueue` (a binary heap), job schedulers, and the event queue in network simulators.

## Key takeaways
- A binary heap is a complete tree with each parent ≤ its children, stored in an array with `2i+1`, `2i+2` and `(i−1)//2`.
- Push sifts up and pop sifts down (swapping with the smaller child); both are O(log n). Peek is O(1).
- Bottom-up heapify is O(n) because most nodes are near the bottom and sift down only a short distance.
- `heapq` is a min-heap on a list; use tuples with a counter for ties and lazy deletion for priority changes.
- For 1 ≤ k ≤ n, top-k takes O(n log(k + 1)); k-way merge takes O(k + N log(k + 1)), including empty-list scanning.

## Further reading
- [Binary heap — Wikipedia](https://en.wikipedia.org/wiki/Binary_heap)
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [Priority Queues — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/24pq/)
- [K-way merge algorithm — Wikipedia](https://en.wikipedia.org/wiki/K-way_merge_algorithm)
- [Heap visualisation — VisuAlgo](https://visualgo.net/en/heap)
