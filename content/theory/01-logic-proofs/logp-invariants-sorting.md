---
id: logp-invariants-sorting
title: Nested loop invariants in insertion sort
level: intermediate
minutes: 3
sourceLesson: logp-invariants
summary: A sorted prefix must also preserve the original items.
---

## Insertion sort and nested loops

Assume a finite mutable list of consistently ordered values, no concurrent changes, and normal execution. This function sorts that same list in place and returns it; defining the function produces no printed output.

```python
def insertion_sort(a):
    for i in range(1, len(a)):
        # I: a[:i] is sorted and holds
        #    the original a[:i]'s items
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            # Open a slot by shifting right.
            a[j + 1] = a[j]
            j -= 1
        # Place key after the smaller
        # prefix.
        a[j + 1] = key
    return a
```

The outer invariant says the prefix is a sorted rearrangement of the original prefix. The inner loop needs its own invariant (roughly: a[j+2 .. i] holds the elements greater than key, shifted right by one). After the last iteration, the processed prefix has length len(a), so the whole array is sorted. Python’s for-loop variable does not advance to len(a); it remains at its last assigned value, or is never assigned if there are no iterations.

Two-part invariants are common. "Sorted" alone is not enough: the empty array is sorted too. You also need "is a **permutation** (a rearrangement) of the input", or a buggy sort that overwrites everything with zeros would pass.


To understand the inner proof, imagine inserting the third value in the list `[3, 1, 2]`. The first two values have already become `[1, 3]`. The next key is two. The inner loop shifts three one place right, leaving a temporary gap, and then inserts two after one. The partly updated list contains a duplicate of three while the key is held separately; a claim that the array itself is always a permutation would therefore be too strong inside that loop.

A precise inner invariant treats the gap as unoccupied: the key held separately, the untouched prefix before the gap and the shifted suffix together contain exactly the original prefix’s items. Every shifted item is greater than the key, and their relative order is preserved. Shifting the next larger item moves the gap left without losing an item. When the test fails, either the gap is at the front or the preceding item is no greater than the key. Putting the key in that gap restores a sorted prefix with exactly the required items.

The strict greater-than test also keeps equal items in their original order, making this implementation a stable sort. Empty and singleton lists require no insertion; they already satisfy the result. This illustrates why a proof needs both an ordering fact and an item-preservation fact.

## Key takeaways
- A sorted prefix must also preserve the original items.
- The inner loop shifts larger elements to open the insertion position; Python does not advance its for index after the last iteration.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [How Amazon Web Services uses formal methods (PDF)](https://lamport.azurewebsites.net/tla/formal-methods-amazon.pdf)
