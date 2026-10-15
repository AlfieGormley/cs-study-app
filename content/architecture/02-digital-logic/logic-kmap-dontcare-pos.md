---
id: logic-kmap-dontcare-pos
title: Don't-cares, zero groups and checking
level: intermediate
minutes: 4
sourceLesson: logic-karnaugh-maps
summary: Use a guaranteed irrelevant input only when the interface allows it.
---

## Don't-care conditions

Sometimes certain input combinations can never occur, or their output doesn't matter. Mark those cells `x`. You may treat each `x` as 1 if that makes a group bigger, or as 0 otherwise.

Example: a circuit takes a BCD digit (0 to 9 in four bits, ABCD) and outputs 1 if the digit is 5 or more. Assume the interface guarantees that codes 10 to 15 never occur.

```
          CD
  AB     00  01  11  10
       +---+---+---+---+
  00   | 0 | 0 | 0 | 0 |
  01   | 0 | 1 | 1 | 1 |
  11   | x | x | x | x |
  10   | 1 | 1 | x | x |
       +---+---+---+---+
```

- Treat the whole bottom half (rows 11 and 10) as 1s: an 8-cell group, `A`.
- m5 and m7 with m13, m15: B AND D.
- m7 and m6 with m15, m14: B AND C.

```formula
F = A + B·D + B·C
where
F: 1 when the BCD digit is 5 or more
A, B, C, D: the four bits of the digit, A the most significant
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the digit is 5 or more if it is 8 or 9 (A = 1), or if it is 5 or 7 (B and D are 1), or 6 or 7 (B and C are 1).
```

If codes ten to fifteen must instead output zero, the strict function needs three three-literal terms:

```formula
A·B′·C′ + A′·B·D + A′·B·C
where
A: Boolean input bit
A′: NOT A
B: Boolean input bit
B′: NOT B
C: Boolean input bit
C′: NOT C
D: Boolean input bit
+: Boolean OR
· or adjacent brackets: Boolean AND
′: NOT of the preceding bit or whole bracket
In words: Read this Boolean expression as ((A AND NOT (B) AND NOT (C)) OR (NOT (A) AND B AND D) OR (NOT (A) AND B AND C)).
```

Don't-cares can save logic only when the interface permits them. An unused opcode is not automatically a don't-care: a processor may require a defined illegal-instruction response.

## Product of sums: group the 0s

To get a minimal POS, group the **0s** instead. Each group gives a sum term, read with the opposite convention: a variable that is 0 throughout appears plain, one that is 1 throughout appears complemented.

Return to the earlier three-input function:

```formula
F = Σm(0, 2, 4, 5, 6)
where
F: Boolean output
Σm(…): OR together the listed binary-indexed minterms, using A, B, C from most to least significant input bit
In words: OR together the minterms of rows 0, 2, 4, 5, 6. The result is one exactly on these rows.
```

Its zero rows are m1, m3 and m7.

- m1, m3 (row 0, columns 01 and 11): A = 0, C = 1. Sum term: 

```formula
(A + C′)
where
A: Boolean input bit
C′: NOT C
+: Boolean OR
′: NOT of the preceding bit or whole bracket
In words: Read this Boolean expression as (A OR NOT (C)).
```

- m3, m7 (column 11): B = 1, C = 1. Sum term: 

```formula
(B′ + C′)
where
B′: NOT B
C′: NOT C
+: Boolean OR
′: NOT of the preceding bit or whole bracket
In words: Read this Boolean expression as (NOT (B) OR NOT (C)).
```


```formula
F = (A + C′)·(B′ + C′)
F = A·B′ + A·C′ + B′·C′ + C′·C′
F = C′ + A·B′
where
F: the function Σm(0, 2, 4, 5, 6) from earlier
A, B, C: the inputs, each 0 or 1
B′, C′: NOT B, NOT C
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the product of sums is 0 exactly where one bracket is 0, at the three 0 cells. Multiplying it out, C′·C′ is C′, and C′ absorbs A·C′ and B′·C′, giving back the sum-of-products answer.
```

Neither form is always smaller; designers try both.

## Checking your answer

K-map mistakes are easy to make and easy to catch. Compare against the minterm list by trying every input:

```python
from itertools import product

def check(f, ones, n, dont_care=()):
    # Enumeration follows binary row order.
    for i, v in enumerate(
            product((0, 1), repeat=n)):
        # Skip allowed rows.
        if i in dont_care:
            continue
        # Check every required zero and one.
        if f(*v) != (i in ones):
            return f"wrong at m{i}"
    return "ok"

f = lambda a, b, c, d: a | (b & d) | (b & c)
print(check(f, {5, 6, 7, 8, 9}, 4,
            dont_care=range(10, 16)))  # ok
```

`product` yields rows in minterm order, A first, so the enumeration index is the minterm number.

## Key takeaways
- Use a guaranteed irrelevant input only when the interface allows it.
- Grouping zeros yields POS; exhaustive checks verify all specified rows.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Karnaugh map — Wikipedia](https://en.wikipedia.org/wiki/Karnaugh_map)
- [Quine–McCluskey algorithm — Wikipedia](https://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm)
- [Espresso heuristic logic minimizer — Wikipedia](https://en.wikipedia.org/wiki/Espresso_heuristic_logic_minimizer)
- [Hazard (logic) — Wikipedia](https://en.wikipedia.org/wiki/Hazard_(logic))
- [Don't-care term — Wikipedia](https://en.wikipedia.org/wiki/Don%27t-care_term)
- [Gray code — Wikipedia](https://en.wikipedia.org/wiki/Gray_code)
