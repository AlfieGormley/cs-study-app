---
id: logic-boolean-algebra
title: Boolean algebra
level: basic
minutes: 16
summary: The algebra of true and false that every circuit is built on, its laws, De Morgan's theorem, truth tables, and the canonical sum-of-products and product-of-sums forms.
---

Boolean algebra models binary signals with values 0 and 1. Physical digital circuits use voltage ranges, have transition intervals and may encounter unknown, metastable or high-impedance states; sequential circuits also depend on stored state. The mathematics of such functions is **Boolean algebra**, named after George Boole, who described an algebra of logic in 1847 and 1854.

For almost a century it was a topic for logicians. Then in 1937 Claude Shannon's master's thesis showed that circuits of relays obey exactly Boole's rules. That idea is the bridge from logic to hardware: write the behaviour you want as a Boolean expression, simplify it with algebra, and the simplified expression can suggest a smaller circuit; actual area, delay and power depend on the implementation.

This lesson covers the operations, the laws, and the two standard ways of writing any function down.

## Values and the three fundamental operations

A Boolean variable takes one of two values: 0 or 1 (mapped here using positive logic to low and high voltage ranges). There are three fundamental operations.

- **AND** (written `A·B` or just `AB`): 1 only when both inputs are 1.
- **OR** (written `A + B`): 1 when at least one input is 1.
- **NOT** (written `A'`, `¬A` or with a bar over A): flips the value. In the formula cards in this module it is written A′ (a prime mark after the letter).

The symbols are borrowed from arithmetic, but they mean something different here. This card lists every case, using 0 and 1 directly:

```formula
0·0 = 0    0·1 = 0    1·1 = 1
0 + 0 = 0  0 + 1 = 1  1 + 1 = 1
0′ = 1     1′ = 0
where
·: AND: the result is 1 only when both sides are 1. In the text it is often left out, so AB means A·B
+: OR, not addition: the result is 1 when at least one side is 1
′: NOT, the complement: it turns 0 into 1 and 1 into 0. The text writes it as an apostrophe (A'); books often draw a bar over the letter instead
In words: AND behaves like multiplication on 0 and 1, and OR almost behaves like addition. The one surprise is that 1 + 1 = 1: OR has no carry, it just asks "is anything true?".
```

A **truth table** lists the output for every input combination. Each extra input doubles the number of combinations, so the table size grows quickly:

```formula
N_rows = 2^n
N_rows = 2^3 = 8   for n = 3
where
N_rows: the number of rows in the truth table, one per input combination
n: the number of inputs (Boolean variables)
2^n: n copies of 2 multiplied together. Each input can be 0 or 1, and every new input doubles the number of combinations
In words: a truth table for n inputs has 2^n rows, so three inputs need 8 rows and four need 16.
```

Here is the table for the three operations, with two inputs:

```
 A B | AB  A+B  A'
-----+-------------
 0 0 |  0   0    1
 0 1 |  0   1    1
 1 0 |  0   1    0
 1 1 |  1   1    0
```

**Precedence**: NOT binds tightest, then AND, then OR, just as powers come before multiplication and multiplication before addition in arithmetic. A NOT written after a bracket applies to the whole bracket:

```formula
A + B·C′ = A + (B·(C′))
(A·B)′ ≠ A′·B′
where
A, B, C: Boolean variables, each 0 or 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
C′, A′, B′: NOT C, NOT A, NOT B: the complement of that one variable
( )′: NOT applied to everything inside the bracket
≠: is not equal to (not the same function: some input gives a different output)
In words: NOT grabs only the thing directly before it, AND is done before OR, and a NOT over a whole group is very different from a NOT on each variable. With A = 1 and B = 0, (A·B)′ is 1 but A′·B′ is 0.
```

### Exclusive OR

One more operation is so common it gets its own symbol. **XOR** (`A ⊕ B`) is 1 when the inputs *differ*:

```
 A B | A⊕B
-----+-----
 0 0 |  0
 0 1 |  1
 1 0 |  1
 1 1 |  0
```

XOR is addition modulo 2: add the bits and keep only the remainder after dividing by 2, so 1 + 1 = 2 leaves 0. That is why it turns up in adders, parity bits, checksums and CRCs. Four facts are worth knowing by heart:

```formula
A ⊕ 0 = A
A ⊕ 1 = A′
A ⊕ A = 0
A ⊕ B = A′·B + A·B′
where
A, B: Boolean variables, each 0 or 1
⊕: XOR (exclusive OR): 1 when the two sides differ, 0 when they are equal
A′, B′: NOT A, NOT B
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: XOR with 0 changes nothing, XOR with 1 flips the bit, anything XORed with itself is 0, and XOR means "A is 0 and B is 1, or A is 1 and B is 0".
```

