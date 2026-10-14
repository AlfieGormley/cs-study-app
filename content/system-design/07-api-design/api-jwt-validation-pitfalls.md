---
id: api-jwt-validation-pitfalls
title: JWT validation and storage pitfalls
level: advanced
minutes: 3
summary: Treat signed JWT claims as readable and pin algorithms, trusted keys and required claims.
sourceLesson: api-auth
---

## JWT in detail

A signed JWT in JWS compact form uses three base64url parts joined by dots. JWTs can also use encrypted JWE forms; this section covers the common signed form:

```
header.payload.signature

{"alg":"RS256","kid":"k1"}
.
{"sub":"user_42",
 "iss":"https://auth.example",
 "aud":"orders-api",
 "exp":1767225600,
 "scope":"orders:read"}
.
<RSA signature over the first two>
```

`exp` is the expiry time as a Unix timestamp, a count of seconds since 1 January 1970 UTC: 1767225600 is midnight UTC on 1 January 2026.

The payload is **encoded, not encrypted**. Anyone holding the token can read it. Never put secrets or sensitive personal data in it.

Signing choices:

- **HS256** (HMAC): one shared secret signs and verifies. Every verifier can also *forge* tokens.
- **RS256 / ES256** (asymmetric): the auth server signs with a private key; services verify with the public key, published at a JWKS endpoint. Verifiers can't mint tokens. Prefer this across services.

## JWT pitfalls

RFC 8725 (JWT Best Current Practices) exists because these mistakes keep happening:

1. **`alg: none`.** Early libraries accepted unsigned tokens if the header said `"alg": "none"`. Always pin the expected algorithm on the verifier; never trust the header.
1. **Algorithm confusion.** A server expects RS256 but the library honours the header's `HS256`, then verifies the HMAC using the RSA *public* key as the secret. The attacker, who knows the public key, can forge tokens.
1. **Not validating claims.** Validate the claims required by your token profile, including expiry, issuer and audience, and enforce `nbf` when present. A token issued for `billing-api` must not be accepted by `admin-api`.
1. **Trusting key hints in the header.** `kid`, `jku` and `x5u` tell the verifier which key to use, or where to fetch it. If the verifier fetches keys from whatever URL the token names, the attacker just points it at their own key. Only look `kid` up in your own allow-listed JWKS.
1. **Long lifetimes.** Since you can't easily revoke, keep access tokens short (typically 5–15 minutes) and use refresh tokens.
1. **Storage in the browser.** `localStorage` is readable by any script on the page, so one XSS bug leaks every token. An `HttpOnly` cookie can't be read by JavaScript (though you then need CSRF protection).
1. **Using a JWT as a session.** Stuffing roles into a 24-hour JWT means a demoted admin stays an admin for a day.

> [!tip] credential revocation strategies
> Short access-token lifetime plus a refresh token that *is* checked against a database on each refresh. For urgent credential revocation, keep a small deny-list of `jti` (token id) values until they expire. That's a lookup, but on a tiny, cacheable set.

## Key takeaways
- JWS compact tokens have three encoded parts; signatures provide integrity rather than secrecy.
- Pin accepted algorithms and bind trusted keys to them; never trust arbitrary key URLs.
- Validate the token profile’s issuer, audience, expiry and any not-before claim.
- Short lifetimes, refresh checks and appropriate browser storage reduce theft and stale roles.

## Further reading
- [RFC 7519: JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519)
- [RFC 8725: JWT Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725)
