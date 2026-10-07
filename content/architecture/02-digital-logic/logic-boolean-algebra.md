---
id: logic-boolean-algebra
title: Boolean algebra
level: basic
minutes: 12
summary: The algebra of true and false that every circuit is built on, its laws, De Morgan's theorem, truth tables, and the canonical sum-of-products and product-of-sums forms.
---

Boolean algebra models binary signals with values 0 and 1. Physical digital circuits use voltage ranges, have transition intervals and may encounter unknown, metastable or high-impedance states; sequential circuits also depend on stored state. The mathematics of such functions is **Boolean algebra**, named after George Boole, who described an algebra of logic in 1847 and 1854.

For almost a century it was a topic for logicians. Then in 1937 Claude Shannon's master's thesis showed that circuits of relays obey exactly Boole's rules. That idea is the bridge from logic to hardware: write the behaviour you want as a Boolean expression, simplify it with algebra, and the simplified expression can suggest a smaller circuit; actual area, delay and power depend on the implementation.

This lesson covers the operations, the laws, and the two standard ways of writing any function down.

## Values and the three basic operations

A Boolean variable takes one of two values: 0 or 1 (mapped here using positive logic to low and high voltage ranges). There are three basic operations.

- **AND** (written `A·B` or just `AB`): 1 only when both inputs are 1.
- **OR** (written `A + B`): 1 when at least one input is 1.
- **NOT** (written `A'`, `¬A` or with a bar over A): flips the value.

A **truth table** lists the output for every input combination. With *n* inputs there are 2^n rows.

```
 A B | AB  A+B  A'
-----+-------------
 0 0 |  0   0    1
 0 1 |  0   1    1
 1 0 |  0   1    0
 1 1 |  1   1    0
```

The notation borrows from arithmetic on purpose: AND behaves like multiplication on 0 and 1, and OR almost behaves like addition. The difference is `1 + 1 = 1`. There is no carry; OR just asks "is anything true?".

**Precedence**: NOT binds tightest, then AND, then OR. So `A + BC'` means `A + (B·(C'))`. A bar drawn over a whole group, such as `(AB)'`, applies to the group, which is very different from `A'B'`.

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

XOR is addition modulo 2, which is why it turns up in adders, parity bits, checksums and CRCs. Useful facts: `A ⊕ 0 = A`, `A ⊕ 1 = A'`, `A ⊕ A = 0`, and in terms of the basic operations `A ⊕ B = A'B + AB'`. Its complement, **XNOR**, is 1 when the inputs are equal.

## The laws

These identities hold for every value of the variables. You can check any of them by writing out the truth table.

| Law | AND form | OR form |
|---|---|---|
| Identity | `A·1 = A` | `A + 0 = A` |
| Null | `A·0 = 0` | `A + 1 = 1` |
| Idempotent | `A·A = A` | `A + A = A` |
| Complement | `A·A' = 0` | `A + A' = 1` |
| Involution | `(A')' = A` | |
| Commutative | `AB = BA` | `A+B = B+A` |
| Associative | `(AB)C = A(BC)` | `(A+B)+C = A+(B+C)` |
| Distributive | `A(B+C) = AB+AC` | `A+BC = (A+B)(A+C)` |
| Absorption | `A(A+B) = A` | `A + AB = A` |
| De Morgan | `(AB)' = A'+B'` | `(A+B)' = A'B'` |

Two of these surprise people who know ordinary algebra:

- **OR distributes over AND**: `A + BC = (A+B)(A+C)`. In arithmetic, `a + bc` is not `(a+b)(a+c)`, but in Boolean algebra it is. Expand the right-hand side: `AA + AC + AB + BC = A + AC + AB + BC = A + BC`, using idempotence and then absorption.
- **Absorption**: `A + AB = A`. If A is 1 the whole thing is 1; if A is 0 then AB is 0 too. The `AB` term adds nothing.

A close cousin of absorption is worth memorising: `A + A'B = A + B`. If A is 1, both sides are 1. If A is 0, both sides reduce to B.

### Duality

Notice that the two columns of the table mirror each other. Swap AND with OR and 0 with 1 in any law and you get another valid law. This is the **duality principle**, and it halves the number of rules you need to remember.

## De Morgan's theorem

De Morgan's laws are the most-used tool in logic design:

```
(A·B)' = A' + B'
(A + B)' = A'·B'
```

