---
id: logp-proof-techniques-contrapositive
title: Proving an implication backwards
level: intermediate
minutes: 3
sourceLesson: logp-proof-techniques
summary: Proving the contrapositive proves the original implication because their truth tables coincide.
---

## Proof by contrapositive

Recall from the first lesson that an implication and its contrapositive are logically equivalent:

```formula
p → q ≡ ¬q → ¬p
where
p, q: propositions (statements that are true or false)
→: implies: "if ... then ...", false only when the left side is true and the right side false
¬: NOT: ¬q is true exactly when q is false
≡: is logically equivalent to: true in exactly the same situations
In words: "if p then q" says the same as "if not q then not p", so proving either one proves the other.
```

So instead of proving p implies q, you may prove not q implies not p directly. This helps when not q gives you something concrete to work with and p does not.

**Claim: if n squared is even, then n is even.** A direct attempt starts with "n squared is twice some integer" and needs a square root, which goes nowhere. The contrapositive is: if n is an **odd integer**, then n squared is an **odd integer**. So write n using the definition of odd and square it:

```formula
n = 2k + 1
n^2 = (2k + 1)^2
    = 4k^2 + 4k + 1
    = 2 × (2k^2 + 2k) + 1
where
n: an odd integer
k: the integer with n = 2 × k + 1
n^2: n multiplied by itself (n squared)
In words: n² is 2 times an integer, plus 1, so it is odd. With n = 7 (k = 3): 49 = 2 × 24 + 1.
```

So n odd forces n squared odd, which proves the claim. ∎

Another one, where the contrapositive turns an awkward "or" into a clean "and". **Claim: if two numbers add up to at least 100, at least one of them is at least 50.** In symbols, with the contrapositive below it:

```formula
x + y ≥ 100  →  x ≥ 50 or y ≥ 50
x < 50 and y < 50  →  x + y < 100
x + y < 50 + 50 = 100
where
→: implies: "if the left side holds, then the right side holds"
x, y: real numbers
≥: is greater than or equal to
<: is less than
In words: the first line is the claim and the second its contrapositive. The third line proves the contrapositive: two numbers that are each under 50 add up to less than 100. So if the sum reaches 100, at least one of them must be 50 or more.
```

This is the pigeonhole principle in miniature. The same reasoning appears in capacity planning: if two shards each hold under half the keys, they cannot together hold them all.


## Key takeaways
- Proving the contrapositive proves the original implication because their truth tables coincide.
- Negating a parity claim uses the fact that every integer is exactly one of even or odd.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Proof by contradiction — Wikipedia](https://en.wikipedia.org/wiki/Proof_by_contradiction)
