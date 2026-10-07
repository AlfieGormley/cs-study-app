---
id: crypto-macs
title: MACs and HMAC
level: intermediate
minutes: 11
summary: How message authentication codes prove a message came from a key holder and wasn't altered, why SHA256(key || msg) is broken, how HMAC works, constant-time verification, replay, and encrypt-then-MAC.
---

A hash tells you whether data changed, but only if you trust where the expected digest came from. An attacker who can modify a message can just recompute its SHA-256. What you really want is a checksum that **only someone holding a secret key can produce**.

That is a **message authentication code (MAC)**. It takes a key and a message and outputs a short **tag**:

```
tag = MAC(key, message)

sender:   send (message, tag)
receiver: recompute MAC(key, message)
          accept only if it equals tag
```

With a suitable MAC, protected key and correct verification, forging a tag for a new message is computationally infeasible within the intended security bounds. A verified tag supports integrity and key-holder authenticity; tag guessing has a nonzero probability, and replay does not establish freshness.

## What a MAC does and doesn't give you

| Gives you | Doesn't give you |
|---|---|
| Integrity | Confidentiality |
| Authenticity (key holder) | Non-repudiation |
| Tamper detection | Replay protection |

- **No confidentiality.** The message travels in the clear unless you also encrypt it.
- **No non-repudiation.** Both sides share the key, so either could have produced the tag. The tag alone cannot distinguish which shared-key holder created it. Digital signatures separate signing from verification authority, but attribution to a human and legal effect require additional evidence.
- **No replay protection.** A captured `(message, tag)` pair remains cryptographically valid while that key and message interpretation are accepted. If an attacker resends "transfer £100 to Mallory", the tag still checks out. Protocols add a timestamp, sequence number or nonce *inside* the authenticated data and reject repeats.

The security goal is called **existential unforgeability**: even after seeing tags for many messages of their choice, an attacker can't produce a valid tag for any new message.

## The tempting mistake: H(key || message)

The obvious construction is to hash the key and message together:

```
tag = SHA256(key || message)
```

With SHA-256 (and SHA-1, MD5, SHA-512) this is **broken by length extension**. As the hashes lesson showed, a Merkle–Damgård digest is the hash function's entire internal state after the last block. An attacker who sees one valid tag can resume hashing from that state.

> [!example] Forging an API request
> An API signs `user=alice&amount=10` with `SHA256(key || msg)`. The attacker sees the tag. Without knowing the key (only guessing its length), they compute a valid tag for `user=alice&amount=10<padding>&amount=9999`. Application abuse also requires the server to accept the inserted padding and interpret the extra parameter as intended; parser and encoding behaviour matter.

This actually happened. In 2009 Thai Duong and Juliano Rizzo showed Flickr's API signatures, built as `MD5(secret || params)`, could be forged this way.

Appending a key is not a generic secure construction either: suitable equal-length internal-state collisions in a Merkle–Damgård hash can remain collisions after a common secret suffix. Rather than patch these designs, use the construction built to be safe.

## HMAC

**HMAC** (RFC 2104, 1997) wraps the hash twice with two derived keys:

```
HMAC(K, m) = H( (K' ^ opad) ||
                H( (K' ^ ipad) || m ) )

K'   = hash key first if over block size,
       then zero-pad to block size
ipad = 0x36 repeated
opad = 0x5c repeated
```

The inner hash processes the message. The outer hash then hashes that result under a different key-derived prefix. An attacker who extends the inner hash still can't produce the outer one, so length extension is defeated.

A collision attack on the unkeyed hash does not automatically forge HMAC. RFC 2104 discusses why HMAC's requirements differ from ordinary collision resistance. Use **HMAC-SHA256** for new work.

> [!note] Content gap: formal HMAC proof
> The full proof paper could not be retrieved reliably during this review (official/archive retrieval failed). Its exact reduction assumptions and bounds are omitted rather than compressed into an unverified one-line theorem.

Some details worth knowing:

- Keys longer than the block size (64 bytes for SHA-256) are first hashed. A random 32-byte key is ideal.
- Tags can be truncated: 128 bits retains 16 bytes from HMAC-SHA256. Choose the length from the protocol, forgery budget and verification limits; 64 bits is not a universal safe minimum.
- Use a specified keyed construction. BLAKE2 has a built-in key parameter, and KMAC is standardised in NIST SP 800-185. Absence of length extension alone does not prove an arbitrary keyed hash construction is a secure MAC.

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
    if not isinstance(tag, str):
        return False
    if len(tag) != 64 or any(
        c not in "0123456789abcdef"
        for c in tag
    ):
        return False
    good = sign(body)
    return hmac.compare_digest(good, tag)
