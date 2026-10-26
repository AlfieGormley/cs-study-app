---
id: disc-integer-division
title: "Integer division and negative remainders"
level: advanced
minutes: 3
summary: "A positive divisor gives a unique non-negative mathematical remainder."
sourceLesson: disc-number-theory
---

Number theory underpins public-key systems such as RSA and finite-field or elliptic-curve key exchange. HTTPS can use different TLS authentication and key-exchange modes; RSA is not required for every connection. Even outside cryptography it is everywhere: hash functions, ring buffers, random number generators, checksums and consistent hashing all live in **modular arithmetic**.

The immediate practical question is how remainders behave when inputs can be negative, particularly when the result becomes an array index.

## Division and remainders

Everything starts with whole-number division with a remainder, the kind you learned before decimals. Dividing any integer by a positive integer gives exactly one quotient and one remainder, as long as the remainder is required to lie between 0 and the divisor:

```formula essential
a = q × n + r
0 ≤ r < n
r = a mod n
where
a: the integer being divided (it may be negative)
n: the divisor, also called the modulus: a positive integer
q: the quotient: how many whole times n fits into a, rounding down
r: the remainder, always from 0 up to n − 1
mod: "modulo": a mod n is the remainder r left after dividing a by n
≤: is less than or equal to
<: is less than
In words: any integer a can be written as a whole number of n's plus a leftover r between 0 and n − 1, and that leftover is a mod n.
```

For negative seven and positive divisor three, the floored quotient is negative three and the remainder is two. The remainder brings negative nine back up to negative seven.

For negative dividends, the mathematical quotient rounds down rather than towards zero. In Python, `divmod(a, n)` returns the quotient and remainder together.

> [!warning] Negative numbers differ by language
> Python's `%` follows the rule above, so `-7 % 3` is `2` (and `-7 // 3` is `-3`). Modern C/C++, Java and Go integer division truncates towards zero. JavaScript Number division is floating-point, but its remainder also gives `-7 % 3 == -1` (BigInt division truncates). A negative remainder may be an invalid index. For a positive modulus use Java `Math.floorMod`, or compute `r = a % n` and add `n` only when `r < 0`. Unconditionally adding `n` in `((a % n) + n) % n` can overflow a fixed-width signed integer.

## Key takeaways

- A positive divisor gives a unique non-negative mathematical remainder.
- Programming languages differ on negative division; use the operation that matches the intended indexing rule.

## Further reading

- [Modular arithmetic — Wikipedia](https://en.wikipedia.org/wiki/Modular_arithmetic)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
