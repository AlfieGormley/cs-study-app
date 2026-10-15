---
id: crypto-dh-parameter-validation
sourceLesson: crypto-key-exchange
title: Reject weak groups and malicious public values
level: advanced
minutes: 3
summary: Small-order public values can collapse a DH shared secret or leak information about reused exponents.
---

## Pitfalls in the parameters

### Small-subgroup and invalid values

What if Mallory replaces Bob's value with 22, one less than the prime, which behaves like −1? Then:

```formula
B′ = p − 1 = 22 ≡ −1 (mod 23)
s = B′^a mod p
s = 1 if a mod 2 = 0
s = 22 if a mod 2 = 1
where
p: the public prime, 23
B′: the value Mallory substitutes for Bob's
a: Alice's secret exponent
s: the "DH shared secret" Alice computes
mod: "modulo": x mod n is the remainder after dividing x by n (n is 23 or 2 here)
≡: "is congruent to": both sides leave the same remainder after dividing by 23
In words: −1 raised to any power is 1 or −1, depending only on whether the exponent is even or odd, so Alice's secret collapses to one of two values.
```

Alice's "secret" is now one of only two values, both known to Mallory. Similar tricks with values of small order can leak bits of a long-term private key.

Defences: use a **safe prime**, use a generator of the large prime-order subgroup, and **validate** received values:

```formula
p = 2 × q + 1
23 = 2 × 11 + 1
2 ≤ B ≤ p − 2
B^q ≡ 1 (mod p)
where
p: the public prime modulus
q: a second prime; p is a safe prime when q is also prime, which leaves a large subgroup of prime order q
B: a public value received from the other side
≤: is less than or equal to
mod: "modulo": arithmetic on remainders after dividing by p
≡: "is congruent to": both sides leave the same remainder after dividing by p
In words: choose p so that p − 1 is twice a prime, reject the trivial values 0, 1 and p − 1, and check that the received value lies in the order-q subgroup.
```

For modulus 23, received value 22 fails the range check. Base 5 fails the order-11 subgroup check because its eleventh power leaves remainder 22 instead of 1. This toy full-group generator therefore does not meet the prime-order-subgroup profile shown in this card. Use the checks required by the protocol and library; not every low-level API enforces all of them.

### Weak or shared groups: Logjam

In 2015 the **Logjam** researchers showed two problems:

1. Many TLS servers still accepted 512-bit "export-grade" DH, a 1990s US export restriction. An active attacker could downgrade connections to it and break them in minutes.
2. Most servers shared a handful of standard 1,024-bit primes. Because most of the work in breaking discrete logs depends only on the prime, a nation-state could plausibly precompute once and then break huge numbers of connections.

The response: at least 2,048-bit groups from vetted lists such as RFC 7919's `ffdhe2048` and up, or, far more commonly now, elliptic curves.

## Key takeaways
- Small-order public values can collapse a DH shared secret or leak information about reused exponents.
- Use vetted groups and the exact validation rules required by the chosen protocol.

## Further reading
- [RFC 7919: vetted finite-field groups](https://www.rfc-editor.org/rfc/rfc7919)
- [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
