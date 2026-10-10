---
id: logp-induction
title: Induction (weak, strong, structural)
level: intermediate
minutes: 18
summary: Proving statements about every natural number, every list or every tree with induction, including strong and structural induction, strengthening the hypothesis, and why recursion and induction are the same idea.
---

Many claims in computer science are about *every* size of input: every n, every list, every tree. You cannot check infinitely many cases, and the techniques from the last lesson often don't get a grip on "every n".

**Mathematical induction** is the tool for this. It turns an infinite claim into two finite pieces of work. It is also exactly how you should think about recursive code: if the base case is right, and each call is right assuming the smaller calls are right, the function is right.

## The domino picture

Imagine an infinite row of dominoes. To know they all fall, you need two facts:

1. The first domino falls.
2. Whenever a domino falls, it knocks over the next one.

Neither fact alone is enough. With both, every domino falls. In the sketch below, P(n) is the claim about the number n (domino n falls), and each arrow means "leads to":

```
P(0)  ->  P(1)  ->  P(2)  ->  P(3) ...
 ^base     \_ step: P(n) -> P(n+1) _/
```

## Weak (ordinary) induction

To prove P(n) for every integer n ≥ b:

1. **Base case**: prove P(b).
2. **Inductive step**: for an arbitrary n ≥ b, **assume P(n)** (the **inductive hypothesis**, IH) and prove P(n + 1).

Written as a single formula, the principle of induction says:

```formula
P(b) ∧ ∀n ≥ b (P(n) → P(n + 1))
  → ∀n ≥ b P(n)
where
P(n): the statement being proved about the integer n, which is either true or false for each n
b: the base value, the first n the claim is about (often 0 or 1)
n: an integer at least b
∧: AND: both parts must be proved
∀: "for all"; ∀n ≥ b means "for every integer n from b upwards"
→: implies: "if ... then ..."
≥: is greater than or equal to
In words: if the claim holds at b, and whenever it holds for some n it also holds for n + 1, then it holds for every n from b upwards.
```

The inductive step is a direct proof of an implication. You do not assume P(n) is true for all n; you assume it for one arbitrary n and show the next case follows.

### Example: the sum 1 + 2 + ... + n

The claim, for all n ≥ 1, is the formula for adding up the first n whole numbers:

```formula
1 + 2 + ... + n = n × (n + 1) / 2
where
n: how many whole numbers are being added, n ≥ 1
...: and so on: every whole number between 2 and n
In words: the sum of 1 to n is n times n + 1, halved. For n = 4: 1 + 2 + 3 + 4 = 10 = 4 × 5 / 2.
```

**Base case**, n = 1: the left-hand side is 1, and the right-hand side is 1 × 2 / 2 = 1. ✓

**Step**: assume the formula holds for n (the IH). Add the next number, n + 1, to both sides:

```formula
1 + ... + n + (n + 1)
  = n × (n + 1) / 2 + (n + 1)
  = (n + 1) × (n / 2 + 1)
  = (n + 1) × (n + 2) / 2
where
n: an arbitrary whole number at least 1, for which the formula is assumed (the inductive hypothesis)
...: every whole number in between
In words: the second line uses the IH to replace 1 + ... + n; factoring out n + 1 then gives exactly the formula with n + 1 in place of n.
```

That is the formula for n + 1, so the claim holds for every n ≥ 1. ∎ (The symbol ∎ marks the end of a proof, and ✓ marks a checked step.)

This is why a nested loop where the inner loop runs i times, for i = 1 to n, does n(n+1)/2 iterations, which grows like n²: in Big-Theta notation, Θ(n²).

### Example: the base case matters

Claim: 2ⁿ > n² for all n ≥ 5 (2ⁿ is 2 multiplied by itself n times, n² is n times n).

**Base case**, n = 5: 2⁵ = 32 and 5² = 25, and 32 > 25. ✓

**Step**: assume 2ⁿ > n² for some n ≥ 5. Doubling both sides gives the first line below; the rest shows that 2n² is at least (n + 1)²:

```formula
2^{n+1} = 2 × 2^n > 2 × n^2
2 × n^2 ≥ (n + 1)^2 = n^2 + 2 × n + 1
  iff n^2 ≥ 2 × n + 1
n^2 ≥ 3 × n = 2 × n + n > 2 × n + 1
  for n ≥ 3
where
n: an integer with 2^n > n^2 assumed (the inductive hypothesis)
2^n: 2 multiplied by itself n times
n^2: n multiplied by itself
>, ≥: is greater than, is greater than or equal to
In words: doubling 2^n keeps it above 2n², and 2n² is at least (n + 1)² whenever n ≥ 3, so 2^{n+1} > (n + 1)².
```

