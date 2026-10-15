---
id: pki-signatures-verification-policy
title: Using signatures safely in applications
level: basic
minutes: 2
sourceLesson: pki-signatures
summary: Use the exact signed bytes after verification, including in structured document handlers.
---

A signature verifier checks a message and signature against a trusted public key. The preceding units separated that verification authority from private-key signing authority.

## Where signatures are used

- **TLS**: a CA signs the server's certificate, and the server signs the handshake (in the certificate and TLS units).
- **Software updates and packages**: apt, Windows Authenticode, Apple code signing, Android APKs, and Sigstore for open-source artefacts.
- **Git**: signed commits and tags, with GPG or SSH keys.
- **Tokens**: JWTs signed with RS256, ES256 or EdDSA, so any service can verify without the issuer's secret.
- **Email**: DKIM validates selected headers and body content against a signing domain's key. The signing domain need not match the visible From address; DMARC alignment is a separate check.
- **Passkeys**: WebAuthn assertions sign authenticator data plus a client-data hash that binds the challenge and origin. Some passkeys synchronize between devices; device-bound and backed-up credentials have different custody models.

## Pitfalls

- **Check what was actually signed.** XML Signature "wrapping" attacks moved the signed element and inserted an unsigned one that the application then read. Sign canonical bytes, and act only on the bytes you verified.
- **Do not let the message choose the algorithm.** Early JWT libraries trusted the token's `alg` header, so `alg: none` or switching RS256 to HS256 (using the public key as an HMAC secret) bypassed verification. Pin the expected algorithm.
- **A signature proves the key, not the person.** Binding a public key to an identity is a separate problem, solved by certificates.
- **Compromised keys can create new forgeries.** Trusted timestamps or other reliable prior records can help distinguish older signatures. Whether an old artifact remains acceptable depends on the earliest plausible compromise, trust-chain validation and policy, not a universal timestamp rule.

## Key takeaways
- Use the exact signed bytes after verification, including in structured document handlers.
- Enforce the expected algorithm and trusted key instead of accepting attacker-chosen JWT algorithms.
- Key identity, compromise timing and relying-party policy remain separate from signature mathematics.

## Further reading
- [RSA signature schemes — RFC 8017](https://www.rfc-editor.org/rfc/rfc8017)
- [EdDSA — RFC 8032](https://www.rfc-editor.org/rfc/rfc8032)
- [Deterministic ECDSA — RFC 6979](https://www.rfc-editor.org/rfc/rfc6979)
- [Digital signature — Wikipedia](https://en.wikipedia.org/wiki/Digital_signature)
- [RFC 8032: Edwards-Curve Digital Signature Algorithm (EdDSA)](https://www.rfc-editor.org/rfc/rfc8032)
- [RFC 6979: Deterministic Usage of DSA and ECDSA](https://www.rfc-editor.org/rfc/rfc6979)
- [Ed25519 signing — pyca/cryptography docs](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/)
- [Critical vulnerabilities in JSON Web Token libraries — Auth0](https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/)
