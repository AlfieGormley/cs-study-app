---
id: auto-pumping-quantifiers
title: The pumping lemma and adversarial choices
level: intermediate
minutes: 4
sourceLesson: auto-pumping
summary: A non-regularity proof must handle every pumping length and every legal split.
---

## The lemma

> [!note] Pumping lemma for regular languages
> If a language is regular, there is a number, its **pumping length**, such that every string in the language at least that long can be cut into three pieces: a non-empty middle piece that lies within the first pumping-length symbols, and that can be repeated any number of times, or deleted, without leaving the language.

In symbols:

```formula
L ∈ REG   ⟹   ∃ p ≥ 1 such that
∀ s ∈ L with |s| ≥ p,
∃ x, y, z with s = x · y · z and:
  1.  |y| ≥ 1
  2.  |x · y| ≤ p
  3.  x · y^i · z ∈ L   for all i ≥ 0
where
L: the language
REG: the class of regular languages, those recognised by some DFA
⟹: implies: if the left side is true, the right side is true
∃: there exists: at least one such thing can be found
∀: for all: whichever one you pick
p: the pumping length, a whole number at least 1
s: any string in L
x, y, z: three pieces of s; y is the pumped piece
·: concatenation: one string straight after another
| |: vertical bars around a string mean its length
∈: is an element of
≥: is greater than or equal to
≤: is less than or equal to
y^i: i copies of y in a row; y^0 is the empty string
i: how many copies of y to use, 0, 1, 2, …
In words: if L is regular, then any long enough string in L has a non-empty piece near its start that can be repeated or deleted while staying in L.
```

For any DFA recognising L, p can be taken to be its number of states. Condition 2 holds because the repeat happens within the first p symbols. Note that zero copies (deleting y) are allowed, and is often the most useful choice.

For example, with the 3-state divisible-by-3 DFA a pumping length of 3 works, and the earlier loop-unit split of `1111` has a loop piece of length 2, lying inside the first 3 symbols.

## Using it: proof by contradiction

The lemma is a statement "if regular, then pumpable". To show L is **not** regular, show that L is not pumpable: then it cannot be regular, a **proof by contradiction**. The quantifiers ("for every", "there exists") matter, so it helps to see the proof as a game against an adversary who claims L is regular:

```formula
∀ p ≥ 1   ∃ s ∈ L with |s| ≥ p :
∀ x, y, z with s = x · y · z,
  |y| ≥ 1 and |x · y| ≤ p :
∃ i ≥ 0 with x · y^i · z ∉ L
where
p: the pumping length, chosen by the adversary; a positive integer measured in input symbols
s: the string you choose
L: the language you want to prove non-regular
x, y, z: the split, chosen by the adversary
·: concatenation
| |: the length of a string
∈: is an element of
∉: is not an element of
≥: is greater than or equal to
≤: is less than or equal to
y^i: i copies of y in a row
i: the number of copies, chosen by you; an integer count, non-negative unless a positive lower bound is stated
∀: for all: the adversary's moves, which you must handle whatever they are
∃: there exists: your moves, where you only need one that works
In words: whatever p the adversary names, you name a long string in L, and whatever legal split they then make, you find a number of copies of y that throws the string out of L.
```

As a game:

1. **Pumping adversary** picks the pumping length. You don't know it, so treat it as a variable.
2. **You** pick a long enough string in L. Choose wisely; this is the creative step.
3. **Pumping adversary** picks any legal split. You must beat **every** possible split.
4. **You** pick the number of copies of the middle piece and show the result is not in L.

If you can always win, L is not regular.

## Key takeaways
- A non-regularity proof must handle every pumping length and every legal split.
- Choose the witness after the pumping length and the repetition count after the split.

## Further reading
- [MIT: the regular pumping lemma and automata to regexes](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec3-1/)
