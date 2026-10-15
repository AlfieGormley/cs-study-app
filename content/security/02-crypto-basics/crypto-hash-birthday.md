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

With independently uniform items, count every distinct pair, then use the number of possible outputs to estimate the chance of at least one match:

```formula
pairs = q(q − 1) / 2
p ≈ 1 − e^(−q(q − 1) / (2N))
p ≈ 1 − e^(−23 × 22 / 730) ≈ 0.50
where
pairs: the number of distinct unordered item pairs, with no units
p: the probability that at least two of the q items share a value, from 0 to 1
q: the number of items: people, or hashed messages
N: the number of equally likely values: 365 birthdays, or 2^n digests
e: Euler's number, about 2.71828, the base of natural exponentials
≈: approximately equal to
In words: the chance of a clash depends on the number of pairs, which grows with the square of q, so it reaches a coin-flip once q is around the square root of N.
```

With 23 people and 365 days the approximation gives 0.500 (the exact figure is 0.507). Solving for a collision probability of one half gives the collision points for an ideal hash:

```formula
q_50 ≈ √(2 ln(2)) × 2^(n/2)
q_50 ≈ 1.1774 × 2^(n/2)
q_mean ≈ √(π / 2) × 2^(n/2)
q_mean ≈ 1.2533 × 2^(n/2)
where
q_50: the number of random hashes at which the chance of a collision reaches 50%
q_mean: the average number of hashes computed until the first collision
n: the digest length in bits
2^(n/2): the square root of the number of possible digests, 2^n
ln: the natural logarithm (logarithm to base e ≈ 2.71828); ln(2) ≈ 0.693
π: pi, about 3.14159
√: square root
≈: approximately equal to
In words: a collision among random n-bit digests is a coin-flip after about 1.18 × 2^(n/2) hashes and arrives on average after about 1.25 × 2^(n/2).
```

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

Truncating SHA-256 to 24 bits gives 16,777,216 possible outputs, yet this finds a collision after 8,865 inputs, because the loop starts at zero (printing `4163 8864`). The uniform-output model predicts:

```formula
q_50 ≈ 1.1774 × 2^12 ≈ 4823
q_mean ≈ 1.2533 × 2^12 ≈ 5134
where
q_50: the number of hashes at which a collision becomes a 50% chance
q_mean: the average number of hashes until the first collision
2^12: 4096, which is 2^(n/2) for an n = 24-bit digest
≈: approximately equal to
In words: for a 24-bit digest, a collision is expected after roughly five thousand hashes, not sixteen million.
```

So 8,865 is a somewhat unlucky but unremarkable run. This particular deterministic input sequence always prints the same pair; changing the sequence can change the first collision.

The practical rule is to halve the digest width for its generic classical collision-strength estimate:

```formula
s_coll = n / 2
s_coll = 256 / 2 = 128 bits
s_coll = 128 / 2 = 64 bits
where
s_coll: the collision security level in bits: a collision costs about 2^s_coll hash computations
n: the digest length in bits: 256 for SHA-256, 128 for MD5
bits: the unit; each extra bit of security doubles the attacker's work
In words: halve the digest length to get the collision security, so SHA-256 gives 128 bits and MD5 never gave more than 64.
```

SHA-256 gives 128-bit collision resistance, which is the standard modern target. A 128-bit hash such as MD5 offered only 64 bits even before it was broken, which is within reach of a determined attacker.

## Key takeaways
- Collision search compares pairs, giving square-root generic work in the output space.
- The 50-percent collision point and the expected first collision have different constants.

## Further reading
- [NIST FIPS 180-4: secure hashes](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
- [Python hashlib API](https://docs.python.org/3/library/hashlib.html)
