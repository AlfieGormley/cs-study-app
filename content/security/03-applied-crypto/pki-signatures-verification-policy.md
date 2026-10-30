---
id: pki-signatures-verification-policy
title: Using signatures safely in applications
level: basic
minutes: 3
sourceLesson: pki-signatures
summary: Use the exact signed bytes after verification, including in structured document handlers.
---

A signature check answers one narrow question: were these exact bytes signed by the private key matching this public key? Most real failures come from the code around that check.

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

> [!analogy] Real-world analogy: A pass that tells the guard how to check it
> Imagine a building pass with a printed note: "Holder of this pass needs no photo check." A guard who follows instructions printed on the pass itself will wave through anyone who prints that note on a home-made card.
>
> **How it maps:** A JWT's `alg` header is that printed note. A verifier that reads `alg` from the token lets the attacker choose `none`, or choose HMAC and use the published RSA public key as the shared secret. A guard with a fixed procedure for each kind of pass is a verifier configured with the allowed algorithm for each key.
>
> **Where it stops:** A guard can use judgement and spot an odd-looking pass. Software does exactly what the code says, so the protection must be an explicit allow-list in the verification call, not an expectation that bad tokens will look suspicious.

## Verifying a JWT safely

RFC 8725 (the JWT Best Current Practices) turns these failures into rules. A relying service should:

1. **Fix the algorithm per key.** The library must let the caller list the allowed algorithms and must reject anything else; each key is used with exactly one algorithm. `none` should never be accepted for a token that is meant to be signed.
2. **Choose the key from its own configuration**, not from the token. A `kid` header may select among keys you already trust, but must be validated before it is used in a lookup. Do not follow a `jku` or `x5u` URL from the token without an allow-list of locations; fetching arbitrary URLs invites server-side request forgery.
3. **Check the claims after the signature**: the issuer (`iss`) must own the verifying key, the audience (`aud`) must be this service, and the expiry (`exp`) must not have passed.
4. **Remember a signed token is readable.** A JWS payload is only encoded, so never put secrets in it.

## Key takeaways
- Use the exact signed bytes after verification, including in structured document handlers.
- Enforce the expected algorithm and trusted key, then check issuer, audience and expiry, instead of trusting token headers.
- Key identity, compromise timing and relying-party policy remain separate from signature mathematics.

## Further reading
- [RFC 8725: JSON Web Token Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725)
- [Critical vulnerabilities in JSON Web Token libraries — Auth0](https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/)
- [SAML Security Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/SAML_Security_Cheat_Sheet.html)
- [Digital signature — Wikipedia](https://en.wikipedia.org/wiki/Digital_signature)
