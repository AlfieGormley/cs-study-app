---
id: sort-heapsort-lower-bound
title: Heapsort and the comparison-sort lower bound
level: intermediate
minutes: 13
summary: How heapsort gets O(n log n) worst case in O(1) space, why it is slower than quicksort in practice, and the decision-tree proof that no comparison sort can beat Ω(n log n).
---

So far we have two O(n log n) sorts, each with a catch. Merge sort is guaranteed n log n but needs O(n) extra memory. Quicksort is in place but can go quadratic. **Heapsort** removes both catches: O(n log n) in the worst case, with O(1) extra space.

Then we will ask a deeper question: could some cleverer algorithm do better than n log n? The answer is no, for any algorithm that sorts by comparing elements, and the proof is one of the most elegant in computer science.

## Heapsort

Heapsort is selection sort with a better data structure. Selection sort spends O(n) finding the maximum each round. A **binary max-heap** (covered in the trees module) finds and removes the maximum in O(log n).

Recall the array layout: the node at index `i` has children at `2i + 1` and `2i + 2`, and every parent is at least as large as its children. So the maximum is always at index 0.

The algorithm has two phases:

1. **Build** a max-heap in place from the array.
2. **Repeatedly** swap the root (the maximum) with the last element of the heap, shrink the heap by one, and sift the new root down to restore the heap property.

The sorted part grows from the right, exactly like selection sort.

```python
def sift_down(a, i, n):
    while True:
        big = i
        l, r = 2*i + 1, 2*i + 2
        if l < n and a[l] > a[big]:
            big = l
        if r < n and a[r] > a[big]:
            big = r
        if big == i:
            return
        a[i], a[big] = a[big], a[i]
        i = big

def heapsort(a):
    n = len(a)
    # phase 1: bottom-up heap build
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
    # phase 2: extract max n-1 times
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down(a, 0, end)
```

### Trace

Input `[4, 10, 3, 5, 1]`.

**Phase 1.** Start at the last parent, index `5 // 2 - 1 = 1`.

```
i=1: 10 vs children 5, 1 -> fine
i=0: 4 vs children 10, 3 -> swap 10
     [10, 4, 3, 5, 1]
     4 vs children 5, 1 -> swap 5
     [10, 5, 3, 4, 1]   max-heap
```

**Phase 2.** Swap root to the end, sift down, repeat.

```
swap 10<->1, sift: [5, 4, 3, 1 | 10]
swap 5<->1,  sift: [4, 1, 3 | 5, 10]
swap 4<->3,  sift: [3, 1 | 4, 5, 10]
swap 3<->1:        [1 | 3, 4, 5, 10]
```

### Why the build phase is O(n), not O(n log n)

Inserting n elements one at a time would cost O(n log n). The bottom-up build is cheaper because most nodes are near the bottom, where sift-down is short. About n/2 nodes are leaves (cost 0), n/4 are one level up (cost at most 1), n/8 cost at most 2, and so on:

```
sum over h of (n / 2^(h+1)) * h  <=  n
```

That series converges, so building the heap is O(n). The extraction phase does n−1 sift-downs of O(log n) each, so heapsort overall is **Θ(n log n) in the worst case**.

### Properties

- **In-place**, O(1) extra memory (the iterative sift-down above needs no stack).
- **Worst case O(n log n)**, with no bad inputs to defend against.
- **Not stable.** The root swap sends elements across the array, past their equals.
- **Not adaptive.** A sorted input still costs n log n (in fact, a sorted ascending array is not a max-heap, so it gets rearranged fully).

### Why it loses to quicksort in practice

On paper heapsort looks strictly better than quicksort. Heapsort can be slower on large arrays, but the ratio depends on implementation, data and hardware. Memory access and comparison counts help explain why:

- Sift-down jumps from index `i` to `2i + 1`. Near the root, frequently reused nodes may remain cached. Deeper in the heap, larger index gaps and less reuse can hurt locality; a different cache line does not by itself imply a cache miss.
- Quicksort's partition scans memory sequentially, which caches and prefetchers love.
- Heapsort also does more comparisons: around 2n log₂ n for the standard version, versus about 1.39 n log₂ n for randomised quicksort.

So heapsort is used where its guarantees matter more than its speed:

- As the **fallback inside introsort** (C++ `std::sort`, .NET), triggered only when quicksort's recursion goes too deep.
- In the **Linux kernel**, whose `sort()` in `lib/sort.c` is a heapsort: no recursion, no allocation and no worst-case input to exploit.
- In embedded and real-time systems where a fixed upper bound on time and memory matters most.

## The lower bound for comparison sorts

Merge sort, heapsort and good quicksorts are all n log n. Is that a coincidence of the algorithms we happened to find, or a law?