```

Use `hmac.compare_digest` for fixed-type, fixed-length tag comparisons. Ordinary equality is not a constant-time API; implementations can compare machine-sized chunks or use other optimisations, so a byte-by-byte timing model is not guaranteed.

In an idealised oracle that reveals each additional matching character, testing 16 candidates at each of 64 positions uses about 1,024 candidate choices, plus repeated measurements. Real exploitability depends on implementation, noise and other checks; this is not a measured network attack. `compare_digest` avoids content-dependent early exit, but does not make the entire request path constant-time.

> [!warning] Verify before you parse
> Check the tag on the exact raw bytes you received, before decoding JSON or acting on the content. Re-serialising parsed JSON can reorder keys or change whitespace, so the bytes no longer match. Worse, acting before verifying means processing attacker-controlled data.

## Where you meet MACs

- **Webhooks.** GitHub sends `X-Hub-Signature-256: sha256=<hex>`, an HMAC-SHA256 of the body using a secret you configured. Stripe's `Stripe-Signature` header signs a timestamp plus the body, so receivers can reject events outside an accepted time window. Preventing duplicate effects within that window also requires replay/idempotency handling.
- **AWS Signature Version 4.** SigV4-authenticated requests use HMAC-SHA256; AWS also supports other authentication paths, including asymmetric SigV4a. The signing key is derived by chaining HMACs over the date, region and service, so a leaked derived key is limited in scope.
- **JWTs with HS256.** The token's signature is HMAC-SHA256 under a shared secret. Anyone who can verify can also mint tokens, which is fine inside one service but wrong when many parties only need to verify.
- **Session cookies.** Frameworks such as Django and Flask provide signed-cookie mechanisms. Their session-storage choices differ; do not assume every default session cookie contains a signed copy of the session data.
- **Inside AEAD.** AES-GCM uses GHASH and ChaCha20-Poly1305 uses Poly1305. ChaCha20-Poly1305 derives a one-time Poly1305 key for each nonce. GCM reuses a GHASH subkey derived from the AES key and combines its result with a nonce-dependent mask; GHASH alone is not a complete secure MAC. Both modes require their specified nonce discipline.

## Combining encryption and a MAC

Before AEAD modes were common, people combined a cipher and a MAC by hand. There are three orders:

| Scheme | Used by | Verdict |
|---|---|---|
| Encrypt-then-MAC | Traditional encryption-plus-integrity IPsec ESP suites | Sound under suitable primitive, key and encoding assumptions |
| MAC-then-encrypt | Original TLS CBC suites | Difficult to implement without side channels |
| Encrypt-and-MAC | SSH (original) | Fragile |

**Encrypt-then-MAC** computes the MAC over the ciphertext. The receiver checks the tag first and never decrypts tampered data. That is what rules out padding oracles.

**MAC-then-encrypt** requires decryption before verifying its inner MAC. TLS also defined an encrypt-then-MAC extension (RFC 7366), so this is not the behavior of every TLS CBC connection. The padding oracle and Lucky Thirteen attacks on TLS CBC suites exploited exactly this. **Encrypt-and-MAC** MACs the plaintext and can leak whether two plaintexts are equal.

Today the answer is simpler: use a maintained AEAD implementation such as AES-GCM or ChaCha20-Poly1305, following its nonce, tag and key-usage limits. If you must compose by hand, use encrypt-then-MAC with **separate keys** for encryption and authentication, and include the IV and any headers in the MAC.

## Pitfalls

- **Comparing tags with `==`.** Use `hmac.compare_digest` or your library's constant-time verify.
- **Weak or shared keys.** A MAC key must be random (32 bytes from a CSPRNG), not a word like `"secret"`. Use different keys for different purposes.
- **Forgetting replay.** Add a timestamp or counter to the signed data, and reject stale or repeated values.
- **Authenticating the wrong thing.** If the URL path, HTTP method or a header changes meaning, it must be inside the MAC.
- **Expecting non-repudiation.** If a third party needs to verify who sent something, use signatures.
- **Inventing your own scheme.** Use HMAC or a library's AEAD; don't design MAC constructions.

## Key takeaways
- A suitable MAC supports integrity and key-holder authenticity under its security assumptions; it does not establish freshness or a particular human sender.
- `SHA256(key || msg)` is forgeable via length extension. Use HMAC-SHA256 (or keyed BLAKE2/KMAC).
- Always verify in constant time with `hmac.compare_digest`, and verify the raw bytes before parsing.
- MACs give no confidentiality, no non-repudiation and no replay protection on their own.
- Prefer AEAD. If you must compose, encrypt-then-MAC with separate keys.

## Further reading
- [RFC 2104: HMAC](https://www.rfc-editor.org/rfc/rfc2104)
- [HMAC — Wikipedia](https://en.wikipedia.org/wiki/HMAC)
- [hmac — Python documentation](https://docs.python.org/3/library/hmac.html)
- [Validating webhook deliveries — GitHub Docs](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)
- [Flickr API signature forgery (Duong and Rizzo, 2009)](https://vnhacker.blogspot.com/2009/09/flickrs-api-signature-forgery.html)
- [Authenticated encryption — Wikipedia](https://en.wikipedia.org/wiki/Authenticated_encryption)
