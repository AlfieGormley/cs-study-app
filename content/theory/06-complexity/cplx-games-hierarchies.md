---
id: cplx-games-hierarchies
title: "Games, regexes and proven space separations"
level: advanced
minutes: 4
summary: "Polynomial-length games can be evaluated in polynomial space."
sourceLesson: cplx-space
---

## Games are PSPACE problems

Alternating quantifiers are a two-player game: "there is a move for me such that for all your replies there is a move for me such that...". TQBF is a game in which players take turns setting variables.

With polynomial-size positions and polynomial-space move generation and end-of-play evaluation, polynomially bounded play gives PSPACE membership by depth-first search. Hardness requires a separate reduction; the following generalised game families are **PSPACE-complete**:

- **Generalised geography** (players extend a path in a directed graph, no repeats), PSPACE-complete.
- **Generalised Hex** and generalised **Othello** on n × n boards, PSPACE-complete.

Games that can last exponentially long are typically harder: generalised **chess** (Fraenkel and Lichtenstein, 1981) and **generalised Go** with the simple-ko rule variant analysed by Robson (Robson, 1983) on n × n boards are **EXPTIME-complete**, so provably not in P.

Real-world PSPACE-complete problems include **equivalence of ordinary regular expressions** using union, concatenation and Kleene star (excluding backreferences and succinct extensions), **LTL model checking** used in hardware and protocol verification, and finite propositional **AI planning** (ground STRIPS plan existence).

## What's proven, what's open

The **space hierarchy theorem** says more space solves strictly more problems:

```formula
SPACE(s) ⊊ SPACE(s′)   when s = o(s′)
SPACE(n) ⊊ SPACE(n^2)
where
SPACE(s): problems a deterministic machine decides using at most a constant times s work cells
s, s′: two space bounds (s′ is read "s prime"); s′ must be space-constructible and at least log n (the machine can mark off the bound within that amount of space)
n: the input size, in bits
o(s′): little o: grows strictly more slowly than s′, so s / s′ shrinks towards 0 as n grows
⊊: "is strictly contained in": every problem on the left is on the right, and some problem on the right is not on the left
In words: give a machine asymptotically more memory and it can decide problems it could not before. For example, quadratic space decides strictly more than linear space.
```

Combined with Savitch's theorem, this proves some separations:

```formula
NL ⊆ SPACE(log^2 n) ⊊ PSPACE
PSPACE ⊊ EXPSPACE
P ⊊ EXPTIME
where
NL: nondeterministic logarithmic space
SPACE(log^2 n): deterministic space of at most a constant times (log n) squared
PSPACE: polynomial space
EXPSPACE: exponential space
P: polynomial time
EXPTIME: exponential time
n: the input size, in bits
log: logarithm base 2
⊆: "is contained in"
⊊: "is strictly contained in": contained, and not equal
In words: NL is strictly smaller than PSPACE, PSPACE strictly smaller than EXPSPACE, and P strictly smaller than EXPTIME (the last from the time hierarchy theorem).
```

- **Proven**: the three strict separations above.
- **Open**: L vs NL, L vs P, NL vs P, P vs PSPACE, NP vs PSPACE, PSPACE vs EXPTIME.

It is striking that P equalling PSPACE has not been ruled out: nobody can prove that polynomial memory gives more power than polynomial time, though it is universally conjectured.

For ordinary regex equivalence, first build linear-size NFAs and consider pairs of subset states. A distinguishing string exists exactly when a reachable pair has different acceptance answers. Although the implicit product graph may have exponentially many vertices, each vertex and a path-length counter need only polynomially many bits. Nondeterministic reachability uses polynomial space, and Savitch removes nondeterminism. Building and remembering every visited DFA state may instead consume exponential memory. Backreferences and succinct repetition operators require separate complexity analyses.

## Key takeaways

- Polynomial-length games can be evaluated in polynomial space.
- Completeness depends on the game rules and generalised input family.
- NL differs from PSPACE and PSPACE differs from EXPSPACE; P versus PSPACE is open.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