In words: "not (A and B)" is the same as "not A, or not B". To push a NOT through a group, **complement each variable and swap AND with OR**. It generalises to any number of terms: `(ABC)' = A' + B' + C'`.

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

Take the **majority function** of three inputs: output 1 when at least two of A, B and C are 1. Reading the rows where it is 1 straight off the truth table gives:

```
M = A'BC + AB'C + ABC' + ABC
```

That is four 3-input AND terms and a 4-input OR. Now simplify. The trick is idempotence: `ABC = ABC + ABC + ABC`, so we can reuse ABC three times.

```
M = (A'BC + ABC) + (AB'C + ABC)
                 + (ABC' + ABC)
  = BC(A' + A) + AC(B' + B)
                 + AB(C' + C)
  = BC + AC + AB
```

Three 2-input ANDs and a 3-input OR. This exact function is the carry-out of a binary adder, which you will meet in lesson 4.

Algebraic simplification works, but it relies on spotting the right move. The next-but-one lesson introduces Karnaugh maps, which make the moves visual.

### The consensus theorem

One more identity removes redundant terms:

```
AB + A'C + BC = AB + A'C
```

The `BC` term is the **consensus** of the other two. Whenever B and C are both 1, either A is 1 (so AB covers it) or A is 0 (so A'C covers it). BC is never needed for correctness. Hold that thought: in lesson 3 you will see that adding it back on purpose removes a timing glitch.

## Canonical forms

Any Boolean function can be written straight from its truth table in two standard ways.

### Sum of products (SOP) and minterms

A **minterm** is an AND of every variable, each either plain or complemented, that is 1 for exactly one row. For row `A=1, B=0, C=1` the minterm is `AB'C`. Number the rows by reading the inputs as a binary number, so this is minterm 5, written `m5`.

The **canonical SOP** ORs together the minterms of every row where the output is 1. The majority function above is:

```
M = Σm(3, 5, 6, 7)
```

because rows 011, 101, 110 and 111 are the 1s.

### Product of sums (POS) and maxterms

A **maxterm** is an OR of every variable that is 0 for exactly one row. For row `A=0, B=1, C=0` (row 2), the maxterm is `A + B' + C`: complement the variables that are 1 in that row. The **canonical POS** ANDs together the maxterms of every row where the output is 0:

```
M = ΠM(0, 1, 2, 4)
  = (A+B+C)(A+B+C')(A+B'+C)(A'+B+C)
```

SOP lists where the function is 1; POS lists where it is 0. The index sets are complements of each other. Both describe the same function, and neither is usually minimal; they are a starting point.

> [!tip] Counting functions
> With *n* inputs there are 2^n rows, and each row's output can be 0 or 1, so there are 2^(2^n) different functions. Two inputs give 16 (AND, OR, XOR, NAND and 12 more). Four inputs already give 65,536.

## Checking identities in Python

Because there are only 2^n input combinations, a computer can prove a Boolean identity by brute force. This is the same idea that **equivalence checkers** in chip design tools use, with much cleverer algorithms for large *n*.

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
- **Forgetting that `1 + 1 = 1`.** OR has no carry. If you need a carry, you need XOR and AND (an adder).
- **Over-applying cancellation.** `A + B = A + C` does not imply `B = C` (try A = 1). Boolean algebra has no subtraction or division.
- **Assuming canonical means minimal.** The canonical SOP for majority uses four 3-input terms; the minimal form uses three 2-input terms.

## Key takeaways
- Boolean algebra has two values and three basic operations: AND, OR and NOT. XOR is addition mod 2.
- The laws come in dual pairs. The non-obvious ones are `A + BC = (A+B)(A+C)`, absorption `A + AB = A`, and `A + A'B = A + B`.
- De Morgan: complement each variable and swap AND with OR. It is how designs move between AND/OR and NAND/NOR.
- Any function can be written as a canonical sum of minterms (where it is 1) or product of maxterms (where it is 0). Simplification then reduces it.
- With few inputs, a truth table (or a brute-force script) is a complete proof.

## Further reading
- [Boolean algebra — Wikipedia](https://en.wikipedia.org/wiki/Boolean_algebra)
- [De Morgan's laws — Wikipedia](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
- [Canonical normal form (minterms and maxterms) — Wikipedia](https://en.wikipedia.org/wiki/Canonical_normal_form)
- [A Symbolic Analysis of Relay and Switching Circuits — Wikipedia](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits)
- [Nand2Tetris: build a computer from first principles](https://www.nand2tetris.org/)
