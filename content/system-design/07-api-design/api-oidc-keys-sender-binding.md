---
id: api-oidc-keys-sender-binding
title: Identity tokens, API keys and sender binding
level: advanced
minutes: 3
summary: Use OIDC identity and API credentials for their intended audiences, with rotatable or sender-bound credentials.
sourceLesson: api-auth
---

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

## Key takeaways
- An OIDC ID token is for the client; use the API’s access credential when calling an API.
- API keys need clear prefixes, hashed storage, scopes and overlapping rotation.
- mTLS authenticates both transport peers and can bind access tokens to certificates.
- DPoP provides application-layer sender constraints where appropriate.

## Further reading
- [OpenID Foundation: How OpenID Connect works](https://openid.net/developers/how-connect-works/)
- [RFC 8705: OAuth 2.0 Mutual-TLS client authentication](https://www.rfc-editor.org/rfc/rfc8705)
- [RFC 9449: DPoP](https://www.rfc-editor.org/rfc/rfc9449)
