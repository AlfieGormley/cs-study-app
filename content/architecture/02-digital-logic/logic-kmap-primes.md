---
id: logic-kmap-primes
title: Prime implicants and minimum covers
level: intermediate
minutes: 3
sourceLesson: logic-karnaugh-maps
summary: A prime group cannot grow while remaining valid.
---

## Prime and essential implicants

Some vocabulary makes the method precise, and is what algorithms use.

- An **implicant** is any valid group (a product term that is 1 only where F is 1).
- A **prime implicant** is a group that cannot be made any bigger.
- An **essential prime implicant** is a prime that covers some 1 that no other prime covers. Every minimal solution must include it.

The systematic procedure: find all prime implicants, take all the essential ones, then cover any remaining 1s with as few extra primes as possible.

The trap is the prime that looks useful but isn't. Consider this function:

```formula
F = Σm(0, 4, 5, 7, 8, 12, 13, 15)
where
F: the function being minimised, of the four inputs A, B, C and D (each 0 or 1)
Σm(…): OR together the minterms with these row numbers
In words: F is 1 on the eight listed rows out of 16.
```

```
          CD
  AB     00  01  11  10
       +---+---+---+---+
  00   | 1 | 0 | 0 | 0 |
  01   | 1 | 1 | 1 | 0 |
  11   | 1 | 1 | 1 | 0 |
  10   | 1 | 0 | 0 | 0 |
       +---+---+---+---+
```

There are three primes: NOT C AND NOT D (the whole first column), B AND D (the middle 2×2 square), and B AND NOT C (rows 01 and 11, columns 00 and 01). The first column and middle square are essential and together cover every one, including all cells covered by B AND NOT C. The minimum is:

```formula
F = C′·D′ + B·D
where
F: the minimised function
B, C, D: inputs, each 0 or 1 (A does not appear: it is eliminated)
C′, D′: NOT C, NOT D
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the first column and the middle square are both essential, and together they cover every 1, so two terms are enough.
```

Adding the third prime, B AND NOT C, would give a correct but non-minimal circuit.

Some functions have **no** essential primes and more than one minimal answer. Consider this three-input function:

```formula
Σm(0, 1, 2, 5, 6, 7)
where
Σm(…): OR together the listed binary-indexed minterms, using A, B, C from most to least significant input bit
In words: OR together the minterms of rows 0, 1, 2, 5, 6, 7. The result is one exactly on these rows.
```

This function has six primes arranged in a ring. One minimal cover is:

```formula
A′·B′ + B·C′ + A·C
where
A: Boolean input bit
A′: NOT A
B: Boolean input bit
B′: NOT B
C: Boolean input bit
C′: NOT C
+: Boolean OR
· or adjacent brackets: Boolean AND
′: NOT of the preceding bit or whole bracket
In words: Read this Boolean expression as ((NOT (A) AND NOT (B)) OR (B AND NOT (C)) OR (A AND C)).
```

A second minimal cover is:

```formula
A′·C′ + B′·C + A·B
where
A: Boolean input bit
A′: NOT A
B: Boolean input bit
B′: NOT B
C: Boolean input bit
C′: NOT C
+: Boolean OR
· or adjacent brackets: Boolean AND
′: NOT of the preceding bit or whole bracket
In words: Read this Boolean expression as ((NOT (A) AND NOT (C)) OR (NOT (B) AND C) OR (A AND B)).
```

Both covers use three two-literal terms.

## Key takeaways
- A prime group cannot grow while remaining valid.
- Essential primes are mandatory; other primes may be redundant.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Karnaugh map — Wikipedia](https://en.wikipedia.org/wiki/Karnaugh_map)
- [Quine–McCluskey algorithm — Wikipedia](https://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm)
- [Espresso heuristic logic minimizer — Wikipedia](https://en.wikipedia.org/wiki/Espresso_heuristic_logic_minimizer)
- [Hazard (logic) — Wikipedia](https://en.wikipedia.org/wiki/Hazard_(logic))
- [Don't-care term — Wikipedia](https://en.wikipedia.org/wiki/Don%27t-care_term)
- [Gray code — Wikipedia](https://en.wikipedia.org/wiki/Gray_code)
