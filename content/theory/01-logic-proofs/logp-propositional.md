---
id: logp-propositional
title: Propositional logic
level: basic
minutes: 16
summary: Propositions, connectives and truth tables, why "if p then q" behaves the way it does, the equivalences you use to simplify conditions, and valid versus invalid arguments.
---

Every `if` statement you have written is a small piece of logic. Propositional logic is the precise version of that: a way of combining true/false statements and working out, mechanically, when the combination is true.

It is the foundation for everything else in this module. Proofs are built from it, predicate logic extends it, and the SAT problem in the last lesson asks one question about it that turns out to be enormously hard and enormously useful.

## Propositions

In the classical two-valued logic used here, a proposition is a statement that is either true or false, never both.

- "7 is prime" is a proposition (true).
- "2 + 2 = 5" is a proposition (false).
- "x > 3" is **not** a proposition on its own: its truth depends on what the unknown x is. (Predicate logic, next lesson, handles this.)
- "Close the door" is not a proposition: it is neither true nor false.

We name propositions with letters: p, q, r. These are **propositional variables**, the logical equivalent of Boolean variables in code. When we write down the truth values themselves, T means true and F means false.

## The connectives

Five connectives build bigger formulas from smaller ones. Each has its own symbol, and these symbols appear in every lesson of this module, so it is worth learning them now.

```formula
¬p
p ∧ q
p ∨ q
p → q
p ↔ q
where
p, q: propositions (propositional variables), each either true or false
¬: NOT (negation). ¬p is true exactly when p is false
∧: AND (conjunction). p ∧ q is true only when both p and q are true
∨: OR (disjunction). p ∨ q is true when at least one of p, q is true, including when both are
→: IMPLIES (implication, the conditional). p → q reads "if p then q", and is false only when p is true and q is false
↔: IF AND ONLY IF (the biconditional). p ↔ q is true when p and q have the same truth value, both true or both false
In words: "not p", "p and q", "p or q", "if p then q" and "p if and only if q": the five ways to build a bigger statement out of p and q.
```

The table gives each one's name and the nearest Python.

| Symbol | Name | Read as | Python |
|---|---|---|---|
| ¬p | negation | not p | `not p` |
| p ∧ q | conjunction | p and q | `p and q` |
| p ∨ q | disjunction | p or q | `p or q` |
| p → q | implication | if p then q | `(not p) or q` |
| p ↔ q | biconditional | p if and only if q | `p == q` |

The Python column assumes Boolean operands. Python and/or return operands and short-circuit; arbitrary objects can have custom truth tests and equality. The logical connectives have their meaning fixed by a **truth table**, which lists every combination of inputs, one per row. Each variable doubles the number of combinations, because every existing row splits into a "true" version and a "false" version:

```formula
N_rows = 2^n
N_rows = 2^2 = 4   for n = 2
N_rows = 2^3 = 8   for n = 3
where
N_rows: the number of rows in the truth table, one per combination of input values
n: the number of propositional variables in the formula
2^n: 2 multiplied by itself n times (2 to the power n)
In words: a truth table over n variables has 2 to the power n rows, so two variables need 4 rows and three need 8.
```

Here is the truth table for all five connectives over p and q. T is true and F is false; each column is one connective.

```
p q | ¬p  p∧q  p∨q  p→q  p↔q
----+-------------------------
T T |  F   T    T    T    T
T F |  F   F    T    F    F
F T |  T   F    T    T    F
F F |  T   F    F    T    T
```

Two things trip people up.

- **∨ is inclusive.** p ∨ q is true when both are true. "Exclusive or" (exactly one) is a separate connective, written ⊕. In Python on booleans it is `p != q`.
- **→ is false in exactly one row**: when p is true and q is false.

Exclusive or is "not (p if and only if q)", because it is true exactly when p and q differ:

```formula
p ⊕ q ≡ ¬(p ↔ q)
where
p, q: propositions, each true or false
⊕: XOR (exclusive or): true when exactly one of p, q is true
↔: if and only if: true when p and q have the same truth value
¬: NOT: flips true to false and false to true
≡: is logically equivalent to: the two sides have the same truth value in every row of the truth table
In words: "exactly one of p and q" means the same as "it is not the case that p and q agree". With p true and q false, both sides are true.
```

## Why implication works this way

The bottom two rows of p → q surprise everyone. Why is "if p then q" true whenever p is false? Here is the rule in one place:

