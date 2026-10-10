---
id: sort-heapsort-lower-bound
title: Heapsort and the comparison-sort lower bound
level: intermediate
minutes: 13
summary: How heapsort gets O(n log n) worst case in O(1) space, why it is slower than quicksort in practice, and the decision-tree proof that no comparison sort can beat Ω(n log n).
---

Throughout this lesson, n is the number of elements being sorted, and log n is the base-2 logarithm of n: how many times n can be halved before reaching 1 (about 20 for a million). O, Θ and Ω are Big O, Big Theta and Big Omega: growth rates of at most, exactly and at least, ignoring constant factors.

So far we have two O(n log n) sorts, each with a catch. Merge sort is guaranteed n log n but needs O(n) extra memory. Quicksort is in place but can go quadratic. **Heapsort** removes both catches: O(n log n) in the worst case, with O(1) extra space.

Then we will ask a deeper question: could some cleverer algorithm do better than n log n? The answer is no, for any algorithm that sorts by comparing elements, and the proof is one of the most elegant in computer science.

## Heapsort

Heapsort is selection sort with a better data structure. Selection sort spends O(n) finding the maximum each round. A **binary max-heap** (covered in the trees module) finds and removes the maximum in O(log n).

Recall the array layout. The heap is a tree stored level by level in the array, with no pointers; the position of a node's children is computed from its own index:

```formula
c_L = 2 × i + 1
c_R = 2 × i + 2
p = ⌊(i − 1) / 2⌋
c_L(1) = 3,  c_R(1) = 4,  p(1) = 0
where
i: the index (position, counting from 0) of a node in the array; the last line uses i = 1
c_L: the index of its left child
c_R: the index of its right child
p: the index of its parent (for any node except the root, which is at index 0)
⌊ ⌋: the floor: round down to a whole number
In words: the children of the node at position i sit at 2i + 1 and 2i + 2, so the tree needs no pointers.
```

Every parent is at least as large as its children (the **heap property**). So the maximum is always at index 0.

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

**Phase 1.** Start at the last node that has a child; every node after it is a leaf, which is already a valid one-element heap:

```formula
i_last = ⌊n / 2⌋ − 1
i_last = ⌊5 / 2⌋ − 1 = 2 − 1 = 1
where
i_last: the index of the last parent in the array, where the bottom-up build starts
n: the number of elements in the heap; here 5
⌊ ⌋: the floor: round down to a whole number (Python's // does this)
In words: the second half of the array is all leaves, so building starts just before the halfway point and works back to index 0.
```


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

Inserting n elements one at a time would cost O(n log n). The bottom-up build is cheaper because most nodes are near the bottom, where sift-down is short. About half the nodes are leaves (cost 0), a quarter are one level up (cost at most 1), an eighth cost at most 2, and so on:

```formula
W ≤ Σ_h (n / 2^{h+1}) × h
W ≤ n × (1/4 + 2/8 + 3/16 + 4/32 + …)
W ≤ n × 1 = n
where
W: the total number of sift-down swaps the bottom-up build can make
n: the number of elements in the heap
h: the height of a node: how many levels it sits above the bottom (0 for a leaf)
Σ_h: "add up the following for every height h = 0, 1, 2, …"
n / 2^{h+1}: about how many nodes have height h (half the nodes have height 0, a quarter height 1, and so on)
…: "and so on", the terms getting ever smaller
≤: less than or equal to
In words: many nodes with short sift-downs and few nodes with long ones add up to at most about one swap per element.
```

The series in brackets converges to 1, so building the heap is O(n). For a million elements that is at most about a million swaps, not 20 million. The extraction phase does n−1 sift-downs of O(log n) each, so heapsort overall is **Θ(n log n) in the worst case**.

### Properties

- **In-place**, O(1) extra memory (the iterative sift-down above needs no stack).
- **Worst case O(n log n)**, with no bad inputs to defend against.
- **Not stable.** The root swap sends elements across the array, past their equals.
- **Not adaptive.** A sorted input still costs n log n (in fact, a sorted ascending array is not a max-heap, so it gets rearranged fully).

### Why it loses to quicksort in practice

On paper heapsort looks strictly better than quicksort. Heapsort can be slower on large arrays, but the ratio depends on implementation, data and hardware. Memory access and comparison counts help explain why:

