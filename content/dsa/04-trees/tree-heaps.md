---
id: tree-heaps
title: Heaps and priority queues
level: intermediate
minutes: 14
summary: The binary heap's array layout, sift up and sift down, why heapify is O(n), Python's heapq, and the top-k and k-way merge patterns.
---

Many problems only ever need the **smallest** (or largest) item: the next job to run, the nearest unvisited city in Dijkstra's algorithm, the earliest timer to fire, the next event in a simulation. A BST can do that, but it keeps far more order than you need.

A **priority queue** is the abstract data type for this job: `push(item)`, `pop_min()` and `peek()`. The standard implementation is the **binary heap**. For a heap of n items it gives O(log n) push and pop (work growing with the logarithm of n, about 20 steps for a million items) and O(1) peek (a fixed cost), stored with implicit parent/child indices rather than tree-link pointers. Python lists still store references to their elements. Costs assume constant-time comparisons; dynamic-array resizing makes push/pop bounds amortized when allocation costs are included.

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
```

The parent and children of any slot are found by arithmetic on its index:

```formula
i_parent = ⌊(i − 1) / 2⌋
i_left = 2 × i + 1
i_right = 2 × i + 2
i_left = 2 × 1 + 1 = 3
i_parent = ⌊(7 − 1) / 2⌋ = 3
where
i: the index (0-based position) of an item in the array; i_parent applies only when i > 0
i_parent: the index of that item's parent
i_left: the index of its left child, if that index is less than the heap size
i_right: the index of its right child, if that index is less than the heap size
⌊ ⌋: floor: round down to a whole number, so ⌊2.5⌋ = 2
In words: the children of slot i are at 2i + 1 and 2i + 2, and the parent is at (i − 1) halved and rounded down.
```

So the 3 at index 1 has children at indices 3 and 4 (4 and 8), and the 9 at index 7 has its parent at index 3 (the 4). In the Python code below, the parent index is `(i - 1) // 2`, where `//` divides and rounds down.

Avoiding explicit tree links saves their storage. The array of slots is contiguous, though referenced payload objects need not be; actual cache behaviour depends on layout and access patterns.

The second half of the array is all **leaves**:

```formula
⌊n / 2⌋ ≤ i ≤ n − 1
L = ⌈n / 2⌉
L = ⌈8 / 2⌉ = 4
where
n: the number of items in the heap (at least 1)
i: the index of a leaf; every index in this range is a leaf, and no other index is
L: the number of leaves
⌊ ⌋: floor: round down to a whole number
⌈ ⌉: ceiling: round up to a whole number, so ⌈4.5⌉ = 5
≤: is at most
In words: in an array heap of n items, the leaves are exactly the last ⌈n/2⌉ slots, starting at index ⌊n/2⌋.
```

In the 8-item example, indices 4 to 7 (values 8, 7, 6 and 9) are leaves: index 4's left child would be at 9, past the end.

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

Pushing 0 into the heap above: it lands at index 8 (child of 4), swaps with 4, then 3, then 1, and becomes the new root. There is at most one swap per level, and a complete tree is short:

```formula
S ≤ ⌊log_2(n)⌋
S ≤ ⌊log_2(9)⌋ = ⌊3.17⌋ = 3
where
S: the number of swaps one sift-up makes
n: the number of items in the heap after the push; 9 in the example
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
⌊ ⌋: floor: round down to a whole number
⌊log_2(n)⌋: the height of a complete binary tree with n nodes, in edges
In words: a sift-up can climb at most the height of the heap, which is the base-2 logarithm of its size rounded down.
```

Pushing 0 made exactly 3 swaps, the most possible. A million-item heap needs at most 19, so push is **O(log n)**.

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

Swapping with the **smaller** child matters: that child becomes the parent of the other, so it must be the smaller of the two. Pop also makes at most one swap per level, the same height limit as push, so for n items it is also **O(log n)**.