```formula
p → q = F   when p = T and q = F
p → q = T   otherwise
where
p: the "if" part (the premise or antecedent), a proposition; here "you pass the exam"
q: the "then" part (the conclusion or consequent), a proposition; here "I buy you dinner"
→: implies: "if p then q"
T: true
F: false
In words: an implication is broken only by a true premise with a false conclusion; in the other three rows it holds.
```

Think of p → q as a **promise**. "If you pass the exam, I'll buy you dinner." The only way I break the promise is if you pass (p true) and I don't buy dinner (q false). If you fail, I have kept my word whatever I do. A promise that was never triggered was never broken.

This is called **vacuous truth**, and it matters. "Every element of the empty list is negative" is true, because there is no element to break it. Python agrees: `all([])` is `True`.

The connective defined by this table is the **material conditional**. It says nothing about cause. "If 2 + 2 = 5 then the Moon is cheese" is true, because the premise is false. That feels wrong in English, but it is the definition that makes proofs work.

> [!tip] Reading p → q
> All of these mean p → q: "if p then q", "p implies q", "p only if q", "q if p", "p is sufficient for q", "q is necessary for p". The phrase "p only if q" catches people out: it means p cannot happen without q, which is p → q, not q → p.

## Converse, inverse, contrapositive

From an implication p → q you can form three related statements by swapping the two sides, negating both, or doing both:

```formula
p → q
q → p
¬p → ¬q
¬q → ¬p
where
p → q: the original implication, "if p then q"
q → p: the converse: the two sides swapped
¬p → ¬q: the inverse: both sides negated
¬q → ¬p: the contrapositive: swapped and negated
p, q: propositions, each true or false
¬: NOT: ¬p is true exactly when p is false
→: implies: false only when the left side is true and the right side is false
In words: the original, its converse, its inverse and its contrapositive. Only the contrapositive always has the same truth table as the original.
```

| Name | Form | Same as p → q? |
|---|---|---|
| Contrapositive | ¬q → ¬p | Yes, always |
| Converse | q → p | Not in general |
| Inverse | ¬p → ¬q | Not in general |

"If it is raining, the ground is wet" does not mean "if the ground is wet, it is raining" (a sprinkler could be on). That is the converse, and assuming it is one of the most common reasoning errors in proofs, code reviews and incident postmortems.

The contrapositive, "if the ground is not wet, it is not raining", is equivalent. You can check by truth table: both are false in exactly one row: p true and q false. The converse and the inverse are equivalent to *each other* (one is the contrapositive of the other).

## Tautologies, contradictions, satisfiable formulas

Tautology, contradiction and contingency form three disjoint classes. Satisfiability is a related property that overlaps them. The two simplest examples, "p or not p" and "p and not p":

```formula
p ∨ ¬p ≡ T
p ∧ ¬p ≡ F
where
p: a proposition, true or false
¬: NOT: ¬p is true exactly when p is false
∨: OR: true when at least one side is true
∧: AND: true only when both sides are true
≡: is logically equivalent to: same truth value in every row
T: the constant "true", a formula that is true in every row
F: the constant "false", a formula that is false in every row
In words: "p or not p" is true whatever p is, and "p and not p" is false whatever p is. Try p = T and p = F: the first gives T both times, the second F both times.
```

- A **tautology** is true in every row. Example: p ∨ ¬p.
- A **contradiction** is false in every row. Example: p ∧ ¬p.
- A **contingent formula** is true in some rows and false in others.
- A formula is **satisfiable** if at least one row makes it true: both tautologies and contingent formulas qualify.

These are linked: a formula A is a tautology exactly when its negation ¬A is unsatisfiable. SAT solvers exploit this to check that something *always* holds: they search for a row where it fails, and "no such row" is a proof.

## Logical equivalence

Two formulas are **logically equivalent** if they have the same truth value in every row:

```formula
A ≡ B
where
A, B: any two formulas built from propositions and connectives
≡: is logically equivalent to: A and B have the same truth value in every row of their truth table
In words: A and B always agree. Equivalently, the formula "A if and only if B" is a tautology.
```

These are the laws you use daily to simplify conditions. Each line can be checked with a four- or eight-row truth table.

