---
id: logic-algebra-proof
title: Simplify and test Boolean identities
level: basic
minutes: 5
sourceLesson: logic-boolean-algebra
summary: Pairing terms can eliminate a changing variable.
---

## Simplifying with algebra

Take the **majority function** of three inputs: output 1 when at least two of A, B and C are 1. Reading the rows where it is 1 straight off the truth table gives four terms, one per row:

```formula essential
Maj = A′·B·C + A·B′·C + A·B·C′ + A·B·C
where
Maj: the majority function of A, B and C: 1 when at least two of them are 1
A, B, C: the three inputs, each 0 or 1
A′, B′, C′: NOT A, NOT B, NOT C
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the output is 1 on exactly four rows: 011, 101, 110 and 111 (A, B, C in that order). Each term is 1 on just one of those rows.
```

That is four 3-input AND terms and a 4-input OR. Pair each two-ones row with the all-ones row. In each pair, one input changes while the other two stay high, so the changing input does not affect that pair's output. Reusing the all-ones row is allowed: OR does not count how many times a row is covered.

```formula essential
Maj = B·C + A·C + A·B
where
Maj: the majority function of A, B and C
A, B, C: the three inputs, each 0 or 1
A′, B′, C′: NOT A, NOT B, NOT C
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the majority output is high whenever any pair of inputs is high. Covering the all-high case more than once does not change its output.
```

Three 2-input ANDs and a 3-input OR. This exact function is the carry-out of a binary adder, which you will meet in adder lessons.

Algebraic simplification works, but it relies on spotting the right move. The K-map lessons introduce Karnaugh maps, which make the moves visual.

### The consensus theorem

One more identity removes redundant terms:

```formula essential
A·B + A′·C + B·C = A·B + A′·C
where
A, B, C: Boolean variables, each 0 or 1
A′: NOT A
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the term B·C (the consensus term of A·B and A′·C) can be dropped without changing the function.
```

Why B·C is redundant: whenever B and C are both 1, either A is 1 (so A·B covers it) or A is 0 (so A′·C covers it). B·C is never needed for correctness. Hold that thought: in K-map lessons you will see that adding it back on purpose removes a timing glitch.

## Checking identities in Python

Because a function has only finitely many input combinations (16 for four inputs, about a million for twenty), a computer can prove a Boolean identity by trying every input combination. This is the same idea that **equivalence checkers** in chip design tools use, with much cleverer algorithms for many inputs.

```python
from itertools import product

# Try every tuple of single-bit inputs.
def equivalent(f, g, n):
    # Every output must match, not a sample.
    return all(f(*v) == g(*v)
               for v in product((0, 1),
                                repeat=n))

# De Morgan: both truth tables must agree.
lhs = lambda a, b: 1 - (a & b)
rhs = lambda a, b: (1 - a) | (1 - b)
print(equivalent(lhs, rhs, 2))   # True

# Consensus term covers no extra rows.
f = lambda a, b, c: (a & b) | ((1-a) & c) \
                    | (b & c)
g = lambda a, b, c: (a & b) | ((1-a) & c)
print(equivalent(f, g, 3))       # True
```

> [!warning] Python's `~` is not Boolean NOT
> On Python integers, `~a` is bitwise NOT in two's complement, so `~1` is `-2` and `~0` is `-1`. Use `1 - a`, `a ^ 1` or `not a` for a single bit. The same trap exists in C, where !1 is 0 but ~1 is a promoted-int bitwise operation; on a 32-bit two's-complement int it is -2, with representation 0xFFFFFFFE.


## Pitfalls

**Misreading a complemented group.** NOT applied to a whole AND differs from AND applied to two complemented inputs. De Morgan also swaps AND with OR.
- **Forgetting that OR has no carry.** In Boolean algebra, 1 OR 1 is 1. If you need a carry, you need XOR and AND (an adder).
- **Over-applying cancellation.** Knowing that "A OR B" equals "A OR C" does not tell you that B equals C: if A is 1, both sides are 1 whatever B and C are. Boolean algebra has no subtraction or division.
- **Assuming canonical means minimal.** The canonical SOP for majority uses four 3-input terms; the minimal form uses three 2-input terms.

## Key takeaways
- Pairing terms can eliminate a changing variable.
- Consensus term is logically redundant; exhaustive finite checks prove small identities.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Boolean algebra — Wikipedia](https://en.wikipedia.org/wiki/Boolean_algebra)
- [De Morgan's laws — Wikipedia](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
- [Canonical normal form (minterms and maxterms) — Wikipedia](https://en.wikipedia.org/wiki/Canonical_normal_form)
- [A Symbolic Analysis of Relay and Switching Circuits — Wikipedia](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits)
- [Nand2Tetris: build a computer from first principles](https://www.nand2tetris.org/)
