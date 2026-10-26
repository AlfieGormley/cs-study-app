---
id: auto-myhill-nerode
title: Myhill–Nerode and DFA lower bounds
level: advanced
minutes: 3
sourceLesson: auto-minimisation
summary: Two prefixes are language-equivalent when no continuation separates them.
---

## The Myhill–Nerode theorem

Minimisation rests on a theorem that describes the minimal DFA without mentioning any machine at all.

For a language, call two strings **L-equivalent** if no suffix tells them apart:

```formula essential
x ≡_L y   iff   ∀ z ∈ Σ* :
  x · z ∈ L   ⟺   y · z ∈ L
where
x, y: two strings, thought of as "inputs read so far"
L: the language
≡_L: is L-equivalent to
∀: for all
z: any possible continuation (suffix)
Σ*: every finite string over the alphabet, including the empty string
·: concatenation: x followed by z
∈: is an element of
⟺: holds exactly when: both sides true, or both false
In words: ("iff" means "if and only if".) Two prefixes are L-equivalent when every possible ending puts both in L or both outside L. The strings sharing one verdict-pattern form an equivalence class.
```

For "strings ending in ab", `a` and `bba` are L-equivalent (both just saw a), while `a` and `b` are not: appending `b` gives `ab` in L and `bb` outside it.

> [!note] Myhill–Nerode theorem
> L is regular if and only if L-equivalence has finitely many classes. When it does, the number of classes equals the number of states in the minimal DFA.

The intuition: a DFA state is exactly "everything about the past that matters for the future". Strings that reach the same state of the minimal DFA are L-equivalent, and each class is one state.

### A second way to prove non-regularity

Myhill–Nerode is an exact test, unlike the pumping lemma for regular languages. To show L is not regular, find infinitely many strings that are pairwise distinguishable.

Take the language of n a's followed by n b's. The strings a, aa, aaa, ... are pairwise distinguishable:

Choose any two different positive lengths of initial a-run. Appending just enough b characters to match the first run accepts that prefix and rejects the other. This works for every pair, so no two different counts can share a state.

For example, `aa` and `aaa` are separated by `bb`: `aabb` is in L and `aaabb` is not. Infinitely many classes, so not regular. No case analysis about splits, no choice of how many copies to pump.

### Lower bounds on DFA size

It also gives tight lower bounds. In the NFA units, "the n-th symbol from the end is 1" needed two to the power n states, that is n copies of 2 multiplied together, where n is the position being checked. That was a Myhill–Nerode argument: the two to the power n strings of length n are pairwise distinguishable. For position 3 that is 8 strings, `000` to `111`, and 8 states.

## Key takeaways
- Two prefixes are language-equivalent when no continuation separates them.
- Infinitely many pairwise distinguishable prefixes prove non-regularity.

## Further reading
- [Minimization of Automata — Berstel, Boasson, Carton and Fagnot](https://arxiv.org/abs/1010.5318)
- [Stanford CS103: nonregular languages](https://web.stanford.edu/class/archive/cs/cs103/cs103.1266/lectures/18/)
