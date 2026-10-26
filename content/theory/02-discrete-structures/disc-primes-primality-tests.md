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

```formula reference
π(x) ≈ x / ln(x)
where
π(x): the prime-counting function: how many primes there are up to x (here π does not mean 3.14159)
x: a large positive number
ln: the natural logarithm, with base approximately 2.718
≈: asymptotically approximate: the ratio of the two sides tends to one as x grows without bound
In words: Primes become less dense as numbers grow, but slowly enough that repeated random candidate testing remains useful. Trying odd candidates avoids the obvious even composites.
```

For uniformly chosen odd candidates of about 1024 bits, the approximate prime density is one in a few hundred. This is a density estimate, not a measured key-generation latency.

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

```formula reference
P_false ≤ (1/4)^k
where
P_false: the probability that a fixed composite number passes every round
k: the positive number of independent rounds
≤: is less than or equal to
In words: For one fixed odd composite, independent uniformly chosen Miller–Rabin bases multiply the per-round false-pass bound. This is not the probability that an arbitrary passing candidate is composite.
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
