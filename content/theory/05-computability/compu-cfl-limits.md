---
id: compu-cfl-limits
title: Proving equal blocks and copying are not context-free
level: intermediate
minutes: 5
summary: A pumping argument must defeat every legal decomposition of the chosen string.
sourceLesson: compu-pda-pumping
---

## Proof: aⁿbⁿcⁿ is not context-free

**Claim.** The language of equal blocks of a's, b's and c's is not context-free.

**Proof.** Suppose L is context-free with CFL pumping length p. Choose the string s below:

```formula
L = { a^n b^n c^n : n ≥ 0 }
s = a^p b^p c^p
|s| = 3p ≥ p
where
L: the language of a's, then b's, then c's, all three blocks the same length
n: the shared block length, any whole number 0, 1, 2, …
a, b, c: the three letters of the alphabet
a^n: the letter a written n times in a row (likewise b^n, c^n)
p: the CFL pumping length the lemma promises, if L were context-free
s: the string we choose to attack, which is in L
|s|: the length of s, in characters
≥: is at least
In words: pick the string with p a's, p b's and p c's; it is in L and is long enough for the lemma to apply.
```

The lemma supplies five consecutive pieces, as defined below: their middle three-piece window is at most the pumping length, and the two pumped pieces are not both empty.

```formula
s = u v x y z
|v x y| ≤ p     |v y| ≥ 1
where
s: the chosen string of equal a, b and c blocks
u, v, x, y, z: consecutive substrings; v and y are pumped together
p: the positive pumping length
|v x y|: the combined length of v, x and y, in symbols
|v y|: the combined length of the two pumped pieces
≤, ≥: is at most, is at least
In words: The pumped pieces are close together and deleting or duplicating them must change at least one symbol.
```

Since vxy spans at most p characters, it cannot contain both an a and a c: there are p b's between them. So vxy lies within aᵖbᵖ or within bᵖcᵖ.

- **Case 1: vxy has no c.** Double both pumped pieces. The string gains at least one a or b, but the number of c's stays p. The counts are no longer equal, so the resulting string is outside the language.
- **Case 2: vxy has no a.** Double both pumped pieces. It gains at least one b or c, but still has p a's. Again the resulting string is outside the language.

Every allowed split fails, contradicting the lemma. So L is not context-free. ∎

The same style of proof shows that the "copy" language is not context-free:

```formula
L_copy = { w w : w ∈ {a, b}* }
s = a^p b^p a^p b^p
where
L_copy: every string that is some string w written twice
w: any finite string of a's and b's
{a, b}*: every finite string of a's and b's, including the empty string
∈: is a member of
s: the string to pump, which is w w for w = a^p b^p
a^p: the letter a written p times (likewise b^p)
p: the CFL pumping length
In words: strings made of a block repeated exactly, such as abab or aabbaabb, are beyond any PDA; the proof pumps s = a^p b^p a^p b^p.
```

Contrast this with palindromes `w wᴿ`, which are. A stack reverses order naturally; copying in the same order needs a queue, and a PDA has none.

> [!warning] How pumping proofs go wrong
> - You choose s; the decomposition chooser supplies the split. You must defeat **every** split satisfying the conditions, not one convenient split.
> - The lemma is a necessary condition only. Some non-CFLs pass it. Ogden's lemma, which lets you mark which positions get pumped, is stronger.
> - Picking a weak s (like `abc` repeated) often makes the proof impossible. Choose the string so the bounded three-piece window cannot reach everything.

## Key takeaways

- A pumping argument must defeat every legal decomposition of the chosen string.
- A short pumping window cannot change all three equal letter blocks.
- A stack reverses order naturally; arbitrary exact copying is beyond a PDA.

## Further reading

- [Sipser: CFL pumping lemma and Turing machines](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec5-1/)
