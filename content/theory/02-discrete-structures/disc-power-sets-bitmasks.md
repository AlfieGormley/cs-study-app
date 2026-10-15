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

```formula
|P(A)| = 2^n   when |A| = n
A = {a, b, c}
P(A) = { ∅, {a}, {b}, {c}, {a, b},
         {a, c}, {b, c}, {a, b, c} }
|P(A)| = 2^3 = 8
where
A: any finite set; in the example, the set of the three letters a, b and c
a, b, c: the three elements of the example set
P(A): the power set of A: the set whose elements are all the subsets of A
n: the number of elements in A
| |: the cardinality: the number of elements in a set
∅: the empty set, the subset with nothing in it
{ }: the set of the things listed inside
2^n: n copies of 2 multiplied together
In words: a set of n elements has 2^n subsets, counting both the empty set and the whole set. Three elements give 2 × 2 × 2 = 8 subsets.
```

That "in or out" view is exactly how programmers enumerate subsets with a **bitmask**: an integer whose binary digits (bits) say which elements are in. Number the elements from 0 upwards; each bit of the mask is 1 when the element with that number is in the subset.

```formula
m = x_0 × 2^0 + x_1 × 2^1 + …
      + x_{n−1} × 2^{n−1}
0 ≤ m ≤ 2^n − 1
{b, c} → m = 0 × 1 + 1 × 2 + 1 × 4 = 6
where
m: the mask: one whole number standing for one subset
x_0, x_1, x_{n−1}: the bits of the mask: bit number i is 1 if element number i is in the subset and 0 if not, for i from 0 up to n − 1
n: the non-negative number of elements in the set; for zero elements the sum is empty and means zero
2^0, 2^1, 2^{n−1}: powers of 2 (1, 2, 4, …), the place value of each bit
…: and so on, one term for every element
≤: is less than or equal to
→: is encoded as
b, c: in the last line, elements 1 and 2 of {a, b, c} (a is element 0)
In words: every subset of an n-element set corresponds to exactly one whole number from 0 to 2^n − 1. For {a, b, c}, the subset {b, c} is mask 6, binary 110.
```

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

There are 2ⁿ subsets: about a million for 20 items and about a trillion for 40. Runtime also includes work per subset. The loop above checks n bit positions for each of the 2ⁿ masks:

```formula
T(n) = Θ(n × 2^n)
T(20) ≈ 20 × 1,048,576 ≈ 21,000,000
where
T(n): the number of elementary operations the loop performs for an n-element set
n: the number of elements
Θ( ): grows at the same rate as the expression inside, up to a constant factor (big-Theta notation)
≈: approximately equal to
In words: the work is roughly n bit checks for each of the 2^n subsets, so 20 items already cost about 21 million basic steps before any printing.
```

This assumes each bit check costs one step (a unit-cost model) and ignores the cost of formatting and printing.

The count includes the empty subset and the whole set. To count non-empty subsets, subtract one from the total.

```formula
N_ne = 2^n − 1
N_ne = 2^3 − 1 = 7
where
N_ne: the number of non-empty subsets
n: the number of elements in the finite set, here 3
In words: Three elements have eight subsets, and removing the empty one leaves seven.
```

## Key takeaways

- Each element independently belongs or does not belong to a subset.
- Enumerating subsets takes exponential time; the shown decoder also checks every bit for every subset.

## Further reading

- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
