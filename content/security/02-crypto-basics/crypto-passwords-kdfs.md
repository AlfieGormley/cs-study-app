---
id: crypto-passwords-kdfs
title: Randomness, KDFs and password hashing
level: advanced
minutes: 15
summary: Why crypto needs a CSPRNG and what happens when randomness fails, HKDF for deriving keys from strong secrets, and how to store passwords with salted, slow, memory-hard hashes (Argon2id, scrypt, bcrypt, PBKDF2).
---

Cryptographic keys and private values such as RSA primes and Diffie–Hellman exponents must be hard to guess. GCM nonces are different: they need not be secret or unpredictable, but must not repeat under the same key. Where those secrets come from matters as much as the algorithms. This lesson covers three closely linked topics:

1. **Randomness**: generating secrets that are truly unpredictable.
2. **Key derivation functions (KDFs)**: turning one secret into the keys you need.
3. **Password hashing**: the special case where the secret is a weak, human-chosen password.

## Randomness: use a CSPRNG

There are two kinds of random number generator in most languages:

| Generator | Python | Safe for secrets? |
|---|---|---|
| Statistical PRNG | `random` | No |
| CSPRNG | `secrets`, `os.urandom` | Yes |

Python's `random` module uses the **Mersenne Twister**. It passes statistical tests and is fine for simulations and games. But it is completely predictable: its whole internal state is 624 numbers of 32 bits each (19,968 bits), so 624 consecutive full 32-bit outputs from the same unchanged generator can reveal enough state to predict subsequent output. Truncated, interleaved or reseeded observations need different analysis. This is not a claim that any 624 API calls reveal every past value.

A **cryptographically secure PRNG (CSPRNG)** is designed so that a computationally bounded attacker observing feasible amounts of output gains only negligible predictive advantage, assuming a secure seed and implementation. State compromise requires separate recovery and backtracking guarantees. Operating systems provide one, seeded from hardware events and CPU entropy sources: `getrandom()` on Linux, `getentropy()` / `arc4random` on macOS and BSDs, `BCryptGenRandom` on Windows.

```python
import secrets

token = secrets.token_urlsafe(32)
key = secrets.token_bytes(32)
pin = secrets.randbelow(10**6)
print(len(token), len(key))
```

This prints `43 32`: 32 random bytes are 43 URL-safe **base64** characters. Base64 writes 6 bits per character, so:

```formula
L_b64 = ⌈8 × L / 6⌉
L_b64 = ⌈8 × 32 / 6⌉ = ⌈42.67⌉ = 43
where
L_b64: the length of the base64 text, in characters
L: the number of random bytes, 32
8: bits per byte
6: bits carried by each base64 character (it has 64 = 2^6 symbols)
⌈ ⌉: ceiling: round up to the next whole number
In words: 32 bytes are 256 bits, which need 42 full characters plus one more for the last 4 bits; `token_urlsafe` drops base64's `=` padding.
```

`secrets` and `os.urandom` both read the operating system's CSPRNG. Don't build your own generator, and don't "improve" the OS one by mixing in timestamps or process IDs.

### When randomness fails

Weak randomness breaks otherwise sound cryptography, often completely:

- **Debian OpenSSL (2008).** A Debian-specific OpenSSL change made key generation predictable. Affected keys had to be replaced after updating the software. Small enumerations often quoted for particular PID limits and architectures are not one universal count covering every key type, architecture and generation path.
- **Sony PlayStation 3 (2010).** ECDSA needs a per-message secret nonce generated securely, either randomly or by a standard deterministic construction such as RFC 6979. The 2010 fail0verflow presentation demonstrated reused ECDSA nonces in the examined PS3 signing system. Two distinct-message signatures under one key and nonce can expose that signing key. This does not establish that every Sony signature or key was affected.
- **Shared RSA primes (2012).** Embedded devices generating keys at first boot, before the OS had gathered entropy, produced keys that shared prime factors. A simple GCD across the keys factored them.

> [!tip] Rule of thumb
> Generate unpredictable keys, tokens, session IDs and reset links with a CSPRNG such as `secrets`, never a predictable generator or timestamp. Generate password salts with the password-hashing library. Nonce requirements depend on the scheme: GCM permits a correctly managed unique counter; salts and encryption nonces are normally public.

## Key derivation with HKDF

