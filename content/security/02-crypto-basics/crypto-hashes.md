---
id: crypto-hashes
title: Hash functions and their properties
level: basic
minutes: 11
summary: What a cryptographic hash guarantees (preimage, second-preimage and collision resistance), the birthday bound, why MD5 and SHA-1 are broken, length extension, and which hash to pick today.
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

A function that just compresses data (like CRC32) is not enough. A cryptographic hash must resist three kinds of attack. Let `H` be the hash and `n` the digest length in bits. The table gives generic classical work estimates for an ideal hash and suitably unconstrained inputs, not guarantees for weak input dictionaries or every long-message construction.

| Property | Attacker's task | Ideal cost |
|---|---|---|
| Preimage | Given `h`, find any `m` with `H(m) = h` | 2^n |
| Second preimage | Given `m1`, find `m2 ≠ m1` with the same hash | 2^n |
| Collision | Find any pair `m1 ≠ m2` with equal hashes | 2^(n/2) |

**Preimage resistance** (one-wayness) means you can't run the hash backwards. **Second-preimage resistance** means that, given a specific document, you can't craft a different one with the same fingerprint. **Collision resistance** means you can't find *any* two inputs that clash, even ones you choose freely.

Collisions must exist: there are more permitted messages than the 2^256 possible SHA-256 outputs. The point is that nobody should be able to *find* one.

Collision search has the lower generic work bound for a fixed digest size. These are distinct security notions with precise assumptions; finding some colliding pair does not let an attacker replace any chosen existing document.

## The birthday bound

Why is the collision cost only 2^(n/2)? This is the **birthday paradox**. Under a simplified model of independent, uniformly distributed birthdays over 365 days, 23 people give a 50.7% chance of a shared birthday, even though there are 365 possible days. You are not looking for a match with one particular day; you are comparing every pair, and the number of pairs grows with the square of the number of people.

For independent uniform `n`-bit outputs, the approximately 50% collision point is `sqrt(2 ln 2) × 2^(n/2) ≈ 1.1774 × 2^(n/2)`. The expected first-collision count instead approaches `sqrt(pi/2) × 2^(n/2) ≈ 1.2533 × 2^(n/2)`.

```python
import hashlib, itertools

seen = {}
for i in itertools.count():
    m = str(i).encode()
    h = hashlib.sha256(m).digest()[:3]
    if h in seen:
        print(seen[h], i)
        break
    seen[h] = i
```

Truncating SHA-256 to 24 bits gives 2^24 ≈ 16.8 million possible outputs, yet this finds a collision after 8,865 inputs, because the loop starts at zero (printing `4163 8864`). The uniform-output model predicts a 50% point near 4,823 and a mean near 5,134. This particular deterministic input sequence always prints the same pair; changing the sequence can change the first collision.

The practical rule: **an n-bit hash gives at most n/2 bits of collision security**. SHA-256 gives 128-bit collision resistance, which is the standard modern target. A 128-bit hash such as MD5 offered only 64 bits even before it was broken, which is within reach of a determined attacker.

## How the common hashes are built

### Merkle–Damgård (MD5, SHA-1, SHA-2)

Most older hashes split the padded message into blocks and feed them through a **compression function**, carrying a fixed-size internal state from one block to the next. The final state is the digest.

```
IV -> [f] -> [f] -> [f] -> digest
       ^      ^      ^
       M1     M2     M3 (+ padding)
```

For MD5, SHA-1, SHA-256 and SHA-512, the digest exposes the final chaining state. This does not apply equally to truncated variants such as SHA-384 and SHA-512/256. So given `H(m)` and the length of `m`, anyone can carry on hashing and compute `H(m || padding || extra)` without knowing `m`. This is a **length-extension attack**. It doesn't break the hash's three properties, but it breaks naive constructions such as `SHA256(secret || message)` used as an authentication code. The next lesson shows how HMAC avoids it.

### Sponge (SHA-3)

**SHA-3** (Keccak, standardised in FIPS 202 in 2015) uses a different design called a **sponge**. It absorbs input into a large state and squeezes output from only part of it. Because the digest doesn't reveal the whole state, SHA-3 is not vulnerable to length extension. It was chosen as a backup with a different internal structure in case SHA-2 were ever broken; SHA-2 is still fine.

## The hash family tree

| Hash | Output | Status |
|---|---|---|
| MD5 | 128 bits | Broken collision resistance; do not use for new cryptographic designs |
| SHA-1 | 160 bits | Broken (practical collisions) |
| SHA-256 / SHA-512 | 256 / 512 | Secure, the default |
| SHA-3-256 | 256 bits | Secure |
| BLAKE2b / BLAKE2s | up to 512 / 256 bits | Configurable digest length |
| BLAKE3 | 256-bit default; extensible output | Longer output does not imply proportionally greater security |

**MD5** collisions were found in 2004 and became cheap enough to weaponise. In 2012 the Flame malware used an MD5 collision to forge a code-signing certificate that Windows Update trusted.

