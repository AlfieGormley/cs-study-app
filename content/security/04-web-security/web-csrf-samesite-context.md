---
id: web-csrf-samesite-context
title: SameSite cookies and browser default modes
level: intermediate
minutes: 3
sourceLesson: web-csrf
summary: Explicit cookie settings and request context determine cross-site sending.
---

Token validation stays independent. This unit revisits schemeful sites: HTTPS sibling subdomains under the same registrable domain can be same-site while remaining cross-origin.

## Defence 2: SameSite cookies

The `SameSite` cookie attribute controls which **cross-site** request contexts permit a cookie; None, Lax and Strict impose different restrictions. Recall from the origin-boundary unit that *site* means scheme + registrable domain, so `app.example.com` and `api.example.com` are same-site.

The following is a `Set-Cookie` value wrapped for display; join its lines with a space into one HTTP field value.

```http
sid=abc; Secure; HttpOnly;
SameSite=Lax; Path=/
```

| Value | Cross-site requests that get the cookie |
|---|---|
| `Strict` | None at all |
| `Lax` | Top-level navigations with safe methods (clicking a link, a GET redirect) |
| `None` | SameSite imposes no restriction; other cookie policies still apply, and `Secure` is required |

So with `Lax`, the hidden-form POST from `evil.example` arrives **without** the session cookie, and the user appears logged out. With `Strict`, an initial navigation from a cross-site webmail page omits the cookie, so cookie-authenticated users can appear logged out on arrival; a common pattern is a `Lax` session cookie plus a `Strict` cookie required for sensitive actions.

### Browser defaults

Since 2020, Chrome (and other Chromium browsers) treat cookies **without** a `SameSite` attribute as `Lax`. Two caveats:

- To avoid breaking some single sign-on flows, Chrome makes an exception: a cookie without an explicit `SameSite` that is under **two minutes old** is still sent on top-level cross-site POSTs ("Lax+POST").
- Exact defaults and compatibility behavior are browser/version dependent. A verified Firefox/Safari version matrix is absent here; this lesson does not assert their current defaults.

So **set `SameSite` explicitly** rather than relying on the default.

```python
# Set transport, script and site rules.
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
```

### Why SameSite alone isn't enough

- **Same-site attackers.** A compromised or taken-over subdomain (`old-blog.example.com`) is same-site with your app, so SameSite alone does not isolate that origin. Other cookie conditions still apply.
- **State-changing GETs.** `Lax` sends cookies on top-level GET navigations, so a GET that transfers money is still exploitable.
- **Old or unusual clients** may not honour the attribute.

OWASP recommends explicit CSRF protection in most deployments, with SameSite as another layer. Its guidance describes constrained cases where SameSite can serve as the primary defence; those require careful conditions rather than a universal guarantee.

## Key takeaways
- Strict omits cookies on cross-site requests; explicit Lax permits eligible top-level safe navigations.
- None still requires Secure and remains subject to other cookie policy.
- A missing SameSite default mode can differ from explicit Lax for recent cookies.
- SameSite does not isolate a compromised same-site sibling origin or repair state-changing GET endpoints.

## Further reading
- [Cookies: HTTP State Management Mechanism](https://httpwg.org/http-extensions/draft-ietf-httpbis-rfc6265bis.html)
- [Chromium SameSite guidance](https://www.chromium.org/updates/same-site/)
