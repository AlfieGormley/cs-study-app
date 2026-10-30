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

> [!analogy] Real-world analogy: The key under the doormat
> A strong front door with an excellent lock is no protection if the key sits under the doormat. A burglar does not pick the lock; they lift the mat.
>
> **How it maps:** AES-256 is the excellent lock and the encrypted database is the house. Storing the key in a config file beside the data, in source code, or in the same backup is the doormat: anyone who gets the data store gets the key with it, and the strength of the cipher no longer matters.
>
> **Where it stops:** A house key is a physical object that can be in only one place. A digital key can be copied silently, any number of times, without the owner noticing, so you cannot tell that it has gone; that is why exposed keys must be treated as compromised and replaced.

## The key lifecycle

A typical key lifecycle includes these stages, and each one has its own failure modes:

1. **Generate** from a cryptographically secure RNG, ideally inside the device that will use it.
2. **Store** with controls against unauthorised copying: never in source code, never in a config file next to the data.
3. **Distribute** only to the systems that need it, over authenticated channels.
4. **Use** for one purpose only, with access control and an audit trail.
5. **Rotate** on a schedule and after any suspected compromise.
6. **Revoke and destroy** when it is no longer needed, including in backups.

> [!tip] One key, one job
> NIST SP 800-57 says that, in general, a single key should be used for only one purpose: encryption, integrity authentication, key wrapping, random bit generation or digital signatures. Using one key for two processes can weaken one or both, and it widens the damage if the key leaks. An RSA key used for both decryption and signing is a classic case: the ROBOT researchers showed that a padding oracle in a TLS server's RSA decryption also lets an attacker create signatures with that server's private key. If you must start from one secret, derive separate keys with a KDF and a different label for each purpose.

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
- [NIST SP 800-57 Part 1: Recommendation for Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [Key Management Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet.html)
