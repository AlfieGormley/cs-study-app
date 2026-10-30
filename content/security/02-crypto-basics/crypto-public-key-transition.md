---
id: crypto-public-key-transition
sourceLesson: crypto-asymmetric
title: Quantum risk and public-key implementation failures
level: intermediate
minutes: 3
summary: Large fault-tolerant quantum computers would threaten RSA and ECC through Shor’s algorithm.
---

## Quantum computers

Shor's algorithm, run on a large enough fault-tolerant quantum computer, would factor numbers and solve discrete logarithms efficiently. That would break RSA, finite-field Diffie–Hellman and elliptic-curve schemes alike, at any practical key size. No cryptographically relevant quantum computer has been publicly demonstrated as of this writing (October 2026), and nobody can give a reliable arrival date. The risk is still current for two reasons:

- **Harvest now, decrypt later.** An attacker can record encrypted traffic today and decrypt it if such a machine arrives. Data that must stay secret for many years is exposed now.
- **Migrations are slow.** Replacing algorithms across protocols, hardware and long-lived devices has historically taken a decade or more.

The status, with dates because it is changing:

- **August 2024:** NIST published the first post-quantum standards: **ML-KEM** (FIPS 203) for key establishment, and **ML-DSA** (FIPS 204) and **SLH-DSA** (FIPS 205) for signatures. NIST has also selected HQC as a backup key-establishment scheme; its standard was still being written at the time of NIST IR 8547.
- **Late 2024 onwards:** browsers and CDNs deployed **hybrid** key exchange combining X25519 with ML-KEM-768 (Google announced the switch for Chrome 131 in September 2024), so a session stays secret if either component holds.
- **October 2026:** NIST IR 8547 says NIST will deprecate quantum-vulnerable public-key algorithms (RSA, ECDSA, EdDSA, finite-field and elliptic-curve Diffie–Hellman) after 2030 and disallow them under its standards after 2035, with earlier deadlines for the most sensitive US federal systems.

Symmetric cryptography is affected far less: Grover's algorithm at most square-roots a brute-force search, so AES-256 and SHA-256-class hashes keep a large margin. The applied cryptography module covers post-quantum deployment in more depth.

## Pitfalls

- **Textbook RSA or PKCS #1 v1.5 encryption.** Use a specified encryption scheme such as RSA-OAEP or a suitable hybrid construction such as HPKE through a maintained library. Raw ECDH is a key-agreement component, not a complete encryption scheme.
- **Short keys.** RSA-1024 offers only about 80-bit classical strength and is unsuitable for new protection under the cited NIST guidance. This is not evidence of a demonstrated general 1,024-bit factorisation.
- **Bad randomness in key generation.** In 2012, researchers scanning the internet found more than 16,000 distinct RSA public keys that shared a prime factor with another key, exposing the private keys of about 64,000 TLS hosts, because embedded devices generated keys with little entropy at boot. Anyone could factor them with a GCD.
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
- [NIST IR 8547: transition to post-quantum standards](https://csrc.nist.gov/pubs/ir/8547/final)
