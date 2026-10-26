---
id: prob-id-hash-lengths
title: Choose ID and hash lengths using birthday risk
level: advanced
minutes: 3
sourceLesson: prob-algorithms
summary: Independent random IDs need enough space for pairwise collision risk.
---

Choose a random identifier space from the expected population and acceptable collision risk. A large-looking range is not enough: every new ID can collide with every earlier ID.

## Population and space size both matter

Under independent uniform generation and small collision risk, doubling the issued population roughly quadruples the risk. Adding one random bit doubles the space and roughly halves that risk. These are planning approximations, not guarantees of uniqueness.

```formula reference
P(C) ≈ n^2 / (2 × m)
where
C: the event "at least one collision"
n: the integer number of independent uniform items (IDs), large enough to approximate the pair count using its squared leading term
m: the positive integer number of possible values; 2^32 ≈ 4.29 billion for a 32-bit ID
n^2: n multiplied by itself
P: probability; probabilities are dimensionless and apply to measurable events
≈: approximately equal to (good while the result is well below 1)
In words: For many independent uniform IDs while collision risk is small, risk is approximately proportional to the square of the population and inversely proportional to the space size.
```

A 32-bit random ID has billions of possible values, yet issuing 10,000 carries roughly a 1.2% chance of some collision under this model. If collisions are unacceptable, detect duplicates and retry or use a coordinated allocation scheme as appropriate.

A version 4 UUID is 128 bits overall, including 122 random bits and fixed version and variant fields. The random space is enormous, but generation quality and the number issued still matter. Fixed formatting bits add no randomness.

## Accidental uniqueness and attack resistance differ

A classical generic **birthday attack** searches for any two inputs with the same ideal hash. It needs work on the order of the square root of the output-space size. Thus an ideal 128-bit hash has about 64-bit generic collision resistance.

A **preimage attack** instead targets one already specified output, a different and generically harder task. Cryptanalytic weaknesses can also beat generic bounds; output length alone does not make a hash secure. MD5 and SHA-1 have demonstrated collision weaknesses beyond the birthday bound.

## Key takeaways
- Size IDs for all-pairs risk and the expected population.
- Random formatting does not guarantee uniqueness.
- Distinguish generic collision search, preimage search and algorithm-specific weaknesses.

## Further reading
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
- [UUID specification — RFC 9562](https://www.rfc-editor.org/rfc/rfc9562.html)