It is a law, for **comparison sorts**: algorithms that learn about the input only by asking "is `a[i] < a[j]`?". That includes every sort so far.

### The decision tree

Model any comparison sort on inputs of size n as a binary tree:

- Each internal node is a comparison, such as `a[1] < a[2]?`.
- Each branch is an answer (yes or no).
- Each leaf is a final answer: the permutation that sorts the input.

Running the algorithm on a particular input traces one path from root to leaf. The number of comparisons is the length of that path.

Here is a decision tree for sorting three elements `a, b, c`:

```
              a<b?
          yes/    \no
         b<c?      a<c?
       y/   \n    y/   \n
    a,b,c  a<c?  b,a,c  b<c?
          y/  \n       y/  \n
       a,c,b c,a,b  b,c,a  c,b,a
```

Six leaves, one per ordering. The worst-case path has 3 comparisons.

### The counting argument

1. There are **n!** possible orderings of n distinct elements. The algorithm must be able to output each one, so the tree needs **at least n! leaves**. (If two orderings led to the same leaf, the algorithm would rearrange them identically and get one of them wrong.)
2. A binary tree of height h has **at most 2ʰ leaves**.
3. So 2ʰ ≥ n!, which means **h ≥ log₂(n!)**.

The height is the worst-case number of comparisons. Now bound log₂(n!). The largest n/2 factors of n! are each at least n/2, so:

```
n! >= (n/2)^(n/2)
log2(n!) >= (n/2) log2(n/2)
         = Ω(n log n)
```

Stirling's approximation is sharper: log₂(n!) ≈ n log₂ n − 1.44n. So **every comparison sort needs Ω(n log n) comparisons in the worst case**. Merge sort and heapsort are **asymptotically optimal**.

The same argument works for the **average** case: in any binary tree with N leaves, the uniformly weighted average leaf depth is at least log₂ N. Averaging over all distinct-key permutations gives Ω(n log n), including expected comparisons of correct randomized sorts. This is not a bound for every nonuniform input distribution.

### Real numbers

| n | n! | min worst-case compares |
|---|---|---|
| 3 | 6 | 3 |
| 4 | 24 | 5 |
| 5 | 120 | 7 |
| 1,000,000 | huge | ≈ 18.5 million |

For n = 10⁶, n log₂ n ≈ 19.9 million, so merge sort is within about 8% of the absolute minimum. There is little left to win on comparison counts; real-world gains come from cache behaviour, branch prediction and exploiting existing order.

> [!note] Exact optimal sorting is hard
> For n = 5 the bound says 7 comparisons. Plain merge sort needs 8 in the worst case. The Ford–Johnson "merge insertion" algorithm achieves 7, but finding the true minimum for every n is an open problem.

### What the bound does not say

- **It only covers comparisons.** If you can look inside the keys (use an integer as an array index, or inspect digits), the decision-tree model does not apply. That is how counting sort and radix sort run in linear time (next lesson).
- **It is about the worst or average case.** An adaptive sort can be O(n) on already sorted input. The bound applies to the set of all n! inputs; a more refined version says you need about log₂(number of possible inputs) comparisons, which is why sorting data with few runs or few distinct values can be faster.
- **It has consequences elsewhere.** Anything that would let you sort is also Ω(n log n). For example, building a binary search tree from n items and reading it in order sorts them, so building a comparison-based BST from arbitrary distinct unsorted keys has Ω(n log n) worst-case cost. Locating one of n + 1 insertion positions with Boolean order tests requires at least ⌈log₂(n + 1)⌉ tests in the worst case, achieved by lower-bound binary search.

## Key takeaways
- Heapsort builds a max-heap in O(n) and extracts the maximum n−1 times: O(n log n) worst case, O(1) extra space, not stable.
- Its less sequential access pattern can hurt performance compared with quicksort; the speed ratio must be measured. It is often used as a safety net (introsort, the Linux kernel) rather than a default.
- A comparison sort is a decision tree with at least n! leaves, so its height is at least log₂(n!) = Θ(n log n).
- This makes merge sort and heapsort asymptotically optimal; beating n log n requires using more than comparisons.

## Further reading
- [Heapsort — Wikipedia](https://en.wikipedia.org/wiki/Heapsort)
- [Priority Queues and heapsort — Algorithms, 4th ed.](https://algs4.cs.princeton.edu/24pq/)
- [Comparison sort (lower bound section) — Wikipedia](https://en.wikipedia.org/wiki/Comparison_sort)
- [Decision tree model — Wikipedia](https://en.wikipedia.org/wiki/Decision_tree_model)
- [Stirling's approximation — Wikipedia](https://en.wikipedia.org/wiki/Stirling%27s_approximation)