- Sift-down jumps from index `i` to `2i + 1`. Near the root, frequently reused nodes may remain cached. Deeper in the heap, larger index gaps and less reuse can hurt locality; a different cache line does not by itself imply a cache miss.
- Quicksort's partition scans memory sequentially, which caches and prefetchers love.
- Heapsort also does more comparisons:

```formula
C_heap ≈ 2 × n × log_2(n)
C_quick ≈ 1.39 × n × log_2(n)
where
C_heap: the comparisons standard heapsort makes, roughly (each sift-down step compares a node with both of its children)
C_quick: the expected comparisons of randomised quicksort
n: the number of elements
log_2(n): the base-2 logarithm of n; about 20 for a million
≈: approximately equal to (leading term only)
In words: heapsort makes roughly 45% more comparisons than randomised quicksort (2 / 1.39 ≈ 1.44), around 40 million versus 28 million for a million elements.
```


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

1. There are **n!** (n factorial: n × (n − 1) × … × 2 × 1) possible orderings of n distinct elements. The algorithm must be able to output each one, so the tree needs **at least n! leaves**. (If two orderings led to the same leaf, the algorithm would rearrange them identically and get one of them wrong.)
2. A binary tree of height h (its longest root-to-leaf path) has **at most 2ʰ leaves**, because the number of nodes can at most double at each level.
3. Put the two together:

```formula
2^h ≥ L ≥ n!
h ≥ log_2(n!)
log_2(3!) = log_2(6) ≈ 2.58
h ≥ ⌈2.58⌉ = 3
where
h: the height of the decision tree, which is the worst-case number of comparisons; a whole number
L: the number of leaves in the tree
n!: n factorial, n × (n − 1) × … × 2 × 1: the number of possible orderings of n distinct elements (3! = 6)
2^h: h copies of 2 multiplied together, the most leaves a binary tree of height h can have
log_2: the base-2 logarithm, which undoes "2 to the power": log_2(8) = 3
n: the number of elements being sorted; 3 in the example lines
⌈ ⌉: the ceiling: round up to the next whole number
≥: greater than or equal to
≈: approximately equal to
In words: a tree tall enough to hold one leaf per possible ordering must have height at least log_2(n!), so some input needs that many comparisons.
```

For three elements that is 3 comparisons, exactly what the tree above uses. The height is the worst-case number of comparisons, so this is the bound. Now estimate log₂(n!). The largest half of the factors of n! are each at least n/2, so:

```formula
n! ≥ (n / 2)^{n/2}
log_2(n!) ≥ (n / 2) × log_2(n / 2)
log_2(n!) = Ω(n × log n)
where
n!: n factorial, the product n × (n − 1) × … × 1
n: the number of elements
(n / 2)^{n/2}: n/2 copies of n/2 multiplied together
log_2: the base-2 logarithm
log: the logarithm (the base does not matter inside Ω)
Ω: Big Omega: grows at least this fast, up to a constant factor
≥: greater than or equal to
In words: throwing away the smaller half of the factors and shrinking the rest to n/2 still leaves something that grows like n log n.
```

**Stirling's approximation**, a standard estimate of n!, is sharper:

```formula
log_2(n!) ≈ n × log_2(n) − 1.44 × n
log_2(10^6 !) ≈ 1.993 × 10^7 − 1.44 × 10^6
log_2(10^6 !) ≈ 1.85 × 10^7
where
log_2(n!): the base-2 logarithm of n factorial: the minimum worst-case number of comparisons to sort n distinct elements
n: the number of elements; here a million (10^6)
log_2(n): the base-2 logarithm of n; log_2(10^6) ≈ 19.93
1.44: log_2(e), where e ≈ 2.718 is the base of natural logarithms; it comes from Stirling's formula
10^6: ten to the power 6, a million; 10^7 is ten million
≈: approximately equal to (lower-order terms dropped)
In words: the true minimum is n log_2 n minus about 1.44 comparisons per element: about 18.5 million for a million elements.
```

So **every comparison sort needs Ω(n log n) comparisons in the worst case**. Merge sort and heapsort are **asymptotically optimal**: no comparison sort beats them by more than a constant factor.

