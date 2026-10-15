---
id: pki-mistakes-pq-pq-standards
title: Post-quantum standards and wire sizes
level: advanced
minutes: 2
sourceLesson: pki-mistakes-pq
summary: ML-KEM, ML-DSA and SLH-DSA have different jobs and mathematical foundations.
---

Cryptographic security depends on the complete construction and its implementation, including key generation, message authentication and correct nonce handling.

## The new standards

NIST ran a public competition from 2016 and published the first standards in August 2024:

- **ML-KEM** (FIPS 203, from Kyber): a lattice-based key encapsulation mechanism for key exchange.
- **ML-DSA** (FIPS 204, from Dilithium): a general-purpose lattice-based signature standard.
- **SLH-DSA** (FIPS 205, from SPHINCS+): hash-based signatures, relying only on hash functions. This offers different mathematical assumptions from lattice schemes, with larger signatures and parameter-dependent performance.

A further lattice signature (FN-DSA, from Falcon) is being standardised, and in 2025 NIST picked **HQC**, a code-based KEM, as a backup to ML-KEM in case lattices fall. The competition showed why hedging matters: two leading candidates, the signature finalist Rainbow and the KEM SIKE, were broken in 2022, the SIKEp434 parameter set in about an hour on a single core in the original attack authors' reported implementation.

The big practical difference is size:

| Scheme | Public key | Ciphertext/sig |
|---|---|---|
| X25519 | 32 B | 32 B peer public share (not a ciphertext/signature) |
| ML-KEM-768 | 1,184 B | 1,088 B |
| Ed25519 | 32 B | 64 B |
| ML-DSA-44 | 1,312 B | 2,420 B |
| ML-DSA-65 | 1,952 B | 3,309 B |
| SLH-DSA-128s | 32 B | 7,856 B |

ML-KEM can be computationally efficient, but relative CPU cost depends on implementation, platform and operation. Key and ciphertext size are additional deployment costs, not the only ones.

## Key takeaways
- ML-KEM, ML-DSA and SLH-DSA have different jobs and mathematical foundations.
- HQC was selected for standardisation to diversify KEM assumptions.
- Wire sizes differ substantially; CPU costs still depend on implementation and platform.

## Further reading
- [Cryptographic storage guidance — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [NIST post-quantum project](https://csrc.nist.gov/projects/post-quantum-cryptography)
