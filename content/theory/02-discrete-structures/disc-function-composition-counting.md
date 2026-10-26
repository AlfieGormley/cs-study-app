---
id: disc-function-composition-counting
title: "Composition, function counts and round trips"
level: basic
minutes: 3
summary: "Composition runs the right-hand function first; merging reachable inputs loses information."
sourceLesson: disc-sets-functions
---

### Composition and inverses

**Composition** chains two functions: apply one, then feed its output to the other.

```formula essential
(g ∘ f)(x) = g(f(x))
where
f: the first function applied, from A to B
g: the second function applied, from B to C
A, B, C: the input, intermediate and final output sets, respectively
x: an input from the domain A of f
∘: composition, read "after": g ∘ f means "g after f"
In words: Composition runs the right-hand function first and feeds its output into the left-hand function. Order can change the result.
```

Adding one then doubling a number can differ from doubling then adding one. Composition therefore depends on order.

Compositions preserve these properties: two injections compose to an injection, two surjections to a surjection, and two bijections to a bijection.

If g ∘ f is injective, then f must be injective (if f merged two inputs, g could not separate them again). If a stage merges two intermediate states actually produced that arose from distinct valid inputs, later deterministic stages cannot recover that distinction without additional information. Non-injectivity only on states the pipeline never reaches need not lose information.

### Counting functions

For finite sets, including empty sets, you can count how many functions of each kind exist. Each input chooses an output; for an injection, each choice must avoid the outputs already used.

```formula reference
N_all = n^m
N_inj = n! / (n − m)!   if m ≤ n
N_inj = 0   if m > n
N_bij = m!   when A = B
where
N_all: the number of functions from A to B
N_inj: the number of injections from A to B
N_bij: the number of bijections from A to itself

A: the domain, with m elements
B: the codomain, with n elements
m: the number of elements in A (the inputs)
n: the number of elements in B (the possible outputs)
n^m: m copies of n multiplied together
!: factorial: k! = k × (k − 1) × … × 2 × 1, with 0! = 1
≤: is less than or equal to
>: is greater than
In words: Counting all functions allows every input to reuse any output. Counting injections forbids reusing an output; counting bijections of a finite set counts its reorderings.
```

For three inputs and four outputs, unrestricted functions allow reuse of outputs. Injections forbid reuse, so their available choices shrink after each assignment.

There is one function on an empty domain: it makes no assignments. The reference count uses the combinatorial convention that zero to the zeroth power is one.

## Functions in real code

The mathematical idea of a function is stricter than a programming "function". A routine whose result depends on changing hidden state may return different results for the same explicit arguments. Including the relevant state in the mathematical input gives a function again; reading an immutable constant does not itself violate determinism. Pure terminating routines fit the simple total-function model and can be easier to test, memoise and parallelise.

Injectivity is essential whenever you need a lossless round trip:

- **Serialisation**: `decode(encode(x)) == x` for every valid x is a requirement that `encode` is injective, and `decode` is its inverse on the image.
- **Base64, UTF-8, gzip**: with a fixed encoder configuration and appropriate valid input domain, lossless round trips require injectivity. Ordinary lossy JPEG and MP3 encoding merge distinct inputs; the JPEG family also includes lossless modes.
- **Primary keys**: projecting each row to its primary-key value uniquely identifies that row. A primary key combines uniqueness with non-nullness; a bare UNIQUE constraint can permit multiple nulls depending on the database and configuration.
- **Permutations in shuffles and ciphers**: a block cipher with a fixed key is a bijection on blocks, otherwise decryption would be ambiguous.

An output side effect can violate purity even when the returned result is deterministic.

## Key takeaways

- Composition runs the right-hand function first; merging reachable inputs loses information.
- Counting total functions chooses an output for every input; lossless round trips require injective encoding.

## Further reading

- [Bijection, injection and surjection — Wikipedia](https://en.wikipedia.org/wiki/Bijection)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
