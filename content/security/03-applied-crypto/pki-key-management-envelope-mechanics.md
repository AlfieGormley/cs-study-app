---
id: pki-key-management-envelope-mechanics
title: Envelope encryption and context binding
level: intermediate
minutes: 4
sourceLesson: pki-key-management
summary: A local DEK encrypts bulk data while a KEK wraps the small DEK.
---

A KMS or HSM keeps its keys safe but accepts only small requests, and every call crosses a network. Envelope encryption lets you encrypt gigabytes locally while the protected master key never leaves the KMS.

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

> [!analogy] Real-world analogy: A key safe at a holiday cottage
> The cottage key is left in a small combination key safe by the door. Guests are given the code, open the safe, take the key and let themselves in. Changing the combination does not require changing the cottage's locks.
>
> **How it maps:** The cottage key is the DEK, which opens the bulk data. The key safe is the wrapping: the DEK is stored only in wrapped form, beside the data. The combination is held by the KMS, which opens the "safe" (unwraps the DEK) only for callers its policy allows. Re-wrapping a DEK under a new KEK is like changing the combination.
>
> **Where it stops:** A guest could copy the cottage key and keep it. Likewise a plaintext DEK, once unwrapped, can be copied or cached by the application, and changing the KEK does nothing about copies already taken. Unlike a key safe, each object gets its own DEK, so one copied key opens one object rather than the whole estate.

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

This prints `60 37`, then `b'card 4242'`, then `wrong context`. The sizes come from AES-GCM's fixed overhead: its ciphertext is exactly as long as the plaintext, `seal()` stores the 12-byte nonce in front and GCM adds a 16-byte tag at the end. So the wrapped 32-byte DEK takes 60 bytes and the 9-byte record takes 37: every sealed value costs 28 bytes more than its plaintext. A real KMS wrapped key is larger, because it also carries key metadata.

The context (`user=42`) is AEAD associated data: it is not secret, but decryption fails if it differs, so a ciphertext copied into another user's row will not decrypt when the application derives the expected context from trusted identity/row information. AWS KMS calls this the **encryption context**, and it can appear in CloudTrail events, so it should never contain secret data.

With the real service, generating and wrapping the DEK become one call:

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
- [Encryption context — AWS KMS docs](https://docs.aws.amazon.com/kms/latest/developerguide/encrypt_context.html)
