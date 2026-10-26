---
id: disc-function-injectivity-surjectivity
title: "Injective, surjective and bijective functions"
level: basic
minutes: 3
summary: "Injective functions preserve distinctions; surjective functions cover the codomain; bijections do both."
sourceLesson: disc-sets-functions
---

Three properties matter:

- **Injective** (one-to-one): different inputs give different outputs.
- **Surjective** (onto): every element of the codomain is hit by some input, so the image equals the codomain.
- **Bijective**: both. Every element of the codomain is hit by exactly one input, so an **inverse function** can undo the mapping.

The domain declares the allowed inputs; the codomain declares the allowed outputs. The reference card expresses these properties and the two-way round trip formally.

```formula reference
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
In words: An injection preserves differences between inputs. A surjection reaches every declared output. A bijection does both, so it has an inverse that undoes the mapping in both directions.
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

For finite sets, an injection cannot have more inputs than possible outputs; a surjection cannot have fewer inputs than required outputs; and a bijection requires equal sizes.

These are necessary size constraints, not guarantees about a particular mapping: even equally sized sets can be connected by a function that merges inputs.

The first one is the **pigeonhole principle** in disguise: put 5 pigeons in 4 holes and two pigeons must share.

> [!example] Why hash functions collide
> Standard SHA-256 accepts messages shorter than 2⁶⁴ bits and produces one of 2²⁵⁶ outputs. Its finite input domain is still vastly larger than its output space. No function from a larger set to a smaller one can be injective, so collisions must exist. Cryptographic hashes are designed so that *finding* one is infeasible, not so that none exist.

## Codomain changes surjectivity

Whether a function is surjective depends on the declared codomain.

Squaring real numbers reaches exactly the non-negative reals. Declaring all real numbers as the codomain makes it non-surjective; declaring only the non-negative reals makes it surjective. Changing the codomain does not stop a positive and negative input sharing a square.

> [!analogy] Real-world analogy: Tickets and seats
> A seat assignment can give every ticket a different seat while leaving some seats empty. It can also fill every seat while assigning some seats more than once.
>
> **How it maps:** Different seats per ticket models injectivity; every seat used models surjectivity. A perfect one-ticket-per-seat match is bijective.
>
> **Where it stops:** This is only a mapping model: a real venue would reject duplicated seat assignments.

## Key takeaways

- Injective functions preserve distinctions; surjective functions cover the codomain; bijections do both.
- Surjectivity depends on the declared codomain, and a smaller hash output space forces collisions.

## Further reading

- [Bijection, injection and surjection — Wikipedia](https://en.wikipedia.org/wiki/Bijection)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
