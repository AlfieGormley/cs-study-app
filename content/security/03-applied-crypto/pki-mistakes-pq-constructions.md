---
id: pki-mistakes-pq-constructions
title: Length extension and safer crypto APIs
level: advanced
minutes: 3
sourceLesson: pki-mistakes-pq
summary: Secret-prefix SHA-256 tags permit length extension when the attacker can construct the required padding.
---

Cryptographic security depends on the complete construction and its implementation, including key generation, message authentication and correct nonce handling.

## Mistake 5: hand-rolled constructions

- **Hash as MAC.** Hashing the key followed by the message with SHA-256 looks like a message authentication code but allows **length extension**: from the tag of one message, an attacker can compute a valid tag for that message with extra data appended, without the key (formulas below). Flickr's API signatures fell to this in 2009. Use HMAC.
- **Fast hashes for passwords.** Fast hashes built for general use make offline guessing cheap relative to purpose-built password hashing. Use appropriately configured Argon2id or scrypt; bcrypt is a legacy option with input-length constraints.
- **Custom protocols.** Every handshake in the earlier lessons has subtle bindings (transcripts, domain separation, key separation). A homemade protocol almost certainly misses one.
- **Letting attackers choose algorithms.** Trusting an unvalidated JWT algorithm field can bypass verification. Enforce the expected algorithm and key type. TLS negotiation is normal; downgrade vulnerabilities arise when version/suite policy and transcript binding fail.

Length extension works because SHA-256 (like MD5 and SHA-1) is a Merkle–Damgård hash: its output is its entire internal state after the last block. HMAC fixes this by hashing twice with two derived keys:

```formula
t = H(K ‖ m)
H(K ‖ m ‖ P_m ‖ x) = H_t(x)
HMAC(K, m) = H(K_o ‖ H(K_i ‖ m))
K_o = K_0 ⊕ opad
K_i = K_0 ⊕ ipad
where
t: the tag of the naive hash-as-MAC construction
H: the hash function, here SHA-256
K: the original secret key supplied to either construction
K_0: the processed HMAC key block: hash K if longer than SHA-256’s 64-byte block size, then zero-pad the resulting or shorter key to 64 bytes
m: the message
P_m: the padding SHA-256 appends after K ‖ m (a 1 bit, zeros and the total length); the attacker can compute it if they know or guess the key's length
x: the attacker's extra data, such as "&amount=1000000"
H_t: SHA-256 restarted from the internal state t instead of its standard starting values, then run over x (with final padding computed for the full, longer length)
HMAC: hash-based message authentication code
K_o: the outer key
K_i: the inner key
opad: the outer pad, the byte 0x5c repeated 64 times
ipad: the inner pad, the byte 0x36 repeated 64 times
⊕: XOR (exclusive OR), byte by byte
‖: concatenation: one value's bytes followed by the next
In words: a plain hash's tag is a saved game the attacker can resume, so they can extend the message and get a valid tag; in HMAC the inner hash's result is hidden inside a second keyed hash, so there is nothing useful to resume.
```

The second line is the attack: the attacker never learns K, but the hash of key, message, padding and extra data equals what they compute by resuming from t.

> [!tip] Choose libraries that make mistakes hard
> High-level APIs can reduce misuse, but responsibilities differ. libsodium's `crypto_secretbox` and `crypto_box` require caller-supplied unique nonces; `secretstream` manages stream nonce/state. Tink AEAD APIs and Fernet manage their own encryption randomness. Fernet is authenticated encryption but has no caller-provided AAD interface. Reach for low-level primitives only when you must, and get the design reviewed.

## Key takeaways
- Secret-prefix SHA-256 tags permit length extension when the attacker can construct the required padding.
- HMAC specifies inner and outer key processing rather than a homemade keyed hash.
- High-level APIs differ in nonce and associated-data responsibilities; read the interface contract.

## Further reading
- [Cryptographic storage guidance — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [NIST post-quantum project](https://csrc.nist.gov/projects/post-quantum-cryptography)
