---
id: logic-karnaugh-maps
title: Karnaugh maps
level: intermediate
minutes: 17
summary: A visual method for minimising Boolean functions of up to four or so variables, with Gray-code layout, prime implicants, don't-cares, product-of-sums, and the glitches that minimal circuits can cause.
---

In lesson 1 we simplified the majority function by spotting this:

```formula
A′·B·C + A·B·C = B·C·(A′ + A) = B·C
where
A, B, C: Boolean inputs, each 0 or 1
A′: NOT A: 1 when A is 0, and 0 when A is 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: two terms that are identical except that one has A and the other has NOT A collapse into one term without A, because A′ + A is always 1.
```

That move, combining two terms that differ in exactly one variable, is the combination step in two-level minimisation; selecting a minimum cover is a separate problem. The hard part is seeing which terms to pair.

A **Karnaugh map** (K-map), introduced by Maurice Karnaugh at Bell Labs in 1953, rearranges the truth table into a grid where terms that differ in one variable sit **next to each other**. Simplification becomes drawing rectangles around 1s.

## The key idea: adjacency

The algebra behind every K-map group is one identity:

```formula
X·Y + X·Y′ = X·(Y + Y′) = X·1 = X
where
X: any product term shared by both terms, for example A·B′
Y: the one variable that differs between the two terms
Y′: NOT Y
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: if two terms are the same except for one variable, which is plain in one and complemented in the other, they merge into the shared part and that variable disappears.
```

Two minterms that differ in one variable merge into one term with that variable removed. Four minterms that form two such pairs merge again, removing a second variable, and so on. Each doubling of the group removes one more variable:

```formula
N_cells = 2^k
N_literals = n − k
N_literals = 4 − 2 = 2   for n = 4, k = 2
where
N_cells: the number of cells in a valid group (1, 2, 4, 8 or 16)
k: how many variables the group eliminates
2^k: 2 multiplied by itself k times
n: the number of input variables in the map
N_literals: the number of literals (variables, plain or complemented) left in the group's product term
In words: in a 4-variable map, a group of 4 cells (k = 2) leaves a 2-literal term, a pair leaves 3 literals and a group of 8 leaves just 1.
```

To make mergeable minterms adjacent, the rows and columns are labelled in **Gray code** order, where neighbours differ in exactly one bit:

```
binary order:  00  01  10  11
Gray order:    00  01  11  10
```

In binary order, 01 and 10 are neighbours but differ in two bits. In Gray order every step flips one bit, **including the wrap from 10 back to 00**.

## Laying out the map

### Three variables

Put A on the rows and BC on the columns. Each cell holds one row of the truth table; here are the minterm numbers:

```
          BC
  A      00  01  11  10
       +---+---+---+---+
   0   | 0 | 1 | 3 | 2 |
       +---+---+---+---+
   1   | 4 | 5 | 7 | 6 |
       +---+---+---+---+
```

Note that columns 3 and 2 are swapped compared with the truth table order. That is the Gray code at work.

### Four variables

AB on the rows, CD on the columns, both in Gray order:

```
          CD
  AB     00  01  11  10
       +---+---+---+---+
  00   | 0 | 1 | 3 | 2 |
  01   | 4 | 5 | 7 | 6 |
  11   |12 |13 |15 |14 |
  10   | 8 | 9 |11 |10 |
       +---+---+---+---+
```

The map has **wrap-round** adjacency in both directions, like the surface of a doughnut. The left column is adjacent to the right column, and the top row to the bottom row. So cells 0, 2, 8 and 10 (the four corners) form a valid group.

## The grouping rules

1. Group only 1s (for sum of products).
2. For maps up to four variables, each group is a rectangle with power-of-two side lengths. Its total size is 1, 2, 4, 8 or 16 cells; a full 16-cell group gives constant 1.
3. Groups may wrap round edges and may **overlap**.
4. Make each group **as large as possible**. Bigger groups mean fewer literals.
5. Use **as few groups as possible** to cover every 1.

To read a group, find the variables that **stay constant** across all its cells. A variable that is 1 throughout appears plain, one that is 0 throughout appears complemented, and one that changes is dropped.

## Worked example: three variables

The function to minimise is given as a list of minterms, the truth-table rows where it is 1:

```formula
F(A, B, C) = Σm(0, 2, 4, 5, 6)
where
F(A, B, C): the function being minimised, of the three inputs A, B and C
A, B, C: the inputs, each 0 or 1; A is the most significant bit of the row number
Σm(…): OR together the minterms with these row numbers (Σ, capital sigma, means "sum of"; m stands for minterm)
In words: F is 1 on rows 0, 2, 4, 5 and 6 (inputs 000, 010, 100, 101 and 110) and 0 everywhere else.
```