Its complement, **XNOR**, is 1 when the inputs are equal.

## The laws

These identities hold for every value of the variables. You can check any of them by writing out the truth table. Each law comes as a pair: an AND form and an OR form.

| Law | What it says |
|---|---|
| Identity | AND with 1, or OR with 0, changes nothing |
| Null | AND with 0 always gives 0; OR with 1 always gives 1 |
| Idempotent | combining a variable with itself gives the variable |
| Complement | a variable AND its NOT is 0; a variable OR its NOT is 1 |
| Involution | NOT twice gives back the original |
| Commutative | the order of the two sides does not matter |
| Associative | the grouping of three terms does not matter |
| Distributive | AND distributes over OR, *and* OR distributes over AND |
| Absorption | A combined with a term that contains A is just A |
| De Morgan | a NOT over a group complements each variable and swaps AND with OR |

The one-variable laws, in table order (identity, null, idempotent, complement, involution), AND form on the left and OR form on the right:

```formula
A·1 = A        A + 0 = A
A·0 = 0        A + 1 = 1
A·A = A        A + A = A
A·A′ = 0       A + A′ = 1
(A′)′ = A
where
A: a Boolean variable, 0 or 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
A′: NOT A: 1 when A is 0, and 0 when A is 1
(A′)′: NOT applied twice to A
In words: line by line, these are the identity, null, idempotent, complement and involution laws. Each one can be checked by trying A = 0 and A = 1.
```

The laws with two or three variables, in table order (commutative, associative, distributive, absorption, De Morgan):

```formula
A·B = B·A        A + B = B + A
(A·B)·C = A·(B·C)
(A + B) + C = A + (B + C)
A·(B + C) = A·B + A·C
A + B·C = (A + B)·(A + C)
A·(A + B) = A    A + A·B = A
(A·B)′ = A′ + B′
(A + B)′ = A′·B′
where
A, B, C: Boolean variables, each 0 or 1
·: AND: 1 only when both sides are 1 (the text often writes A·B as AB)
+: OR: 1 when at least one side is 1
A′, B′: NOT A, NOT B
( )′: NOT applied to the whole bracket
In words: order and grouping do not matter, each operator distributes over the other, a term is absorbed by a simpler term it contains, and De Morgan pushes a NOT inside a bracket by complementing each variable and swapping AND with OR.
```

Two of these surprise people who know ordinary algebra.

**OR distributes over AND.** In arithmetic, 1 + 2 × 3 is 7 but (1 + 2) × (1 + 3) is 12, so the rule fails. In Boolean algebra it holds. Expand the right-hand side, then use idempotence and absorption:

```formula
(A + B)·(A + C)
  = A·A + A·C + A·B + B·C
  = A + A·C + A·B + B·C
  = A + B·C
where
A, B, C: Boolean variables, each 0 or 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: multiply out the brackets as usual; A·A is just A (idempotence), and A swallows A·C and A·B (absorption), leaving A + B·C.
```

**Absorption**: A + A·B is just A. If A is 1 the whole thing is 1; if A is 0 then A·B is 0 too. The A·B term adds nothing.

A close cousin of absorption is worth memorising. Check it by trying both values of A:

```formula
A + A′·B = A + B
1 + 0·B = 1 = 1 + B     for A = 1
0 + 1·B = B = 0 + B     for A = 0
where
A, B: Boolean variables, each 0 or 1
A′: NOT A: 1 when A is 0, and 0 when A is 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: if A is 1 both sides are 1; if A is 0 both sides reduce to B. So "A, or (not A and B)" is the same as "A or B".
```

### Duality

Notice that each law comes in a mirrored pair. Swap AND with OR and 0 with 1 in any law and you get another valid law. This is the **duality principle**, and it halves the number of rules you need to remember.

## De Morgan's theorem

De Morgan's laws are the most-used tool in logic design. They tell you how to push a NOT inside a bracket:

```formula
(A·B)′ = A′ + B′
(A + B)′ = A′·B′
(A·B·C)′ = A′ + B′ + C′
where
A, B, C: Boolean variables, each 0 or 1
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
A′, B′, C′: NOT A, NOT B, NOT C
( )′: NOT applied to the whole bracket
In words: "not (A and B)" is the same as "not A, or not B", and "not (A or B)" is "not A and not B". To push a NOT through a group, complement each variable and swap AND with OR. The third line shows it works for any number of terms.
```

Proof by truth table:

```
 A B | (AB)'  A'+B' | (A+B)'  A'B'
-----+--------------+--------------
 0 0 |   1      1   |   1      1
 0 1 |   1      1   |   0      0
 1 0 |   1      1   |   0      0
 1 1 |   0      0   |   0      0
```

