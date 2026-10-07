---
id: api-auth
title: Authentication and authorisation
level: advanced
minutes: 18
summary: Sessions vs tokens, JWTs and their pitfalls, OAuth 2.0 and OpenID Connect flows, API keys, mTLS, and RBAC vs ABAC.
---

Two questions sit in front of every API call:

- **Authentication (authn)**: *who* is calling?
- **Authorisation (authz)**: *are they allowed* to do this?

They're separate concerns and often separate systems. A valid identity tells you nothing about permissions. Mixing them up is behind a large share of real-world API breaches; "broken object level authorisation" (checking that the user is logged in, but not that the invoice is *theirs*) tops the OWASP API Security Top 10.

## Sessions vs tokens

### Server-side sessions

The classic web approach. After login, the server creates a session record and gives the browser an opaque, random session id in a cookie.

```
Set-Cookie: sid=9f8c...; HttpOnly;
  Secure; SameSite=Lax; Path=/
```

On each request the server looks up `sid` in a shared store (Redis, a database) to find the user.

- **Revocation is instant**: delete that session record and subsequent validated requests using that session are rejected. Other device sessions require separate revocation, and cached sessions can delay enforcement.
- **The cookie reveals nothing**: it's just a random pointer.
- **Cost**: a store lookup per request, and the store must be shared across servers (to stay stateless at the app tier).

### Self-contained tokens

The token *itself* carries the claims, signed so the server can verify it without a lookup. JWT is the common format.

- **No lookup**: any service with the public key can verify it. Great for microservices.
- **Hard to revoke**: without additional revocation enforcement, a stolen token remains usable until expiry.

| | Session id | JWT |
|---|---|---|
| Verify | Store lookup | Signature check |
| Revoke | On next authoritative session validation; caches affect delay | Expiry or added revocation/status mechanism |
| Size | Chosen random identifier plus encoding overhead | Depends on claims, signature algorithm and encoding |
| Cross-service | Needs shared store | Just a public key |

Neither is universally better. Many systems use **both**: an opaque session cookie at the edge for browsers, translated by the gateway into a short-lived internal JWT for service-to-service calls.

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

The payload is **encoded, not encrypted**. Anyone holding the token can read it. Never put secrets or sensitive personal data in it.

Signing choices:

- **HS256** (HMAC): one shared secret signs and verifies. Every verifier can also *forge* tokens.
- **RS256 / ES256** (asymmetric): the auth server signs with a private key; services verify with the public key, published at a JWKS endpoint. Verifiers can't mint tokens. Prefer this across services.

### JWT pitfalls

RFC 8725 (JWT Best Current Practices) exists because these mistakes keep happening:

1. **`alg: none`.** Early libraries accepted unsigned tokens if the header said `"alg": "none"`. Always pin the expected algorithm on the verifier; never trust the header.
1. **Algorithm confusion.** A server expects RS256 but the library honours the header's `HS256`, then verifies the HMAC using the RSA *public* key as the secret. The attacker, who knows the public key, can forge tokens.
1. **Not validating claims.** Validate the claims required by your token profile, including expiry, issuer and audience, and enforce `nbf` when present. A token issued for `billing-api` must not be accepted by `admin-api`.
1. **Trusting key hints in the header.** `kid`, `jku` and `x5u` tell the verifier which key to use, or where to fetch it. If the verifier fetches keys from whatever URL the token names, the attacker just points it at their own key. Only look `kid` up in your own allow-listed JWKS.
1. **Long lifetimes.** Since you can't easily revoke, keep access tokens short (typically 5–15 minutes) and use refresh tokens.
1. **Storage in the browser.** `localStorage` is readable by any script on the page, so one XSS bug leaks every token. An `HttpOnly` cookie can't be read by JavaScript (though you then need CSRF protection).
1. **Using a JWT as a session.** Stuffing roles into a 24-hour JWT means a demoted admin stays an admin for a day.

> [!tip] Revocation strategies
> Short access-token lifetime plus a refresh token that *is* checked against a database on each refresh. For urgent revocation, keep a small deny-list of `jti` (token id) values until they expire. That's a lookup, but on a tiny, cacheable set.

## OAuth 2.0

OAuth 2.0 (RFC 6749) is a **delegated authorisation** framework. It answers: "how can an app access a user's data on another service *without* being given the user's password?"

