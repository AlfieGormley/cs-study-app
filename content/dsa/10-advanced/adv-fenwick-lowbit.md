---
id: adv-fenwick-lowbit
title: Understanding the Fenwick lowbit trick
level: advanced
minutes: 3
summary: Bitwise AND of a positive index and its negation extracts its lowest set bit.
sourceLesson: adv-fenwick-trees
---

Here n is the number of input elements. Fenwick positions start at 1; the empty prefix is valid, but an update at zero is not. Arithmetic costs assume word-sized values.

## The lowbit trick

The lowest set bit of i is `i & -i` in code. This works because of two's complement, the way computers store negative integers:

```formula
lowbit(i) = i & (−i)
−i = (~i) + 1
12 = …0000 1100₂
~12 = …1111 0011₂
−12 = …1111 0100₂
12 & (−12) = …0000 0100₂ = 4
where
i: a positive whole number, a position in the tree
lowbit(i): the value of the lowest (rightmost) 1-bit of i
~i: bitwise NOT: i with every bit flipped
&: bitwise AND: a bit is 1 in the result only where it is 1 in both inputs
₂: the number is written in binary (base 2)
…: the same digit repeats to the left (all 0s for a positive number, all 1s for a negative one)
In words: flipping every bit and adding one carries through the trailing zeros and stops at the lowest 1, so i and −i share exactly that one bit, and AND keeps only it.
```

So `lowbit(12)` is 4: 12 is 1100 in binary, and its rightmost 1 is worth 4. For any odd number the answer is 1.

Python integers behave as if they had infinitely many sign bits, so `i & -i` works there too.

Each entry therefore covers this block:

```formula
t[i] = a[i − lowbit(i) + 1] + … + a[i]
t[6] = a[6 − 2 + 1] + … + a[6] = a[5] + a[6]
where
i: the index of the entry, from 1 to n
t[i]: the value stored at index i of the Fenwick array
a[k]: the array element at position k
lowbit(i): the value of the lowest 1-bit of i
…: every element in between
In words: entry i holds the sum of the lowbit(i) elements that end at position i.
```

For an eight-element array:

| i | binary | lowbit | t[i] covers |
|---|---|---|---|
| 1 | 0001 | 1 | a[1] |
| 2 | 0010 | 2 | a[1..2] |
| 3 | 0011 | 1 | a[3] |
| 4 | 0100 | 4 | a[1..4] |
| 5 | 0101 | 1 | a[5] |
| 6 | 0110 | 2 | a[5..6] |
| 7 | 0111 | 1 | a[7] |
| 8 | 1000 | 8 | a[1..8] |

Odd indices hold single elements; powers of two hold whole prefixes.

## Key takeaways

- Bitwise AND of a positive index and its negation extracts its lowest set bit.
- Each tree entry stores the block of that length ending at its index.

## Further reading
- [Fenwick Tree — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
- [Fenwick tree — Wikipedia](https://en.wikipedia.org/wiki/Fenwick_tree)
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
