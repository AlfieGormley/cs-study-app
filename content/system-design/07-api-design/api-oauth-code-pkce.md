---
id: api-oauth-code-pkce
title: OAuth delegation and the PKCE code flow
level: advanced
minutes: 4
summary: Trace scoped delegated access and bind an authorisation code to its original client verifier.
sourceLesson: api-auth
---

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

## Authorisation code flow with PKCE

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
- The code alone is useless. Exchanging it needs the **code verifier** `v`, a high-entropy random string sent only to the authorization server’s token endpoint, not in the front-channel authorization request. **PKCE** (RFC 7636, "pixy") binds the code to the client that started the flow. The client sends a one-way hash of the verifier, the **code challenge**, at the start (the `S256` method, shown below); the `plain` method (sending the verifier itself as the challenge) gives up most of the protection and shouldn't be used.
- PKCE also stops **authorisation code injection**: an attacker who slips a stolen code into a victim's session can't redeem it, because the victim's client holds a different verifier.
- Tokens return from the token endpoint, not in the redirect URL. A browser-based public client still receives them in its browser process; a BFF can keep them server-side.

The `S256` challenge is computed like this:

```formula
c = BASE64URL(SHA256(v))
where
c: the code challenge, sent in the /authorize redirect at the start of the flow and stored by the authorisation server
v: the code verifier: a high-entropy random string of 43 to 128 characters that the client keeps until the token request
SHA256: the SHA-256 hash function, which turns any input into a 32-byte digest and cannot feasibly be reversed
BASE64URL: base64url encoding without padding, which writes those 32 bytes as 43 URL-safe characters
In words: the challenge is a one-way fingerprint of the verifier, so seeing the challenge in the browser reveals nothing that lets an attacker redeem the code.
```

At the token endpoint the server recomputes the challenge from the verifier the client sends and compares it with the stored one. RFC 7636's own example: the verifier `dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk` gives the challenge `E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM`. The protection rests on the verifier being long and random: a short or guessable one could be found by trying candidates.

## Key takeaways
- OAuth delegates access without handing the client the resource owner’s password.
- S256 exposes a one-way challenge while keeping the high-entropy verifier for the token endpoint.
- PKCE protects intercepted and injected codes; browser public clients cannot keep a client secret.
- A BFF can keep issued tokens server-side instead of exposing them to browser JavaScript.

## Further reading
- [OAuth 2.0 overview (oauth.net)](https://oauth.net/2/)
- [oauth.net: PKCE](https://oauth.net/2/pkce/)
- [RFC 9700: OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700)
- [RFC 7636: PKCE](https://www.rfc-editor.org/rfc/rfc7636)
