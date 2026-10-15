---
id: crypto-randomness-sources
sourceLesson: crypto-passwords-kdfs
title: Generate secrets with the operating system
level: advanced
minutes: 4
summary: Use a CSPRNG for unpredictable keys and tokens, with nonce requirements specific to the scheme.
---

Cryptographic keys and private values such as RSA primes and Diffie–Hellman exponents must be hard to guess. GCM nonces are different: they need not be secret or unpredictable, but must not repeat under the same key. Where those secrets come from matters as much as the algorithms. This sequence of short units covers three closely linked topics:

1. **Randomness**: generating secrets that are truly unpredictable.
2. **Key derivation functions (KDFs)**: turning one secret into the keys you need.
3. **Password hashing**: the special case where the secret is a weak, human-chosen password.

## Randomness: use a CSPRNG

There are two kinds of random number generator in most languages:

| Generator | Python | Safe for secrets? |
|---|---|---|
| Statistical PRNG | `random` | No |
| CSPRNG | `secrets`, `os.urandom` | Yes |

Python's `random` module uses the **Mersenne Twister**. It passes statistical tests and is fine for simulations and games. But it is completely predictable: its stored array contains 624 words of 32 bits each, plus a position index (the recurrence has a 19,937-bit effective state), so 624 consecutive full 32-bit outputs from the same unchanged generator can reveal enough state to predict subsequent output. Truncated, interleaved or reseeded observations need different analysis. This is not a claim that any 624 API calls reveal every past value.

A **cryptographically secure PRNG (CSPRNG)** is designed so that a computationally bounded attacker observing feasible amounts of output gains only negligible predictive advantage, assuming a secure seed and implementation. State compromise requires separate recovery and backtracking guarantees. Operating systems expose cryptographic randomness services, with entropy collection and reseeding rules specific to each platform: `getrandom()` on Linux, `getentropy()` / `arc4random` on macOS and BSDs, `BCryptGenRandom` on Windows.

```python
import secrets

# URL-safe text encodes 32 random bytes.
token = secrets.token_urlsafe(32)
# Raw bytes suit a cryptographic key.
key = secrets.token_bytes(32)
# Uniform integer below one million.
pin = secrets.randbelow(10**6)
# Lengths are fixed; the values are random.
print(len(token), len(key))
```

This prints `43 32`: 32 random bytes are 43 URL-safe **base64** characters. Base64 writes 6 bits per character, so:

```formula
L_b64 = ⌈8L / 6⌉
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

## Key takeaways
- Use a CSPRNG for unpredictable keys and tokens, with nonce requirements specific to the scheme.
- Predictable generator state and failed entropy collection have caused real cryptographic failures.

## Further reading
- [Python secrets API](https://docs.python.org/3/library/secrets.html)
- [Mining your Ps and Qs: original research](https://factorable.net/paper.html)