**SHA-1** fell in 2017, when Google and CWI Amsterdam published **SHAttered**: two different PDF files with the same SHA-1 hash. It took around 2^63 SHA-1 computations, about 6,500 CPU-years plus 110 GPU-years. Later "chosen-prefix" attacks made it cheaper still. Browser vendors phased out SHA-1-signed public TLS certificates; the 2017 collision is a historical result, not a new benchmark.

**SHA-2** (SHA-224, SHA-256, SHA-384, SHA-512 and the truncated variants SHA-512/224 and SHA-512/256) is the workhorse: TLS certificates, code signing, Bitcoin, package managers. **BLAKE2** and **BLAKE3** provide modern alternatives. WireGuard specifies BLAKE2s; do not infer that each named product uses both families.

> [!tip] What to pick
> Use **SHA-256** when you need a general-purpose hash. Use SHA-512/256, SHA-3 or BLAKE2 if you want immunity to length extension. Do not choose MD5 or SHA-1 for new cryptographic designs; collision attacks do not automatically break every legacy HMAC use.

## What hashes are used for

- **Integrity against a trusted digest.** A download page lists the SHA-256 of a file; you hash what you received and compare. This only works if you got the digest through a channel the attacker can't change (an HTTPS page, a signed release file). If the attacker can swap both the file and the hash, a hash proves nothing.
- **Content addressing.** Git names every object by its hash (historically SHA-1, now hardened against SHAttered-style collisions and gradually moving to SHA-256). Docker image digests, IPFS and many build caches work the same way.
- **Merkle trees.** Hash data in pairs up a tree so one 32-byte root commits to millions of items, and you can prove any one item is included with a handful of hashes. Certificate Transparency logs, Bitcoin blocks and Cassandra's anti-entropy repair use them.
- **Digital signatures.** Signature schemes often hash messages internally, but their exact signed encoding and prehash interface vary. Do not replace a scheme's message input with your own digest unless its specification calls for that. If an attacker can find collisions, they can get you to sign one document and reuse the signature on another, which is exactly what happened with MD5 certificates.
- **Building blocks.** Hashes sit inside HMAC, HKDF, password hashing and many protocols.

## Pitfalls

- **Hashing passwords with a fast hash.** SHA-256 is designed to be fast. Attack speed depends on hardware, candidate distribution and implementation; plain SHA-256 provides no tunable password-hardening cost. Use a slow, salted password hash (lesson 6).
- **Using a hash as a MAC.** `H(key || message)` is vulnerable to length extension with SHA-256. Use HMAC.
- **Hashing low-entropy data to "anonymise" it.** Hashing a predictable identifier can permit dictionary recovery or linkage. A bounded phone-number format may be enumerable; all possible email addresses are not necessarily a small enumerable set.
- **Non-cryptographic hashes for security.** CRC32, MurmurHash and xxHash are great for hash tables and checksums against accidental corruption, but they offer no resistance to a deliberate attacker.
- **Ambiguous concatenation.** `H("ab" + "c")` equals `H("a" + "bc")`. When hashing several fields, encode lengths or use a structured format so different inputs can't produce the same byte string.

```python
import hashlib

data = b"abc"
print(hashlib.sha256(data).hexdigest()[:16])
print(hashlib.sha3_256(data).digest_size)
print(hashlib.blake2b(data,
      digest_size=32).digest_size)
```

This prints `ba7816bf8f01cfea`, then `32` and `32`: all three produce 32-byte digests. Python's `hashlib` provides maintained implementations; the backing code depends on the algorithm and Python build. Some constructors use OpenSSL and some have other implementations or fallbacks. Prefer the library over implementing a cryptographic hash yourself.

## Key takeaways
- A cryptographic hash maps any input to a fixed-size digest that is deterministic, keyless and one-way.
- It must resist preimages, second preimages and collisions; collision resistance is limited to n/2 bits by the birthday bound.
- MD5 and SHA-1 are broken for collision resistance. Use SHA-256 (or SHA-3, SHA-512/256, BLAKE2/3).
- Full-state SHA-256 and SHA-512 allow classic length extension. Truncated variants differ; use a specified MAC such as HMAC instead of inventing a prefix-key construction.
- A hash only proves integrity if the expected digest comes from a trusted channel. Never use a fast hash for passwords.

## Further reading
- [Cryptographic hash function — Wikipedia](https://en.wikipedia.org/wiki/Cryptographic_hash_function)
- [Birthday attack — Wikipedia](https://en.wikipedia.org/wiki/Birthday_attack)
- [Google: announcing the first SHA-1 collision](https://security.googleblog.com/2017/02/announcing-first-sha1-collision.html)
- [Length extension attack — Wikipedia](https://en.wikipedia.org/wiki/Length_extension_attack)
- [NIST FIPS 202: SHA-3 Standard](https://csrc.nist.gov/pubs/fips/202/final)
- [hashlib — Python documentation](https://docs.python.org/3/library/hashlib.html)