> [!warning] Heaps are not sorted
> Only `a[0]` is guaranteed to be the minimum. `a[1]` is not necessarily the second smallest (in the example it is 3, but 2 is smaller), and iterating over a heap list does not give sorted order. Popping repeatedly does.

## Heapify in O(n)

Given n unsorted items, you could push them one at a time. Each push can climb the full height, so in the worst case:

```formula
W ≤ n × ⌊log_2(n)⌋
W ≤ 10^6 × 19 = 1.9 × 10^7
where
W: the total swaps for building a heap by n separate pushes, in the worst case
n: the number of items; 10^6 (a million) in the example
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n; log_2(10^6) ≈ 19.93
⌊ ⌋: floor: round down to a whole number
In words: n pushes, each climbing at most the heap's height, cost up to about n × log_2(n) swaps.
```

That is O(n log n): n multiplied by log n. There is a faster way. Treat the array as a complete tree already, and sift down every **non-leaf** from the bottom up:

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

The cost of sifting down a node is at most its **height**, and most nodes have tiny heights. A rigorous bound counts nodes able to move down at least a given number of levels: at most half the nodes can move one level, a quarter two levels, an eighth three, and so on. Summing those possible levels gives:

```formula
S ≤ ⌊n/2⌋ + ⌊n/4⌋ + ⌊n/8⌋ + …
S < n × (1/2 + 1/4 + 1/8 + …) = n
S ≤ 4 + 2 + 1 = 7 < 8
where
S: the total number of swaps bottom-up heapify makes
n: the number of items; 8 in the last line, the trace above
j: a number of levels (1, 2, 3, …); at most ⌊n/2^j⌋ nodes have height at least j, and each such node can contribute a swap at its j-th level
⌊ ⌋: floor: round down to a whole number
…: "and so on": the terms keep halving until they reach 0
In words: half the nodes can move down at least one level, a quarter at least two, an eighth at least three, and those halving counts add up to less than n.
```

The trace above made 0 + 1 + 2 + 3 = 6 swaps, within the bound of 7. For the shown sift-down algorithm, this bounds swaps by n and key comparisons by 2n (two child comparisons per swap level); loop and index checks are additional constant work per step. Pushing one at a time is slower because new items arrive at the *bottom*, the level with the most nodes, and each may climb the full height.

The intuition: sift-down costs are cheap where nodes are plentiful (the bottom) and expensive only where they are rare (the top). Sift-up is the reverse.

### Heapsort

