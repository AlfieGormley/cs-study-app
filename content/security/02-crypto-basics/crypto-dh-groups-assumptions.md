---
id: crypto-dh-groups-assumptions
sourceLesson: crypto-key-exchange
title: Why DH agrees and what hardness it assumes
level: advanced
minutes: 4
summary: Exponent multiplication explains agreement; computational DH is the direct shared-secret hardness assumption.
---

Continue with prime modulus 23, generator 5 and secret exponents 6 and 15. The public values are 8 and 19; both parties compute shared value 2.

### Why they agree

Exponents multiply, and the order doesn't matter:

```formula
B^a ≡ (g^b)^a ≡ g^(ba) (mod p)
A^b ≡ (g^a)^b ≡ g^(ab) (mod p)
g^(a × b) = 5^(6 × 15) = 5^90
5^22 ≡ 1 (mod 23)
90 = 4 × 22 + 2
5^90 ≡ 1^4 × 5^2 = 25 ≡ 2 (mod 23)
where
g: the generator, 5
p: the prime modulus, 23
a, b: Alice's and Bob's secret exponents, 6 and 15
A, B: the public values g^a and g^b (mod 23)
mod: "modulo": arithmetic on remainders after dividing by 23
≡: "is congruent to": both sides leave the same remainder after dividing by 23
In words: both sides compute g raised to a × b, just in a different order; and because 5^22 leaves remainder 1, only the remainder of the exponent after dividing by 22 matters.
```

The fact that the twenty-second power of 5 leaves remainder 1 is an instance of **Fermat's little theorem**:

```formula
x^(p − 1) ≡ 1 (mod p)
5^(23 − 1) = 5^22 ≡ 1 (mod 23)
where
p: a prime
x: any whole number not divisible by p
mod: "modulo": arithmetic on remainders after dividing by p
≡: "is congruent to": both sides leave the same remainder after dividing by p
In words: modulo a prime p, raising any number not divisible by p to the power p − 1 gives remainder 1, so exponents can be reduced modulo p − 1.
```

### Why Eve can't

Eve sees everything public: 23, 5, 8 and 19. Recovering either secret exponent is one way to compute the DH shared secret, and that is the **discrete logarithm problem**:

```formula
g^a ≡ A (mod p)
5^a ≡ 8 (mod 23)
5^6 = 15625 = 679 × 23 + 8
where
g: the public generator, 5
p: the public prime, 23
A: Alice's public value, 8
a: the secret exponent Eve wants: the discrete logarithm of A to base g
mod: "modulo": arithmetic on remainders after dividing by p
≡: "is congruent to": both sides leave the same remainder after dividing by p
In words: given g, p and A, find the exponent a; with only 22 possible exponents Eve tries them all and finds 6, but for a well-chosen 2,048-bit group no known method is practical.
```

The **computational Diffie–Hellman assumption** directly assumes that obtaining the DH shared secret from the public values is infeasible in the chosen group; it does not assert a general equivalence to solving discrete logs. A prime's bit length alone is insufficient: subgroup order, exponent randomness and known attacks matter. Vetted 2,048-bit finite-field groups target roughly 112-bit classical strength, not 2^2048 work.

### What "generator" means

The **element order** of a number is how many steps its powers take to get back to 1:

```formula
g^k ≡ 1 (mod p)
5^22 ≡ 1 (mod 23), 5^11 ≡ 22 (mod 23)
2^11 ≡ 1 (mod 23)
where
g: a base, such as 5 or 2
k: the order of g: the smallest positive exponent for which the first line holds
p: the prime modulus, 23
mod: "modulo": arithmetic on remainders after dividing by p
≡: "is congruent to": both sides leave the same remainder after dividing by p
In words: 5 needs all 22 steps to return to 1, but 2 is back at 1 after only 11, so its powers can only ever reach half the values.
```

Powers of 5 mod 23 visit every number from 1 to 22 before repeating, so 5 has order 22: it generates the whole group. Not every base does. Powers of 2 mod 23 cycle through only 11 values, so a secret derived from base 2 has half as many possible values. Real parameters are chosen so the generator's order is a large prime.

## Key takeaways
- Exponent multiplication explains agreement; computational DH is the direct shared-secret hardness assumption.
- Generator order and subgroup size matter alongside modulus size.

## Further reading
- [Diffie and Hellman: New Directions in Cryptography](https://ee.stanford.edu/~hellman/publications/24.pdf)
- [RFC 7919: vetted finite-field groups](https://www.rfc-editor.org/rfc/rfc7919)
