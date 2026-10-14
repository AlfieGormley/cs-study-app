---
id: rel-envelope-keys-rotation-erasure
title: Envelope keys, rotation and erasure
level: advanced
minutes: 3
summary: Keep bulk encryption local while controlling data-key use, rotation and destruction.
sourceLesson: rel-security
---

Storage encryption limits depend on who can use the keys. This unit separates a data encryption key (DEK), used locally for bulk bytes, from a key encryption key (KEK) that protects the DEK. AWS KMS product behaviour is scoped to the stated key type and mode, not every KMS service.

## Key management and envelope encryption

Encryption moves the problem to **key management**. A plaintext key accessible to the same attacker as its ciphertext provides little protection; an encrypted DEK can safely accompany the ciphertext when its wrapping key remains protected.

A **Key Management Service** controls key use through an authenticated API. AWS KMS provides HSM-backed key protection; Google Cloud KMS and Azure Key Vault also offer software-backed options. Select the required protection level explicitly and configure audit logging. The following envelope example uses AWS KMS-style data-key APIs.

AWS KMS’s symmetric Encrypt API accepts at most 4,096 plaintext bytes per call. Sending terabytes as hundreds of millions of tiny remote calls would also require a secure framing and nonce/key design. **Envelope encryption** solves this:

```
1. Ask KMS for a data key (DEK)
   ← plaintext DEK + DEK encrypted
     under the master key (KEK)
2. Encrypt data locally with DEK
   (AES-256-GCM, fast)
3. Store ciphertext + encrypted DEK
   + GCM nonce and authentication tag
4. Discard plaintext DEK from memory

Decrypt: send encrypted DEK to KMS
  → plaintext DEK → decrypt locally
```

For AES-GCM, never reuse a nonce with the same key and respect the implementation's per-key/message limits. Prefer a vetted encryption SDK and framed format for large objects.

Benefits:

- Bulk encryption happens locally and fast; KMS only handles tiny keys.
- The master key never leaves the HSM.
- Each KMS unwrap call is subject to access controls and audit logging. A cached plaintext DEK can decrypt many records locally without another KMS call, so KMS logs alone do not audit every data read.
- **Key rotation** need not rewrite bulk data. AWS KMS automatic rotation retains old key material for decrypting existing DEKs; moving to a different KEK may instead require re-wrapping DEKs.
- **Crypto-shredding**: destroy the relevant key material and every remaining plaintext or alternate-wrapped DEK, and ciphertext with no other recovery path becomes unreadable, which is useful for erasure requests and per-tenant keys.

AWS services including S3, EBS, RDS and DynamoDB offer KMS integrations; exact key handling and defaults depend on the service and selected encryption mode.

## Key takeaways

- Encrypt bulk data with a local data key, protect its wrapped copy and retain nonce/tag information.
- Select the KMS protection level; cached plaintext keys bypass per-read KMS audit.
- KMS automatic rotation retains decryptable old material. Erasure requires destroying every remaining recovery path and obeying provider deletion timing.

## Further reading

- [AWS KMS concepts](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html)
- [AWS Encryption SDK concepts: envelope encryption](https://docs.aws.amazon.com/encryption-sdk/latest/developer-guide/concepts.html)
- [AWS KMS Encrypt API](https://docs.aws.amazon.com/kms/latest/APIReference/API_Encrypt.html)
- [AWS KMS rotation](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html)
- [AWS KMS deletion](https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html)