So 2ⁿ⁺¹ > (n + 1)². ∎

The inductive step works for every n ≥ 3, yet the claim is **false** at n = 3 (2³ = 8 is less than 3² = 9) and at n = 4 (2⁴ = 16 equals 4² = 16). Without a correct base case, a valid step proves nothing. The dominoes are lined up, but the first one you push must actually fall.

## Recursion is induction

Here is a recursive function and its correctness proof side by side.

```python
def total(xs):
    if not xs:              # base case
        return 0
    return xs[0] + total(xs[1:])
```

In an ideal execution model, total(xs) returns the exact sum of any finite integer list. Induct on the length n of the list. Actual Python has a recursion limit and finite resources; this slicing implementation also copies Θ(n²) list elements overall (a number of copies that grows like n²). Floating-point addition does not obey all exact-arithmetic rearrangements.

- **Base, n = 0**: the empty list returns 0, its sum. ✓
- **Step**: assume `total` is correct on all lists of length n. A list of length n + 1 returns `xs[0] + total(xs[1:])`. The tail has length n, so by the IH that call returns the tail's sum. Adding `xs[0]` gives the whole sum. ✓

That is exactly the "leap of faith" you make when writing recursion: trust the recursive call on a smaller input. Induction is what makes the leap legitimate. It also tells you what can go wrong: a missing base case, or a recursive call that is not on a smaller input, breaks the proof and usually the program.

## Strong induction

Sometimes P(n + 1) depends not on P(n) but on some earlier case. **Strong induction** lets you assume P holds for *every* value from the base up to n.

1. **Base case(s)**: prove P(b), and any others the step can't reach.
2. **Step**: assume P(b), P(b + 1), ..., P(n) all hold; prove P(n + 1).

### Example: every integer n ≥ 2 is a product of primes

**Step**: assume every k with 2 ≤ k ≤ n is a product of primes, and consider n + 1. There are two cases.

- If n + 1 is prime, it is a product of one prime. ✓
- If n + 1 is composite, split it into two smaller factors, as below. By the IH, a and b are products of primes, so a·b is too. ✓ ∎

```formula
n + 1 = a × b
2 ≤ a ≤ n
2 ≤ b ≤ n
where
n: an integer at least 2; every k from 2 to n is assumed to be a product of primes (the strong inductive hypothesis)
a, b: whole-number factors of n + 1, neither equal to 1 nor to n + 1 itself (they exist because n + 1 is composite)
≤: is less than or equal to
In words: a composite number splits into two factors that are both at least 2 and both smaller than itself, so the hypothesis covers both. For example 12 = 3 × 4.
```

Weak induction would only let you assume the claim for n, which says nothing about a and b. (Base n = 2: 2 is prime. The case analysis actually covers it, but stating it is good practice.)

### Example: postage with 4p and 5p stamps

Claim: every amount n ≥ 12 (in pence, p) can be made with 4p and 5p stamps.

**Bases**: the four amounts 12 to 15.

```formula
12 = 4 + 4 + 4
13 = 4 + 4 + 5
14 = 4 + 5 + 5
15 = 5 + 5 + 5
where
4, 5: the stamp values, in pence (p), the hundredth part of a pound sterling
In words: each of the amounts 12p, 13p, 14p and 15p can be made from 4p and 5p stamps.
```

**Step**: for n + 1 ≥ 16, the amount four pence lower is at least 12, so by the IH it can be made. Add one 4p stamp:

```formula
(n + 1) − 4 ≥ 12   for n + 1 ≥ 16
where
n + 1: the amount being made, in pence, at least 16
≥: is greater than or equal to
In words: taking a 4p stamp off any amount of 16p or more leaves an amount of at least 12p, which the hypothesis already covers. ∎
```

The step reaches back 4 places, so it needs four base cases. Leave one out and 15 (say) is never covered. Note 11 is impossible, which is why the claim starts at 12.

Strong and weak induction prove exactly the same things: you can always turn strong into weak by making the hypothesis "P holds for all values up to n". Use whichever makes the proof clearer. Both rest on the **well-ordering principle**: every non-empty set of natural numbers has a smallest element. If P failed somewhere there would be a *smallest* failure, and the step shows it cannot be one.

## Structural induction

Lists, trees, expressions and programs are defined **recursively**: base objects, plus rules that build bigger objects from smaller ones. **Structural induction** proves a property for every such object.

1. **Base**: prove it for each base object.
2. **Step**: for each construction rule, assume it for the parts and prove it for the whole.

### Example: leaves in a full binary tree

