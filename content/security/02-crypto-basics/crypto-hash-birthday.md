---
id: crypto-hash-birthday
sourceLesson: crypto-hashes
title: Counting collision risk with the birthday bound
level: basic
minutes: 5
summary: Collision search compares pairs, giving square-root generic work in the output space.
---

## The birthday bound

Why does generic collision search need only about the square root of the digest space? This is the **birthday paradox**. Under a simplified model of independent, uniformly distributed birthdays over 365 days, 23 people give a 50.7% chance of a shared birthday, even though there are 365 possible days. You are not looking for a match with one particular day; you are comparing every pair, and the number of pairs grows with the square of the number of people.

The same thing happens with digests. Every new hash you compute can clash with *any* of the ones you already have, so the number of chances grows with the square of how many you have computed. Collisions therefore become likely once you have computed roughly the square root of the number of possible digests:

```formula essential
q ≈ √(N) = 2^(n/2)
where
q: the number of random hashes after which a collision becomes likely
N: the number of possible digests, 2^n
n: the digest length in bits
√: square root: √(N) is the number that multiplied by itself gives N
≈: approximately equal to; the 50 percent point is about 1.18 times this value
In words: collisions among random n-bit digests become likely after about 2^(n/2) hashes, so halving the digest length in bits gives its generic collision strength.
```

That is the practical rule: halve the digest width for its generic classical collision-strength estimate. SHA-256 gives about 128-bit collision resistance, the standard modern target. A 128-bit hash such as MD5 offered only 64 bits even before it was broken, which is within reach of a determined attacker. The same reasoning sizes random identifiers, nonces and truncated digests: in a 64-bit random ID space a clash becomes likely after a few billion items, not after 2^64.

If you need a probability rather than a rule of thumb, the standard approximation is below.

```formula reference
p ≈ 1 − e^(−q(q − 1) / (2N))
where
p: the probability that at least two of q items share a value, from 0 to 1
q: the number of items: people, or hashed messages
N: the number of equally likely values: 365 birthdays, or 2^n digests
e: Euler's number, about 2.71828, the base of natural exponentials
≈: approximately equal to
In words: the chance of a clash depends on the number of pairs, which grows with the square of q; for 23 people and 365 days it gives about 0.50, close to the exact 0.507.
```

You can watch this happen by keeping only 24 bits of SHA-256 (16,777,216 possible values) and hashing the counters 0, 1, 2, … until two collide:

```python
import hashlib, itertools

# Remember the first input for each digest.
seen = {}
for i in itertools.count():
    m = str(i).encode()
    # Only 24 bits: collisions are visible.
    h = hashlib.sha256(m).digest()[:3]
    # Equal digests from different counters.
    if h in seen:
        print(seen[h], i)
        break
    # Keep the first witness for this ID.
    seen[h] = i
```

It prints `4163 8864`: a collision after 8,865 inputs (the loop starts at zero), not after millions. Under the uniform-output model, a 24-bit collision is expected after roughly five thousand hashes, so this run is a little unlucky but unremarkable. The input sequence is fixed, so it always prints the same pair; a different sequence would collide at a different point.

## Key takeaways
- Collision search compares pairs, giving square-root generic work in the output space.
- Halve the digest length in bits for its generic collision strength; the same rule sizes random IDs and nonces.

## Further reading
- [NIST FIPS 180-4: secure hashes](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
- [Python hashlib API](https://docs.python.org/3/library/hashlib.html)
