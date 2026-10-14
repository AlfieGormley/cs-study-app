---
id: api-oauth-grants-refresh-policy
title: OAuth grants and refresh-token safety
level: advanced
minutes: 3
summary: Choose machine and device grants, detect refresh-token reuse and apply current PKCE requirements.
sourceLesson: api-auth
---

## Other grants

- **Client credentials**: machine-to-machine, no user. A backend service exchanges its client id and secret for a token.
- **Device code**: TVs and CLIs with no browser. The device shows a code; you approve on your phone.
- **Refresh token**: exchange a long-lived refresh token for a new access token. Use **rotation**: each refresh issues a new refresh token and invalidates the old one, so reuse of a stolen one is detectable.

> [!warning] Deprecated grants
> The **implicit** grant (access token returned directly in the URL fragment, where it is exposed to browser history and page scripts; fragments are not sent in ordinary HTTP Referer headers) and the **password** grant (client collects the user's password) are out. The OAuth 2.0 Security Best Current Practice, published as RFC 9700 in January 2025, says the implicit grant should not be used and the password grant must not be. OAuth 2.1 (still an IETF draft, consolidating these rules) drops both grants entirely. Use authorisation code + PKCE instead, including for single-page apps.

## PKCE for every client

PKCE was first designed for *public* clients (mobile and single-page apps) that can't keep a client secret. It turned out to protect confidential clients too, against code injection, which a client secret doesn't prevent.

- **RFC 9700**: PKCE is required for public clients and recommended for confidential ones.
- **OAuth 2.1**: PKCE is required for every client using the authorisation code flow, with only a narrow exception for confidential OpenID Connect clients that use the `nonce` parameter correctly. It also bans the `plain` method and requires exact redirect-URI matching, except for the allowed variable port in native-app loopback redirects.

In practice: use PKCE with `S256` everywhere, and configure your authorisation server to reject code requests without it.

When an invalidated rotated refresh token is presented again, the authorisation server detects possible theft. It cannot tell which participant is legitimate, so revoke the active refresh-token lineage and require a new login. Already issued access tokens need separate credential revocation or expire according to their lifetime. RFC 9700 requires public-client refresh tokens to use rotation or sender constraints.

## Key takeaways
- Client credentials suit machines without a user; device code supports limited-input clients.
- Rotation detects refresh-token reuse; reject the old token and revoke its active refresh lineage.
- RFC 9700 rules and the OAuth 2.1 draft differ in PKCE requirements; use S256 for code flows.
- Implicit and password grants are unsuitable for new deployments under the current security guidance.

## Further reading
- [OAuth 2.0 overview (oauth.net)](https://oauth.net/2/)
- [RFC 9700: OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700)
- [oauth.net: OAuth 2.1](https://oauth.net/2.1/)
- [IETF: OAuth 2.1 draft](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/)