The same argument works for the **average** case. A binary tree with many leaves cannot have all of them shallow:

```formula
d_avg ≥ log_2(N)
N ≥ n!  ⇒  d_avg ≥ log_2(n!)
where
d_avg: the average depth of a leaf, with every leaf weighted equally: the average number of comparisons
N: the number of leaves in the binary tree
n!: n factorial, the number of orderings of n distinct elements
n: the number of elements
log_2: the base-2 logarithm
⇒: "which means"
≥: greater than or equal to
In words: a binary tree with N leaves has average leaf depth at least log_2(N), so averaged over all n! orderings a comparison sort still needs about log_2(n!) comparisons.
```

Averaging over all distinct-key permutations gives Ω(n log n), including expected comparisons of correct randomized sorts. This is not a bound for every nonuniform input distribution.

### Real numbers

The last column below is log₂(n!) rounded up: for n = 4 it is log₂ 24 ≈ 4.58, rounded up to 5.

| n | n! | min worst-case compares |
|---|---|---|
| 3 | 6 | 3 |
| 4 | 24 | 5 |
| 5 | 120 | 7 |
| 1,000,000 | huge | ≈ 18.5 million |

How close does merge sort get? Use the exact worst-case count for top-down merge sort from lesson 2:

```formula
C_w = n × ⌈log_2(n)⌉ − 2^{⌈log_2(n)⌉} + 1
C_w = 10^6 × 20 − 2^20 + 1
C_w = 18951425 ≈ 1.895 × 10^7
r = C_w / log_2(n!)
r ≈ 1.895 × 10^7 / (1.849 × 10^7) ≈ 1.025
where
C_w: the most comparisons top-down merge sort makes on any input of n elements
n: the number of elements, a million (10^6)
log_2(n): the base-2 logarithm of n, about 19.93 here
⌈ ⌉: the ceiling: round up to a whole number, so ⌈19.93⌉ = 20
2^20: 20 copies of 2 multiplied together, 1,048,576
log_2(n!): the minimum worst-case comparisons any comparison sort needs, about 18.49 million here
r: the ratio of merge sort's worst case to that minimum
10^6: ten to the power 6, a million; 10^7 is ten million
≈: approximately equal to
In words: in its worst case, merge sort uses only about 2.5% more comparisons than the theoretical minimum for a million elements.
```

So merge sort's worst case is within about 3% of the absolute minimum (the rough estimate n log₂ n would put it within about 8%). There is little left to win on comparison counts; real-world gains come from cache behaviour, branch prediction and exploiting existing order.

> [!note] Exact optimal sorting is hard
> For n = 5 the bound says 7 comparisons. Plain merge sort needs 8 in the worst case. The Ford–Johnson "merge insertion" algorithm achieves 7, but finding the true minimum for every n is an open problem.

### What the bound does not say

- **It only covers comparisons.** If you can look inside the keys (use an integer as an array index, or inspect digits), the decision-tree model does not apply. That is how counting sort and radix sort run in linear time (next lesson).
- **It is about the worst or average case.** An adaptive sort can be O(n) on already sorted input. The bound applies to the set of all n! inputs; a more refined version says you need about log₂(number of possible inputs) comparisons, which is why sorting data with few runs or few distinct values can be faster.
- **It has consequences elsewhere.** Anything that would let you sort is also Ω(n log n). For example, building a binary search tree from n items and reading it in order sorts them, so building a comparison-based BST from arbitrary distinct unsorted keys has Ω(n log n) worst-case cost. Locating one of n + 1 insertion positions with Boolean order tests requires a matching minimum number of tests in the worst case (formula below), achieved by lower-bound binary search.

```formula
q ≥ ⌈log_2(n + 1)⌉
q ≥ ⌈log_2(1024)⌉ = 10
where
q: the worst-case number of yes/no order tests needed to find where a new key belongs
n: the number of elements already in the sorted array; here 1,023, which leaves 1,024 possible insertion positions
log_2: the base-2 logarithm
⌈ ⌉: the ceiling: round up to the next whole number
≥: greater than or equal to
In words: each yes/no test can at best halve the possible positions, so choosing among n + 1 positions needs about log_2(n + 1) tests.
```

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