Fill in the map:

```
          BC
  A      00  01  11  10
       +---+---+---+---+
   0   | 1 | 0 | 0 | 1 |
       +---+---+---+---+
   1   | 1 | 1 | 0 | 1 |
       +---+---+---+---+
```

- **Group 1**: the four cells in columns 00 and 10 (m0, m2, m4, m6). They wrap round the edge. A changes, B changes, C is 0 throughout. Term: `C'`.
- **Group 2**: the pair m4, m5 in row 1, columns 00 and 01. A = 1, B = 0, C changes. Term: `AB'`.

```formula
F = C′ + A·B′
where
F: the minimised function
A, B, C: the inputs, each 0 or 1
C′, B′: NOT C, NOT B
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: F is 1 whenever C is 0 (group 1), or when A is 1 and B is 0 (group 2). Check row 5 (101): C′ = 0 but A·B′ = 1, so F = 1, as required.
```

The canonical sum of products needed five 3-literal minterms. A direct AND/OR implementation needs complements B' and C', a two-input AND and a two-input OR; shared complements or a different gate mapping can change that count.

> [!warning] Don't stop at the obvious pairs
> A beginner might group m0 with m2 and m4 with m6 separately (giving `A'C' + A·C'`). That covers the same cells with two terms where one, `C'`, would do. Always look for the wrap-round.

## Worked example: four variables

This time there are four inputs:

```formula
F(A, B, C, D) = Σm(0, 1, 2, 5, 8, 9, 10)
where
F(A, B, C, D): the function being minimised, of four inputs
A, B, C, D: the inputs, each 0 or 1; A is the most significant bit of the row number
Σm(…): OR together the minterms with these row numbers (m stands for minterm)
In words: F is 1 on rows 0, 1, 2, 5, 8, 9 and 10 out of 16, and 0 on the rest.
```

```
          CD
  AB     00  01  11  10
       +---+---+---+---+
  00   | 1 | 1 | 0 | 1 |
  01   | 0 | 1 | 0 | 0 |
  11   | 0 | 0 | 0 | 0 |
  10   | 1 | 1 | 0 | 1 |
       +---+---+---+---+
```

- Rows 00 and 10 are adjacent (wrap-round). Columns 00 and 01 in those rows give m0, m1, m8, m9: B = 0, C = 0. Term: `B'C'`.
- The four corners m0, m2, m8, m10: B = 0, D = 0. Term: `B'D'`.
- That leaves m5 (row 01, column 01). Its best partner is m1 directly above it: A = 0, C = 0, D = 1. Term: `A'C'D`.

```formula
F = B′·C′ + B′·D′ + A′·C′·D
where
F: the minimised function
A, B, C, D: the inputs, each 0 or 1
A′, B′, C′, D′: NOT A, NOT B, NOT C, NOT D
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: three groups (a wrap-round block of four, the four corners and one pair) cover all seven 1s, giving three short terms instead of seven 4-literal minterms.
```

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

There are three primes: `C'D'` (the whole first column), `BD` (the middle 2×2 square) and `BC'` (rows 01 and 11, columns 00 and 01). `C'D'` and `BD` are both essential, and together they already cover every 1, including all of `BC'`. So the minimum is:

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

Adding `BC'`, a perfectly good prime, would give a correct but non-minimal circuit.

Some functions have **no** essential primes and more than one minimal answer. `Σm(0, 1, 2, 5, 6, 7)` has six primes arranged in a ring, and both `A'B' + BC' + A·C` and `A'C' + B'C + AB` are minimal.

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
- m5 and m7 with m13, m15: `BD`.
- m7 and m6 with m15, m14: `BC`.

```formula
F = A + B·D + B·C
where
F: 1 when the BCD digit is 5 or more
A, B, C, D: the four bits of the digit, A the most significant
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the digit is 5 or more if it is 8 or 9 (A = 1), or if it is 5 or 7 (B and D are 1), or 6 or 7 (B and C are 1).
```

Without the don't-cares, the same function needs `AB'C' + A'BD + A'BC`: three terms of three literals each. Don't-cares are a major source of savings in real control logic, such as instruction decoders where many opcodes are unused.

## Product of sums: group the 0s

To get a minimal POS, group the **0s** instead. Each group gives a sum term, read with the opposite convention: a variable that is 0 throughout appears plain, one that is 1 throughout appears complemented.

