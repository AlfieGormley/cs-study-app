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
- **Content addressing.** Git names every object by its hash. According to the Git 2.56 documentation (October 2026), new repositories still default to SHA-1, using a hardened implementation that resists the SHAttered attack; SHA-256 repositories are supported, and Git plans to make SHA-256 the default for new repositories in Git 3.0, which has no release date yet. Docker image digests, IPFS and many build caches work the same way.
- **Merkle trees.** Hash data in pairs up a tree so one 32-byte root hash fixes the contents of millions of items, and you can prove any one item is included with a logarithmic number of sibling hashes. Certificate Transparency logs, Bitcoin blocks and Cassandra's anti-entropy repair use them.
- **Digital signatures.** Signature schemes often hash messages internally, but their exact signed encoding and prehash interface vary. Do not replace a scheme's message input with your own digest unless its specification calls for that. If an attacker can find collisions, they can get you to sign one document and reuse the signature on another, which is exactly what happened with MD5 certificates.
- **Building blocks.** Hashes sit inside HMAC, HKDF, password hashing and many protocols.

For a balanced complete binary Merkle tree with 1,048,576 leaves, an inclusion path contains 20 sibling digests: each step halves the remaining leaf range. With 32-byte digests that is 640 bytes of sibling hashes, excluding metadata and the leaf itself.

> [!analogy] Real-world analogy: A sports tournament bracket
> In a knockout bracket, every match combines two entrants into one winner, round by round, until one champion remains. To trace one entrant's place in the bracket up to the champion, you don't need the whole bracket: just the other side of each match along that path, one per round, which is only a handful even for a huge tournament.
>
> **How it maps:** The entrants are the leaves (hashes of data items), each match is hashing two child hashes together, and the champion is the Merkle root. An inclusion proof is the list of sibling hashes along one path, about 20 of them for a million leaves, because each level halves the field.
>
> **Where it stops:** A bracket result is just a record that someone could edit; a Merkle root depends on every leaf, so changing any item changes the root. The verifier must already trust the root (for example from a signed log head), and secure designs hash leaves and internal nodes differently so one cannot be passed off as the other.

## Pitfalls

- **Hashing passwords with a fast hash.** SHA-256 is designed to be fast. Attack speed depends on hardware, candidate distribution and implementation; plain SHA-256 provides no tunable password-hardening cost. Use a slow, salted password hash (covered later in password hashing).
- **Using a hash as a MAC.** Hashing a secret key followed by the message is vulnerable to length extension with SHA-256. Use HMAC.
- **Hashing low-entropy data to "anonymise" it.** Anyone can hash every candidate for a predictable identifier and match the results, which reveals the original values, and equal digests let records be linked. A bounded phone-number format may be enumerable; all possible email addresses are not necessarily a small enumerable set.
- **Non-cryptographic hashes for security.** CRC32, MurmurHash and xxHash are great for hash tables and checksums against accidental corruption, but they offer no resistance to a deliberate attacker.
- **Ambiguous concatenation.** Hashing the fields "ab" and "c" gives the same digest as hashing "a" and "bc". When hashing several fields, encode lengths or use a structured format so different inputs can't produce the same byte string.

The fix is to make the encoding unambiguous *before* hashing. One simple way is to write each field's length in front of it, so `alice` + `report` and `alicer` + `eport` become different byte strings even though their letters run together the same way:

```python
import hashlib

def naive(*fields):
    # Joins fields with no boundaries.
    return hashlib.sha256(
        b"".join(fields)).hexdigest()

def framed(*fields):
    h = hashlib.sha256()
    for f in fields:
        # 4-byte length prefix, then data.
        h.update(len(f).to_bytes(4, "big"))
        h.update(f)
    return h.hexdigest()

a = (b"alice", b"report")
b = (b"alicer", b"eport")
print(naive(*a) == naive(*b))    # True
print(framed(*a) == framed(*b))  # False
```

The first comparison prints `True`: the naive join turns both pairs into the bytes `alicereport`, so SHA-256 is working correctly when it returns the same digest. The second prints `False`, because the length prefixes make the inputs different. A structured format with a canonical encoding works too. Python's `hashlib` provides maintained implementations of SHA-2, SHA-3 and BLAKE2; prefer it, or your platform's library, over implementing a hash yourself.

## Key takeaways
- A digest needs a trusted comparison value to support file integrity.
- Encode field boundaries; hashing cannot repair an ambiguous byte representation.

## Further reading
- [Python hashlib API](https://docs.python.org/3/library/hashlib.html)
- [NIST FIPS 180-4: secure hashes](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104)
