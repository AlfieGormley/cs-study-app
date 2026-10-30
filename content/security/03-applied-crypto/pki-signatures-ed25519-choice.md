---
id: pki-signatures-ed25519-choice
title: Ed25519 and signature format choices
level: basic
minutes: 2
sourceLesson: pki-signatures
summary: Ed25519 signing is deterministic and needs no fresh random per-signature nonce.
---

The RSA and ECDSA units showed two ways a signature scheme can be misused: raw encodings and bad nonces. Newer designs try to remove those choices from the developer altogether.

## Ed25519: designed to be hard to misuse

**Ed25519** (EdDSA on the Edwards-form edwards25519 curve, RFC 8032) bakes these lessons in:

- The nonce is computed from a secret and the message by a fixed rule. Same key and message, same signature; no fresh per-signature RNG input is required. Key generation still needs secure randomness.
- Its design supports efficient constant-time implementations, with small keys and signatures. Choose a maintained implementation; the scheme does not make every implementation side-channel safe.
- There are fewer parameters to get wrong. You do not pick a hash or a padding scheme.

```python
from cryptography.hazmat.primitives \
    .asymmetric import ed25519
from cryptography import exceptions

# Generate a fresh secret signing key.
sk = ed25519.Ed25519PrivateKey.generate()
pk = sk.public_key()

msg = b"pay alice 10 GBP"
# Sign these exact bytes, not ciphertext.
sig = sk.sign(msg)
print(len(sig))          # 64

# Success returns without an exception.
pk.verify(sig, msg)      # no exception
# The same signature rejects changed data.
try:
    pk.verify(sig, b"pay alice 99 GBP")
except exceptions.InvalidSignature:
    print("rejected")
print(sk.sign(msg) == sig)  # True
```

The last line prints `True` because Ed25519 is deterministic. ECDSA with independently random nonces would normally print False; deterministic ECDSA can instead repeat the signature for the same key and message.

## Choosing an algorithm

| Scheme | Public key | Signature | Notes |
|---|---|---|---|
| RSA-2048 | 256 B modulus plus exponent/encoding | 256 B | Cost depends on exponent and implementation |
| ECDSA P-256 | 65 B uncompressed SEC1; 33 B compressed | 64 B (r then s, 32 B each) | Needs a correctly generated nonce |
| Ed25519 | 32 B | 64 B | Deterministic, fast |
| ML-DSA-44 | 1,312 B | 2,420 B | Post-quantum |

Sizes depend on encoding: DER ECDSA signatures vary, commonly around 70–72 bytes for P-256; smaller encodings can occur. Ed25519 is a useful choice when the protocol supports it. ECDSA P-256 is widely interoperable, but FIPS 186-5 also specifies EdDSA; compliance depends on a validated implementation and applicable policy. WebAuthn support depends on negotiated algorithms and authenticators. Post-quantum signatures are covered later.

## Key takeaways
- Ed25519 signing is deterministic and needs no fresh random per-signature nonce.
- A modified message fails verification even when the original signature remains unchanged.
- Compare protocol support, validated implementations and actual encodings rather than key sizes alone.

## Further reading
- [EdDSA — RFC 8032](https://www.rfc-editor.org/rfc/rfc8032)
- [Ed25519 signing — pyca/cryptography docs](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/)