You often have one strong secret but need several keys. A TLS handshake produces one Diffie–Hellman shared secret, yet needs separate keys and IVs for each direction. Re-using one key for multiple purposes is dangerous, and raw DH output isn't uniformly random anyway.

**HKDF** (HMAC-based KDF, RFC 5869) solves this in two steps:

```formula
PRK = HMAC(S, IKM)
T(0) = ε
T(i) = HMAC(PRK, T(i − 1) ‖ ctx ‖ i)
OKM = trunc_L(T(1) ‖ T(2) ‖ … ‖ T(N))
N = ⌈L / H_len⌉ ≤ 255
L ≤ 255 × 32 = 8160 bytes
where
PRK: the pseudorandom key produced by the Extract step, one hash length long
HMAC: HMAC with the chosen hash, here SHA-256; its first argument is the key
S: the optional salt: a non-secret random value (a string of zero bytes if absent)
IKM: the input keying material: the strong secret you start from, such as a DH shared secret
T(i): the i-th output block of the Expand step, one hash length long
ε: the empty string, so T(1) starts from nothing
i: the block counter 1, 2, 3, …, written as a single byte
ctx: the context label (the `info` parameter), such as `b"client write key"`
OKM: the output keying material: the derived key or keys
trunc_L: keep only the first L bytes
L: the number of output bytes you ask for
N: the number of blocks needed
H_len: the hash output length in bytes: 32 for SHA-256
⌈ ⌉: ceiling: round up to the next whole number
‖: concatenation: joining byte strings end to end
≤: is at most
…: and so on, up to T(N)
bytes: the unit of data, 8 bits each
In words: Extract squeezes the input secret into one uniform key; Expand then runs HMAC as a counter-driven chain, mixing in the label, and keeps as many bytes as you asked for.
```

1. **Extract** concentrates the input's entropy into a uniform pseudorandom key (PRK). An optional salt strengthens this.
2. **Expand** produces up to 255 hash lengths (8,160 bytes for SHA-256), because the counter i is a single byte. The `info` string binds each output to its purpose, such as `b"client write key"`, so different labels give independent keys.

For example, asking for L = 44 bytes (a 32-byte AES-256 key plus a 12-byte IV) with SHA-256 needs N = 2 blocks, T(1) and T(2), and keeps the first 44 of their 64 bytes.

TLS 1.3, the Signal Protocol, WireGuard (via its Noise framework) and the Web Push standard all build their key schedules on HKDF. The previous lesson's X25519 example used it.

> [!warning] HKDF is not a password hash
> HKDF is fast and assumes its input already has high entropy (a random key or a DH secret). It does not deliberately increase password-guessing cost. Actual attack throughput depends on derivation and candidate-verification work. Passwords need the deliberately slow functions below.

## The password problem

Passwords are the opposite of keys: short, human-chosen and guessable. If an attacker steals your user table, they will try to recover passwords **offline**, on their own hardware, with no rate limits. Your job is to make each guess as expensive as possible.

Here is how storage has evolved:

| Storage | What goes wrong |
|---|---|
| Plaintext | One breach reveals everything |
| Encrypted | Whoever obtains or can use the decryption key can recover passwords |
| `sha256(pw)` | Fast to brute-force; rainbow tables |
| `sha256(salt + pw)` | Still deliberately fast; no password-specific work factor |
| Argon2id, scrypt, bcrypt | Each guess is slow and costly |

### Salts

A **salt** is a random value (16 bytes is typical) generated per user and stored next to the hash. It means:

- Different salts prevent direct equality matching and reuse of one computed hash across accounts. But a password learned from one account remains a valuable candidate for others.
- Precomputed **rainbow tables** (precomputed hash chains supporting time/memory trade-offs) cannot be reused directly across sufficiently large, distinct salts, because the attacker would need a separate table for every salt.

Salts are not secret. They don't make a single guess slower; they force the attacker to attack each account separately.

### Slowness (work factor)

SHA-256 is built for speed.

> [!note] Content gap: cracking throughput
> No reproducible GPU or end-to-end password-guessing benchmark was supplied, so fixed rate claims are omitted. Quiz rates are explicitly hypothetical arithmetic inputs.

A password hash is built to be slow, with a tunable **work factor**. The arithmetic for one sequential verifier is simple:

```formula
r = 1 / t_hash
r = 1 / 0.1 s = 10 per s
t_total = N / r
t_total = 10^6 / (10 per s) = 10^5 s
where
r: guesses checked per second by one sequential verifier
t_hash: the time for one hash, here 100 ms = 0.1 s
t_total: the time to try every candidate
N: the number of candidate passwords, here 10^6 (a million)
s: seconds; 10^5 s is about 27.8 hours
ms: milliseconds, thousandths of a second
In words: a 100 ms hash allows ten guesses a second per verifier, so a million candidates take about a day instead of a fraction of a second.
```

So a 100 ms hash means about ten sequential verifications per second on that measured setup. It does not cap an attacker at that rate: hardware, parallelism and implementation differ, and an attacker with many parallel units divides t_total by their number. Benchmark your deployment and use memory-hard settings to raise offline attack costs.

### Memory-hardness

Attackers use GPUs and custom ASICs with thousands of cores. If a hash needs only CPU time, these cores run it massively in parallel. A **memory-hard** function also requires a large amount of RAM per guess (tens of megabytes or more). Memory is expensive to replicate across thousands of cores, so this blunts the attacker's hardware advantage.

## The password hashing functions

| Function | Year | Memory-hard | Notes |
|---|---|---|---|
| PBKDF2 | 2000 | No | FIPS-approved |
| bcrypt | 1999 | Small fixed state, not tunable memory-hardness | 72-byte limit |
| scrypt | 2009 | Yes | Tunable memory |
| Argon2id | 2015 | Yes | Best default |

**Argon2** won the Password Hashing Competition in 2015. Its **Argon2id** variant is specified in RFC 9106. It has three parameters: memory (m, in kibibytes), iterations (t, passes over that memory) and parallelism (p, independent lanes). The "id" variant mixes resistance to GPU cracking and to side-channel attacks. **This is the recommended default.**

**scrypt** (Colin Percival, 2009) is a memory-hard password KDF. It's a good choice where Argon2 isn't available.

**bcrypt** (1999) is based on the Blowfish cipher and is still a respectable choice if it is what your framework provides. It has a cost parameter where each +1 doubles the work:

```formula
W ∝ 2^c
W_12 / W_10 = 2^12 / 2^10 = 2^2 = 4
where
W: the work (and so the time) for one bcrypt hash
c: the bcrypt cost parameter, at least 10 under OWASP guidance
W_12, W_10: the work at cost 12 and cost 10
∝: is proportional to: doubling the right-hand side doubles the left
In words: bcrypt runs 2^c rounds of its expensive key setup, so raising the cost by 2 makes every hash, yours and the attacker's, four times slower.
```

It only uses the first **72 bytes** of the password. Some libraries truncate silently; the Python `bcrypt` package (version 5) raises an error instead.

**PBKDF2** simply iterates HMAC many times. It is not memory-hard. PBKDF2 may be required by a particular FIPS compliance profile, using approved settings in an appropriately validated module; selecting an algorithm alone does not make an application FIPS compliant.

OWASP's Password Storage Cheat Sheet gives these minimum settings:

| Function | Minimum parameters |
|---|---|
| Argon2id | m = 19 MiB, t = 2, p = 1 |
| scrypt | N = 2^17 (128 MiB), r = 8, p = 1 |
| bcrypt | cost 10 or more |
| PBKDF2 | 600,000 iterations, HMAC-SHA-256 |

The scrypt memory figure comes straight from its parameters:

```formula
M = 128 × N × r bytes
M = 128 × 2^17 × 8 = 2^27 bytes
M = 2^27 / 2^20 MiB = 128 MiB
where
M: the memory one scrypt hash needs
N: the CPU/memory cost parameter, a power of 2; here 2^17 = 131,072
r: the block-size parameter; here 8
128: the bytes per unit of r in scrypt's internal block (128 × r bytes per block)
MiB: mebibyte: 2^20 = 1,048,576 bytes
bytes: the unit of data, 8 bits each
In words: scrypt fills N blocks of 128 × r bytes each, so N = 2^17 with r = 8 needs 128 MiB per guess; doubling N doubles both the memory and the time.
```

Treat these as floors. Tune upwards until a hash takes a comfortable fraction of a second on your production hardware, and make sure login endpoints are rate-limited so attackers can't use your servers to burn CPU.

## Doing it in Python

