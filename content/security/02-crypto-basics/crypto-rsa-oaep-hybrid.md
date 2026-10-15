---
id: crypto-rsa-oaep-hybrid
sourceLesson: crypto-asymmetric
title: RSA-OAEP, message limits and hybrid encryption
level: intermediate
minutes: 4
summary: RSA-OAEP randomises message encoding and has a strict maximum input length.
---

The fix is **padding**: a randomised encoding applied to the message before exponentiation. The modern scheme is **OAEP** (Optimal Asymmetric Encryption Padding, in PKCS #1 v2). It mixes in fresh random bytes so repeated encryptions of one message normally differ. Its decoding checks reject invalid encodings; OAEP does not authenticate the sender, and random seeds can in principle repeat.

> [!warning] Avoid PKCS #1 v1.5 encryption
> The older v1.5 encryption padding is vulnerable to **Bleichenbacher's attack** (1998). If a server reveals whether decrypted padding was valid, an attacker can decrypt ciphertexts with many queries. It kept coming back: the ROBOT study in 2017 found major vendors' TLS stacks still vulnerable. TLS 1.3 removed RSA key transport entirely.

Here is RSA done properly with Python's `cryptography` library:

```python
from cryptography.hazmat.primitives \
    .asymmetric import rsa, padding
from cryptography.hazmat.primitives \
    import hashes

# Generate a fresh demonstration key pair.
priv = rsa.generate_private_key(
    public_exponent=65537,
    key_size=3072)
pub = priv.public_key()

# Use a specified randomised RSA encoding.
oaep = padding.OAEP(
    mgf=padding.MGF1(hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None)

ct = pub.encrypt(b"session key", oaep)
# One ciphertext occupies 384 bytes.
print(len(ct))
# The private key recovers the exact bytes.
print(priv.decrypt(ct, oaep))
```

This prints `384` (a 3,072-bit ciphertext is 384 bytes, however short the message) then `b'session key'`. Two runs produce different ciphertexts with overwhelming probability because OAEP uses a fresh random seed; equality is possible if the seed repeats. Implementations commonly use CRT acceleration and blinding as part of their defenses. Exact performance and side-channel behavior depend on the library and platform. OAEP encryption alone does not authenticate the sender: anyone with the public key can create a fresh valid ciphertext.

## Key sizes and performance

The classical RSA and ECC schemes below use larger key parameters than symmetric schemes for comparable estimated classical security. NIST SP 800-57 gives these rough equivalents:

| Security | Symmetric | RSA | ECC |
|---|---|---|---|
| 112-bit | 3-key TDEA (historical comparison, not new use) | 2048 | 224 |
| 128-bit | AES-128 | 3072 | 256 |
| 192-bit | AES-192 | 7680 | 384 |
| 256-bit | AES-256 | 15360 | 512+ |

NIST SP 800-57 Part 1 Rev. 5 maps RSA-2048 to about 112-bit classical strength and RSA-3072 to 128 bits, with at least 128 bits for applying protection from 2031. Algorithm suitability also depends on the protocol, policy and post-quantum transition; larger RSA is not quantum resistant.

OAEP's structure also caps the message size:

```formula
L_max = L_n − 2L_h − 2
L_max = 384 − 2 × 32 − 2 = 318 bytes
where
L_max: the longest message RSA-OAEP can encrypt in one operation, in bytes
L_n: the modulus length in bytes: 3,072 bits / 8 = 384
L_h: the hash output length in bytes: 32 for SHA-256
2 × L_h: room for OAEP's random seed and the hash of its label, one hash length each
2: one leading 0x00 byte and one 0x01 byte that marks where the message starts
bytes: the unit of data, 8 bits each
In words: a 3,072-bit RSA-OAEP key with SHA-256 can carry at most 318 bytes, which is plenty for a 32-byte symmetric key but useless for a file.
```

So RSA-OAEP with a 3,072-bit modulus and SHA-256 allows at most 318 message bytes per encryption. Bulk data is therefore usually handled with symmetric encryption. Instead, systems use **hybrid encryption**:

```
1. Generate random AES key K
2. Encrypt data with AES-GCM under K
3. Encrypt (wrap) K with recipient's
   public key
4. Send wrapped K + ciphertext
```

This is one hybrid design. HPKE instead combines a key-encapsulation mechanism, key derivation and AEAD. Key size and wrapping method vary; cloud envelope encryption may use a symmetric wrapping key rather than a public-key operation.

## Key takeaways
- RSA-OAEP randomises message encoding and has a strict maximum input length.
- Hybrid schemes use public-key establishment with symmetric authenticated encryption for bulk data.

## Further reading
- [RFC 8017: RSA and OAEP](https://www.rfc-editor.org/rfc/rfc8017)
- [Python cryptography: RSA API](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/)
- [NIST SP 800-57: key strength estimates](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
