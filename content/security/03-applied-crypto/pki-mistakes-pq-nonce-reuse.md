---
id: pki-mistakes-pq-nonce-reuse
title: Nonce reuse and overlapping plaintext
level: advanced
minutes: 4
sourceLesson: pki-mistakes-pq
summary: Reusing a stream-mode key and nonce exposes the XOR of overlapping plaintext bytes.
---

Broken ciphers are rare. Broken *uses* of good ciphers are everywhere. Common causes of production cryptographic failure include a repeated nonce, a missing message authentication code, a predictable random number, a comparison that leaks time.

Later units cover the one change in the field that does involve breaking the algorithms themselves: quantum computers, and the migration already under way to replace RSA and elliptic curves.

## Mistake 1: reusing a nonce

Stream-like modes (CTR, GCM, ChaCha20) turn the key and nonce into a **keystream** and XOR it with the plaintext. Use the same key and nonce twice and both messages are XORed with the same keystream, which then cancels out:

```formula essential
c_1 ⊕ c_2 = p_1 ⊕ p_2
where
c_1: the first ciphertext, seen by the attacker
c_2: the second ciphertext, encrypted under the same key and nonce
p_1: the first plaintext
p_2: the second plaintext
⊕: XOR (exclusive OR), bit by bit: 1 where the bits differ; anything XORed with itself gives 0
In words: with a repeated key and nonce, both messages were XORed with the same keystream, so XORing the two ciphertexts cancels the keystream and leaves the two plaintexts XORed together; knowing either plaintext then reveals the overlapping part of the other, with no key needed.
```

Know or guess one plaintext and you get the other:

```python
import os
from cryptography.hazmat.primitives \
    .ciphers.aead import AESGCM

g = AESGCM(AESGCM.generate_key(128))
n = os.urandom(12)  # BUG: used twice
p1 = b"attack at dawn!"
p2 = b"retreat at ten!"
# Deliberate misuse below: same key/nonce.
c1 = g.encrypt(n, p1, None)
c2 = g.encrypt(n, p2, None)

def xor(a, b):
    # zip stops at the shorter input.
    # The outer call truncates at p1.
    pairs = zip(a, b)
    return bytes(x ^ y for x, y in pairs)

# attacker knows (or guesses) p1
print(xor(xor(c1, c2), p1))
```

This prints `b'retreat at ten!'`. With GCM it is worse still: nonce reuse creates equations in the authentication subkey and can enable tag forgery. The exact recovery and forgery depend on message structure and available observations; this does not reveal the AES key or automatically provide the mask for every unused nonce.

> [!analogy] Real-world analogy: Two notes written through the same stencil
> Imagine hiding a note by laying a sheet of random scribbles over it and photocopying the combination. One note is unreadable. But if you use the same scribble sheet for a second note, someone holding both copies can line them up so the scribbles cancel, leaving the two notes superimposed; if they can guess one note, they can read the other.
>
> **How it maps:** The scribble sheet is the keystream that the cipher derives from the key and nonce. A fresh nonce means a fresh sheet for every message. Reusing a key and nonce reuses the sheet, so the XOR of the two ciphertexts equals the XOR of the two plaintexts.
>
> **Where it stops:** Paper scribbles cannot be cancelled exactly; XOR cancels perfectly, bit for bit, so the leak is exact. In GCM the damage goes further than reading: the repeated nonce also exposes material that can let an attacker forge authentication tags.

Real cases: the 2017 **KRACK** attacks tricked WPA2 devices into reinstalling a key and resetting its nonce counter. In 2016 researchers scanning the internet found 184 HTTPS servers repeating GCM nonces, some of them belonging to large organisations, and tens of thousands more using random nonces in ways that risked collisions.

Fixes: use a counter you can guarantee never repeats, random 96-bit nonces only well below 4,294,967,296 messages per key, or a nonce-misuse-resistant mode such as **AES-GCM-SIV**. Under its usage bounds, repeated nonces expose equality of identical plaintext/associated-data inputs rather than GCM’s catastrophic reuse failure; lengths remain visible. Do not deliberately repeat nonces or ignore the mode’s bounds.

## Key takeaways
- Reusing a stream-mode key and nonce exposes the XOR of overlapping plaintext bytes.
- Known plaintext can then recover the other message’s overlapping bytes without the cipher key.
- GCM reuse can also compromise authentication; nonce-misuse-resistant modes still have usage bounds and leakage.

## Further reading
- [Nonce-disrespecting adversaries: practical forgery attacks on GCM in TLS](https://eprint.iacr.org/2016/475)
- [Cryptographic Storage Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
