---
id: pki-mistakes-pq-timing
title: Timing leaks and comparison APIs
level: advanced
minutes: 1
sourceLesson: pki-mistakes-pq
summary: Ordinary equality does not promise constant-time comparison.
---

Cryptographic security depends on the complete construction and its implementation, including key generation, message authentication and correct nonce handling.

## Mistake 4: leaking secrets through time

Ordinary equality has no constant-time security guarantee. An early-exit comparison can reveal prefix information in suitable timing conditions, but Python byte equality is not a guaranteed one-byte-at-a-time oracle. Use the dedicated comparison API and validate expected types and lengths.

```python
import hmac

def check(tag, expected):
    # avoids content-based short circuit
    return hmac.compare_digest(
        tag, expected)
```

The same principle applies inside primitives: table-lookup AES and naive RSA leak keys through cache timing, which is why libraries use constant-time code. Even post-quantum code is not immune: the **KyberSlash** timing bugs (a division that took secret-dependent time), disclosed around the start of 2024, affected several Kyber implementations.

## Key takeaways
- Ordinary equality does not promise constant-time comparison.
- Use compare_digest with expected types and lengths for suitable secret tags.
- Primitive implementations also need side-channel review; post-quantum algorithms are not exempt.

## Further reading
- [Cryptographic storage guidance — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [NIST post-quantum project](https://csrc.nist.gov/projects/post-quantum-cryptography)
