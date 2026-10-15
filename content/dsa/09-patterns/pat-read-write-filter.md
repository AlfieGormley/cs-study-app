---
id: pat-read-write-filter
title: Filter a sorted array with read and write indices
level: basic
minutes: 2
sourceLesson: pat-two-pointers
summary: The kept prefix contains the distinct values seen so far; the list itself is not resized.
---

Here n is the sorted array length. A read index scans the input and a write index marks the next kept position; constant extra space requires avoiding temporary slices.

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
            # Write the new distinct value
            # into prefix.
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

## Key takeaways
- The kept prefix contains the distinct values seen so far; the list itself is not resized.
- Keep at most two copies by comparing with the value two kept positions back.
- Fast and slow linked-list pointers use a related movement pattern with a different invariant.

## Further reading
- [Two pointers — USACO Guide](https://usaco.guide/silver/two-pointers)
- [Dutch national flag problem — Wikipedia](https://en.wikipedia.org/wiki/Dutch_national_flag_problem)
- [Array cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/array/)