Programmers use this daily. `if not (logged_in and is_admin)` is the same test as `if not logged_in or not is_admin`. In hardware it matters even more, because simple inverting multi-input gates in conventional complementary CMOS include NAND and NOR (next lesson), and De Morgan is how you convert between AND/OR designs and NAND/NOR ones.

## Simplifying with algebra

Take the **majority function** of three inputs: output 1 when at least two of A, B and C are 1. Reading the rows where it is 1 straight off the truth table gives four terms, one per row:

```formula
Maj = A′·B·C + A·B′·C + A·B·C′ + A·B·C
where
Maj: the majority function of A, B and C: 1 when at least two of them are 1
A, B, C: the three inputs, each 0 or 1
A′, B′, C′: NOT A, NOT B, NOT C
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the output is 1 on exactly four rows: 011, 101, 110 and 111 (A, B, C in that order). Each term is 1 on just one of those rows.
```

That is four 3-input AND terms and a 4-input OR. Now simplify. The trick is idempotence: A·B·C = A·B·C + A·B·C + A·B·C, so we can reuse the A·B·C term three times, pairing it with each of the others. Each pair then differs in only one variable, and the complement law (A′ + A = 1) removes that variable:

```formula
Maj = (A′·B·C + A·B·C)
    + (A·B′·C + A·B·C)
    + (A·B·C′ + A·B·C)
    = B·C·(A′ + A) + A·C·(B′ + B)
    + A·B·(C′ + C)
    = B·C + A·C + A·B
where
Maj: the majority function of A, B and C
A, B, C: the three inputs, each 0 or 1
A′, B′, C′: NOT A, NOT B, NOT C
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: pair the all-ones term with each other term, factor out what they share, and each bracket of the form (X′ + X) becomes 1. The result says "some pair of inputs is 1".
```

Three 2-input ANDs and a 3-input OR. This exact function is the carry-out of a binary adder, which you will meet in lesson 4.

Algebraic simplification works, but it relies on spotting the right move. The next-but-one lesson introduces Karnaugh maps, which make the moves visual.

### The consensus theorem

One more identity removes redundant terms:

```formula
A·B + A′·C + B·C = A·B + A′·C
where
A, B, C: Boolean variables, each 0 or 1
A′: NOT A
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the term B·C (the consensus of A·B and A′·C) can be dropped without changing the function.
```

Why B·C is redundant: whenever B and C are both 1, either A is 1 (so A·B covers it) or A is 0 (so A′·C covers it). B·C is never needed for correctness. Hold that thought: in lesson 3 you will see that adding it back on purpose removes a timing glitch.

## Canonical forms

Any Boolean function can be written straight from its truth table in two standard ways.

### Sum of products (SOP) and minterms

A **minterm** is an AND of every variable, each either plain or complemented, that is 1 for exactly one row. Number the rows by reading the inputs as a binary number (A as the most significant bit), so row `A=1, B=0, C=1` is 101 in binary, which is 5:

```formula
m_5 = A·B′·C
m_5 = 1·1·1 = 1   for A = 1, B = 0, C = 1
where
m_5: minterm number 5: the product term that is 1 on row 5 (inputs 101) and 0 on every other row
A, B, C: the inputs, each 0 or 1
B′: NOT B: here B is 0, so B′ is 1
·: AND: 1 only when both sides are 1
In words: use each variable plain where the row has a 1 and complemented where it has a 0, so the term is 1 on that one row only.
```

The **canonical SOP** ORs together the minterms of every row where the output is 1. The majority function above is 1 on rows 011, 101, 110 and 111, which are rows 3, 5, 6 and 7:

```formula
Maj = Σm(3, 5, 6, 7)
Maj = m_3 + m_5 + m_6 + m_7
where
Maj: the majority function of A, B and C
Σm(…): shorthand for "OR together the minterms with these row numbers" (Σ, the Greek capital sigma, means "sum of")
m_3, m_5, m_6, m_7: the minterms of rows 3, 5, 6 and 7, for example m_3 = A′·B·C
+: OR: 1 when at least one side is 1
In words: the majority function is 1 exactly on rows 3, 5, 6 and 7, and this is the shorthand for the four-term SOP written out earlier.
```

### Product of sums (POS) and maxterms

A **maxterm** is an OR of every variable that is 0 for exactly one row: complement the variables that are 1 in that row. For row `A=0, B=1, C=0` (row 2):

```formula
M_2 = A + B′ + C
M_2 = 0 + 0 + 0 = 0
where
M_2: maxterm number 2: the sum term that is 0 on row 2 (inputs 010) and 1 on every other row
A, B, C: the inputs, each 0 or 1; on row 2, A = 0, B = 1 and C = 0
B′: NOT B: here B is 1, so B′ is 0
+: OR: 1 when at least one side is 1
In words: a maxterm uses each variable plain where the row has a 0 and complemented where it has a 1, so every part is 0 on that one row and the OR is 0 there only.
```

