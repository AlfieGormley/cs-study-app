---
id: pki-mistakes-pq-constructions
title: Length extension and safer crypto APIs
level: advanced
minutes: 3
sourceLesson: pki-mistakes-pq
summary: Secret-prefix SHA-256 tags permit length extension when the attacker can construct the required padding.
---

Most cryptographic failures in applications come from combining sound primitives in an unsound way. This unit collects the common hand-rolled constructions and the safer alternatives.

## Mistake 5: hand-rolled constructions

- **Hash as MAC.** Hashing the key followed by the message with SHA-256 looks like a message authentication code but allows **length extension**: from the tag of one message, an attacker can compute a valid tag for that message with extra data appended, without the key. Flickr's API signatures fell to this in 2009. Use HMAC.
- **Fast hashes for passwords.** Fast hashes built for general use make offline guessing cheap relative to purpose-built password hashing. Use appropriately configured Argon2id or scrypt; bcrypt is a legacy option with input-length constraints.
- **Custom protocols.** Every handshake in the earlier lessons has subtle bindings (transcripts, domain separation, key separation). A homemade protocol almost certainly misses one.
- **Letting attackers choose algorithms.** Trusting an unvalidated JWT algorithm field can bypass verification. Enforce the expected algorithm and key type. TLS negotiation is normal; downgrade vulnerabilities arise when version/suite policy and transcript binding fail.

Length extension works because SHA-256 (like MD5 and SHA-1) is a Merkle–Damgård hash: its output is its entire internal state after the last block. An attacker who sees the tag can load that state and keep hashing extra data, producing the correct hash of key, message, SHA-256's own padding and the extra data, without ever learning the key; they need only guess the key's length to reconstruct the padding.

```formula reference
t = H(K ‖ m)
H(K ‖ m ‖ P_m ‖ x) = H_t(x)
where
t: the tag of the naive hash-as-MAC construction
H: the hash function, here SHA-256
K: the secret key, unknown to the attacker
m: the original message
P_m: the padding SHA-256 appends after K ‖ m (a 1 bit, zeros and the total length); computable once the key's length is known or guessed
x: the attacker's extra data, such as "&amount=1000000"
H_t: SHA-256 restarted from the internal state t instead of its standard starting values, then run over x with final padding for the full, longer length
‖: concatenation: one value's bytes followed by the next
In words: a plain hash tag is a saved game the attacker can resume, so they can append data and compute a valid tag for the longer message without knowing the key.
```

HMAC fixes this by hashing twice with two keys derived from the secret: the inner hash's result is hidden inside an outer keyed hash, so there is no exposed internal state to resume (the crypto basics module shows the construction). SHA-3 and BLAKE2 are not vulnerable to length extension either, but use a real MAC such as HMAC rather than relying on that.

> [!analogy] Real-world analogy: A signed form with space left at the bottom
> A manager signs a payment form at the bottom of the text, leaving blank space below. Someone adds "and a further £10,000" in the blank space; the signature still sits there, looking as if it approves everything above it.
>
> **How it maps:** The secret-prefix tag "signs" the message only in the sense that the hash state at the end is published. Length extension writes extra data after that point and produces a valid tag for the longer message. HMAC is like a form with the signature covering a sealed summary of the whole page, so nothing can be added afterwards.
>
> **Where it stops:** On paper the addition might be spotted by its handwriting. The forged tag is mathematically perfect; only the server's parser decides whether the appended bytes (which include padding) form a useful request, which is why defences must not rely on the format looking odd.

> [!tip] Choose libraries that make mistakes hard
> High-level APIs can reduce misuse, but responsibilities differ. libsodium's `crypto_secretbox` and `crypto_box` require caller-supplied unique nonces; `secretstream` manages stream nonce/state. Tink AEAD APIs and Fernet manage their own encryption randomness. Fernet is authenticated encryption but has no caller-provided AAD interface. Reach for low-level primitives only when you must, and get the design reviewed.

## Key takeaways
- Secret-prefix SHA-256 tags permit length extension when the attacker can construct the required padding.
- HMAC hides the inner hash state inside an outer keyed hash, so tags cannot be extended.
- High-level APIs differ in nonce and associated-data responsibilities; read the interface contract.

## Further reading
- [Length extension attack — Wikipedia](https://en.wikipedia.org/wiki/Length_extension_attack)
- [Cryptographic Storage Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [Password Storage Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
