---
id: pki-key-management-access-and-recovery
title: Key access controls and recovery
level: intermediate
minutes: 2
sourceLesson: pki-key-management
summary: Least privilege, quorum and witnessed ceremonies constrain sensitive key operations.
---

Envelope encryption separates a locally used data encryption key (DEK) from the key encryption key (KEK) protecting it. Key custody and application authorisation remain essential.

## Controlling who can use keys

- **Least privilege**: configure policies so the order service may decrypt only its intended data/context and analysts may not. Administrative and cryptographic-use permissions can be separated; this is a policy design, not an automatic guarantee.
- **Dual control and quorum**: critical operations need several people. HSMs support M-of-N smart-card quorums, and backup keys are often split with Shamir's secret sharing.
- **Key ceremonies**: the DNSSEC root key is used in scripted, filmed ceremonies at two ICANN facilities. Trusted community members hold smart cards, and several of them must be present to activate the HSM.
- **Deletion safeguards**: AWS KMS enforces a waiting period of 7 to 30 days before deleting a key, because loss of the last usable decryption key makes its ciphertext unrecoverable. It does not physically delete ciphertext or copies of plaintext.

## Pitfalls

- **Secrets in source control.** Bots scan public commits continuously. Use secret scanning and pre-commit hooks, and rotate any key that was ever pushed, even after deleting the commit.
- **Logging plaintext keys** or decrypted data in debug output or crash dumps.
- **KMS as a single point of failure.** If every request decrypts a DEK through KMS, a regional outage or quota limit stops your service. Cache plaintext DEKs in memory for a short time, accepting longer plaintext-key residency, weaker per-read audit granularity and delayed revocation. Cached keys help only until they drop out of the cache or expire; newly needed keys still require KMS.
- **Lost keys mean lost data.** Keep KEKs durable and backed up within the HSM or KMS's own mechanisms; test recovery.
- **Encrypting with the KEK directly.** Calling KMS `Encrypt` on records works for small values, but adds latency to every operation and fails above the API's algorithm-specific payload limit (4,096 bytes for symmetric KMS encryption).
- **Forgetting the threat model.** Disk encryption protects a stolen drive. It does nothing against SQL injection, because the database decrypts for any query it is allowed to run.

## Key takeaways
- Least privilege, quorum and witnessed ceremonies constrain sensitive key operations.
- Short DEK caching can reduce repeated KMS calls but extends key exposure and delays revocation.
- Test durable key recovery and account for service outages, quotas, logs and plaintext copies.

## Further reading
- [AWS KMS cryptographic details](https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html)
- [NIST key-management guidance](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [AWS KMS concepts: envelope encryption — AWS docs](https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html)
- [Encryption at rest in Google Cloud](https://cloud.google.com/docs/security/encryption/default-encryption)
- [Hardware security module — Wikipedia](https://en.wikipedia.org/wiki/Hardware_security_module)
- [NIST SP 800-57 Part 1: Recommendation for Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [Root KSK Ceremonies — IANA](https://www.iana.org/dnssec/ceremonies)
- [Key Management Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet.html)
