---
id: crypto-public-key-transition
sourceLesson: crypto-asymmetric
title: Quantum risk and public-key implementation failures
level: intermediate
minutes: 3
summary: Large fault-tolerant quantum computers would threaten RSA and ECC through Shor’s algorithm.
---

## Quantum computers

Shor's algorithm, run on a large enough quantum computer, would factor numbers and solve discrete logs efficiently. That would break RSA and ECC alike. No publicly demonstrated cryptographically relevant machine is established by the sources used here; recorded ciphertext can nevertheless create a future decryption risk ("harvest now, decrypt later"). NIST standardised **ML-KEM** (FIPS 203) in 2024 as a post-quantum replacement for key establishment, and Google announced a transition to a hybrid with X25519 for Chrome 131 in September 2024. The applied cryptography module covers this.

## Pitfalls

- **Textbook RSA or PKCS #1 v1.5 encryption.** Use a specified encryption scheme such as RSA-OAEP or a suitable hybrid construction such as HPKE through a maintained library. Raw ECDH is a key-agreement component, not a complete encryption scheme.
- **Short keys.** RSA-1024 offers only about 80-bit classical strength and is unsuitable for new protection under the cited NIST guidance. This is not evidence of a demonstrated general 1,024-bit factorization.
- **Bad randomness in key generation.** In 2012, researchers scanning the internet found tens of thousands of RSA keys sharing a prime factor, because embedded devices generated keys with little entropy at boot. Anyone could factor them with a GCD.
- **Implementing curve arithmetic yourself.** Real ECC implementations must resist side channels and perform the validation required by the specific scheme; X25519 processing rules differ from conventional Weierstrass point validation. These are notoriously hard to get right.
- **Using the same key pair for encryption and signing.** Keep separate keys for separate purposes.

## Key takeaways
- Large fault-tolerant quantum computers would threaten RSA and ECC through Shor’s algorithm.
- Weak randomness, missing validation and key reuse can break otherwise sound public-key designs.

## Further reading
- [NIST FIPS 203: ML-KEM](https://csrc.nist.gov/pubs/fips/203/final)
- [Mining your Ps and Qs: original research](https://factorable.net/paper.html)
- [RFC 8017: RSA and OAEP](https://www.rfc-editor.org/rfc/rfc8017)

- [Google’s September 2024 announcement for Chrome 131](https://security.googleblog.com/2024/09/a-new-path-for-kyber-on-web.html)
