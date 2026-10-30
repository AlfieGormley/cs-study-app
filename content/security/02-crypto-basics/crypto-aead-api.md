---
id: crypto-aead-api
sourceLesson: crypto-symmetric
title: Authenticated encryption through a library
level: basic
minutes: 3
summary: AEAD encrypts data and authenticates it together with optional public associated data.
---

## AEAD: what you should actually use

**Authenticated Encryption with Associated Data (AEAD)** does both jobs in one primitive. It encrypts the plaintext and computes an authentication **tag** over the ciphertext plus optional **associated data** (headers that must not be changed but needn't be secret, such as a record ID or protocol version). A safe API returns plaintext only after successful authentication. Internal decryption may happen before verification; callers must not use unauthenticated output.

Two common AEAD configurations (GCM also defines other permitted tag lengths):

| AEAD | Nonce | Tag | Notes |
|---|---|---|---|
| AES-256-GCM | 96 bits | 128 bits | Fast with AES-NI |
| ChaCha20-Poly1305 | 96 bits | 128 bits | Fast in software |

**AES-GCM** combines CTR encryption with a tag formed from the GHASH polynomial authentication function and a nonce-dependent AES mask. GHASH alone is not a secure standalone MAC. **ChaCha20-Poly1305** (RFC 8439) pairs a stream cipher with the Poly1305 MAC; it is quick on phones and devices without AES instructions. TLS 1.3 only allows AEAD cipher suites, and these two are the common choices.

Here is what it looks like with Python's `cryptography` library:

```python
import os
from cryptography.hazmat.primitives \
    .ciphers.aead import AESGCM

# Generate a fresh random AES key.
key = AESGCM.generate_key(bit_length=256)
aead = AESGCM(key)

# A random demo nonce; never reuse per key.
nonce = os.urandom(12)  # random
aad = b"order-id:4711"  # authed, not secret
# AAD is authenticated without encryption.
ct = aead.encrypt(nonce, b"pay Bob 10", aad)

print(len(ct))           # 10 + 16-byte tag
# Release plaintext only after a valid tag.
print(aead.decrypt(nonce, ct, aad))
```

This prints `26` and then `b'pay Bob 10'`. GCM adds no padding: the output is the 10-byte ciphertext with a 16-byte (128-bit) tag appended. The 12-byte nonce is not part of that output.

An invalid tag makes `decrypt` raise `InvalidTag` instead of returning plaintext. Altering `ct`, the nonce or `aad` is intended to fail authentication under the scheme’s forgery bounds; the probability of an accepted forgery is small, not mathematically zero. You store or send the nonce alongside the ciphertext; it doesn't need to be secret, only unique.

> [!analogy] Real-world analogy: A parcel with tamper-evident tape over the label
> A courier parcel is sealed with tamper-evident tape that also runs over the address label. Anyone can read the label, but if the contents or the label are disturbed the tape shows it, and the recipient refuses the parcel unopened.
>
> **How it maps:** The sealed contents are the ciphertext; the readable label under the tape is the associated data, authenticated but not secret; the tape is the authentication tag. A safe AEAD API is the recipient who refuses the parcel: `decrypt` raises `InvalidTag` and hands back nothing.
>
> **Where it stops:** A skilled forger can sometimes reseal a parcel; an AEAD forgery has a tiny, bounded probability instead. And there is no parcel equivalent of the nonce rule: reusing a nonce under one key can quietly destroy both secrecy and the tag's protection.

Python `cryptography`'s **Fernet** manages a random IV and token format for authenticated encryption, but has no associated-data interface. Libsodium's low-level `secretbox` requires the caller to supply a nonce; some wrappers manage it. Check the specific API rather than assuming automatic nonce generation.

## Key takeaways
- AEAD encrypts data and authenticates it together with optional public associated data.
- The demonstrated AESGCM API appends a 16-byte tag and rejects failed authentication.

## Further reading
- [Python cryptography: AEAD APIs](https://cryptography.io/en/latest/hazmat/primitives/aead/)
- [NIST SP 800-38D: GCM](https://csrc.nist.gov/pubs/sp/800/38/d/final)
