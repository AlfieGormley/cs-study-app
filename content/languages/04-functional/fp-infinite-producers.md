---
id: fp-infinite-producers
title: Infinite structures and finite consumers
level: intermediate
minutes: 3
sourceLesson: fp-laziness
summary: Productive infinite structures yield finite demanded prefixes.
---

Productive infinite structures yield finite demanded prefixes. This unit develops that mechanism using the earlier units as prerequisites.

## Infinite data structures

Laziness lets you define structures that are conceptually infinite, because only the parts you look at are ever built.

```haskell
-- Only the requested prefix is demanded.
nats = [1 ..]          -- 1, 2, 3, ...
take 5 nats            -- [1,2,3,4,5]

evens = filter even [1 ..]
take 3 evens           -- [2,4,6]
```

The famous self-referential Fibonacci list:

```haskell
-- The tail shares earlier sequence values.
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)
take 8 fibs   -- [0,1,1,2,3,5,8,13]
```

It works because each element only depends on the two before it, which already exist by the time it's demanded:

```
fibs        = 0 : 1 : 1 : 2 : 3 : ...
tail fibs   = 1 : 1 : 2 : 3 : ...
zipWith (+) = 1 : 2 : 3 : 5 : ...
```

(In Haskell, `:` puts an element on the front of a list, and `zipWith (+)` adds two lists element by element.) The code is a direct transcription of the mathematical definition of the Fibonacci numbers:

```formula
F_0 = 0
F_1 = 1
F_n = F_{n−1} + F_{n−2}   for n ≥ 2
where
F_n: the n-th Fibonacci number, counting from F_0
F_0, F_1: the two starting values, 0 and 1
F_{n−1}, F_{n−2}: the two Fibonacci numbers just before F_n
n: the position in the sequence, a whole number
≥: greater than or equal to
In words: after the first two, every Fibonacci number is the sum of the two before it; adding fibs to its own tail (fibs shifted one place) computes exactly those sums.
```

For example, the eighth value, counting the initial zero, is thirteen: it adds the preceding eight and five. It is the final value in `take 8 fibs`.

## Separating producers from consumers

John Hughes's paper *Why Functional Programming Matters* argued that this is the real power of laziness: you can write a **producer** that generates every candidate, and a separate **consumer** that decides how many to take. Neither needs to know about the other.

```haskell
-- Definitions of the helpers are omitted.
-- producer: all approximations
approx = iterate improve guess
-- consumer: stop when close enough
answer = within 1e-9 approx
```

Strict languages can also separate producers and consumers using iterators, callbacks or explicit thunks.

## Key takeaways
- Productive infinite structures yield finite demanded prefixes.
- A separate consumer controls how far a producer is evaluated.

## Further reading
- [Haskell 2010 report: Prelude definitions](https://www.haskell.org/onlinereport/haskell2010/haskellch9.html)
- [Hughes](https://www.cse.chalmers.se/~rjmh/Papers/whyfp.html)
