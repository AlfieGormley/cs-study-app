---
id: pat-two-pointers
title: Two pointers
level: basic
minutes: 12
summary: Using two indices that move through an array to replace a nested loop with a single pass, in three flavours (opposite ends, same direction and partitioning), with pair sum, container with most water, remove duplicates and the Dutch flag.
---

Many brute-force solutions look at every pair `(i, j)`: O(n²). The **two-pointer** pattern keeps two indices and moves each one only forwards (or only backwards), so each pointer makes O(n) moves and together they make O(n) moves. Two same-direction pointers can make nearly 2n moves. Costs below assume constant-time numeric operations and indexing.

It works when there is a rule that tells you, after looking at the current pair, which pointer can safely move: that some whole set of pairs can be discarded without checking them. Usually that rule comes from the array being **sorted**, or from an invariant you maintain about the region each pointer has passed.

There are three common flavours:

```
Opposite ends    lo ->        <- hi
Same direction   slow ->  fast ->
Partitioning     [ <p | =p | ?? | >p ]
```

## Opposite ends: pair sum in a sorted array

**Problem.** Given a sorted array and a target, find two elements that add up to the target.

Start with the smallest and largest elements. Compare their sum with the target:

- **Too small?** Among the two allowed inward moves, moving `lo` right can increase the sum. `a[lo]` paired with any other remaining element gives a sum no larger, so `a[lo]` can't be in any answer: discard it.
- **Too big?** Symmetrically, `a[hi]` paired with any other remaining element is too big: move `hi` left.

```python
def pair_sum_sorted(a, target):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        s = a[lo] + a[hi]
        if s == target:
            return lo, hi
        if s < target:
            lo += 1
        else:
            hi -= 1
    return None
```

Trace with `a = [1, 3, 4, 6, 8, 11]`, target 10:

```
lo hi  a[lo]+a[hi]  action
0  5   1+11=12      too big, hi--
0  4   1+8 = 9      too small, lo++
1  4   3+8 = 11     too big, hi--
1  3   3+6 = 9      too small, lo++
2  3   4+6 = 10     found (2, 3)
```

Each step discards one element for good, so at most n − 1 steps: O(n) time, O(1) space. Compare the hash-map version of two sum (lesson 1), which is expected O(n) under constant-time, well-distributed hashing but needs O(n) extra memory and works on unsorted input.

> [!tip] Three sum
> "Find all triples summing to 0" is: sort (O(n log n)), then for each `i`, run pair sum on the part after `i` with target `-a[i]`. That's O(n²) total for this algorithm, excluding integer bit costs. Skip equal neighbours to avoid duplicate triples.

## Opposite ends: container with most water

**Problem.** `h[i]` is a nonnegative height of a vertical line at position `i`. Choose two lines that, with the x-axis, hold the most water. Area = `(j - i) * min(h[i], h[j])`.

The array isn't sorted, so why do two pointers work? Start with the widest container (`lo = 0`, `hi = n - 1`). Suppose `h[lo] < h[hi]`. Any other container using `lo` with a partner inside the range:

- is **narrower** (the partner is closer), and
- has height at most `h[lo]` (the shorter line caps it).

So it can never beat the current one. Every pair involving `lo` is discarded in one move: advance `lo`. Move the **shorter** line; if heights tie, either endpoint can be discarded. For fewer than two lines, the code returns 0.

```python
def max_area(h):
    lo, hi = 0, len(h) - 1
    best = 0
    while lo < hi:
        width = hi - lo
        area = width * min(h[lo], h[hi])
        best = max(best, area)
        if h[lo] < h[hi]:
            lo += 1
        else:
            hi -= 1
    return best
```

For `[1, 8, 6, 2, 5, 4, 8, 3, 7]` the answer is 49: lines at positions 1 and 8, width 7, height `min(8, 7) = 7`.

> [!note] The proof is the pattern
> Two pointers are only correct when you can argue that the move discards nothing useful. If you can't say *why* a move is safe, you don't yet have a two-pointer solution; you have a guess.

## Same direction: remove duplicates in place

**Problem.** Given a sorted array, remove duplicates in place so each value appears once, and return the length of the distinct prefix. The list is not resized; ignore the tail after that prefix. Extra space must be O(1).

Use a **read pointer** `r` that scans every element and a **write pointer** `w` marking where the next kept element goes. The invariant: `a[0:w]` holds the distinct values seen so far, in order.

