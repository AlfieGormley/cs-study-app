---
id: logp-propositional
title: Propositional logic
level: basic
minutes: 13
summary: Propositions, connectives and truth tables, why "if p then q" behaves the way it does, the equivalences you use to simplify conditions, and valid versus invalid arguments.
---

Every `if` statement you have written is a small piece of logic. Propositional logic is the precise version of that: a way of combining true/false statements and working out, mechanically, when the combination is true.

It is the foundation for everything else in this module. Proofs are built from it, predicate logic extends it, and the SAT problem in the last lesson asks one question about it that turns out to be enormously hard and enormously useful.

## Propositions

In the classical two-valued logic used here, a proposition is a statement that is either true or false, never both.

- "7 is prime" is a proposition (true).
- "2 + 2 = 5" is a proposition (false).
- "x > 3" is **not** a proposition on its own: its truth depends on x. (Predicate logic, next lesson, handles this.)
- "Close the door" is not a proposition: it is neither true nor false.

We name propositions with letters: p, q, r. These are **propositional variables**, the logical equivalent of Boolean variables in code.

## The connectives

Five connectives build bigger formulas from smaller ones.

| Symbol | Name | Read as | Python |
|---|---|---|---|
| ¬p | negation | not p | `not p` |
| p ∧ q | conjunction | p and q | `p and q` |
| p ∨ q | disjunction | p or q | `p or q` |
| p → q | implication | if p then q | `(not p) or q` |
| p ↔ q | biconditional | p if and only if q | `p == q` |

The Python column assumes Boolean operands. Python and/or return operands and short-circuit; arbitrary objects can have custom truth tests and equality. The logical connectives have their meaning fixed by a **truth table**, which lists every combination of inputs. With two variables there are 2² = 4 rows; with n variables there are 2ⁿ.

```
p q | ¬p  p∧q  p∨q  p→q  p↔q
----+-------------------------
T T |  F   T    T    T    T
T F |  F   F    T    F    F
F T |  T   F    T    T    F
F F |  T   F    F    T    T
```

Two things trip people up.

- **∨ is inclusive.** p ∨ q is true when both are true. "Exclusive or" (exactly one) is a separate connective, written ⊕, and equals ¬(p ↔ q). In Python on booleans it is `p != q`.
- **→ is false in exactly one row**: when p is true and q is false.

## Why implication works this way

The bottom two rows of p → q surprise everyone. Why is "if p then q" true whenever p is false?

Think of p → q as a **promise**. "If you pass the exam, I'll buy you dinner." The only way I break the promise is if you pass (p true) and I don't buy dinner (q false). If you fail, I have kept my word whatever I do. A promise that was never triggered was never broken.

This is called **vacuous truth**, and it matters. "Every element of the empty list is negative" is true, because there is no element to break it. Python agrees: `all([])` is `True`.

The connective defined by this table is the **material conditional**. It says nothing about cause. "If 2 + 2 = 5 then the Moon is cheese" is true, because the premise is false. That feels wrong in English, but it is the definition that makes proofs work.

> [!tip] Reading p → q
> All of these mean p → q: "if p then q", "p implies q", "p only if q", "q if p", "p is sufficient for q", "q is necessary for p". The phrase "p only if q" catches people out: it means p cannot happen without q, which is p → q, not q → p.

## Converse, inverse, contrapositive

From an implication p → q you can form three related statements.

| Name | Form | Same as p → q? |
|---|---|---|
| Contrapositive | ¬q → ¬p | Yes, always |
| Converse | q → p | Not in general |
| Inverse | ¬p → ¬q | Not in general |

"If it is raining, the ground is wet" does not mean "if the ground is wet, it is raining" (a sprinkler could be on). That is the converse, and assuming it is one of the most common reasoning errors in proofs, code reviews and incident postmortems.

The contrapositive, "if the ground is not wet, it is not raining", is equivalent. You can check by truth table: both are false in exactly the row p = T, q = F. The converse and the inverse are equivalent to *each other* (one is the contrapositive of the other).

## Tautologies, contradictions, satisfiable formulas

Tautology, contradiction and contingency form three disjoint classes. Satisfiability is a related property that overlaps them:

- A **tautology** is true in every row. Example: p ∨ ¬p.
- A **contradiction** is false in every row. Example: p ∧ ¬p.
- A contingent formula is true in some rows and false in others.
- A formula is satisfiable if at least one row makes it true: both tautologies and contingent formulas qualify.

These are linked: F is a tautology exactly when ¬F is unsatisfiable. SAT solvers exploit this to check that something *always* holds: they search for a row where it fails, and "no such row" is a proof.

## Logical equivalence

Two formulas are **logically equivalent**, written A ≡ B, if they have the same truth value in every row. Equivalently, A ↔ B is a tautology.

These are the laws you use daily to simplify conditions.

| Law | Equivalence |
|---|---|
| Double negation | ¬¬p ≡ p |
| De Morgan | ¬(p ∧ q) ≡ ¬p ∨ ¬q |
| De Morgan | ¬(p ∨ q) ≡ ¬p ∧ ¬q |
| Implication | p → q ≡ ¬p ∨ q |
| Contrapositive | p → q ≡ ¬q → ¬p |
| Distribution | p ∧ (q ∨ r) ≡ (p ∧ q) ∨ (p ∧ r) |
| Distribution | p ∨ (q ∧ r) ≡ (p ∨ q) ∧ (p ∨ r) |
| Absorption | p ∨ (p ∧ q) ≡ p |
| Biconditional | p ↔ q ≡ (p → q) ∧ (q → p) |

