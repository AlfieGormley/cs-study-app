---
id: pki-mistakes-pq-timing
title: Timing leaks and comparison APIs
level: advanced
minutes: 2
sourceLesson: pki-mistakes-pq
summary: Ordinary equality does not promise constant-time comparison.
---

Software can leak a secret without ever printing it: the time an operation takes can depend on the secret, and an attacker who measures that time learns something.

## Mistake 4: leaking secrets through time

Ordinary equality has no constant-time security guarantee. An early-exit comparison can reveal prefix information in suitable timing conditions, but Python byte equality is not a guaranteed one-byte-at-a-time oracle. Use the dedicated comparison API and validate expected types and lengths.

```python
import hmac

def check(tag, expected):
    # avoids content-based short circuit
    return hmac.compare_digest(
        tag, expected)
```

> [!analogy] Real-world analogy: A safe-cracker listening to the dial
> In films, a safe-cracker presses an ear to the safe and turns the dial, listening for the tiny click that means one number is right. They never need the whole combination at once; they learn it one number at a time.
>
> **How it maps:** An early-exit comparison is the clicking dial: it can stop sooner when the first byte is wrong than when several leading bytes match, so response times can leak how much of a guessed tag is correct, and an attacker can build the tag byte by byte. `hmac.compare_digest` is a dial that makes no clicks: its running time does not depend on where the inputs first differ.
>
> **Where it stops:** A click is loud and immediate. Real timing differences are tiny and noisy over a network, so an attack may need many repeated measurements, and whether it succeeds depends on the implementation and the environment. The defence is still to remove the signal, not to hope it is too small.

The same principle applies inside primitives: table-lookup AES and naive RSA leak keys through cache timing, which is why libraries use constant-time code. Even post-quantum code is not immune: the **KyberSlash** timing bugs (a division that took secret-dependent time), disclosed around the start of 2024, affected several Kyber implementations.

## Key takeaways
- Ordinary equality does not promise constant-time comparison.
- Use compare_digest with expected types and lengths for suitable secret tags.
- Primitive implementations also need side-channel review; post-quantum algorithms are not exempt.

## Further reading
- [hmac.compare_digest — Python docs](https://docs.python.org/3/library/hmac.html#hmac.compare_digest)
- [Timing attack — Wikipedia](https://en.wikipedia.org/wiki/Timing_attack)
