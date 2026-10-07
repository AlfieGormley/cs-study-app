---
id: logp-induction
title: Induction (weak, strong, structural)
level: intermediate
minutes: 15
summary: Proving statements about every natural number, every list or every tree with induction, including strong and structural induction, strengthening the hypothesis, and why recursion and induction are the same idea.
---

Many claims in computer science are about *every* size of input: every n, every list, every tree. You cannot check infinitely many cases, and the techniques from the last lesson often don't get a grip on "every n".

**Induction** is the tool for this. It turns an infinite claim into two finite pieces of work. It is also exactly how you should think about recursive code: if the base case is right, and each call is right assuming the smaller calls are right, the function is right.

## The domino picture

Imagine an infinite row of dominoes. To know they all fall, you need two facts:

1. The first domino falls.
2. Whenever a domino falls, it knocks over the next one.

Neither fact alone is enough. With both, every domino falls.

```
P(0)  ->  P(1)  ->  P(2)  ->  P(3) ...
 ^base     \_ step: P(n) -> P(n+1) _/
```

## Weak (ordinary) induction

To prove P(n) for every integer n ≥ b:

1. **Base case**: prove P(b).
2. **Inductive step**: for an arbitrary n ≥ b, **assume P(n)** (the *inductive hypothesis*, IH) and prove P(n + 1).

As a formula: P(b) ∧ ∀n ≥ b (P(n) → P(n + 1)) → ∀n ≥ b P(n).

The inductive step is a direct proof of an implication. You do not assume P(n) is true for all n; you assume it for one arbitrary n and show the next case follows.

### Example: the sum 1 + 2 + ... + n

```
Claim: for all n ≥ 1,
  1 + 2 + ... + n = n(n+1)/2.

Base n = 1:  LHS = 1,
             RHS = 1·2/2 = 1.  ✓

Step: assume 1 + ... + n = n(n+1)/2.
  1 + ... + n + (n+1)
  = n(n+1)/2 + (n+1)        by IH
  = (n+1)(n/2 + 1)
  = (n+1)(n+2)/2
This is the formula for n+1.     ∎
```

This is why a nested loop where the inner loop runs i times, for i = 1 to n, does n(n+1)/2 iterations: Θ(n²).

### Example: the base case matters

Claim: 2ⁿ > n² for all n ≥ 5.

```
Base n = 5:  32 > 25.  ✓

Step: assume 2ⁿ > n², n ≥ 5.
  2ⁿ⁺¹ = 2·2ⁿ > 2n²       by IH
Need 2n² ≥ (n+1)² = n² + 2n + 1,
i.e. n² ≥ 2n + 1.
For n ≥ 3, n² ≥ 3n = 2n + n > 2n + 1.
So 2ⁿ⁺¹ > (n+1)².                ∎
```

The inductive step works for every n ≥ 3, yet the claim is **false** at n = 3 (8 < 9) and n = 4 (16 = 16). Without a correct base case, a valid step proves nothing. The dominoes are lined up, but the first one you push must actually fall.

## Recursion is induction

Here is a recursive function and its correctness proof side by side.

```python
def total(xs):
    if not xs:              # base case
        return 0
    return xs[0] + total(xs[1:])
```

In an ideal execution model, total(xs) returns the exact sum of any finite integer list. Induct on length n. Actual Python has a recursion limit and finite resources; this slicing implementation also copies Θ(n²) list elements overall. Floating-point addition does not obey all exact-arithmetic rearrangements.

- **Base, n = 0**: the empty list returns 0, its sum. ✓
- **Step**: assume `total` is correct on all lists of length n. A list of length n + 1 returns `xs[0] + total(xs[1:])`. The tail has length n, so by the IH that call returns the tail's sum. Adding `xs[0]` gives the whole sum. ✓

That is exactly the "leap of faith" you make when writing recursion: trust the recursive call on a smaller input. Induction is what makes the leap legitimate. It also tells you what can go wrong: a missing base case, or a recursive call that is not on a smaller input, breaks the proof and usually the program.

## Strong induction

Sometimes P(n + 1) depends not on P(n) but on some earlier case. **Strong induction** lets you assume P holds for *every* value from the base up to n.

1. **Base case(s)**: prove P(b), and any others the step can't reach.
2. **Step**: assume P(b), P(b + 1), ..., P(n) all hold; prove P(n + 1).

### Example: every integer n ≥ 2 is a product of primes

```
Step: assume every k with 2 ≤ k ≤ n
is a product of primes. Consider n+1.

Case n+1 is prime: it is a product of
  one prime.  ✓
Case n+1 is composite: n+1 = a·b with
  2 ≤ a, b ≤ n. By the IH, a and b
  are products of primes, so a·b is
  too.  ✓                         ∎
```

Weak induction would only let you assume the claim for n, which says nothing about a and b. (Base n = 2: 2 is prime. The case analysis actually covers it, but stating it is good practice.)

### Example: postage with 4p and 5p stamps

Claim: every amount n ≥ 12 can be made with 4p and 5p stamps.