Commutativity, associativity and identities such as p ∧ T ≡ p and p ∨ T ≡ T complete the toolkit.

> [!example] Simplifying a guard
> A code review finds `if not (user.banned or not user.verified):`. Apply De Morgan, then double negation:
>
> ¬(b ∨ ¬v) ≡ ¬b ∧ ¬¬v ≡ ¬b ∧ v
>
> So it is `if not user.banned and user.verified:`, which reads far better.

You can also prove an equivalence algebraically. Here is ¬(p → q) ≡ p ∧ ¬q, which tells you exactly when an implication fails:

```
¬(p → q)
≡ ¬(¬p ∨ q)      implication law
≡ ¬¬p ∧ ¬q       De Morgan
≡ p ∧ ¬q         double negation
```

## Checking equivalence in code

With n variables there are only 2ⁿ rows, so a computer can check any equivalence by brute force.

```python
from itertools import product

def equivalent(f, g, n):
    for v in product([False, True],
                     repeat=n):
        if f(*v) != g(*v):
            return False, v
    return True, None

imp = lambda p, q: (not p) or q
contra = lambda p, q: imp(not q, not p)
conv = lambda p, q: imp(q, p)

print(equivalent(imp, contra, 2))
print(equivalent(imp, conv, 2))
```

The output is `(True, None)` then `(False, (False, True))`. The second line hands you a counterexample: with p false and q true, p → q is true but its converse q → p is false.

This works for 10 or 20 variables. At 60 variables it is 2⁶⁰ ≈ 10¹⁸ rows, and brute force is hopeless. That gap is the subject of the SAT lesson.

## Precedence

By convention, ¬ binds tightest, then ∧, then ∨, then →, then ↔. So ¬p ∧ q → r means ((¬p) ∧ q) → r. Implication is usually read right-associatively: p → q → r means p → (q → r).

Python follows the same order for `not`, `and`, `or`. When in doubt, add brackets: other people will read the code too.

## Valid arguments

An **argument** has premises and a conclusion. It is **valid** if the conclusion is true in every row where all the premises are true. Equivalently, (P1 ∧ P2 ∧ ...) → C is a tautology.

The standard valid forms:

| Rule | Premises | Conclusion |
|---|---|---|
| Modus ponens | p → q, p | q |
| Modus tollens | p → q, ¬q | ¬p |
| Hypothetical syllogism | p → q, q → r | p → r |
| Disjunctive syllogism | p ∨ q, ¬p | q |

And two famous invalid ones:

- **Affirming the consequent**: from p → q and q, conclude p. Invalid (row p = F, q = T).
- **Denying the antecedent**: from p → q and ¬p, conclude ¬q. Invalid (same row).

> [!warning] Debugging with the converse
> "If the cache is down, latency spikes. Latency spiked, so the cache is down." That is affirming the consequent. Latency spikes have many causes. Modus tollens is the safe direction: "latency did not spike, so the cache is not down" (given the premise holds).

Validity is about form, not truth. "If pigs fly, I am the Queen; pigs fly; so I am the Queen" is valid. Its conclusion is false only because a premise is false. An argument that is valid *and* has true premises is called **sound**.

## How many connectives do you need?

Not five. Since p → q ≡ ¬p ∨ q and p ↔ q ≡ (p → q) ∧ (q → p), the set {¬, ∧, ∨} can express every truth table. By De Morgan, even {¬, ∧} alone suffices. A set like this is **functionally complete**.

Remarkably, a single connective is enough: **NAND** (written ↑, p ↑ q ≡ ¬(p ∧ q)).

```
¬p     ≡ p ↑ p
p ∧ q  ≡ (p ↑ q) ↑ (p ↑ q)
p ∨ q  ≡ (p ↑ p) ↑ (q ↑ q)
```

This is why chips can be built from NAND gates alone. NOR is also complete on its own; AND, OR and NOT individually are not.

## Key takeaways
- A proposition is true or false; connectives combine them, and a truth table with 2ⁿ rows defines any formula's meaning.
- p → q is false only when p is true and q is false; when p is false it is vacuously true.
- The contrapositive ¬q → ¬p is always equivalent to p → q; converse and inverse are not equivalent to it in general.
- De Morgan, implication-as-disjunction and distribution let you simplify conditions safely.
- An argument is valid when the conclusion holds in every row where the premises do; affirming the consequent is the classic fallacy.
- {¬, ∧} and NAND alone are functionally complete.

## Further reading
- [Propositional calculus — Wikipedia](https://en.wikipedia.org/wiki/Propositional_calculus)
- [Truth table — Wikipedia](https://en.wikipedia.org/wiki/Truth_table)
- [Material conditional — Wikipedia](https://en.wikipedia.org/wiki/Material_conditional)
- [De Morgan's laws — Wikipedia](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
- [Functional completeness — Wikipedia](https://en.wikipedia.org/wiki/Functional_completeness)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
