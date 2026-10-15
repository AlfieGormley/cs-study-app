---
id: prob-id-hash-lengths
title: Choose ID and hash lengths using birthday risk
level: advanced
minutes: 3
sourceLesson: prob-algorithms
summary: Independent random IDs need enough space for pairwise collision risk.
---

## Why engineers care

| Space | Size | 50% collision at |
|---|---|---|
| Birthdays | 365 | ~23 |
| 7 hex chars (28 bits) | 2²⁸ | ~19,000 |
| 32-bit hash | 2³² | ~77,000 |
| 64-bit hash | 2⁶⁴ | ~5.1 billion |
| UUIDv4 (122 random bits) | 2¹²² | ~2.7 × 10¹⁸ |

- **Short IDs.** A 32-bit random ID looks huge (4 billion values), but collisions are a coin flip after about 77,000 IDs. Even at 10,000 IDs the chance is about 1.2%.
- **Git abbreviations.** Seven hex characters give 28 bits, so a repository with tens of thousands of objects has a material probability of ambiguous abbreviations of one set length under an ideal uniform-hash model. That is why Git automatically lengthens abbreviations as a repository grows.
- **UUIDs.** Version 4 UUIDs have 122 random bits. You would need about 2.7 quintillion of them for an even chance of a single collision, which is why systems generate them without coordination.
- **Cryptographic hashes.** For an ideal b-bit hash under a classical generic attack, finding *some* collision takes on the order of 2 to the power b/2 evaluations (the square root of the 2 to the power b possible outputs), a **birthday attack**. A 128-bit hash gives only 64-bit collision resistance. MD5 and SHA-1 also have cryptanalytic collision weaknesses beyond this generic bound; their history cannot be explained by output length alone. SHA-256 offers a generic 128-bit classical collision bound, assuming no better attack.

> [!tip] Quick estimate
> For small probabilities, the collision chance is about the expected number of colliding pairs. Doubling the number of items quadruples the risk; adding 1 bit to the ID halves it.

```formula
P(C) ≈ n^2 / (2 × m)
P(C) ≈ 10,000^2 / (2 × 2^32) ≈ 0.012
where
C: the event "at least one collision"
n: the nonnegative integer number of independent uniform items (IDs); 10,000 in the second line
m: the positive integer number of possible values; 2^32 ≈ 4.29 billion for a 32-bit ID
n^2: n multiplied by itself
P: probability; probabilities are dimensionless and apply to measurable events
≈: approximately equal to (good while the result is well below 1)
In words: 10,000 random 32-bit IDs collide with about a 1.2% chance.
```

## Key takeaways
- Independent random IDs need enough space for pairwise collision risk.
- Generic classical collision resistance is roughly half the bit length.

## Further reading
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
- [UUID specification — RFC 9562](https://www.rfc-editor.org/rfc/rfc9562.html)
