---
id: api-session-token-revocation
title: Sessions, tokens and credential revocation
level: advanced
minutes: 3
summary: Separate identity from permission and compare authoritative session lookups with self-contained tokens.
sourceLesson: api-auth
---

Two questions sit in front of every API call:

- **Authentication (authn)**: *who* is calling?
- **Authorisation (authz)**: *are they allowed* to do this?

They're separate concerns and often separate systems. A valid identity tells you nothing about permissions. Mixing them up is behind a large share of real-world API breaches; "broken object level authorisation" (checking that the user is logged in, but not that the invoice is *theirs*) tops the OWASP API Security Top 10.

## Sessions vs tokens

## Server-side sessions

The classic web approach. After login, the server creates a session record and gives the browser an opaque, random session id in a cookie.

```http
Set-Cookie: sid=9f8c...; HttpOnly;
  Secure; SameSite=Lax; Path=/
```

On each request the server looks up `sid` in a shared store (Redis, a database) to find the user.

- **Session credential revocation applies at validation**: delete that session record and subsequent validated requests using that session are rejected. Other device sessions require separate credential revocation, and cached sessions can delay enforcement.
- **The cookie reveals nothing**: it's just a random pointer.
- **Cost**: a store lookup per request, and the store must be shared across servers (to stay stateless at the app tier).

## Self-contained tokens

The token *itself* carries the claims, signed so the server can verify it without a lookup. JWT is the common format.

- **No lookup**: with asymmetric signing, a service with the trusted public key can verify its signature and then validate its required claims. Great for microservices.
- **Hard to revoke**: without additional credential revocation enforcement, a stolen token remains usable until expiry.

| | Session id | JWT |
|---|---|---|
| Verify | Store lookup | Signature check |
| Revoke | On next authoritative session validation; caches affect delay | Expiry or added credential revocation/status mechanism |
| Size | Chosen random identifier plus encoding overhead | Depends on claims, signature algorithm and encoding |
| Cross-service | Shared authoritative state | Trusted verification key and profile checks |

Neither is universally better. Many systems use **both**: an opaque session cookie at the edge for browsers, translated by the gateway into a short-lived internal JWT for service-to-service calls.

A short-lived access token plus a refresh token checked against current account state narrows the period after an account is disabled. It does not give instant credential revocation: a token issued immediately before disabling can remain valid for its remaining lifetime unless the API enforces a credential revocation mechanism.

## Key takeaways
- Authentication establishes identity; authorisation still checks the requested object.
- An opaque session identifier points to server-side state; authoritative validation enforces credential revocation.
- A self-contained token verifies locally but remains valid until expiry unless credential revocation is enforced.
- Short access tokens plus checked refreshes reduce stale-access exposure.

## Further reading
- [OWASP: Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [RFC 8725: JWT Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725)
