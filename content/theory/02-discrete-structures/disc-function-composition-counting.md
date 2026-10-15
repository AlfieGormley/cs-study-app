---
id: disc-function-composition-counting
title: "Composition, function counts and round trips"
level: basic
minutes: 4
summary: "Composition runs the right-hand function first; merging reachable inputs loses information."
sourceLesson: disc-sets-functions
---

### Composition and inverses

**Composition** chains two functions: apply one, then feed its output to the other.

```formula
(g ∘ f)(x) = g(f(x))
f(x) = x + 1,  g(y) = 2 × y
(g ∘ f)(3) = g(4) = 8
where
f: the first function applied, from A to B
g: the second function applied, from B to C
x: an input from the domain A of f
y: an input to g, from the set B
∘: composition, read "after": g ∘ f means "g after f"
In words: g ∘ f runs f first and then g on the result. With f adding 1 and g doubling, 3 becomes 4 and then 8. The order matters: f ∘ g would give 2 × 3 + 1 = 7.
```

Compositions preserve the properties above: two injections compose to an injection, two surjections to a surjection, and two bijections to a bijection.

If g ∘ f is injective, then f must be injective (if f merged two inputs, g could not separate them again). If a stage merges two intermediate states actually produced that arose from distinct valid inputs, later deterministic stages cannot recover that distinction without additional information. Non-injectivity only on states the pipeline never reaches need not lose information.

### Counting functions

For finite sets, including empty sets, you can count how many functions of each kind exist. Each input chooses an output; for an injection, each choice must avoid the outputs already used.

```formula
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
In words: each of the m inputs freely picks one of n outputs, giving n^m functions; an injection must use a new output each time, giving n × (n − 1) × … for m factors; a bijection from a set to itself is a reordering (permutation), and there are m! of those.
```

A worked example with three inputs and four possible outputs:

```formula
n^m = 4^3 = 64
n! / (n − m)! = 4! / 1! = 4 × 3 × 2 = 24
where
n: the number of possible outputs, here 4
m: the number of inputs, here 3
!: factorial: the product of all whole numbers from 1 up to that number, so 4! = 24 and 1! = 1
In words: from a 3-element set to a 4-element set there are 64 functions, of which 24 never repeat an output.
```

Use the counting convention 0⁰ = 1 for the unique empty-domain function. There are 2⁸ = 256 functions from the 8 bit positions of a byte to {0, 1}: one per byte value.

## Functions in real code

The mathematical idea of a function is stricter than a programming "function". A routine whose result depends on changing hidden state may return different results for the same explicit arguments. Including the relevant state in the mathematical input gives a function again; reading an immutable constant does not itself violate determinism. Pure terminating routines fit the simple total-function model and can be easier to test, memoise and parallelise.

Bijections show up whenever you need a lossless round trip:

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
