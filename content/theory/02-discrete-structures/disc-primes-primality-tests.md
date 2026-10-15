---
id: disc-primes-primality-tests
title: "Prime density and primality tests"
level: advanced
minutes: 3
summary: "Prime density explains why choosing random candidate integers can work efficiently."
sourceLesson: disc-number-theory
---

## Primes

A **prime number** has exactly two positive divisors, 1 and itself. The **fundamental theorem of arithmetic** says every integer above 1 factors into primes in exactly one way (up to order). There are infinitely many primes (Euclid again), and the **prime number theorem** says how common they are:

```formula
π(x) ≈ x / ln(x)
1 / ln(2^1024) ≈ 1 / 710
2 × (1 / 710) ≈ 1 / 355
where
π(x): the prime-counting function: how many primes there are up to x (here π does not mean 3.14159)
x: a large positive number
ln: the natural logarithm, log to base e ≈ 2.718; ln(2^1024) = 1024 × ln(2) ≈ 709.8
≈: is approximately equal to (the approximation improves as x grows)
In words: about 1 in ln(x) numbers near x are prime. Near 2^1024 that is about 1 in 710, and if you only try odd numbers the prime probability roughly doubles to about 1 in 355.
```

So a random 1024-bit odd number is prime with probability roughly 1 in 355. That is why generating RSA primes by "pick random, test, repeat" is quick: a few hundred tries on average.

### Finding and testing primes

- **Trial division**: try every divisor up to the square root of the number (a factor above the square root would need a partner below it). Fine for small numbers, hopeless for 300-digit numbers.
- **Sieve of Eratosthenes**: list all primes up to a limit N in O(N log log N) time by crossing out multiples of each prime.

```python
from math import isqrt

def primes_upto(n):
    if n < 2:
        return []
    is_p = [True] * (n + 1)
    # Neither zero nor one is prime.
    is_p[0] = is_p[1] = False
    for i in range(2, isqrt(n) + 1):
        if is_p[i]:
            # Smaller multiples are marked.
            for j in range(i*i, n+1, i):
                is_p[j] = False
    return [i for i, p in enumerate(is_p)
            if p]
```

- **Miller–Rabin**: a probabilistic test. For a fixed odd composite number, each round with an independently, uniformly chosen base wrongly reports "probably prime" with probability at most 1/4. OpenSSL documents trial division followed by Miller–Rabin rounds; its round policy is version-dependent.

The rounds are independent, so their failure chances multiply:

```formula
P_false ≤ (1/4)^k
(1/4)^40 = 2^{−80} ≈ 8.3 × 10^{−25}
where
P_false: the probability that a fixed composite number passes every round
k: the number of independent rounds, here 40
≤: is less than or equal to
≈: is approximately equal to
In words: each round lets a composite slip through at most a quarter of the time, so 40 rounds let it through at most 1 time in 2^80.
```

This is a conditional false-pass bound for one given composite, not the probability that a number which passed is composite (that also depends on how candidates are chosen).

Testing primality is easy; **factoring** a product of two large primes is believed to be hard. Factoring an RSA modulus breaks its private-key protection, but hardness of factoring alone is not a proof that every RSA-based scheme is secure.

## Key takeaways

- Prime density explains why choosing random candidate integers can work efficiently.
- Miller–Rabin gives a conditional false-pass bound for a fixed composite with independent random bases.

## Further reading

- [Miller–Rabin primality test — Wikipedia](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [Handbook of Applied Cryptography, Chapter 4](https://cacr.uwaterloo.ca/hac/about/chap4.pdf)
