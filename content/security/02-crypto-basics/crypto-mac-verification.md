---
id: crypto-mac-verification
sourceLesson: crypto-macs
title: Verify exact bytes without a timing shortcut
level: intermediate
minutes: 3
summary: Use the library’s content-independent comparison on validated fixed-type tags.
---

## Verifying a tag safely

This example checks a lowercase hexadecimal body tag. It omits HTTP header handling, key provisioning/rotation and replay protection, so it is not a complete webhook receiver:

```python
import hmac, hashlib, secrets

# Demo only: share and persist securely.
KEY = secrets.token_bytes(32)

def sign(body: bytes) -> str:
    return hmac.new(KEY, body,
        hashlib.sha256).hexdigest()

def verify(body: bytes, tag: str) -> bool:
    # Validate the demo tag format.
    if not isinstance(tag, str):
        return False
    if len(tag) != 64 or any(
        c not in "0123456789abcdef"
        for c in tag
    ):
        return False
    # Sign the exact bytes that arrived.
    good = sign(body)
    # No content-dependent comparison exit.
    return hmac.compare_digest(good, tag)
```

Use `hmac.compare_digest` for fixed-type, fixed-length tag comparisons. Ordinary equality is not a constant-time API; implementations can compare machine-sized chunks or use other optimisations, so a byte-by-byte timing model is not guaranteed.

In an idealised oracle that reveals each additional matching character, the attacker can guess the tag one character at a time instead of all at once:

```formula
G_timing ≤ 16 × 64 = 1024
G_brute = 16^64 = 2^256
where
G_timing: candidate characters the attacker tries when the oracle confirms each position separately (at most 16 per position)
G_brute: the number of possible 64-character tags, to be searched blind without the oracle
16: the number of possible hex characters (0–9, a–f) at each position
64: the number of hex characters in an HMAC-SHA256 tag (32 bytes)
≤: is at most
In words: a leak that confirms one character at a time turns an impossible 2^256 search into about a thousand guesses.
```

Each of those guesses still needs repeated timing measurements to beat noise. Real exploitability depends on implementation, noise and other checks; this is not a measured network attack. `compare_digest` avoids content-dependent early exit, but does not make the entire request path constant-time.

> [!warning] Verify before you parse
> Check the tag on the exact raw bytes you received, before decoding JSON or acting on the content. Re-serialising parsed JSON can reorder keys or change whitespace, so the bytes no longer match. Worse, acting before verifying means processing attacker-controlled data.

## Key takeaways
- Use the library’s content-independent comparison on validated fixed-type tags.
- Authenticate exact raw bytes before parsing or acting on the message.

## Further reading
- [Python hmac API](https://docs.python.org/3/library/hmac.html)
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104)