```formula
¬¬p ≡ p
¬(p ∧ q) ≡ ¬p ∨ ¬q
¬(p ∨ q) ≡ ¬p ∧ ¬q
p → q ≡ ¬p ∨ q
p → q ≡ ¬q → ¬p
p ∧ (q ∨ r) ≡ (p ∧ q) ∨ (p ∧ r)
p ∨ (q ∧ r) ≡ (p ∨ q) ∧ (p ∨ r)
p ∨ (p ∧ q) ≡ p
p ↔ q ≡ (p → q) ∧ (q → p)
where
p, q, r: propositions, each true or false
¬: NOT: flips true and false; ¬¬p is NOT applied twice
∧: AND: true only when both sides are true
∨: OR (inclusive): true when at least one side is true
→: implies: false only when the left side is true and the right side false
↔: if and only if: true when both sides have the same truth value
≡: is logically equivalent to: same truth value in every row
In words: line by line, these are double negation, De Morgan's two laws, the implication law, the contrapositive, distribution of AND over OR and of OR over AND, absorption, and the biconditional law.
```

**De Morgan's laws** are the ones you will use most: to negate an AND, negate each part and switch to OR (and vice versa).

Commutativity (order doesn't matter), associativity (grouping doesn't matter) and the identity laws complete the toolkit:

```formula
p ∧ T ≡ p
p ∨ T ≡ T
p ∨ F ≡ p
p ∧ F ≡ F
where
p: a proposition, true or false
T: the constant true
F: the constant false
∧: AND: true only when both sides are true
∨: OR: true when at least one side is true
≡: is logically equivalent to
In words: AND with true and OR with false change nothing; OR with true is always true and AND with false is always false.
```

> [!example] Simplifying a guard
> A code review finds `if not (user.banned or not user.verified):`. Write b for `user.banned` and v for `user.verified`, then apply De Morgan and double negation, as shown below.

```formula
¬(b ∨ ¬v) ≡ ¬b ∧ ¬¬v
          ≡ ¬b ∧ v
where
b: the proposition "the user is banned"
v: the proposition "the user is verified"
¬: NOT; ¬¬v is NOT applied twice, which gives v back
∨: OR: true when at least one side is true
∧: AND: true only when both sides are true
≡: is logically equivalent to
In words: "not (banned or unverified)" is the same as "not banned and verified". The first step is De Morgan, the second is double negation.
```

So it is `if not user.banned and user.verified:`, which reads far better.

You can also prove an equivalence algebraically, one law per step. Here is a derivation that tells you exactly when an implication fails:

```formula
¬(p → q) ≡ ¬(¬p ∨ q)
         ≡ ¬¬p ∧ ¬q
         ≡ p ∧ ¬q
where
p, q: propositions, each true or false
¬: NOT: flips true and false
→: implies: "if p then q"
∨: OR: true when at least one side is true
∧: AND: true only when both sides are true
≡: is logically equivalent to
In words: an implication is false exactly when p is true and q is false. The steps use the implication law, then De Morgan, then double negation.
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

How far does brute force go? Count the rows:

```formula
N_rows = 2^n
N_rows = 2^20 = 1,048,576   for n = 20
N_rows = 2^60 ≈ 1.15 × 10^18   for n = 60
where
N_rows: the number of rows (assignments) to check
n: the number of propositional variables
2^n: 2 multiplied by itself n times
≈: approximately equal to
10^18: a 1 followed by 18 zeros (a billion billion)
In words: 20 variables is about a million rows, which takes a laptop well under a second, but 60 variables is over a billion billion rows, far too many to check one by one.
```

This works for 10 or 20 variables. At 60 variables brute force is hopeless. That gap is the subject of the SAT lesson.

## Precedence

By convention, ¬ binds tightest, then ∧, then ∨, then →, then ↔. Implication is usually read right-associatively (grouped from the right):

```formula
¬p ∧ q → r   means   ((¬p) ∧ q) → r
p → q → r    means   p → (q → r)
where
p, q, r: propositions, each true or false
¬: NOT: applies only to the thing directly after it
∧: AND: binds more tightly than → (it is grouped first)
→: implies: binds more loosely than ¬ and ∧
In words: NOT is applied first, then AND, then OR, then implication; a chain of implications groups from the right.
```

Python follows the same order for `not`, `and`, `or`. When in doubt, add brackets: other people will read the code too.

## Valid arguments

An **argument** has premises and a conclusion. It is **logically valid** if the conclusion is true in every row where all the premises are true. Equivalently:

```formula
(P_1 ∧ P_2 ∧ ... ∧ P_k) → C ≡ T
where
P_1, P_2, ..., P_k: the k premises, each a formula
C: the conclusion, a formula
k: the number of premises
...: "and so on", the premises in between
∧: AND: true only when every part is true
→: implies: false only when the left side is true and the right side false
≡: is logically equivalent to
T: the constant true, so "≡ T" means "is a tautology"
In words: an argument is valid exactly when "if all the premises hold then the conclusion holds" is true in every row.
```

The standard valid forms, written with ⊢ ("therefore"):

```formula
p → q, p ⊢ q
p → q, ¬q ⊢ ¬p
p → q, q → r ⊢ p → r
p ∨ q, ¬p ⊢ q
p ∨ q, p → r, q → r ⊢ r
where
p, q, r: propositions, each true or false
,: separates the premises
⊢: "therefore": the formula on the right follows validly from the premises on the left. (Strictly ⊢ means "can be derived by the rules of a proof system", and ∴ is the usual "therefore" sign; for classical propositional logic the soundness and completeness theorems make ⊢ coincide with "true in every row where the premises are true", which is written ⊨)
→: implies
¬: NOT
∨: OR (inclusive)
In words: line by line, modus ponens, modus tollens, hypothetical syllogism, disjunctive syllogism and proof by cases (disjunction elimination).
```

| Rule | Premises | Conclusion |
|---|---|---|
| Modus ponens | p → q, p | q |
| Modus tollens | p → q, ¬q | ¬p |
| Hypothetical syllogism | p → q, q → r | p → r |
| Disjunctive syllogism | p ∨ q, ¬p | q |
| Proof by cases | p ∨ q, p → r, q → r | r |

And two famous invalid ones:

- **Affirming the consequent**: from p → q and q, conclude p. Invalid (row p = F, q = T).
- **Denying the antecedent**: from p → q and ¬p, conclude ¬q. Invalid (same row).

```formula
p → q, q ⊬ p
p → q, ¬p ⊬ ¬q
where
p, q: propositions, each true or false
→: implies
¬: NOT
⊬: "does not follow": some row makes every premise true and the conclusion false
In words: knowing the "then" part is true doesn't tell you the "if" part, and knowing the "if" part is false doesn't tell you the "then" part. The row p = F, q = T breaks both.
```

> [!warning] Debugging with the converse
> "If the cache is down, latency spikes. Latency spiked, so the cache is down." That is affirming the consequent. Latency spikes have many causes. Modus tollens is the safe direction: "latency did not spike, so the cache is not down" (given the premise holds).

Validity is about form, not truth. "If pigs fly, I am the Queen; pigs fly; so I am the Queen" is valid. Its conclusion is false only because a premise is false. An argument that is valid *and* has true premises is called a **sound argument**.

## How many connectives do you need?

Not five. Implication and the biconditional can be rewritten with the others, and OR can be rewritten with NOT and AND:

```formula
p → q ≡ ¬p ∨ q
p ↔ q ≡ (p → q) ∧ (q → p)
p ∨ q ≡ ¬(¬p ∧ ¬q)
where
p, q: propositions, each true or false
¬: NOT
∧: AND: true only when both sides are true
∨: OR: true when at least one side is true
→: implies
↔: if and only if
≡: is logically equivalent to
In words: anything written with → and ↔ can be rewritten with NOT, AND and OR, and by De Morgan OR itself can be written with NOT and AND.
```

So the set {¬, ∧, ∨} can express every truth table, and even {¬, ∧} alone suffices. A set like this is **functionally complete**.

Remarkably, a single connective is enough: **NAND** ("not and"), written ↑. Feeding a value into both inputs of a NAND negates it, which is the key to building the rest:

```formula
p ↑ q ≡ ¬(p ∧ q)
¬p ≡ p ↑ p
p ∧ q ≡ (p ↑ q) ↑ (p ↑ q)
p ∨ q ≡ (p ↑ p) ↑ (q ↑ q)
where
p, q: propositions, each true or false
↑: NAND (not and): false only when both sides are true
¬: NOT
∧: AND
∨: OR
≡: is logically equivalent to
In words: NAND is "not both". NAND of a value with itself is its negation; NAND of a NAND gives AND back; NAND of two negations gives OR (by De Morgan).
```

Check the AND line with p = T and q = T: p ↑ q is F, and F ↑ F is T, which matches p ∧ q.

This is why chips can be built from NAND gates alone. NOR is also complete on its own; AND, OR and NOT individually are not.

## Key takeaways
- A proposition is true or false; connectives combine them, and a truth table with 2ⁿ rows (n variables) defines any formula's meaning.
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