```python
def remove_dups(a):
    if not a:
        return 0
    w = 1          # a[0] is always kept
    for r in range(1, len(a)):
        if a[r] != a[w - 1]:
            a[w] = a[r]
            w += 1
    return w
```

```
a = [0, 0, 1, 1, 1, 2]
r=1 a[r]=0 == a[0]   skip
r=2 a[r]=1 != 0      a[1]=1, w=2
r=3 a[r]=1 == 1      skip
r=4 a[r]=1 == 1      skip
r=5 a[r]=2 != 1      a[2]=2, w=3
result: [0, 1, 2], length 3
```

The same read/write shape solves "move all zeros to the end", "remove all copies of value v" and "keep at most two of each value" (keep an item when `w < 2` or it differs from `a[w - 2]`).

Another same-direction variant is **fast and slow pointers** on a linked list: the slow pointer moves one step, the fast one two. Check equality after advancing: they eventually meet if there's a cycle (Floyd's algorithm). On an acyclic list, stop when fast cannot take another two-step advance; the chosen loop convention determines which middle node is returned for an even-length list.

## Partitioning: the Dutch national flag

**Problem.** An array contains only 0s, 1s and 2s. Sort it in one pass, in place. (Dijkstra posed it with the red, white and blue of the Dutch flag.)

Keep three pointers and four regions:

```
 0..lo-1  lo..mid-1  mid..hi   hi+1..
 [ 0s  ]  [  1s   ]  [unknown] [ 2s ]
```

Look at `a[mid]`, the first unknown element:

- **0:** swap it into the 0s region (`a[lo]`), advance `lo` and `mid`.
- **1:** already in place; advance `mid`.
- **2:** swap it with `a[hi]`, shrink `hi`. **Don't** advance `mid`: the element that just arrived from `hi` hasn't been examined yet.

```python
def sort_colours(a):
    lo, mid, hi = 0, 0, len(a) - 1
    while mid <= hi:
        if a[mid] == 0:
            a[lo], a[mid] = a[mid], a[lo]
            lo += 1
            mid += 1
        elif a[mid] == 1:
            mid += 1
        else:
            a[mid], a[hi] = a[hi], a[mid]
            hi -= 1
```

Why is it safe to advance `mid` after swapping with `lo`? If `lo < mid`, the swapped-in value comes from the known 1s region. If `lo == mid`, the swap is with itself and the current value has just been identified as 0. In either case advancing is safe.

Each step either advances `mid` or shrinks `hi`, so the unknown region shrinks every iteration: O(n) time, O(1) space. Three-way partitioning is also how quicksort copes with many duplicate keys.

## Recognising the pattern

| Cue | Flavour |
|---|---|
| Sorted array, find pair/triple | Opposite ends |
| Palindrome check | Opposite ends |
| Pick two ends to maximise | Opposite ends |
| In place, O(1) space, filter | Read/write |
| Linked list middle or cycle | Fast/slow |
| Group by category in place | Partition |
| Merge two sorted arrays | One pointer each |

## Pitfalls

- **Unsorted input.** Pair sum's move rule depends on sortedness. If the input isn't sorted, either sort it (O(n log n), and you lose original indices unless you sort `(value, index)` pairs) or use a hash map.
- **`lo < hi` vs `lo <= hi`.** Pair problems need two *distinct* elements, so stop when they meet. Dutch flag uses `mid <= hi` because the element at `hi` is still unknown.
- **Advancing after a swap from the right.** In partitioning, the element swapped in from the right is unexamined; advancing past it is the classic bug.
- **Duplicates in three sum.** Without skipping equal values you'll report the same triple many times.

## Key takeaways
- Two pointers replace an O(n²) scan of pairs with O(n) by proving each move discards only useless pairs.
- Opposite ends suits sorted arrays and "choose two ends" problems: move the pointer that can't be part of a better answer.
- Same direction (read/write, fast/slow) does in-place filtering and linked-list tricks in O(1) space.
- Partitioning keeps regions with invariants; the Dutch flag sorts three values in one pass.
- Always be able to state the invariant or the reason a move is safe.

## Further reading
- [Two pointers — USACO Guide](https://usaco.guide/silver/two-pointers)
- [Dutch national flag problem — Wikipedia](https://en.wikipedia.org/wiki/Dutch_national_flag_problem)
- [Array cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/array/)
