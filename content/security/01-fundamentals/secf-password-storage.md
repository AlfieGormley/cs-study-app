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

| Algorithm | OWASP baseline consulted for this review |
|---|---|
| Argon2id | 19 MiB memory, 2 iterations, parallelism 1 |
| scrypt | Cost 131,072; block size 8; parallelism 1 |
| bcrypt | cost 10+, 72-byte input limit |
| PBKDF2-HMAC-SHA256 | 600,000 iterations |

The scrypt parameters represent CPU/memory cost, block size and parallelism; the following card names them. Together they set how much memory each password guess needs, which is what makes scrypt expensive to attack with many cheap parallel chips:

```formula
M ≈ 128Nr bytes
M ≈ 128 × 2^17 × 8 bytes
M ≈ 134217728 bytes = 128 MiB
where
M: the memory one scrypt hash computation needs
N: the CPU/memory cost parameter: how many 128 × r-byte blocks scrypt fills and then reads back in a data-dependent order; it must be a power of 2, here 2^17 = 131,072
r: the block size parameter, here 8; it scales the size of each block
128: bytes per unit of r: scrypt's basic block is two 64-byte chunks, so a block is 128 × r bytes (1,024 bytes when r = 8)
bytes: the unit of memory; one byte is 8 bits
MiB: mebibyte, 2^20 = 1,048,576 bytes
≈: approximately equal to (scrypt also needs a little extra working memory)
In words: these settings make every single guess fill about 128 MiB of memory, so an attacker cannot cheaply run millions of guesses side by side.
```

The parallelism parameter is 1 here. More independent lanes add work. Executing those lanes simultaneously can multiply their working storage; sequential execution can reuse the large workspace. The Python example below sets `maxmem=2**28` (256 MiB) because `hashlib.scrypt` raises an error when the memory needed exceeds its limit, and an implementation's default may be insufficient. Python's documentation specifically notes a 32 MiB default for OpenSSL 1.1.0; defaults and build support need checking on the target system.

Prefer Argon2id; OWASP lists scrypt when Argon2id is unavailable, bcrypt mainly for legacy systems, and PBKDF2 for applicable compliance needs. Tune and periodically revisit costs; the table is not a universal deployment prescription.

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
