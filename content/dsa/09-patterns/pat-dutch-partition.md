---
id: pat-dutch-partition
title: Partition the unknown region into three categories
level: basic
minutes: 4
sourceLesson: pat-two-pointers
summary: Dutch flag keeps known zero, one and two regions around an unknown region.
---

Here n is the input length. For the Dutch flag example every element must be 0, 1 or 2; the code sorts in place in one scan.

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
            # Move this zero into the known
            # zero region.
            a[lo], a[mid] = a[mid], a[lo]
            lo += 1
            mid += 1
        elif a[mid] == 1:
            mid += 1
        else:
            # The incoming value still needs
            # examining.
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
| Gather by category in place | Partition |
| Merge two sorted arrays | One pointer each |

## Pitfalls

- **Unsorted input.** Pair sum's move rule depends on sortedness. If the input isn't sorted, either sort it (O(n log n), and you lose original indices unless you sort `(value, index)` pairs) or use a hash map.
- **`lo < hi` vs `lo <= hi`.** Pair problems need two *distinct* elements, so stop when they meet. Dutch flag uses `mid <= hi` because the element at `hi` is still unknown.
- **Advancing after a swap from the right.** In partitioning, the element swapped in from the right is unexamined; advancing past it is the classic bug.
- **Duplicates in three sum.** Without skipping equal values you'll report the same triple many times.

## Recap of the pattern family
- Two pointers replace an O(n²) scan of pairs with O(n) by proving each move discards only useless pairs.
- Opposite ends suits sorted arrays and "choose two ends" problems: move the pointer that can't be part of a better answer.
- Same direction (read/write, fast/slow) does in-place filtering and linked-list tricks in O(1) space.
- Partitioning keeps regions with invariants; the Dutch flag sorts three values in one pass.
- Always be able to state the invariant or the reason a move is safe.

## Key takeaways
- Dutch flag keeps known zero, one and two regions around an unknown region.
- A value swapped from the right is unexamined, so do not advance the middle index.
- State the invariant behind a pointer move rather than applying a template blindly.

## Further reading
- [Two pointers — USACO Guide](https://usaco.guide/silver/two-pointers)
- [Dutch national flag problem — Wikipedia](https://en.wikipedia.org/wiki/Dutch_national_flag_problem)
- [Array cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/array/)
- [Dijkstra on the Dutch National Flag](https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD608.html)
