---
id: secf-password-storage
title: Salted, costly password verification
level: intermediate
minutes: 4
sourceLesson: secf-authentication
summary: Use a unique salt and a password-specific function.
---

## Storing passwords

The server must be able to *verify* a password without being able to *recover* it. Never store plaintext, and never use reversible encryption.

1. **Hash** the password with a suitable password function; attackers can still test guesses against a stolen verifier.
2. **Salt** it: add a unique random value per user before hashing. Identical passwords then produce different hashes, and precomputed tables (rainbow tables) become useless.
3. Use a **slow, memory-hard** password hashing function, so each guess has a substantial resource cost tuned to the deployment.

Fast hashes like SHA-256 are designed to be quick; actual cracking rates depend on hardware, implementation and candidate generation. That's great for file integrity and terrible for passwords.

| Algorithm | OWASP minimum (checked October 2026) |
|---|---|
| Argon2id | 19 MiB memory, 2 iterations, parallelism 1 |
| scrypt | Cost 131,072; block-size parameter 8; parallelism 1 |
| bcrypt | cost 10+, 72-byte input limit |
| PBKDF2-HMAC-SHA256 | 600,000 iterations |

The scrypt settings are a CPU/memory cost, a block-size parameter and a parallelism value. Together the first two set how much memory each password guess needs, which is what makes scrypt expensive to attack with many cheap parallel chips:

```formula reference
M ≈ 128Nr
where
M: the memory one scrypt hash computation needs, in bytes
N: the CPU/memory cost parameter: how many blocks scrypt fills and then reads back in a data-dependent order; it must be a power of 2, such as 2^17 = 131,072
r: the block-size parameter, such as 8; each block is 128r bytes
128: bytes per unit of r: scrypt's basic block is two 64-byte chunks
≈: approximately equal to (scrypt also needs a little extra working memory)
In words: memory per guess grows in proportion to both the cost setting and the block-size parameter; OWASP's scrypt minimum (cost 131,072, block-size parameter 8) makes every guess fill about 128 MiB.
```

The parallelism parameter is 1 here. More independent lanes add work. Executing those lanes simultaneously can multiply their working storage; sequential execution can reuse the large workspace. The Python example below sets `maxmem=2**28` (256 MiB) because `hashlib.scrypt` raises an error when the memory needed exceeds its limit, and an implementation's default may be insufficient. Python's documentation specifically notes a 32 MiB default for OpenSSL 1.1.0; defaults and build support need checking on the target system.

Prefer Argon2id; OWASP lists scrypt when Argon2id is unavailable, bcrypt only for legacy systems where neither is available, and PBKDF2 when FIPS-140 compliance is required. Tune and periodically revisit costs; the table is not a universal deployment prescription.

Python provides scrypt when the build has the required OpenSSL support:

```python
import hashlib, hmac, os

N, R, P = 2**17, 8, 1  # ~128 MiB

def hash_pw(pw: str):
    # Save a fresh salt with this verifier.
    salt = os.urandom(16)
    h = hashlib.scrypt(
        pw.encode(), salt=salt,
        n=N, r=R, p=P,
        maxmem=2**28)
    # Store both values, never the password.
    return salt, h

def verify(pw, salt, stored):
    # Recompute using the saved
    # salt/settings.
    h = hashlib.scrypt(
        pw.encode(), salt=salt,
        n=N, r=R, p=P,
        maxmem=2**28)
    # True means these same-length tags
    # match.
    return hmac.compare_digest(h, stored)
```

`hmac.compare_digest` avoids content-dependent early exit for same-type, same-length inputs. It does not make the whole login constant-time; type or length differences and other code can still affect timing. In production you'd normally use a maintained library (such as `argon2-cffi`) that stores the parameters with the hash, so you can raise them later and rehash on next login.

## Key takeaways
- Use a unique salt and a password-specific function.
- Scrypt memory settings need an explicit implementation limit.
- Constant-time comparison does not make the whole login constant-time.

## Further reading
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [RFC 7914: scrypt](https://www.rfc-editor.org/rfc/rfc7914)
- [Python hashlib documentation](https://docs.python.org/3/library/hashlib.html)