Heapify, then repeatedly swap the root with the last item and sift down over a shrinking prefix. That is **heapsort**: for n items, O(n log n) worst case (n pops, each sifting down at most the heap's height), O(1) extra memory, but not stable and with poor cache locality (it jumps between i and 2i), which can affect practical performance. One use is the worst-case fallback inside **introsort** (the usual implementation of C++ `std::sort`), which switches to heapsort if quicksort recurses too deeply.

## heapq in Python

Python's `heapq` module implements a **min-heap on a plain list**. There is no heap class.

Here n is the number of items in the heap (or in the input, for `heapify` and `nlargest`), and k is how many items you ask for.

| Function | Cost |
|---|---|
| `heappush(h, x)` | O(log n) |
| `heappop(h)` | O(log n) |
| `h[0]` (peek) | O(1) |
| `heapify(h)` | O(n), in place |
| `heapreplace(h, x)` | pop then push, O(log n) |
| `heappushpop(h, x)` | push then pop, O(log n) |
| `nlargest(k, it)` | O(n log(k + 1)) when k is between 1 and n; implementation may choose max or sorting |

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

Each item costs one comparison with the root, and at most one replace that sifts through a heap of only k items:

```formula
W ≈ n × log_2(k + 1)
log_2(100 + 1) ≈ 6.7
log_2(10^9) ≈ 29.9
where
W: the total work for top-k over the whole input, counted in heap levels sifted
n: the number of input items; 10^9 (a billion) log lines in the example
k: how many of the largest items you want, between 1 and n; 100 in the example
log_2(x): the base-2 logarithm of x: the power you raise 2 to in order to get x; it counts the levels in a heap of x items
≈: approximately equal to
In words: each of the n items costs at most about log_2(k + 1) heap levels, because the heap never grows beyond k items.
```

So for 1 ≤ k ≤ n (k at least 1 and at most n), cost is O(n log(k + 1)) time including final sorting, and O(k) memory. The + 1 keeps the logarithm above zero when k = 1. Larger k returns all n items; k = 0 returns immediately. With a billion log lines and k = 100, that is about 7 heap levels per item instead of the 30 a heap of all n items would need, and it works on a stream that never fits in memory. `heapq.nlargest` does this for you.

> [!tip] Min-heap for the largest, max-heap for the smallest
> It feels backwards, but for the k **largest** you want quick access to the **smallest** of your keepers, because that is the one a newcomer must beat.

If all n items are in memory and you only need the k-th element, **quickselect** finds it in expected O(n), but it does not stream and reorders the array.

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

The heap never holds more than k items, so each of the N output items costs one pop and at most one push through a small heap:

```formula
W ≈ k + N × log_2(k + 1)
W ≈ 3 + 7 × log_2(3 + 1)
W ≈ 3 + 7 × 2 = 17
W_pair ≈ N × k
where
W: the work for the heap merge, counted in list visits plus heap levels sifted
k: the number of sorted input lists; 3 in the example above
N: the total number of items across all the lists; 7 in the example
log_2(k + 1): the base-2 logarithm of k + 1, about the number of levels in a heap of k items
W_pair: the work, up to a constant factor, for merging the lists one after another instead
≈: approximately equal to (these are growth estimates, not exact counts)
In words: the heap merge visits every list once and then pays about log_2(k) heap levels per output item; merging lists one by one can re-copy items about k times.
```

So the heap merge costs O(k + N log(k + 1)), including scanning empty input lists, with O(k) heap space plus O(N) returned output. Merging the lists pairwise one after another would cost up to O(N·k), N times k. `heapq.merge` is a lazy version of this.

## Beyond binary heaps

- **d-ary heaps** (4-ary is common) are shallower, which makes push cheaper and improves cache use, at the cost of more comparisons per sift-down level.
- Fibonacci heaps support amortised O(1) decrease-key and O(log n) delete-min (for n items in the heap), giving O(E + V log V) for Dijkstra on a graph with V vertices and E edges, with suitable handles and nonnegative edge weights. Ordinary pairing heaps do not share this combined constant-amortized decrease-key guarantee; their analysis is different. Benchmark concrete implementations before choosing.
- Real uses: OS timer queues, Go's `container/heap`, Java's `PriorityQueue` (a binary heap), job schedulers, and the event queue in network simulators.

## Key takeaways
- A binary heap is a complete tree with each parent less than or equal to its children, stored in an array with children at `2*i + 1` and `2*i + 2` and the parent at `(i - 1) // 2`.
- Push sifts up and pop sifts down (swapping with the smaller child); both are O(log n) for n items. Peek is O(1).
- Bottom-up heapify is O(n) because most nodes are near the bottom and sift down only a short distance.
- `heapq` is a min-heap on a list; use tuples with a counter for ties and lazy deletion for priority changes.
- Top-k of n items (k from 1 to n) takes O(n log(k + 1)); merging k lists holding N items in total takes O(k + N log(k + 1)), including empty-list scanning.

## Further reading
- [Binary heap — Wikipedia](https://en.wikipedia.org/wiki/Binary_heap)
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [Priority Queues — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/24pq/)
- [K-way merge algorithm — Wikipedia](https://en.wikipedia.org/wiki/K-way_merge_algorithm)
- [Heap visualisation — VisuAlgo](https://visualgo.net/en/heap)