Back to `F = Σm(0, 2, 4, 5, 6)`. The 0s are m1, m3 and m7.

- m1, m3 (row 0, columns 01 and 11): A = 0, C = 1. Sum term: `(A + C')`.
- m3, m7 (column 11): B = 1, C = 1. Sum term: `(B' + C')`.

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
    for i, v in enumerate(
            product((0, 1), repeat=n)):
        if i in dont_care:
            continue
        if f(*v) != (i in ones):
            return f"wrong at m{i}"
    return "ok"

f = lambda a, b, c, d: a | (b & d) | (b & c)
print(check(f, {5, 6, 7, 8, 9}, 4,
            dont_care=range(10, 16)))  # ok
```

`product` yields rows in minterm order, A first, so the enumeration index is the minterm number.

## Hazards: when minimal is too minimal

A minimal circuit can produce a brief false output, a **glitch**, when an input changes. Take this function with B and C both held at 1:

```formula
F = A·B + A′·C
F = A·1 + A′·1 = A + A′ = 1   for B = C = 1
where
F: the circuit's output
A, B, C: inputs, each 0 or 1
A′: NOT A, produced by an inverter
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: with B and C at 1, the logic says F is "A or not A", which is always 1, so F should stay 1 whatever A does.
```

The `A'` signal comes through an inverter, so it changes slightly later than A. When A falls from 1 to 0, unequal path delays can leave a moment when AB has dropped but A'C has not risen:

```
A     --------________________
AB    --------________________
A'    __________--------------
A'C   __________--------------
F     --------__--------------
              ^^
         both terms 0: glitch
```

This is a **static-1 hazard**. On the K-map, it shows up as two groups that touch but do not overlap: m7 (in AB) and m3 (in A'C) are adjacent, yet no single group contains both.

The fix is to add the redundant group that bridges them, the consensus term from lesson 1:

```formula
F = A·B + A′·C + B·C
where
F: the circuit's output, now hazard-free for this input change
A, B, C: inputs, each 0 or 1
A′: NOT A
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the extra term B·C does not change the function (it is the redundant consensus term), but it does not depend on A at all.
```

`BC` stays 1 throughout the transition, holding F up. At ordinary synchronous data inputs, glitches outside setup/hold sampling windows need not affect the captured value when timing constraints are met. They can still increase power. They matter in asynchronous logic, in anything that drives a clock, reset or enable, and for power, since every glitch is a wasted switching event.

## Beyond four variables

K-maps work well up to four variables, are awkward at five or six (two or four stacked maps, with adjacency between layers), and are hopeless beyond. Tools use:

- **Quine–McCluskey**: the same prime-implicant method done in tables. Exact, but the number of primes can grow exponentially with the number of variables.
- **Espresso**: a heuristic two-level minimiser associated with Berkeley. It seeks compact covers without guaranteeing a globally minimal answer.
- **Multi-level synthesis**: real chips are not two-level. Synthesis tools factor logic into many levels and map it onto the gates in a cell library, trading depth for area.

K-maps remain the best way to *understand* minimisation, and they are still handy for small pieces of control logic and for spotting hazards.

## Key takeaways
- A K-map is a truth table arranged in Gray code, so that adjacent cells differ in one variable and can be merged, dropping the variable that changes.
- Group 1s into rectangles of 1, 2, 4 or 8 cells, as large and as few as possible, wrapping round the edges. Keep the variables that stay constant.
- Essential prime implicants must be in every minimal answer; extra primes may be redundant.
- Don't-cares can be used as 1s or 0s, whichever helps. Grouping 0s gives a minimal product of sums.
- Minimal two-level logic can glitch. Adding the bridging consensus term removes the illustrated static-1 hazard in the two-level model with one input changing; it is not a universal cure for arbitrary multi-input or multi-level hazards. Beyond about six variables, tools use Quine–McCluskey, Espresso and multi-level synthesis.

## Further reading
- [Karnaugh map — Wikipedia](https://en.wikipedia.org/wiki/Karnaugh_map)
- [Quine–McCluskey algorithm — Wikipedia](https://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm)
- [Espresso heuristic logic minimizer — Wikipedia](https://en.wikipedia.org/wiki/Espresso_heuristic_logic_minimizer)
- [Hazard (logic) — Wikipedia](https://en.wikipedia.org/wiki/Hazard_(logic))
- [Don't-care term — Wikipedia](https://en.wikipedia.org/wiki/Don%27t-care_term)
- [Gray code — Wikipedia](https://en.wikipedia.org/wiki/Gray_code)
