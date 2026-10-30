---
id: pki-mistakes-pq-authenticated-modes
title: Patterns, CBC oracles and authenticated modes
level: advanced
minutes: 1
sourceLesson: pki-mistakes-pq
summary: ECB repeats ciphertext blocks for equal plaintext blocks under one key.
---

Encryption that hides data is not the same as encryption that stops tampering. Two older modes show the gap: ECB leaks patterns, and unauthenticated CBC lets an attacker probe the server.

## Mistake 2: encryption without authentication

ECB mode encrypts each block independently (16 bytes for AES, 8 for 3DES), so equal blocks give equal ciphertext. The famous "ECB penguin" image stays recognisable when encrypted. For password verification, deterministic encryption would reveal repeated values; store salted password hashes instead.

CBC hides patterns, but without a message authentication code an attacker can still flip bits, and if the server reveals whether padding was valid, the **padding oracle** attack (Vaudenay, 2002) decrypts whole messages one byte at a time. It broke ASP.NET in 2010, and the same family produced POODLE and Lucky 13 in TLS.

Fix: use an **AEAD** (AES-GCM, ChaCha20-Poly1305). If you must combine a cipher and a message authentication code yourself, encrypt-then-MAC, and verify the tag before decrypting or releasing plaintext.

## Key takeaways
- ECB repeats ciphertext blocks for equal plaintext blocks under one key.
- Unauthenticated CBC permits manipulation and padding-oracle leakage.
- Use a reviewed AEAD API that withholds unauthenticated plaintext.

## Further reading
- [Block cipher mode of operation — Wikipedia](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation)
- [Padding oracle attack — Wikipedia](https://en.wikipedia.org/wiki/Padding_oracle_attack)