```
Bases:
  12 = 4+4+4      13 = 4+4+5
  14 = 4+5+5      15 = 5+5+5
Step (n+1 ≥ 16): (n+1) − 4 ≥ 12,
  so by the IH it can be made.
  Add one 4p stamp.               ∎
```

The step reaches back 4 places, so it needs four base cases. Leave one out and 15 (say) is never covered. Note 11 is impossible, which is why the claim starts at 12.

Strong and weak induction prove exactly the same things: you can always turn strong into weak by making the hypothesis "P holds for all values up to n". Use whichever makes the proof clearer. Both rest on the **well-ordering principle**: every non-empty set of natural numbers has a smallest element. If P failed somewhere there would be a *smallest* failure, and the step shows it cannot be one.

## Structural induction

Lists, trees, expressions and programs are defined **recursively**: base objects, plus rules that build bigger objects from smaller ones. **Structural induction** proves a property for every such object.

1. **Base**: prove it for each base object.
2. **Step**: for each construction rule, assume it for the parts and prove it for the whole.

### Example: leaves in a full binary tree

A **full binary tree** is either a single leaf, or a root with exactly two children, each of which is a full binary tree.

Claim: in every full binary tree, leaves L = internal nodes I + 1.

```
Base: one leaf. L = 1, I = 0.  ✓

Step: tree T = root + subtrees T1, T2.
IH: L1 = I1 + 1 and L2 = I2 + 1.
Leaves of T:    L = L1 + L2
Internal of T:  I = I1 + I2 + 1
                       (the root)
L = (I1 + 1) + (I2 + 1)
  = (I1 + I2 + 1) + 1 = I + 1.    ∎
```

Consequence: a full binary tree with n leaves has 2n − 1 nodes. A single-elimination tournament with 64 teams, one elimination per match and no extra placement or replay matches, has 63 matches; a Huffman tree over 256 symbols has 255 internal nodes.

The induction follows the tree constructors rather than incrementing a numerical size parameter. You could induct on height or node count, but structural induction follows the definition directly, which is usually simpler. It is also how compilers and type checkers are proved correct: by induction over the syntax tree, one rule per kind of node.

## Strengthening the hypothesis

Sometimes induction fails because the IH is too *weak* to carry the step. The surprising fix is to prove something **stronger**.

Claim: 1/1² + 1/2² + ... + 1/n² < 2 for every n ≥ 1.

Try it directly: assume S(n) < 2. Then S(n + 1) = S(n) + 1/(n+1)² < 2 + (something positive). Stuck: knowing S(n) < 2 leaves no room for the next term.

Prove instead the stronger S(n) ≤ 2 − 1/n:

```
Base n = 1:  S(1) = 1 ≤ 2 − 1 = 1. ✓

Step: assume S(n) ≤ 2 − 1/n.
S(n+1) ≤ 2 − 1/n + 1/(n+1)²
Want   ≤ 2 − 1/(n+1), i.e.
  1/n − 1/(n+1) ≥ 1/(n+1)²
  1/(n(n+1))    ≥ 1/(n+1)²
True since n < n+1.               ∎
```

Since 2 − 1/n < 2, the original claim follows. The stronger statement tracks *how far* below 2 we are, which is exactly what the step needs. The same trick appears when choosing loop invariants in the next lesson.

## How induction proofs go wrong

The famous bad proof: "all horses are the same colour".

```
Claim: any n horses share a colour.
Base n = 1: trivially true.
Step: take n+1 horses. Remove horse A:
  n horses, same colour by IH.
Remove horse B instead: same colour.
They overlap, so all n+1 match.
```

The step silently assumes the two groups of n overlap. For n + 1 = 2, removing A leaves {B} and removing B leaves {A}: no overlap. The step P(1) → P(2) fails, so the chain breaks at the first link.

Other common errors:

- **No base case**, or one that doesn't match where the step starts.
- **Assuming P(n + 1)** in the step and working backwards to something true.
- **Step that doesn't apply to every n**, as with the horses.
- **Calling a strong-induction step on a value below the base**, such as using n − 4 when n − 4 < 12.

## Key takeaways
- Weak induction: prove P(base) and P(n) → P(n + 1) for arbitrary n; both parts are essential.
- Strong induction assumes all earlier cases; use it when the step reaches back further than one, and supply enough base cases.
- Structural induction follows a recursive definition: one base case per base object, one step per construction rule.
- A recursive correctness proof uses base cases and correctness of smaller calls, with termination and implementation limits handled explicitly.
- If the step gets stuck, try proving a stronger statement.

## Further reading
- [Mathematical induction — Wikipedia](https://en.wikipedia.org/wiki/Mathematical_induction)
- [Strong induction — Wikipedia](https://en.wikipedia.org/wiki/Strong_induction)
- [Structural induction — Wikipedia](https://en.wikipedia.org/wiki/Structural_induction)
- [Well-founded relation — Wikipedia](https://en.wikipedia.org/wiki/Well-founded_relation)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
