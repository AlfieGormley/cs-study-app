---
id: pat-sorted-pair-scan
title: Discard impossible pairs in sorted input
level: basic
minutes: 4
sourceLesson: pat-two-pointers
summary: Sortedness proves which endpoint cannot participate in a remaining answer.
---

Many brute-force solutions look at every pair of positions `(i, j)` in an array of n elements: roughly half the square of the input length in pairs, which is O(n²) work (the work grows with the square of n). The **two-pointer** pattern keeps two indices and moves each one only forwards (or only backwards), so each pointer makes O(n) moves and together they make O(n) moves. Two same-direction pointers can together make nearly twice as many moves as there are elements. Costs below assume constant-time numeric operations and indexing.

It works when there is a rule that tells you, after looking at the current pair, which pointer can safely move: that some whole set of pairs can be discarded without checking them. Usually that rule comes from the input being a **sorted sequence**, or from an invariant you maintain about the region each pointer has passed.

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

Each step discards one element for good, so at most one fewer step than the array length: O(n) time, O(1) space. Compare the hash-map version of two sum (the earlier approach units), which is expected O(n) under constant-time, well-distributed hashing but needs O(n) extra memory and works on unsorted input.

> [!tip] Three sum
> "Find all triples summing to 0" is: sort (O(n log n)), then for each `i`, run pair sum on the part after `i` with target `-a[i]`. That's O(n²) total for this algorithm, excluding integer bit costs. Skip equal neighbours to avoid duplicate triples.

## Other safe opposite-end moves

A palindrome scan compares the two outer values. If they differ, the sequence is not a palindrome; if they match, discard both and check the inner range. Each inward move is justified by an equality already checked. A merge of two sorted sequences instead keeps one forward index per input and takes the smaller current value.

For the existing `count_less` question, if the two endpoint values sum below the target, the left endpoint pairs successfully with every remaining position up to the right endpoint. Count that whole block, then discard the left endpoint. Otherwise discard the right endpoint. This rule depends on sortedness just as pair-sum search does.

## Key takeaways
- Sortedness proves which endpoint cannot participate in a remaining answer.
- Use distinct positions: stop when the pointers meet.
- Sorting then fixing one element reduces three sum to repeated pair scans.

## Further reading
- [Two pointers — USACO Guide](https://usaco.guide/silver/two-pointers)
- [Dutch national flag problem — Wikipedia](https://en.wikipedia.org/wiki/Dutch_national_flag_problem)
- [Array cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/array/)
