---
id: crypto-hash-uses-encoding
sourceLesson: crypto-hashes
title: Trusted digests, Merkle paths and unambiguous inputs
level: basic
minutes: 4
summary: A digest needs a trusted comparison value to support file integrity.
---

## What hashes are used for

- **Integrity against a trusted digest.** A download page lists the SHA-256 of a file; you hash what you received and compare. This only works if you got the digest through a channel the attacker can't change (an HTTPS page, a signed release file). If the attacker can swap both the file and the hash, a hash proves nothing.
- **Content addressing.** Git names every object by its hash (historically SHA-1, now hardened against SHAttered-style collisions and gradually moving to SHA-256). Docker image digests, IPFS and many build caches work the same way.
- **Merkle trees.** Hash data in pairs up a tree so one 32-byte root commits to millions of items, and you can prove any one item is included with a logarithmic number of sibling hashes. Certificate Transparency logs, Bitcoin blocks and Cassandra's anti-entropy repair use them.
- **Digital signatures.** Signature schemes often hash messages internally, but their exact signed encoding and prehash interface vary. Do not replace a scheme's message input with your own digest unless its specification calls for that. If an attacker can find collisions, they can get you to sign one document and reuse the signature on another, which is exactly what happened with MD5 certificates.
- **Building blocks.** Hashes sit inside HMAC, HKDF, password hashing and many protocols.

For a balanced complete binary Merkle tree with 1,048,576 leaves, an inclusion path contains 20 sibling digests: each step halves the remaining leaf range. With 32-byte digests that is 640 bytes of sibling hashes, excluding metadata and the leaf itself.

## Pitfalls

- **Hashing passwords with a fast hash.** SHA-256 is designed to be fast. Attack speed depends on hardware, candidate distribution and implementation; plain SHA-256 provides no tunable password-hardening cost. Use a slow, salted password hash (covered later in password hashing).
- **Using a hash as a MAC.** Hashing a secret key followed by the message is vulnerable to length extension with SHA-256. Use HMAC.
- **Hashing low-entropy data to "anonymise" it.** Hashing a predictable identifier can permit dictionary recovery or linkage. A bounded phone-number format may be enumerable; all possible email addresses are not necessarily a small enumerable set.
- **Non-cryptographic hashes for security.** CRC32, MurmurHash and xxHash are great for hash tables and checksums against accidental corruption, but they offer no resistance to a deliberate attacker.
- **Ambiguous concatenation.** Hashing the fields "ab" and "c" gives the same digest as hashing "a" and "bc". When hashing several fields, encode lengths or use a structured format so different inputs can't produce the same byte string.

Why, and how a length prefix fixes it:

```formula
H("ab" ‖ "c") = H("a" ‖ "bc")
enc("ab", "c") = 0x02 ‖ "ab" ‖ 0x01 ‖ "c"
enc("a", "bc") = 0x01 ‖ "a" ‖ 0x02 ‖ "bc"
where
H: the hash function
enc: encode each of these short ASCII fields by prepending its length as one byte; field lengths here must be below 256 bytes
0x02, 0x01: one-byte lengths 2 and 1, written in hexadecimal
‖: concatenation: joining byte strings end to end, with no separator
In words: plain concatenation turns both field pairs into the same bytes "abc", so they hash identically; writing each field's length before it makes these byte strings distinct. Their SHA-256 digests also differ in this concrete example, but distinct inputs can still collide in principle.
```

```python
import hashlib

data = b"abc"
# Display the first 16 hexadecimal digits.
print(hashlib.sha256(data).hexdigest()[:16])
# These two APIs report a byte count.
print(hashlib.sha3_256(data).digest_size)
print(hashlib.blake2b(data,
      digest_size=32).digest_size)
```

This prints `ba7816bf8f01cfea`, then `32` and `32`: all three produce 32-byte digests. Python's `hashlib` provides maintained implementations; the backing code depends on the algorithm and Python build. Some constructors use OpenSSL and some have other implementations or fallbacks. Prefer the library over implementing a cryptographic hash yourself.

## Key takeaways
- A digest needs a trusted comparison value to support file integrity.
- Encode field boundaries; hashing cannot repair an ambiguous byte representation.

## Further reading
- [Python hashlib API](https://docs.python.org/3/library/hashlib.html)
- [NIST FIPS 180-4: secure hashes](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104)