Four roles:

| Role | Example |
|---|---|
| Resource owner | You |
| Client | A budgeting app |
| Authorisation server | Google's login |
| Resource server | Gmail API |

The output is an **access token** with limited **scopes** (`gmail.readonly`), which the client sends as `Authorization: Bearer <token>`.

### Authorisation code flow with PKCE

The recommended flow for any app with a user: web, mobile, single-page apps.

```
User  Client       Auth server   API
 |-tap->|               |          |
 |      | make verifier v          |
 |      | c = S256(v)              |
 |<-redirect /authorize?c--|       |
 |------ login + consent ->|       |
 |<-redirect ?code=xyz-----|       |
 |--code->|                |       |
 |        |-code + v------>|       |
 |        |  check S256(v)==c      |
 |        |<-access+refresh|       |
 |        |-Bearer token---------->|
```

Why the extra steps?

- The **code** travels via the browser (redirect URL), where it might leak: browser history, logs, a malicious app registered for the same URL scheme on mobile.
- The code alone is useless. Exchanging it needs the **code verifier** `v`, a high-entropy random string sent only to the authorization server’s token endpoint, not in the front-channel authorization request. **PKCE** (RFC 7636, "pixy") binds the code to the client that started the flow. The challenge is `c = BASE64URL(SHA256(v))`, the `S256` method; the `plain` method (sending `v` itself as the challenge) gives up most of the protection and shouldn't be used.
- PKCE also stops **code injection**: an attacker who slips a stolen code into a victim's session can't redeem it, because the victim's client holds a different verifier.
- Tokens return from the token endpoint, not in the redirect URL. A browser-based public client still receives them in its browser process; a BFF can keep them server-side.

### Other grants

- **Client credentials**: machine-to-machine, no user. A backend service exchanges its client id and secret for a token.
- **Device code**: TVs and CLIs with no browser. The device shows a code; you approve on your phone.
- **Refresh token**: exchange a long-lived refresh token for a new access token. Use **rotation**: each refresh issues a new refresh token and invalidates the old one, so reuse of a stolen one is detectable.

