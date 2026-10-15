---
id: disc-function-domain-image
title: "Functions, domains and images"
level: basic
minutes: 3
summary: "A total function gives each allowed input exactly one output."
sourceLesson: disc-sets-functions
---

## Functions

A **mathematical function** assigns to every element of its **domain** exactly one element of its **codomain**. Two conditions: every input has an output, and no input has two outputs.

```formula
f : A → B
f(a) ∈ B   for every a ∈ A
where
f: the function's name
A: the domain: the set of allowed inputs
B: the codomain: the set the outputs are declared to lie in
a: any input taken from A
f(a): the single output f gives for input a
→: in "f : A → B", "maps elements of A to elements of B"
∈: is an element of
In words: f takes each element of A and gives back exactly one element of B.
```

There is exactly one function from an empty domain to any codomain: it makes no assignments. A nonempty domain cannot map into an empty codomain.

The **function image** (often called the range) is the set of outputs actually hit:

```formula
f(A) = { f(a) : a ∈ A }
f(A) ⊆ B
where
f(A): the image of f: every output that some input actually produces
f: a function from the set A to the set B
A: the domain, the set of inputs
B: the codomain
a: an input taken from A
f(a): the output for input a
∈: is an element of
⊆: is a subset of
{ : }: the set of all values f(a), one for each a in A
In words: the image collects every output f really produces. It is always inside the codomain and may be smaller.
```

For example, doubling an integer:

```formula
f : ℤ → ℤ,   f(x) = 2 × x
f(ℤ) = {…, −4, −2, 0, 2, 4, …}
where
f: the doubling function
x: an integer input
ℤ: the integers: …, −2, −1, 0, 1, 2, …
f(ℤ): the image of f: every output it actually produces
→: in "f : ℤ → ℤ", f takes integers and its declared codomain is the integers
…: and so on in both directions
In words: doubling hits only the even integers, so the image is smaller than the codomain: 3, for example, is in the codomain but never an output.
```

## Key takeaways

- A total function gives each allowed input exactly one output.
- The codomain declares possible outputs; the image contains only outputs actually reached.

## Further reading

- [Set (mathematics) — Wikipedia](https://en.wikipedia.org/wiki/Set_(mathematics))
- [Bijection, injection and surjection — Wikipedia](https://en.wikipedia.org/wiki/Bijection)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
