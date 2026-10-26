---
id: disc-function-domain-image
title: "Functions, domains and images"
level: basic
minutes: 2
summary: "A total function gives each allowed input exactly one output."
sourceLesson: disc-sets-functions
---

## Functions

A **mathematical function** assigns to every element of its **domain** exactly one element of its **codomain**. Two conditions: every input has an output, and no input has two outputs.

```formula essential
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

The **function image** (often called the range) is the set of outputs actually hit. It is contained in the codomain but can leave some declared outputs unused.

For example, doubling integer inputs produces only even integers. If all integers are the codomain, 3 is allowed by that declaration but never reached.

## Key takeaways

- A total function gives each allowed input exactly one output.
- The codomain declares possible outputs; the image contains only outputs actually reached.

## Further reading

- [Set (mathematics) — Wikipedia](https://en.wikipedia.org/wiki/Set_(mathematics))
- [Bijection, injection and surjection — Wikipedia](https://en.wikipedia.org/wiki/Bijection)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