> [!warning] Deprecated grants
> The **implicit** grant (access token returned directly in the URL fragment, where it is exposed to browser history and page scripts; fragments are not sent in ordinary HTTP Referer headers) and the **password** grant (client collects the user's password) are out. The OAuth 2.0 Security Best Current Practice, published as RFC 9700 in January 2025, says the implicit grant should not be used and the password grant must not be. OAuth 2.1 (still an IETF draft, consolidating these rules) drops both grants entirely. Use authorisation code + PKCE instead, including for single-page apps.

### PKCE for every client

PKCE was first designed for *public* clients (mobile and single-page apps) that can't keep a client secret. It turned out to protect confidential clients too, against code injection, which a client secret doesn't prevent.

- **RFC 9700**: PKCE is required for public clients and recommended for confidential ones.
- **OAuth 2.1**: PKCE is required for every client using the authorisation code flow, with only a narrow exception for confidential OpenID Connect clients that use the `nonce` parameter correctly. It also bans the `plain` method and requires exact redirect-URI matching, except for the allowed variable port in native-app loopback redirects.

In practice: use PKCE with `S256` everywhere, and configure your authorisation server to reject code requests without it.

## OpenID Connect

OAuth 2.0 is about *authorisation*. It doesn't define how the client learns *who the user is*. OpenID Connect (OIDC) adds an identity layer:

- Request `scope=openid profile email`.
- The token response includes an **ID token**: a JWT with required identity/security claims including `sub`, intended for the *client*. Claims such as `email` and `name` depend on requested scopes, consent and provider behavior and are not guaranteed to be present.
- A standardized UserInfo protocol and discovery document (`/.well-known/openid-configuration`); the UserInfo URL is provider metadata, not a mandatory literal `/userinfo` path.

The distinction matters:

| Token | Audience | Purpose |
|---|---|---|
| ID token | The client app | Who logged in |
| Access token | The API | What it may access |

Never send an ID token to an API as a bearer credential. "Sign in with Google/Apple/Microsoft" is OIDC.

## API keys

For server-to-server integrations, a long random **API key** is simple and common (Stripe's `sk_live_...`, for example).

Good practice:

- **Prefix keys** (`sk_live_`, `sk_test_`) so leaked keys are recognisable, and so secret-scanning tools (GitHub has this) can detect them in public code.
- **Store only a hash** (like passwords), and show the full key once at creation.
- **Scope them** (read-only, specific resources) and allow multiple keys per account so they can be **rotated** without downtime.
- API keys commonly identify a *project or account*; some systems also associate them with users, and are usually long-lived. Never ship a secret key inside a mobile app or browser bundle.

## Mutual TLS (mTLS)

Normal TLS authenticates the server to the client. **mTLS** also makes the client present a certificate, so both sides prove identity at the transport layer.

- Common for **service-to-service** traffic inside a service mesh. Istio and Linkerd issue each workload a short-lived certificate automatically; Istio's identities follow the SPIFFE standard.
- Used by **open banking** and payments partners, in profiles that require certificate-based client authentication.
- RFC 8705 defines **certificate-bound access tokens**: the token is tied to the client's cert, so a stolen token is useless without the private key.
- Where mTLS isn't practical, such as in browsers, **DPoP** (RFC 9449) achieves similar *sender-constraining* at the application layer: the client signs a small proof with its own key on every request.

The main cost is certificate issuance and rotation, which is why meshes automate it.

## Authorisation models

Once you know who the caller is, decide what they can do.

### RBAC: role-based

Users get **roles**; roles have **permissions**.

```
alice -> [editor]
editor -> posts:read, posts:write
viewer -> posts:read
```

Simple, auditable and good enough for most internal tools. It strains when permissions depend on context: "editors can edit posts *in their own department*, *during business hours*". Teams end up with role explosion: `editor-uk`, `editor-uk-weekend`...

### ABAC: attribute-based

Decisions are policies over **attributes** of the user, the resource, the action and the environment:

```
allow if
  user.dept == resource.dept
  and action == "edit"
  and resource.status != "locked"
```

More expressive, but harder to audit ("who can see this document?" requires evaluating policies). Tools such as Open Policy Agent (Rego) and AWS IAM policies are ABAC-style.

### ReBAC: relationship-based

Permissions follow relationships in a graph: "you can view this doc because you're in a group that has access to the folder that contains it". Google's **Zanzibar** (behind Drive, YouTube, Calendar) is the canonical example; OpenFGA and SpiceDB are open-source implementations.

| Model | Best for |
|---|---|
| RBAC | Simple apps, admin tools |
| ABAC | Context-dependent rules |
| ReBAC | Sharing, hierarchies |

Whatever the model, **enforce authorisation on the server for every object**, not just at login, and not just by hiding buttons in the UI.

## Key takeaways
- **Authentication** establishes identity; **authorisation** decides access. Check both, on every request, for every object.
- **Sessions** revoke on authoritative validation (subject to caches) and need a lookup; **JWTs** verify locally but are hard to revoke. Keep JWTs **short-lived**.
- JWT payloads are **readable**. Pin the algorithm, validate `exp`/`iss`/`aud`, prefer asymmetric signing, and avoid `localStorage`.
- **OAuth 2.0** delegates access via scoped tokens. Use **authorisation code + PKCE (S256)** for every client with a user, and **client credentials** for machines. Implicit and password grants are deprecated by RFC 9700 and removed in OAuth 2.1.
- **OIDC** adds identity with an **ID token** for the client; the **access token** is for the API.
- **API keys**: prefixed, hashed, scoped, rotatable. **mTLS** authenticates both ends and can bind tokens to certificates.
- **RBAC** is simple, **ABAC** is expressive, **ReBAC** models sharing.

## Further reading
- [OAuth 2.0 overview (oauth.net)](https://oauth.net/2/)
- [oauth.net: PKCE](https://oauth.net/2/pkce/)
- [OpenID Foundation: How OpenID Connect works](https://openid.net/developers/how-connect-works/)
- [RFC 7519: JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519)
- [RFC 8725: JWT Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725)
- [RFC 9700: OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700)
- [oauth.net: OAuth 2.1](https://oauth.net/2.1/)
- [OWASP: Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [RFC 8705: OAuth 2.0 Mutual-TLS client authentication](https://www.rfc-editor.org/rfc/rfc8705)
- [OWASP API Security Top 10: Broken object level authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)
- [Google Research: Zanzibar](https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/)
- [NIST: Attribute based access control](https://csrc.nist.gov/projects/attribute-based-access-control)
