---
id: sort-merge-recursion-cost
title: Merge sort and its recursion tree
level: basic
minutes: 4
sourceLesson: sort-merge
summary: Balanced recursive halves and linear merging give a logarithmic number of full-data levels.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## The full sort

```python
def merge_sort(a):
    # Empty and one-item ranges are sorted.
    if len(a) <= 1:
        return a
    # Split before recursively sorting
    # halves.
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

## Why it costs O(n log n): the recursion tree

Look at the work level by level rather than call by call. The final merge at the top touches all n elements. The level below it has two merges of half the elements each, which again touches all n elements. Every level of the tree touches every element exactly once:

```
8-element example (element counts):
level 0:       8             total 8
level 1:     4   4           total 8
level 2:   2 2   2 2         total 8
level 3:  1 1 1 1 1 1 1 1    total 8
```

The pieces halve at each level, so they reach single elements after a logarithmic number of halvings: 3 levels of merging for 8 elements, 10 for 1,024 and about 20 for a million. Linear work on each of logarithmically many levels gives **O(n log n)**, on every input.

```formula reference
T(n) = 2T(n / 2) + cn
T(n) = cn(log_2(n) + 1)
where
T(n): the running time of merge sort on n elements, in basic steps, when n is a power of two
n: the number of elements to sort
T(n / 2): the running time of one recursive call on half the elements
c: a fixed constant: the cost per element of merging, and the cost of a one-element base case
log_2(n): the base-2 logarithm of n: how many times n can be halved before reaching 1
In words: sorting n elements costs two half-size sorts plus a merge that touches every element once; each of the levels of the recursion tree does the same linear amount of work, so the total grows like n log n.
```

The neat formula assumes the input size is a power of two; for other sizes the halves differ by at most one element and the growth is the same. Doubling the input adds only **one** more level, which is why merge sort scales so much better than the quadratic sorts.

> [!analogy] Real-world analogy: a team sorting a pile of forms
> A supervisor splits a pile of forms in half and hands each half to an assistant, who splits theirs again for two more helpers, until everyone holds a single form. Then the work flows back up: each person merges the two sorted piles handed back to them and passes the result up a level.
>
> **How it maps:** each person is a recursive call, a single form is the base case, and merging two returned piles is the merge step. Each layer of the organisation chart handles every form once between them, and the number of layers is the number of times the pile can be halved.
>
> **Where it stops:** the helpers in a team work at the same time. A plain merge sort does the calls one after another on one processor, so the levels add up rather than overlap; parallel merge sorts exist but need extra coordination.

## Key takeaways
- The balanced recursion tree has logarithmically many levels, each touching the full input.

## Further reading
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
