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

Both sides end up with the generator raised to the product of the two secret exponents, just computed in a different order. Raising a power to a power multiplies the exponents, and multiplication doesn't care about order. With the toy numbers that is 5 raised to 6 × 15 = 90, which leaves remainder 2 after dividing by 23.

### Why Eve can't

Eve sees everything public: 23, 5, 8 and 19. One way to get the shared value is to recover a secret exponent from its public value: given the generator, the prime and Alice's public value 8, find the exponent that produced it. That is the **discrete logarithm problem**. Going forwards (raising the generator to a known exponent) is fast; going backwards has no known efficient classical method in a well-chosen large group.

In the toy group Eve simply tries all 22 possible exponents and finds that 5 to the power 6 leaves remainder 8. For a well-chosen 2,048-bit group no known classical method is practical.

The **computational Diffie–Hellman assumption** directly assumes that obtaining the DH shared secret from the public values is infeasible in the chosen group; it does not assert a general equivalence to solving discrete logs. A prime's bit length alone is insufficient: subgroup order, exponent randomness and known attacks matter. Vetted 2,048-bit finite-field groups target roughly 112-bit classical strength, not 2^2048 work.

### What "generator" means

The **element order** of a number is how many steps its powers take to get back to 1. Powers of 5 modulo 23 visit every number from 1 to 22 before returning to 1, so 5 has order 22: it generates the whole group. Not every base does. Powers of 2 modulo 23 run 2, 4, 8, 16, 9, 18, 13, 3, 6, 12 and then 1, cycling through only 11 values. A shared secret built from base 2 can only ever be one of those 11 values, half as many.

At real sizes the same principle decides security: what matters is the size of the subgroup the generator produces, not just the size of the prime. Real parameters, such as the RFC 7919 groups, are chosen so the generator's order is a large prime.

## Key takeaways
- Exponent multiplication explains agreement; computational DH is the direct shared-secret hardness assumption.
- Generator order and subgroup size matter alongside modulus size.

## Further reading
- [Diffie and Hellman: New Directions in Cryptography](https://ee.stanford.edu/~hellman/publications/24.pdf)
- [RFC 7919: vetted finite-field groups](https://www.rfc-editor.org/rfc/rfc7919)
