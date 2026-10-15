---
id: compu-cfl-closure
title: Which operations preserve context-free languages
level: intermediate
minutes: 3
summary: CFLs are closed under union, concatenation and star.
sourceLesson: compu-pda-pumping
---

## Closure properties

| Operation | Regular | CFL |
|---|---|---|
| Union | yes | yes |
| Concatenation, star | yes | yes |
| Intersection | yes | no |
| Complement | yes | no |
| ∩ with a regular language | yes | yes |

"Closed under" an operation means that applying it to CFLs always gives another CFL.

```formula
L_1 = { a^n b^n c^m : n, m ≥ 0 }
L_2 = { a^m b^n c^n : n, m ≥ 0 }
L_1 ∩ L_2 = { a^n b^n c^n : n ≥ 0 }
A ∩ B = Σ* − (Ā ∪ B̄)
where
L_1: strings a…b…c… with as many a's as b's (any number of c's)
L_2: strings a…b…c… with as many b's as c's (any number of a's)
n, m: whole numbers 0, 1, 2, … giving block lengths
a, b, c: the three letters of the alphabet
a^n: the letter a written n times (likewise b^n, c^m)
∩: intersection: the strings in both languages
∪: union: the strings in either language
A, B: any two languages over the same alphabet
Ā: the complement of A: every string over the alphabet that is outside A (likewise B̄)
Σ*: every finite string over the alphabet Σ (sigma)
−: set difference: everything on the left except what is on the right
≥: is at least
In words: the two context-free languages overlap exactly in a^n b^n c^n, which is not context-free; and intersection can be built from union and complement, so complement cannot always work either.
```

**Intersection fails:** each of the first two displayed languages is context-free: generate the equal blocks using a nested rule and the independent block by ordinary repetition. Their intersection is the equal three-block language, already proved not context-free. **Complement fails** as a consequence: CFLs are closed under union, so if they were closed under complement, De Morgan's law (the last line) would make them closed under intersection too.

Intersection with a *regular* language does work: run the PDA and a DFA side by side, since only one of them needs the stack. This is a handy proof tool. To show L is not context-free, intersect it with a regular language to get something you already know is not context-free.

## Key takeaways

- CFLs are closed under union, concatenation and star.
- Intersecting two CFLs may produce a non-CFL; complement closure would imply intersection closure and therefore fails.
- Intersecting a CFL with a regular language remains context-free and is useful in impossibility proofs.

## Further reading

- [Context-free language closure properties — further reference](https://en.wikipedia.org/wiki/Context-free_language)
- [Sipser: CFL pumping lemma and Turing machines](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec5-1/)