The **canonical POS** ANDs together the maxterms of every row where the output is 0. The majority function is 0 on rows 0, 1, 2 and 4:

```formula
Maj = ΠM(0, 1, 2, 4)
Maj = (A + B + C)·(A + B + C′)
      ·(A + B′ + C)·(A′ + B + C)
where
Maj: the majority function of A, B and C
ΠM(…): shorthand for "AND together the maxterms with these row numbers" (Π, the Greek capital pi, means "product of")
A, B, C: the inputs, each 0 or 1
A′, B′, C′: NOT A, NOT B, NOT C
+: OR: 1 when at least one side is 1
·: AND: 1 only when both sides are 1
In words: each bracket is 0 on exactly one of the rows where the majority is 0, so the AND of all four is 0 on those rows and 1 everywhere else.
```

SOP lists where the function is 1; POS lists where it is 0. The index sets are complements of each other: {3, 5, 6, 7} and {0, 1, 2, 4} together make every row from 0 to 7. Both describe the same function, and neither is usually minimal; they are a starting point.

### Counting functions

Each row of a truth table can independently output 0 or 1, so the number of different functions grows extremely fast with the number of inputs:

```formula
N_f = 2^{2^n}
N_f = 2^{2^2} = 2^4 = 16        for n = 2
N_f = 2^{2^4} = 2^16 = 65536    for n = 4
where
N_f: the number of different Boolean functions of n inputs
n: the number of inputs
2^n: the number of truth-table rows (n copies of 2 multiplied together)
2^{2^n}: 2 raised to the number of rows: each row's output is a free 0-or-1 choice
In words: two inputs give 16 different functions (AND, OR, XOR, NAND and 12 more); four inputs already give 65,536.
```

## Checking identities in Python

Because a function has only finitely many input combinations (16 for four inputs, about a million for twenty), a computer can prove a Boolean identity by trying every input combination. This is the same idea that **equivalence checkers** in chip design tools use, with much cleverer algorithms for many inputs.

```python
from itertools import product

def equivalent(f, g, n):
    return all(f(*v) == g(*v)
               for v in product((0, 1),
                                repeat=n))

# De Morgan
lhs = lambda a, b: 1 - (a & b)
rhs = lambda a, b: (1 - a) | (1 - b)
print(equivalent(lhs, rhs, 2))   # True

# Consensus
f = lambda a, b, c: (a & b) | ((1-a) & c) \
                    | (b & c)
g = lambda a, b, c: (a & b) | ((1-a) & c)
print(equivalent(f, g, 3))       # True
```

> [!warning] Python's `~` is not Boolean NOT
> On Python integers, `~a` is bitwise NOT in two's complement, so `~1` is `-2` and `~0` is `-1`. Use `1 - a`, `a ^ 1` or `not a` for a single bit. The same trap exists in C, where !1 is 0 but ~1 is a promoted-int bitwise operation; on a 32-bit two's-complement int it is -2, with representation 0xFFFFFFFE.

## Pitfalls

- **Reading `(AB)'` as `A'B'`.** A NOT over a group is not distributed variable by variable. Apply De Morgan, which also swaps the operator.
- **Forgetting that OR has no carry.** In Boolean algebra, 1 OR 1 is 1. If you need a carry, you need XOR and AND (an adder).
- **Over-applying cancellation.** Knowing that "A OR B" equals "A OR C" does not tell you that B equals C: if A is 1, both sides are 1 whatever B and C are. Boolean algebra has no subtraction or division.
- **Assuming canonical means minimal.** The canonical SOP for majority uses four 3-input terms; the minimal form uses three 2-input terms.

## Key takeaways
- Boolean algebra has two values and three fundamental operations: AND, OR and NOT. XOR is addition mod 2.
- The laws come in dual pairs. The non-obvious ones are that OR distributes over AND, absorption (A OR (A AND B) is just A), and that "A, or (not A and B)" equals "A or B".
- De Morgan: complement each variable and swap AND with OR. It is how designs move between AND/OR and NAND/NOR.
- Any function can be written as a canonical sum of minterms (where it is 1) or product of maxterms (where it is 0). Simplification then reduces it.
- With few inputs, a truth table (or a script that tries every input) is a complete proof.

## Further reading
- [Boolean algebra — Wikipedia](https://en.wikipedia.org/wiki/Boolean_algebra)
- [De Morgan's laws — Wikipedia](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
- [Canonical normal form (minterms and maxterms) — Wikipedia](https://en.wikipedia.org/wiki/Canonical_normal_form)
- [A Symbolic Analysis of Relay and Switching Circuits — Wikipedia](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits)
- [Nand2Tetris: build a computer from first principles](https://www.nand2tetris.org/)