A **full binary tree** is either a single leaf, or a root with exactly two children, each of which is a full binary tree.

Claim: in every full binary tree, the number of leaves is one more than the number of internal nodes:

```formula
L = I + 1
where
L: the number of leaves (nodes with no children)
I: the number of internal nodes (nodes with two children)
In words: a full binary tree always has exactly one more leaf than it has internal nodes. A root with two leaf children has L = 2 and I = 1.
```

**Base**: a single leaf has L = 1 and I = 0. ✓

**Step**: a bigger tree T is a root joined to two smaller full binary trees T₁ and T₂. By the IH, each subtree satisfies the claim. Count T's leaves and internal nodes (the root is one extra internal node):

```formula
L_1 = I_1 + 1,   L_2 = I_2 + 1
L = L_1 + L_2
I = I_1 + I_2 + 1
L = (I_1 + 1) + (I_2 + 1)
  = (I_1 + I_2 + 1) + 1 = I + 1
where
L, I: the leaves and internal nodes of the whole tree T
L_1, I_1: the leaves and internal nodes of the left subtree T_1
L_2, I_2: the leaves and internal nodes of the right subtree T_2
T_1, T_2: the two subtrees hanging from the root
In words: the whole tree's leaves are the subtrees' leaves, and its internal nodes are the subtrees' internal nodes plus the root. Substituting the hypothesis gives L = I + 1 again. ∎
```

Consequence: a full binary tree with n leaves has n − 1 internal nodes, so 2n − 1 nodes in total. A single-elimination tournament with 64 teams, one elimination per match and no extra placement or replay matches, has 63 matches; a Huffman tree over 256 symbols has 255 internal nodes.

The induction follows the tree constructors rather than incrementing a numerical size parameter. You could induct on height or on the number of nodes, but structural induction follows the definition directly, which is usually simpler. It is also how compilers and type checkers are proved correct: by induction over the syntax tree, one rule per kind of node.

## Strengthening the hypothesis

Sometimes induction fails because the IH is too *weak* to carry the step. The surprising fix is to prove something **stronger**.

Claim: the sum of the reciprocals of the squares stays below 2:

```formula
S(n) = 1/1^2 + 1/2^2 + ... + 1/n^2
S(n) < 2   for n ≥ 1
where
S(n): the sum of 1 divided by each square from 1² up to n²
n: a whole number, n ≥ 1
...: and so on, one term for every whole number up to n
In words: however many terms you add, the total stays below 2. For n = 3: 1 + 1/4 + 1/9 ≈ 1.36.
```

Try it directly: assume S(n) < 2. Then S(n + 1) = S(n) + 1/(n + 1)², which is less than 2 plus something positive. Stuck: knowing S(n) < 2 leaves no room for the next fraction.

Prove instead the stronger claim S(n) ≤ 2 − 1/n. **Base**, n = 1: S(1) = 1 and 2 − 1 = 1, so 1 ≤ 1. ✓ **Step**: assume S(n) ≤ 2 − 1/n. The aim is to reach S(n + 1) ≤ 2 − 1/(n + 1). Adding the next fraction gives the first line below, so it is enough that the next fraction fits into the gap between 2 − 1/n and 2 − 1/(n + 1), which is the second line:

```formula
S(n + 1) ≤ 2 − 1/n + 1/(n + 1)^2
1/n − 1/(n + 1) ≥ 1/(n + 1)^2
1/(n × (n + 1)) ≥ 1/(n + 1)^2
where
S(n): the sum 1/1² + ... + 1/n², assumed at most 2 − 1/n (the strengthened hypothesis)
n: a whole number, n ≥ 1
≤, ≥: is at most, is at least
In words: the last line holds because n is less than n + 1, so n × (n + 1) is less than (n + 1)², and dividing 1 by a smaller number gives a bigger result. The third line is the second with the gap simplified, so the second line is true, which is exactly what the step needs. ∎
```

Since 2 − 1/n < 2, the original claim follows. The stronger statement tracks *how far* below 2 we are, which is exactly what the step needs. The same trick appears when choosing loop invariants in the next lesson.

## How induction proofs go wrong

The famous bad proof: "all horses are the same colour".

- **Claim**: any n horses share a colour.
- **Base**, n = 1: trivially true.
- **Step**: take n + 1 horses. Remove horse A: the remaining n horses are the same colour by the IH. Remove horse B instead: the same colour again. The two groups overlap, so all n + 1 match.

The step silently assumes the two groups of n overlap. For n + 1 = 2, removing A leaves {B} and removing B leaves {A}: no overlap. The step from P(1) to P(2) fails, so the chain breaks at the first link.

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
