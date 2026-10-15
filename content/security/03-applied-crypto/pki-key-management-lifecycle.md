---
id: pki-key-management-lifecycle
title: Key lifecycle and storage boundaries
level: intermediate
minutes: 3
sourceLesson: pki-key-management
summary: Encryption concentrates protection into the keys and their authorised use.
---

Encryption does not make a secret go away. It turns a big secret (a database, a disk, a backup) into a small one: the key. Whoever gets the key gets everything, so the security of the whole system now rests on where that key lives, who can use it, and what happens when it leaks or is lost.

Key handling is a major source of encryption failures, alongside implementation errors and protocol misuse. Publicly exposed credentials must be treated as compromised.

> [!note] Content gap
> A percentage of failures attributed to key management, a universal time until leaked credentials are discovered and generic HSM throughput figures are omitted because no supporting measurement dataset was available.

## The key lifecycle

A typical key lifecycle includes these stages, and each one has its own failure modes:

1. **Generate** from a cryptographically secure RNG, ideally inside the device that will use it.
2. **Store** with controls against unauthorised copying: never in source code, never in a config file next to the data.
3. **Distribute** only to the systems that need it, over authenticated channels.
4. **Use** for one purpose only, with access control and an audit trail.
5. **Rotate** on a schedule and after any suspected compromise.
6. **Revoke and destroy** when it is no longer needed, including in backups.

> [!tip] One key, one job
> Never use the same key for encryption and signing, or for two different applications. If one use leaks the key, or interacts badly with another (for example, an RSA key used for both decryption and signatures), both are compromised. Derive separate keys with a KDF if you must start from one secret.

## Where keys can live

| Location | Key extractable? | Typical use |
|---|---|---|
| Source code / env var | Readable by sufficiently privileged code | Avoid committed secrets; runtime injection still exposes the process |
| Secrets manager | Yes, by the app | API tokens, DB passwords |
| Cloud KMS | Usually not exported through normal key APIs; origin/protection level matters | Wrapping data keys |
| HSM | Depends on key attributes and export policy | CA roots, payment keys |

A **secrets manager** (HashiCorp Vault, AWS Secrets Manager) stores secrets encrypted and hands them to authorised workloads at runtime. That beats a config file, but the application ends up holding the plaintext secret in memory.

Hardware isolation can strengthen key custody; a software service can also hide key material from ordinary calling applications, with a different trusted boundary.

## Key takeaways
- Encryption concentrates protection into the keys and their authorised use.
- Generate, store, distribute, use, rotate and finally retire keys under explicit controls.
- A secrets manager delivers plaintext secrets to authorised processes; storage controls do not defeat a compromised authorised caller.

## Further reading
- [AWS KMS cryptographic details](https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html)
- [NIST key-management guidance](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
