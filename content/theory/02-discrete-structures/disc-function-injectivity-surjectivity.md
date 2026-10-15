---
id: disc-function-injectivity-surjectivity
title: "Injective, surjective and bijective functions"
level: basic
minutes: 4
summary: "Injective functions preserve distinctions; surjective functions cover the codomain; bijections do both."
sourceLesson: disc-sets-functions
---

Three properties matter:

- **Injective** (one-to-one): different inputs give different outputs.
- **Surjective** (onto): every element of the codomain is hit by some input, so the image equals the codomain.
- **Bijective**: both. Every element of the codomain is hit by exactly one input, so f has an **inverse function** that undoes it.

In symbols, for a function f from A to B, the first line is injectivity, the second surjectivity, and the last two describe the inverse of a bijection:

```formula
f(x) = f(y) ⇒ x = y
∀ b ∈ B, ∃ a ∈ A such that f(a) = b
f^{−1} : B → A
f^{−1}(f(a)) = a   and   f(f^{−1}(b)) = b
where
f: a function from A to B
A: the domain, the set of inputs
B: the codomain, the set outputs lie in
x, y: any two inputs from A
a: an input from A
b: an element of the codomain B
⇒: implies
∀: "for every"
∃: "there exists": at least one such element exists
f^{−1}: the inverse of f, read "f inverse": the function that sends each output back to the one input that produced it. The −1 is a label, not a power: f^{−1} is not 1 / f
∈: is an element of
→: in "f^{−1} : B → A", "maps elements of B to elements of A"
In words: injective means two inputs only share an output if they are the same input; surjective means every b in B is the output of at least one a; when both hold (bijective), every b has exactly one a, so f^{−1} can run f backwards and the round trip in either direction gets you back where you started.
```

```
injective    surjective   bijective
not onto     not 1-to-1
a -> 1       a -> 1       a -> 1
b -> 2       b -> 1       b -> 2
c -> 3       c -> 2       c -> 3
     4
```

In the left column nothing maps to 4, so the map is not onto. In the middle, a and b share 1, so it is not one-to-one. The right column is a perfect pairing.

For finite sets these properties limit the sizes. An injection from A to B can exist only when A is no bigger than B; a surjection only when A is at least as big as B; and a bijection only when they are the same size:

```formula
|A| ≤ |B|
|A| ≥ |B|
|A| = |B|
where
A: the domain, a finite set
B: the codomain, a finite set
| |: the cardinality: the number of elements
≤: is less than or equal to
≥: is greater than or equal to
In words: line 1 must hold for an injection (you cannot send more things to fewer places without two sharing), line 2 for a surjection (you cannot cover more places than you have things), and line 3 for a bijection (a perfect pairing needs equal sizes).
```

The first one is the **pigeonhole principle** in disguise: put 5 pigeons in 4 holes and two pigeons must share.

> [!example] Why hash functions collide
> Standard SHA-256 accepts messages shorter than 2⁶⁴ bits and produces one of 2²⁵⁶ outputs. Its finite input domain is still vastly larger than its output space. No function from a larger set to a smaller one can be injective, so collisions must exist. Cryptographic hashes are designed so that *finding* one is infeasible, not so that none exist.

## Codomain changes surjectivity

Whether a function is surjective depends on the declared codomain.

The codomain-versus-image example in symbols:

```formula
f : ℝ → ℝ,   f(x) = x^2
f(ℝ) = [0, ∞)
where
f: the squaring function, with domain and codomain ℝ in this displayed declaration
→: maps inputs to outputs in the declared codomain
x: a real-number input
x^2: x multiplied by itself
ℝ: the real numbers: every point on the number line
f(ℝ): the image of f: every output it actually produces
[0, ∞): the non-negative reals: every real number from 0 upwards, with no upper limit
∞: infinity: the interval goes on without end
In words: squaring hits exactly the non-negative reals, so it is surjective if its declared codomain is [0, ∞) and not surjective if the codomain is all of ℝ (−1 is never an output).
```

## Key takeaways

- Injective functions preserve distinctions; surjective functions cover the codomain; bijections do both.
- Surjectivity depends on the declared codomain, and a smaller hash output space forces collisions.

## Further reading

- [Bijection, injection and surjection — Wikipedia](https://en.wikipedia.org/wiki/Bijection)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
