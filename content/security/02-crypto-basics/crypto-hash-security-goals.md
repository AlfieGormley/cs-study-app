---
id: crypto-hash-security-goals
sourceLesson: crypto-hashes
title: Digests and three different security goals
level: basic
minutes: 4
summary: A hash is deterministic and keyless; it does not encrypt its input.
---

A **cryptographic hash function** takes a message within its defined length limits and produces a short, fixed-size **digest** (also called a hash or fingerprint). SHA-256 always outputs 256 bits, whether you feed it one byte or a 4 GB disk image.

```
"abc"      --SHA-256--> ba7816bf...f20015ad
"abd"      --SHA-256--> a52d159f...298449c9
4 GB file  --SHA-256--> (another 32 bytes)
```

There is no key. Anyone can compute the hash of anything, and the same input always gives the same output. That makes a hash a public, deterministic fingerprint: a matching digest is useful evidence under the hash's security assumptions, not proof that two inputs must be identical.

Notice that changing one letter (`c` to `d`) changed the whole digest. This is the **avalanche effect**: flipping any input bit should flip about half the output bits, unpredictably.

> [!warning] A hash is not encryption
> There is no key and no way back. You cannot "decrypt" a hash. People who say "we hash the data so it's encrypted" are usually confused, and if the input has low entropy (a phone number, a password) an attacker can simply hash every candidate and compare.

## The three security properties

A function that just compresses data (like CRC32) is not enough. A cryptographic hash must resist three kinds of attack. To compare them, count an attacker's work as the number of hash computations a generic attack needs against an ideal hash with an n-bit digest. The key relationship is that finding *any* clash is far cheaper than hitting a *particular* digest:

```formula essential
W_pre ≈ 2^n
W_coll ≈ 2^(n/2)
where
W_pre: the work to find a preimage (or a second preimage): an input that matches one particular digest, counted in hash computations
W_coll: the work to find a collision: any two different inputs with equal digests
n: the digest length in bits: 256 for SHA-256, 160 for SHA-1, 128 for MD5
≈: approximately equal to
In words: hitting one particular digest takes about 2^n tries, but finding any two inputs that clash takes only about 2^(n/2), its square root. For SHA-256 that is about 2^256 versus 2^128.
```

These are generic classical work estimates for an ideal hash and suitably unconstrained inputs, not guarantees for weak input dictionaries or every long-message construction. The square root comes from the birthday effect, explained in the next unit.

| Property | Attacker's task | Ideal cost |
|---|---|---|
| Preimage | Given a digest, find any input that hashes to it | Full digest-space scale |
| Second preimage | Given one input, find a different input with the same hash | Full digest-space scale |
| Collision | Find any two different inputs with equal hashes | Square-root digest-space scale |

**Preimage resistance** (one-wayness) means you can't run the hash backwards. **Second-preimage resistance** means that, given a specific document, you can't craft a different one with the same fingerprint. **Collision resistance** means you can't find *any* two inputs that clash, even ones you choose freely.

> [!analogy] Real-world analogy: Fingerprints
> Police can match a fingerprint to a suspect on file, but a fingerprint alone does not let them reconstruct the person. Fingerprints are meant to be practically unique, even though nothing in principle stops two people sharing one.
>
> **How it maps:** The person is the input and the fingerprint is the digest. A preimage attack is building a person to fit a given print; a second-preimage attack is finding someone whose print matches a particular suspect's; a collision attack is finding *any* two people in the world with matching prints, which is far easier to stumble on.
>
> **Where it stops:** Real fingerprints were never designed against an adversary, and only the owner can produce theirs. Anyone can compute a digest of any input, there is no key, and the hash's resistance is a calculated work estimate rather than a biological accident.

Collisions must exist: there are more permitted messages than the 2^256 possible SHA-256 outputs. The point is that nobody should be able to *find* one.

Collision search has the lower generic work bound for a fixed digest size. These are distinct security notions with precise assumptions; finding some colliding pair does not let an attacker replace any chosen existing document.

## Key takeaways
- A hash is deterministic and keyless; it does not encrypt its input.
- Preimage, second-preimage and collision resistance describe distinct attacker tasks.

## Further reading
- [NIST FIPS 180-4: secure hashes](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
- [NIST FIPS 202: SHA-3](https://csrc.nist.gov/pubs/fips/202/final)
- [Python hashlib API](https://docs.python.org/3/library/hashlib.html)
