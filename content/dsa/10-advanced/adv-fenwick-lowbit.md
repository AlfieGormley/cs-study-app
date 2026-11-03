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

The lowest set bit of i is `i & -i` in code. It isolates the rightmost one in the binary representation. In two's-complement arithmetic, negation preserves that bit while flipping the higher bits; AND discards those higher bits. The bit-level derivation is optional:

```formula reference
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
In words: negating a positive index preserves its lowest set bit and flips all higher bits, so AND with the original index keeps just that lowest bit.
```

So `lowbit(12)` is 4: 12 is 1100 in binary, and its rightmost 1 is worth 4. For any odd number the answer is 1.

Python integers behave as if they had infinitely many sign bits, so `i & -i` works there too.

Each entry therefore covers this block:

Entry `t[i]` stores a block ending at position `i`, with length `i & -i`. At index six the block length is two, so the entry covers positions five and six, not the whole prefix.

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
- [Fenwick trees — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
