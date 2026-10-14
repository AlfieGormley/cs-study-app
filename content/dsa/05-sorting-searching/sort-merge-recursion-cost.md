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

## Proof of O(n log n): the recursion tree

A **recurrence** describes a cost in terms of the same cost on smaller inputs. Merge sort's running time obeys this one:

```formula
T(n) = 2T(n / 2) + cn
T(1) = c
where
T(n): the running time of merge sort on n elements, in basic steps
n: the number of elements to sort
T(n / 2): the running time of one recursive call on half the elements
T(1): the cost of the base case, a single element
c: a fixed constant: the cost per element of merging
In words: sorting n elements costs two half-size sorts plus a merge that touches every element once.
```

Draw it as a tree. The root does the merge constant times the input size in work. Its two children each do half that, so that level also totals the merge constant times the input size. Every level works the same way:

```formula
W_k = 2^k c(n / 2^k) = cn
L = log_2(n) + 1
T(n) = cn(log_2(n) + 1)
T(n) = Θ(n log(n))
where
W_k: the total work done on level k of the recursion tree
k: the level number, 0 at the root
2^k: k copies of 2 multiplied together: the number of subproblems on level k, which doubles each level
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
8-element example (element counts):
level 0:       8             total 8
level 1:     4   4           total 8
level 2:   2 2   2 2         total 8
level 3:  1 1 1 1 1 1 1 1    total 8
```

Subproblem sizes halve each level, so they reach 1 after a base-two logarithmic number of levels. That gives one more than a base-two logarithmic number of levels, each costing the per-element merge constant times the input size. For 1,024 elements that is 11 levels. The proof assumes the input size is a power of two; for other sizes the halves differ by at most one element and the result is the same.

## Key takeaways
- The balanced recursion tree has logarithmically many levels, each touching the full input.

## Further reading
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
