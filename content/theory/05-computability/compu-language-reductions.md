---
id: compu-language-reductions
title: Language emptiness and machine equivalence
level: advanced
minutes: 5
summary: Language nonemptiness is recognisable by dovetailing; emptiness is co-recognisable and undecidable.
sourceLesson: compu-reductions-rice
---

## Example 3: emptiness, E_TM

```formula
E_TM = { ⟨M⟩ : L(M) = ∅ }
where
E_TM: the emptiness problem for Turing machines
M: any Turing machine
⟨M⟩: angle brackets: the encoding of M as a string
L(M): the language of M: the set of strings it accepts
∅: the empty set, with no members
In words: E_TM holds the machines that accept no string at all.
```

**Theorem.** E_TM is undecidable.

**Proof.** Reduce A_TM to the complement Ē_TM. Given ⟨M, w⟩, build

```
M₁(x):
  if x ≠ w: reject
  run M on w; accept if it accepts
```

```formula
L(M_1) = {w}   if w ∈ L(M)
L(M_1) = ∅     if w ∉ L(M)
w ∈ L(M)  ⇔  ⟨M_1⟩ ∈ Ē_TM
where
M: the given Turing machine
w: the given input
M_1: the new machine built from M and w
L(M): the language of M: the strings it accepts
{w}: the set containing just w
∅: the empty set
Ē_TM: the complement of E_TM: the machines whose language is not empty
∈, ∉: is a member of, is not a member of
⇔: if and only if
In words: M₁ accepts only w, and only if M accepts w, so M₁ has a non-empty language exactly when M accepts w.
```

Thus M accepts w exactly when the constructed machine has nonempty language. The displayed map reduces acceptance to nonemptiness, so nonemptiness is undecidable. A language is decidable iff its complement is, so E_TM is undecidable. ∎

(Ē_TM is recognisable: dovetail M on all strings and accept if any is accepted. So E_TM itself is co-recognisable but not recognisable.)

## Example 4: equivalence is neither

```formula
EQ_TM = { ⟨M, N⟩ : L(M) = L(N) }
where
EQ_TM: the equivalence problem for Turing machines
M, N: any two Turing machines
⟨M, N⟩: angle brackets: one string encoding both machines
L(M): the language of M: the strings it accepts (likewise L(N))
In words: EQ_TM holds every pair of machines that accept exactly the same strings.
```

Both proofs below build a machine N that ignores its own input, simulates the given M on the fixed input w, and accepts only if that simulation accepts. Thus N accepts every string if M accepts w, and accepts nothing otherwise.

**Not recognisable.** Map ⟨M, w⟩ to ⟨M_rej, N⟩ where M_rej rejects everything. Acceptance by M on w occurs exactly when N differs in language from this rejecting machine. Taking complements gives a map from nonacceptance to equivalence, as shown below. Nonacceptance is unrecognisable, so equivalence is too.

**Not co-recognisable.** Same N, but compare with a machine M_all that accepts everything: Now acceptance by M on w occurs exactly when N has the same language as the all-accepting machine. Taking complements gives a map from nonacceptance to inequivalence, so inequivalence is also unrecognisable.

```formula
f_1(⟨M, w⟩) = ⟨M_rej, N⟩
f_2(⟨M, w⟩) = ⟨M_all, N⟩
A_TM ≤_m EQ̄_TM   so   Ā_TM ≤_m EQ_TM
A_TM ≤_m EQ_TM   so   Ā_TM ≤_m EQ̄_TM
where
f_1, f_2: the two mapping reductions, total computable functions on encodings
M: the given machine
w: the given input
N: the machine that ignores its input and accepts iff M accepts w
M_rej: a machine that rejects every input, so L(M_rej) = ∅
M_all: a machine that accepts every input, so L(M_all) = Σ*
A_TM: the acceptance problem: pairs where M accepts w
Ā_TM: the complement of A_TM: pairs where M does not accept w; it is not recognisable
EQ_TM: the equivalence problem: pairs of machines with the same language
EQ̄_TM: the complement of EQ_TM: pairs of machines whose languages differ
≤_m: is mapping reducible to
In words: one map turns "M accepts w" into "these two machines differ", the other into "these two machines agree", so neither EQ_TM nor its complement can be recognised.
```

This is why "are these two programs equivalent?" has no general algorithm, neither a complete recogniser for equivalence nor a complete recogniser for inequivalence. Sound tools can still settle particular instances.

## Key takeaways

- Language nonemptiness is recognisable by dovetailing; emptiness is co-recognisable and undecidable.
- Comparisons with an empty-language machine and an all-language machine give two reductions.
- Neither machine-language equivalence nor its complement is recognisable.

## Further reading

- [Lynch: mapping reductions and Rice’s theorem](https://ocw.mit.edu/courses/6-045j-automata-computability-and-complexity-spring-2011/resources/mit6_045js11_lec09/)
