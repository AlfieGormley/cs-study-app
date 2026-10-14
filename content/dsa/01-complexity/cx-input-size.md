---
id: cx-input-size
sourceLesson: cx-growth-rates
title: Input size and dominant terms
level: basic
minutes: 4
summary: Choose the right input measure and simplify a cost without forgetting its limits.
---

## What "input size" means

n should measure whatever drives the work. Usually it is obvious, but not always:

- For a list or string, n is its length.
- For a graph, the cost often depends on both vertices **V** and edges **E**, so you state both (for example "V + E").
- For arithmetic on big numbers, n is the number of **digits** or bits, not the value. Checking whether a number N is prime by trying every divisor up to N is linear in the *value*, but N has only about log_2(N) bits, so it is exponential in the *size of the input* (worked through below).
- For a matrix, say whether n is the side length or the number of entries. A matrix with n rows and n columns has n × n = n^2 entries, so a 1,000 by 1,000 matrix has a million.

The number-size point is easy to get wrong, so here it is as a formula:

```formula
b = ⌊log_2(N)⌋ + 1
N ≈ 2^b
2^64 ≈ 1.8 × 10^19
where
N: the value of the number being tested, for example 1,000,003
b: the input size: how many bits (binary digits) it takes to write N down
log_2(N): the base-2 logarithm of N, the power you raise 2 to in order to get N
⌊x⌋: floor: round x down to the nearest whole number
2^b: b copies of 2 multiplied together
≈: approximately equal to; a 64-bit number can be as large as 2^64 − 1, about 1.8 × 10^19
In words: adding one bit doubles the largest value you can write, so a loop that runs once per unit of value runs about 2^b times: exponential in the number of bits.
```

When you describe an algorithm's cost, always say what n is.

## Why we ignore the small stuff

Counting precisely (n × (n − 1) / 2 comparisons rather than "about half of n squared") quickly becomes tedious and depends on what you call "one operation". So we make two simplifications. Here they are applied to the duplicate check's count:

```formula
C(n) = n × (n − 1) / 2
C(n) = 0.5 × n^2 − 0.5 × n
C(1000) = 500000 − 500
C(2 × n) ≈ 0.5 × 4 × n^2 ≈ 4 × C(n)
where
C(n): the number of comparisons the pairwise duplicate check makes on n items
n: the number of items in the list
n^2: n squared, n × n
≈: approximately equal to (the small 0.5 × n term is ignored)
In words: the n-squared term is a thousand times bigger than the other term at n = 1,000, and doubling n multiplies it by four whatever the constant in front.
```

1. **Keep only the fastest-growing term.** In 0.5 × n^2 − 0.5 × n, the n^2 term dominates. At n = 1,000 it is 500,000 versus 500.
2. **Drop constant factors.** 0.5 × n^2 and 3 × n^2 grow in the same way: double n, quadruple the work. The constant depends on the machine and how you count; the growth shape does not.

The result is a coarse but robust label: "this algorithm is quadratic". The following asymptotic-notation lessons make this precise with Big-O, Big-Omega and Big-Theta.

> [!warning] Constants are not irrelevant in practice
> Dropping constants is a tool for comparing growth, not a claim that constants never matter. An algorithm doing 100 × n operations loses to one doing n^2 (n × n) for every input size n below 100: at n = 50 that is 5,000 operations against 2,500. The later lessons on complexity in practice cover when constants and hardware effects decide the winner.

## Key takeaways
- For integers, input size usually counts bits or digits rather than the represented value.
- State separate dimensions when several quantities drive the work.
- Dominant terms predict growth; constants can still decide the winner for small inputs.

## Further reading
- [Analysis of algorithms — Wikipedia](https://en.wikipedia.org/wiki/Analysis_of_algorithms)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
