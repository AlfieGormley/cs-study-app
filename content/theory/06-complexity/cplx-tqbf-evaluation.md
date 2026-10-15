---
id: cplx-tqbf-evaluation
title: "Evaluating quantified Boolean formulas"
level: advanced
minutes: 3
summary: "Quantifier order allows or forbids choices that depend on earlier variables."
sourceLesson: cplx-space
---

## PSPACE-completeness: TQBF

A **quantified Boolean formula** puts quantifiers in front of a formula:

```formula
∀x ∃y ∀z ((x ∨ y) ∧ (¬y ∨ z))
where
x, y, z: Boolean variables, each true or false
∀: "for all": the rest must hold for both values of the variable
∃: "there exists": the rest must hold for at least one value of the variable
∨: OR: true when at least one side is true
∧: AND: true only when both sides are true
¬: NOT: ¬y is true exactly when y is false
In words: "for every x there is a y such that, for every z, (x or y) and (not y or z) both hold". This particular formula is false, as traced below.
```

**TQBF** asks whether a fully quantified formula is true. It is **PSPACE-complete** (Stockmeyer and Meyer, 1973). SAT is the special case where every quantifier is ∃.

The obvious recursive evaluator runs in polynomial space and exponential time:

```python
def tqbf(quants, phi, a=()):
    # quants: string of 'E'/'A', one per var
    if len(a) == len(quants):
        return phi(a)
    q = quants[len(a)]
    # Finish one branch before using the
    # next.
    r = tqbf(quants, phi, a + (False,))
    if q == 'E' and r:
        return True
    if q == 'A' and not r:
        return False
    return tqbf(quants, phi, a + (True,))

f = lambda a: a[0] != a[1]
print(tqbf('AE', f))  # True:  ∀x ∃y x≠y
print(tqbf('EA', f))  # False: ∃x ∀y x≠y

g = lambda a: ((a[0] or a[1]) and
               (not a[1] or a[2]))
print(tqbf('AEA', g))  # False
```

The recursion depth is the number of variables. A careful implementation keeps one shared assignment array and a constant amount of data per frame:

```formula
S = O(n + |φ|)
T = O(2^n × |φ|)
T ≈ 2^30 × |φ| ≈ 10^9 × |φ|   for n = 30
where
S: the working space: a shared n-bit assignment and quantifier stack, plus linear-in-formula workspace for evaluating φ
T: the running time, in steps
n: the number of variables (and so the recursion depth)
φ: phi, the quantifier-free part of the formula; |φ| is its length, the cost of evaluating it once
O(...): Big O: at most a constant times this
≈: approximately equal to
In words: space linear in the assignment plus formula length, but exponential time, because the two recursive invocations run one after the other and reuse the same space. With 30 variables that is about a billion evaluations of φ, held in only 30 frames.
```

(This Python version copies the tuple at each level, which costs space quadratic in n: still polynomial.)

Trace the last one: if x is false, (x ∨ y) forces y true, and then (¬y ∨ z) requires z true for **all** z, which fails when z is false. So the ∀x fails.

## Key takeaways

- Quantifier order allows or forbids choices that depend on earlier variables.
- Depth-first evaluation reuses memory across truth assignments.
- TQBF is PSPACE-complete, with SAT as the all-existential case.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
