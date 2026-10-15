---
id: pki-key-management-envelope-mechanics
title: Envelope encryption and context binding
level: intermediate
minutes: 3
sourceLesson: pki-key-management
summary: A local DEK encrypts bulk data while a KEK wraps the small DEK.
---

Envelope encryption separates a locally used data encryption key (DEK) from the key encryption key (KEK) protecting it. Key custody and application authorisation remain essential.

## Envelope encryption

Use two layers of keys:

- A **data encryption key** (DEK): a fresh random AES key per object, file or record, used locally to encrypt the data.
- A **key encryption key** (KEK): a long-lived key inside the KMS or HSM, used only to encrypt ("wrap") DEKs.

```
       KMS / HSM
     +-----------+
     |   KEK     |  protected key
     +-----------+
        | wrap / unwrap (32 bytes)
        v
  wrapped DEK  +  data encrypted
  (stored)        locally with DEK
```

To write: ask the KMS for a new data key. It returns the DEK in plaintext *and* wrapped under the KEK. Encrypt the data locally, store the wrapped DEK beside the ciphertext, and minimise the plaintext DEK's lifetime. Reliable erasure is runtime-dependent; the Python illustration below does not securely erase immutable byte objects.

To read: send the wrapped DEK (whose encoded size depends on the service) to the KMS, get the plaintext DEK back if policy allows, and decrypt locally.

Here is the whole idea, with a local AES key standing in for the KMS:

```python
import os
from cryptography.hazmat.primitives \
    .ciphers.aead import AESGCM
from cryptography.exceptions import \
    InvalidTag

# stands in for a KMS key; a real one
# stays inside its configured boundary
KEK = AESGCM(AESGCM.generate_key(256))

def seal(data, ctx):
    # New data key limits each object’s
    # scope.
    dek = AESGCM.generate_key(256)
    # Nonces serve different encryption
    # keys.
    n1, n2 = os.urandom(12), os.urandom(12)
    ct = AESGCM(dek).encrypt(n1, data, ctx)
    # Persist wrap nonce beside protected
    # DEK.
    wrapped = n2 + KEK.encrypt(n2, dek, ctx)
    return wrapped, n1 + ct

def unseal(wrapped, blob, ctx):
    # Split stored nonce from wrapped
    # key/tag.
    dek = KEK.decrypt(wrapped[:12],
                      wrapped[12:], ctx)
    return AESGCM(dek).decrypt(
        blob[:12], blob[12:], ctx)

w, b = seal(b"card 4242", b"user=42")
print(len(w), len(b))
print(unseal(w, b, b"user=42"))
try:
    unseal(w, b, b"user=99")
except InvalidTag:
    print("wrong context")
```

This prints `60 37`, then `b'card 4242'`, then `wrong context`. The sizes come from AES-GCM's fixed overhead: its ciphertext is exactly as long as the plaintext, and `seal()` adds a nonce in front and GCM adds a tag at the end:

```formula
L_out = L_nonce + L_in + L_tag
L_wrap = 12 + 32 + 16 = 60 B
L_blob = 12 + 9 + 16 = 37 B
where
L_out: the length of one value stored by seal(), in bytes (B)
L_nonce: the random nonce stored in front, 12 B (96 bits, the size GCM is designed for)
L_in: the length of the plaintext encrypted: the 32-byte DEK, or the 9-byte record "card 4242"
L_tag: the GCM authentication tag, 16 B
L_wrap: the wrapped DEK
L_blob: the encrypted record
B: bytes
In words: every value sealed this way costs 28 bytes more than its plaintext: 12 for the nonce and 16 for the tag.
```

The context (`user=42`) is AEAD associated data: it is not secret, but decryption fails if it differs, so a ciphertext copied into another user's row will not decrypt when the application derives the expected context from trusted identity/row information. AWS KMS calls this the **encryption context**, and it can appear in CloudTrail events, so it should never contain secret data.

With the real service, the first two lines of `seal` become one call:

```python
# Illustrative call: kms is a client
# configured with AWS access and policy.
r = kms.generate_data_key(
    KeyId="alias/orders",
    KeySpec="AES_256",
    EncryptionContext={"user": "42"})
dek = r["Plaintext"]
wrapped = r["CiphertextBlob"]
```

## Key takeaways
- A local DEK encrypts bulk data while a KEK wraps the small DEK.
- Authenticated context binds the ciphertext to trusted application identity information.
- The local illustration adds a 12-byte nonce and 16-byte tag, and does not promise secure Python-memory erasure.

## Further reading
- [AWS KMS cryptographic details](https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html)
- [NIST key-management guidance](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
