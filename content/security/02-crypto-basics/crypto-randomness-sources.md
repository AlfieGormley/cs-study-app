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

Python's `random` module uses the **Mersenne Twister**. It passes statistical tests and is fine for simulations and games, but it is completely predictable. Its internal state is 624 words of 32 bits, and each full 32-bit output is a reversible scrambling of one state word. An attacker who sees 624 consecutive full outputs from the same generator can rebuild the state and predict everything it produces next. (Truncated or interleaved outputs need more work, but "more work" is not a security guarantee.)

> [!analogy] Real-world analogy: A dealer who always shuffles the same way
> A card dealer uses an elaborate shuffle that produces well-mixed-looking hands. But the shuffle is mechanical: the same starting deck always gives the same order. A player who watches enough cards come out can work out where the dealer is in the pattern and call the next cards before they are dealt.
>
> **How it maps:** The shuffle is the Mersenne Twister's fixed recurrence, the cards dealt are its outputs, and watching 624 outputs is enough to recover its position. A CSPRNG is a dealer whose next card cannot feasibly be predicted however many earlier cards you have seen.
>
> **Where it stops:** A real dealer's shuffles are a little imprecise; the generator is exactly deterministic, which makes prediction certain rather than likely once the state is known. And "looks well mixed" is precisely the property statistical tests check, which is why passing them says nothing about unpredictability.

A **cryptographically secure PRNG (CSPRNG)** is designed so that a computationally bounded attacker observing feasible amounts of output gains only negligible predictive advantage, assuming a secure seed and implementation. What happens if its internal state ever leaks is a separate question; well-designed generators keep reseeding from fresh entropy so that they become unpredictable again. Operating systems expose cryptographic randomness services, with entropy collection and reseeding rules specific to each platform: `getrandom()` on Linux, `getentropy()` / `arc4random` on macOS and BSDs, `BCryptGenRandom` on Windows.

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

This prints `43 32`. The 32 random bytes (256 bits) become 43 URL-safe **base64** characters, because each base64 character carries 6 bits and `token_urlsafe` drops base64's `=` padding. The encoding changes how the token looks, not how unpredictable it is: it still holds 256 random bits.

`secrets` and `os.urandom` both read the operating system's CSPRNG. Don't build your own generator, and don't "improve" the OS one by mixing in timestamps or process IDs.

### When randomness fails

Weak randomness breaks otherwise sound cryptography, often completely:

- **Debian OpenSSL (disclosed 2008).** A Debian-specific change to OpenSSL (package versions 0.9.8c-1 up to 0.9.8g-9) left its random number generator producing predictable numbers. Keys generated on affected systems came from a small enough set to be guessed by brute force, so they all had to be regenerated after the fix, not just the software updated.
- **Sony PlayStation 3 (2010).** ECDSA needs a fresh secret nonce for every signature, generated securely either at random or by a standard deterministic construction such as RFC 6979. In 2010 the fail0verflow group showed that the PS3 signing system they examined reused the same nonce. Two signatures on different messages with the same key and nonce let anyone solve for the private signing key.
- **Shared RSA primes (2012).** Embedded devices generating keys at first boot, before the OS had gathered entropy, produced keys that shared prime factors. A simple GCD across the keys factored them.

> [!tip] Rule of thumb
> Generate unpredictable keys, tokens, session IDs and reset links with a CSPRNG such as `secrets`, never a predictable generator or timestamp. Generate password salts with the password-hashing library. Nonce requirements depend on the scheme: GCM permits a correctly managed unique counter; salts and encryption nonces are normally public.

## Key takeaways
- Use a CSPRNG for unpredictable keys and tokens, with nonce requirements specific to the scheme.
- Predictable generator state and failed entropy collection have caused real cryptographic failures.

## Further reading
- [Python secrets API](https://docs.python.org/3/library/secrets.html)
- [Mining your Ps and Qs: original research](https://factorable.net/paper.html)
