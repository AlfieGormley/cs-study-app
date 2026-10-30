---
id: crypto-gcm-nonce-limits
sourceLesson: crypto-symmetric
title: Nonce discipline and GCM usage limits
level: basic
minutes: 3
summary: A GCM nonce repeat can leak plaintext relations and enable authentication forgeries.
---

## GCM's sharp edge: nonce reuse

GCM inherits CTR's nonce rule, and the consequences are worse. Reusing a nonce under the same key:

1. Leaks `P1 XOR P2`, exactly as in CTR.
2. Can expose equations for GCM's authentication key and enable **forgeries**. Distinct messages, tag length and available observations affect whether the key is uniquely recovered.

Random nonces can collide by chance, and the chance grows with the *square* of the number of messages, because every pair of messages is a chance for a match (the birthday effect, covered properly in the hashing units later in this module). For 96-bit random nonces the risk is negligible for a few billion messages under one key, but it would approach a coin flip around 2^48 messages, which busy services can reach.

```formula reference
p_coll ≈ q^2 / 2^(b+1)
where
p_coll: the probability that at least two of the q messages got the same nonce, from 0 (never) to 1 (certain)
q: the number of messages encrypted under one key
b: the nonce length in bits, 96 for standard GCM
2^(b+1): twice the number of possible nonces, 2^b; the factor 2 comes from counting each pair of messages once
≈: approximately equal to; the approximation is good while p_coll is small
In words: the chance of a random-nonce repeat grows with the square of the message count, so at 2^32 messages it is about 2^−33 (roughly 1 in 8.6 billion) for 96-bit nonces.
```

NIST SP 800-38D requires the chance that one key is ever used with a repeated IV on different data to be at most 2^−32, and for random 96-bit nonces it caps each key at 2^32 (about 4.3 billion) encryptions. At that cap the collision chance is about 1 in 8.6 billion, inside the requirement. Apply the limit across all devices using that key, plus message-length and tag-dependent limits. These figures come from the 2007 standard; NIST is revising it, but as of October 2026 it had published only calls for comments (proposing, among other things, to drop tags shorter than 96 bits), not a revised draft. A counter requires coordinated uniqueness across restarts and workers. **AES-GCM-SIV** tolerates accidental nonce repetition better, though repetition can still leak equality and usage limits remain. **XChaCha20-Poly1305** has a 192-bit nonce that makes random collisions negligible at practical volumes; it is **not** nonce-misuse resistant and must not repeat a nonce under a key.

## Common mistakes

- **ECB for application data.** Select the intended authenticated scheme explicitly.
- **Hard-coded or reused IVs and nonces**, such as a zero IV "for simplicity".
- **Encryption without authentication**, such as AES-CBC with no MAC, which invites padding oracles and tampering.
- **Using a password as the key.** Keys must be random bytes; derive a key from a password with a password KDF (covered later in password hashing).
- **Ignoring decryption failures** or showing different errors for "bad padding" and "bad MAC", which builds an oracle.
- **Keys in source code.** Use a key management service or secrets manager.

## Key takeaways
- A GCM nonce repeat can leak plaintext relations and enable authentication forgeries.
- Coordinate nonce uniqueness, key rotation and usage limits across all workers and restarts.

## Further reading
- [NIST SP 800-38D: GCM](https://csrc.nist.gov/pubs/sp/800/38/d/final)
- [Python cryptography: AEAD APIs](https://cryptography.io/en/latest/hazmat/primitives/aead/)
