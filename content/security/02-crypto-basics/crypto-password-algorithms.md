---
id: crypto-password-algorithms
sourceLesson: crypto-passwords-kdfs
title: Choose password hashing parameters
level: advanced
minutes: 4
summary: Argon2id is the OWASP starting choice for new password storage, subject to deployment constraints.
---

## The password hashing functions

| Function | Year | Memory-hard | Notes |
|---|---|---|---|
| PBKDF2 | RFC in 2000 | No | Approved settings and module required |
| bcrypt | 1999 | Small fixed state, not tunable memory-hardness | 72-byte limit |
| scrypt | 2009 | Yes | Tunable memory |
| Argon2id | Winning family: 2015 | Yes | OWASP starting choice |

**Argon2** won the Password Hashing Competition in 2015. Its **Argon2id** variant is specified in RFC 9106. Its principal cost parameters are memory in kibibytes, iteration count in passes over memory, and parallelism in lanes. The "id" variant mixes resistance to GPU cracking and to side-channel attacks. **This is the recommended default.**

**scrypt** (Colin Percival, 2009) is a memory-hard password KDF. It's a good choice where Argon2 isn't available.

**bcrypt** (1999) is based on the Blowfish cipher and is still a respectable choice if it is what your framework provides. Its cost parameter is an exponent: each +1 doubles the expensive key-setup work, so raising the cost from 10 to 12 makes every new hash, yours and the attacker's, roughly four times slower. Existing hashes keep the cost they were made with until you rehash them.

It only uses the first **72 bytes** of the password. Some libraries truncate silently; the Python `bcrypt` package (version 5) raises an error instead.

**PBKDF2** simply iterates HMAC many times. It is not memory-hard. PBKDF2 may be required by a particular FIPS compliance profile, using approved settings in an appropriately validated module; selecting an algorithm alone does not make an application FIPS compliant.

OWASP's Password Storage Cheat Sheet gives these minimum settings:

| Function | Minimum parameters |
|---|---|
| Argon2id | 19 MiB memory, 2 passes, 1 lane |
| scrypt | 131,072 blocks, size 8, parallelism 1 (about 128 MiB) |
| bcrypt | cost 10 or more |
| PBKDF2 | 600,000 iterations, HMAC-SHA-256 |

The scrypt memory figure comes straight from its parameters: memory grows in proportion to both the cost parameter and the block size.

```formula reference
M ≈ 128Nr bytes
M ≈ 128 × 2^17 × 8 bytes = 2^27 bytes
M ≈ 128 MiB
where
M: the dominant ROMix storage for one sequential scrypt computation, in bytes; implementation buffers and parallel execution can need more
N: the CPU/memory cost parameter, a power of 2; here 2^17 = 131,072
r: the block-size parameter; here 8
128: the bytes per unit of r in scrypt's internal block (128 × r bytes per block)
MiB: mebibyte: 2^20 = 1,048,576 bytes
bytes: the unit of data, 8 bits each
≈: approximately equal to; small buffers and overhead are excluded
In words: scrypt fills N blocks of 128 × r bytes each, so N = 2^17 with r = 8 needs 128 MiB per guess; doubling N doubles the dominant storage and asymptotic work under this fixed-parameter model.
```

Treat these as floors. Tune upwards until a hash takes a comfortable fraction of a second on your production hardware, and make sure login endpoints are rate-limited so attackers can't use your servers to burn CPU.

## Key takeaways
- Argon2id is the OWASP starting choice for new password storage, subject to deployment constraints.
- Treat minimum settings as floors, account for bcrypt’s input limit, and benchmark capacity.

## Further reading
- [OWASP: Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [RFC 9106: Argon2](https://www.rfc-editor.org/rfc/rfc9106)