The `argon2-cffi` library wraps the reference implementation. In argon2-cffi 25.1, defaults derive from RFC 9106's low-memory profile but can vary by platform. The example selects that profile explicitly (64 MiB, t = 3, p = 4), generates a random salt and stores parameters with the result.

```python
from argon2 import PasswordHasher
from argon2.profiles import \
    RFC_9106_LOW_MEMORY
from argon2.exceptions import \
    VerifyMismatchError

ph = PasswordHasher.from_parameters(
    RFC_9106_LOW_MEMORY)

stored = ph.hash("correct horse")
header = "$".join(
    stored.split("$")[:4]) + "$"
print(header)

def login(stored, attempt):
    try:
        ph.verify(stored, attempt)
    except VerifyMismatchError:
        return False, stored
    if ph.check_needs_rehash(stored):
        stored = ph.hash(attempt)
    return True, stored

print(login(stored, "correct horse")[0])
print(login(stored, "battery")[0])
```

This prints:

```
$argon2id$v=19$m=65536,t=3,p=4$
True
False
```

The `m=65536` in that header is in kibibytes (KiB, 1,024 bytes each):

```formula
m = 65536 KiB
m = 65536 / 1024 MiB = 64 MiB
where
m: Argon2's memory parameter
KiB: kibibyte: 1,024 bytes
MiB: mebibyte: 1,024 KiB = 1,048,576 bytes
In words: the stored hash records that each verification used 64 MiB of memory, three passes (t) and four lanes (p).
```

The stored string is self-describing: algorithm, version, parameters, then the salt and hash (cut off here). That is what lets you raise parameters later. `check_needs_rehash` spots hashes made with old settings, and you upgrade them the next time that user logs in successfully, one point at which the submitted password is available. Treat hashes as trusted server-side records, persist upgrades atomically, and handle malformed stored records and operational errors separately; this minimal helper is not a full login endpoint.

One temporary migration option is a salted outer Argon2id hash over the legacy SHA-1 representation, marked with its exact old encoding. Replace it with direct Argon2id after successful login. This cannot undo an earlier leak of the fast hash; forced resets may be necessary after compromise. Remove or separately protect retained legacy copies and backups.

## Peppers and other defences

A **pepper** is a secret key applied to every password, for example an HMAC of the password keyed with the pepper, computed before Argon2id:

```formula
x = HMAC(K_pep, P)
h = Argon2id(x, S)
where
x: the peppered password
HMAC: HMAC-SHA256, keyed with its first argument
K_pep: the pepper, a secret key kept outside the database
P: the user's password
h: the stored password hash
Argon2id: the slow, memory-hard password hash, with its usual parameters
S: the user's random salt, stored next to h
In words: mix in a secret the database never holds, then hash slowly with a per-user salt as usual.
```

Unlike the salt it is *not* stored in the database: it lives in a secrets manager or HSM. If attackers steal only the database (say, through SQL injection), a strong unavailable pepper prevents ordinary offline password-only verification. It does not help if they can guess the pepper or use a compromised application as an oracle. The cost is operational: lose or rotate the pepper carelessly and nobody can log in.

Password hashing is the last line of defence. It slows cracking after a breach; it doesn't stop weak passwords from being guessed online. Combine it with rate limiting, checks against known-breached passwords, and multi-factor authentication.

## Key takeaways
- Generate every secret with a CSPRNG (`secrets`, `os.urandom`); consecutive full 32-bit Mersenne Twister outputs can reveal its state.
- Broken randomness, as in Debian OpenSSL 2008 and the PS3, destroys otherwise sound cryptography.
- Use HKDF to derive several independent keys from one strong secret, with an `info` label per purpose.
- Store passwords with a salted, slow, memory-hard hash: Argon2id by default, scrypt or bcrypt if needed, PBKDF2 where FIPS requires it.
- Use a vetted library, store the self-describing hash string, rehash on login when parameters change, and never invent a scheme.

## Further reading
- [Password Storage Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [RFC 9106: Argon2](https://www.rfc-editor.org/rfc/rfc9106)
- [RFC 5869: HKDF](https://www.rfc-editor.org/rfc/rfc5869)
- [secrets — Python documentation](https://docs.python.org/3/library/secrets.html)
- [argon2-cffi documentation](https://argon2-cffi.readthedocs.io/en/stable/)
- [Cryptographically secure PRNG — Wikipedia](https://en.wikipedia.org/wiki/Cryptographically_secure_pseudorandom_number_generator)
