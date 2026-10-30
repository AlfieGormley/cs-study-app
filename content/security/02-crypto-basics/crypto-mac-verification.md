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

Why does the comparison matter? A comparison that stops at the first mismatching character takes slightly longer the more leading characters are right. In an idealised timing oracle that reveals each additional matching character, the attacker no longer has to guess the whole 64-character hex tag at once (2^256 possibilities). They can solve it one position at a time: at most 16 candidates per position, about a thousand guesses in all.

Each of those guesses still needs repeated timing measurements to beat noise. Real exploitability depends on implementation, noise and other checks; this is not a measured network attack. `compare_digest` avoids content-dependent early exit, but does not make the entire request path constant-time.

> [!analogy] Real-world analogy: A keypad that pauses on each correct digit
> Imagine a door keypad that checks a code digit by digit and takes a moment longer for every leading digit you got right. Instead of trying every full code, you try each first digit until the pause grows, then each second digit, and so on.
>
> **How it maps:** The keypad is an early-exit comparison, the pause is the timing difference, and solving digit by digit is the attacker confirming one tag position at a time. `hmac.compare_digest` is a keypad that always takes the same time whatever you type.
>
> **Where it stops:** Over a network the timing difference per character is tiny and buried in noise, so a real attack needs many repeated measurements and may not be practical at all. The fix is still cheap, so use it rather than gambling on noise.

> [!warning] Verify before you parse
> Check the tag on the exact raw bytes you received, before decoding JSON or acting on the content. Re-serialising parsed JSON can reorder keys or change whitespace, so the bytes no longer match. Worse, acting before verifying means processing attacker-controlled data.

## Key takeaways
- Use the library’s content-independent comparison on validated fixed-type tags.
- Authenticate exact raw bytes before parsing or acting on the message.

## Further reading
- [Python hmac API](https://docs.python.org/3/library/hmac.html)
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104)
