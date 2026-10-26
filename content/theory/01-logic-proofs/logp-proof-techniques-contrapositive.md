---
id: logp-proof-techniques-contrapositive
title: Proving an implication backwards
level: intermediate
minutes: 3
sourceLesson: logp-proof-techniques
summary: Proving the contrapositive proves the original implication because their truth tables coincide.
---

## Proof by contrapositive

The first lesson established that an implication and its contrapositive are logically equivalent:

```formula essential
p → q ≡ ¬q → ¬p
where
p, q: propositions (statements that are true or false)
→: implies: "if ... then ...", false only when the left side is true and the right side false
¬: NOT: ¬q is true exactly when q is false
≡: is logically equivalent to: true in exactly the same situations
In words: "if p then q" says the same as "if not q then not p", so proving either one proves the other.
```

So instead of proving p implies q, you may prove not q implies not p directly. This helps when not q gives you something concrete to work with and p does not.

**Claim: if n squared is even, then n is even.** Writing the square as twice an integer does not immediately reveal the original integer's parity. The contrapositive is: if n is an **odd integer**, then n squared is an **odd integer**. So write n using the definition of odd and square it:

```formula essential
n = 2k + 1
n^2 = 2(2k^2 + 2k) + 1
where
n: an odd integer
k: the integer with n = 2 × k + 1
n^2: n multiplied by itself (n squared)
In words: squaring any odd integer leaves twice an integer plus one, so its square is odd.
```

So n odd forces n squared odd, which proves the claim. ∎

Another one, where the contrapositive turns an awkward "or" into a clean "and". **Claim: if two numbers add up to at least 100, at least one of them is at least 50.** Negating the conclusion makes a particularly simple starting point:

If both numbers are below fifty, their sum is below one hundred. Therefore a sum of at least one hundred requires at least one number to reach fifty. The negation of “at least one reaches fifty” is “both are below fifty”.

This is the pigeonhole principle in miniature. The same reasoning appears in capacity planning: if two shards each hold under half the keys, they cannot together hold them all.


## Key takeaways
- Proving the contrapositive proves the original implication because their truth tables coincide.
- Negating a parity claim uses the fact that every integer is exactly one of even or odd.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Proof by contradiction — Wikipedia](https://en.wikipedia.org/wiki/Proof_by_contradiction)
