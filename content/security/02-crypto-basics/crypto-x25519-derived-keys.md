---
id: crypto-x25519-derived-keys
sourceLesson: crypto-key-exchange
title: ECDH, X25519 and deriving separate traffic keys
level: advanced
minutes: 3
summary: ECDH combines scalar multiplication; X25519 has specific encoding and all-zero-secret rules.
---

## ECDH and X25519

**Elliptic-curve Diffie–Hellman (ECDH)** is the same protocol with points instead of numbers: exponentiation becomes scalar multiplication. Use the earlier toy curve: arithmetic modulo 17, coefficients 2 and 2, and generator (5, 1) of order 19:

```formula
A = a × G, B = b × G
s = a × B = b × A = (a × b) × G
A = 3 × G = (10, 6)
B = 7 × G = (0, 6)
s = 21 × G = 2 × G = (6, 3)
where
G: the public generator point, (5, 1), on the toy curve specified above
a, b: Alice's and Bob's secret scalars, 3 and 7
A, B: the public points they send
s: the shared point both compute
×: scalar multiplication: k × G means G added to itself k times with the curve's point-addition rule
In words: each side multiplies the other's public point by its own secret, and both arrive at (a × b) × G; since the toy group has 19 elements, 21 × G wraps round to 2 × G.
```


**X25519** (RFC 7748) uses Curve25519 with 32-byte public encodings and roughly 128-bit classical strength. Its arithmetic supports constant-time implementations and specifies handling of non-canonical encodings, but safe implementations still need side-channel care. Some inputs yield an all-zero DH shared secret. TLS 1.3 requires aborting in that case, and Python cryptography rejects a null shared key. Accepting bytes as an encoding does not guarantee a usable authenticated exchange.

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

Note the last step. The raw DH shared secret is not a uniformly random key, so you should never use it directly as an AES key. Pass it through a **key derivation function** such as HKDF (covered later in password hashing), ideally with the handshake transcript mixed in, to derive separate keys for each direction and purpose. TLS 1.3's key schedule does exactly this.

## Key takeaways
- ECDH combines scalar multiplication; X25519 has specific encoding and all-zero-secret rules.
- Derive direction-specific keys with a KDF; this example does not authenticate peers.

## Further reading
- [RFC 7748: X25519 and X448](https://www.rfc-editor.org/rfc/rfc7748)
- [RFC 5869: HKDF](https://www.rfc-editor.org/rfc/rfc5869)
- [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
