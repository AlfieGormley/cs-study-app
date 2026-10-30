---
id: crypto-x25519-derived-keys
sourceLesson: crypto-key-exchange
title: ECDH, X25519 and deriving separate traffic keys
level: advanced
minutes: 3
summary: ECDH combines scalar multiplication; X25519 has specific encoding and all-zero-secret rules.
---

## ECDH and X25519

**Elliptic-curve Diffie–Hellman (ECDH)** is the same protocol with points instead of numbers: exponentiation becomes scalar multiplication. Each side multiplies the generator point by its secret scalar and sends the resulting point; each then multiplies the other side's point by its own secret.

```formula reference
A = a × G, B = b × G
s = a × B = b × A = (a × b) × G
where
G: the public generator point fixed by the curve
a, b: Alice's and Bob's secret scalars
A, B: the public points they send
s: the shared point both compute
×: scalar multiplication: k × G means G added to itself k times with the curve's point-addition rule
In words: each side multiplies the other's public point by its own secret scalar, and both arrive at the generator multiplied by the product of the two secrets.
```

It is the finite-field exchange from the earlier units with the group swapped: the agreement works for the same reason, and an eavesdropper faces the elliptic-curve discrete logarithm problem instead of the finite-field one.

**X25519** (RFC 7748) uses Curve25519 with 32-byte public encodings and roughly 128-bit classical strength. Its arithmetic supports constant-time implementations and specifies handling of non-canonical encodings, but safe implementations still need side-channel care. A peer can send one of a few low-order points, and then the shared secret comes out as all zero bytes whatever your private key is: a value the attacker knows. RFC 7748 lets implementations check for this, and TLS 1.3 requires aborting the handshake if it happens. Python's `cryptography` library (checked with version 50) raises `ValueError` from `exchange` in that case. Treat that error as a failed handshake; never "recover" by carrying on with a default secret. Accepting 32 bytes as a valid encoding does not make the exchange authenticated.

```python
from cryptography.hazmat.primitives \
    .asymmetric import x25519
from cryptography.hazmat.primitives \
    .kdf.hkdf import HKDF
from cryptography.hazmat.primitives \
    import hashes

alice = x25519.X25519PrivateKey.generate()
bob = x25519.X25519PrivateKey.generate()

# swap public keys (32 bytes each)
# Each private key combines the peer share.
s1 = alice.exchange(bob.public_key())
s2 = bob.exchange(alice.public_key())
print(s1 == s2, len(s1))   # True 32

# Bind the derived key to a demo purpose.
# This step adds no peer authentication.
key = HKDF(algorithm=hashes.SHA256(),
           length=32, salt=None,
           info=b"demo v1 enc key"
          ).derive(s1)
```

This snippet demonstrates agreement and derivation only: it does not authenticate either peer and is not a deployable handshake.

Note the last step. The raw DH shared secret is not a uniformly random key, so you should never use it directly as an AES key. Pass it through a **key derivation function** such as HKDF (covered in its own unit shortly), ideally with the handshake transcript mixed in, to derive separate keys for each direction and purpose. TLS 1.3's key schedule does exactly this.

## Key takeaways
- ECDH combines scalar multiplication; X25519 has specific encoding and all-zero-secret rules.
- Derive direction-specific keys with a KDF; this example does not authenticate peers.

## Further reading
- [RFC 7748: X25519 and X448](https://www.rfc-editor.org/rfc/rfc7748)
- [RFC 5869: HKDF](https://www.rfc-editor.org/rfc/rfc5869)
- [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
