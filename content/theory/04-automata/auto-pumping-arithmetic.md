---
id: auto-pumping-arithmetic
title: Arithmetic witnesses and pumping down
level: intermediate
minutes: 5
sourceLesson: auto-pumping
summary: Square-length witnesses pump strictly between consecutive squares.
---

## Example 3: perfect squares

Consider strings of a characters whose length is a **perfect square** (0, 1, 4, 9, 16, …). The useful observation is that gaps between squares grow. Choose a square large enough that duplicating any allowed pumped piece increases the length without reaching the next square. The following short inequality is the proof of that gap, rather than a calculation to memorise.

```formula essential
s = a^{p²},   |s| = p²
y = a^k,   1 ≤ k ≤ p
|x · y^2 · z| = p² + k
p² < p² + k ≤ p² + p < (p + 1)²
where
s: the string we choose: p² a's
a: the only symbol
p: the pumping length; a positive integer measured in input symbols
p²: p squared, p × p
| |: the length of a string
x, y, z: the adversary's split
y^2: y twice, so one extra copy
k: the length of y; an integer count, non-negative unless a positive lower bound is stated
·: concatenation
<: is less than
≤: is less than or equal to (the first comparison makes k at least 1)
(p + 1)²: the next perfect square after p², equal to p² + 2p + 1
In words: one extra copy of y adds between 1 and p symbols, which lands strictly between p² and the next square, so the new length is not a square.
```

So p² + k lies strictly between two consecutive squares and is not a square. Contradiction. With pumping length 3: lengths 10, 11 or 12, all between 9 and 16.

## Example 4: more a's than b's

Let L be the strings of a's then b's with more a's than b's. Pumping up only adds more a's, which keeps the string in L. So pump **down**.

Choose a string with exactly one more a than b, with the b-run as long as the proposed pumping length. Any legal pumped piece contains only a characters. Removing it loses at least the one-character lead, while leaving every b in place. The result no longer has more a characters than b characters.

For example, with pumping length three, `aaaabbb` loses at least one a and becomes, say, `aaabbb`. Equality already violates the strict requirement for more a characters.

The lesson: try both directions. Different languages break under different numbers of copies.

## A prime-length witness

The prime-length language is another arithmetic example. Choose a prime length at least two larger than the positive pumping length; arbitrarily large primes exist. Once the adversary chooses a legal non-empty piece, choose enough repetitions to make the resulting length a product of two integers greater than one. Such a product is composite, so it leaves the prime-length language. The choice is allowed to depend on the piece length; it must work for every permitted piece.

Here is the optional factorisation that supplies that repetition count:

```formula reference
q ≥ p + 2     1 ≤ k ≤ p
i = q − k
(q − k) + ik = (q − k)(1 + k)
q − k ≥ 2     1 + k ≥ 2
where
q: a prime integer, the chosen input length in symbols
p: the positive integer pumping length in symbols
k: the integer length of the non-empty pumped piece in symbols
i: the non-negative integer number of copies of that piece
≥, ≤: greater than or equal to, less than or equal to
In words: choose the number of copies to equal the length left after deleting the original piece. The resulting total is that remaining length multiplied by one more than the piece length; both factors are at least two, so the new length is composite.
```

For example, prime length seven and a pumped substring of length two give five copies and a new length of fifteen. The argument works for every legal pumped-substring length, rather than relying on this one example.

## Key takeaways
- Square-length witnesses pump strictly between consecutive squares.
- For a strict count inequality, deleting the pumped piece can break membership when repeating it cannot.

## Further reading
- [MIT: the regular pumping lemma and automata to regexes](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec3-1/)
