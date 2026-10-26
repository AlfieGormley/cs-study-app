---
id: disc-power-sets-bitmasks
title: "Power sets and bitmask enumeration"
level: basic
minutes: 3
summary: "Each element independently belongs or does not belong to a subset."
sourceLesson: disc-sets-functions
---

## Power sets

The **power set** P(A) is the set of all subsets of A. Its size is a power of two, because each element is independently either in or out of a subset: two choices, made once per element.

```formula essential
|P(A)| = 2^n   when |A| = n
where
A: any finite set; in the example, the set of the three letters a, b and c
P(A): the power set of A: the set whose elements are all the subsets of A
n: the number of elements in A
| |: the cardinality: the number of elements in a set
2^n: n copies of 2 multiplied together
In words: Each extra element doubles the number of subsets: every old subset has a version excluding it and a version including it.
```

That "in or out" view is exactly how programmers enumerate subsets with a **bitmask**: an integer whose binary digits (bits) say which elements are in. Number the elements from 0 upwards; each bit of the mask is 1 when the element with that number is in the subset.

With items a, b and c assigned bit positions from lowest to highest, the binary mask 110 selects b and c. Mask zero selects nothing; the mask with every bit set selects everything.

The loop below visits every mask and decodes it back into a subset:

```python
items = ['a', 'b', 'c']
n = len(items)
# One mask per subset.
for mask in range(1 << n):
    # Low shifted bit selects the item.
    sub = [items[i] for i in range(n)
           if mask >> i & 1]
    print(mask, sub)
```

For 20 items there are about a million subsets; for 40, about a trillion. The displayed loop also decodes every mask by checking every item position.

Each mask requires checking every item position. Doubling the number of masks doubles that part of the work; adding items also lengthens the decoding step.

This assumes each bit check costs one step (a unit-cost model) and ignores the cost of formatting and printing.

The count includes the empty subset and the whole set. To count non-empty subsets, subtract one from the total.

For three elements, the eight subsets include the empty one. Excluding only that subset leaves seven.

## Key takeaways

- Each element independently belongs or does not belong to a subset.
- Enumerating subsets takes exponential time; the shown decoder also checks every bit for every subset.

## Further reading

- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
