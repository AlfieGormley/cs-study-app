---
id: web-csrf-samesite-context
title: SameSite cookies and browser default modes
level: intermediate
minutes: 4
sourceLesson: web-csrf
summary: Explicit cookie settings and request context determine cross-site sending.
---

Tokens make the server check intent. The `SameSite` cookie attribute attacks CSRF from the other side: it lets the browser *withhold* the cookie from cross-site requests, so a faked request arrives looking logged out.

## Defence 2: SameSite cookies

Recall from the origin unit that a *site* is the scheme plus the registrable domain. So `https://app.example.com` and `https://api.example.com` are same-site, even though they are different origins. SameSite only restricts **cross-site** requests.

Here is a `Set-Cookie` value, wrapped for display (it is one line in the real header):

```http
sid=abc; Secure; HttpOnly;
SameSite=Lax; Path=/
```

| Value | Cross-site requests that get the cookie |
|---|---|
| `Strict` | None at all |
| `Lax` | Top-level navigations with safe methods (clicking a link, a GET redirect) |
| `None` | SameSite imposes no restriction; other cookie policies still apply, and `Secure` is required |

So with `Lax`, the hidden-form POST from `evil.example` arrives **without** the session cookie, and the user appears logged out. `Strict` is tighter but has a usability cost: a user who follows a link from their webmail to your site arrives logged out, because that first navigation is cross-site. A common pattern is a `Lax` session cookie plus a separate `Strict` cookie that sensitive actions require.

### Browser defaults

The cookie standard's revision ("6265bis", approved but still waiting in the RFC Editor queue in October 2026) treats a cookie with no `SameSite` attribute much like `Lax`. Browsers differ. As of November 2026, both MDN's compatibility data and OWASP report that Chrome and other Chromium-based browsers have done this since 2020, Firefox only behind a non-default setting, and Safari not at all.

Chromium also adds a compatibility exception, which the draft standard permits. A cookie with **no** SameSite attribute that is at most **two minutes old** is still sent on top-level cross-site POSTs ("Lax+POST"). It exists so that some single sign-on flows keep working, and Chromium describes it as temporary. Explicitly setting `SameSite=Lax` removes it.

So **set `SameSite` explicitly** rather than relying on any browser's default:

```python
# Set transport, script and site rules.
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
```

### Why SameSite alone isn't enough

- **Same-site attackers.** A compromised or taken-over subdomain (`old-blog.example.com`) is same-site with your app, so its requests carry your SameSite cookies.
- **State-changing GETs.** `Lax` sends cookies on top-level GET navigations, so a GET that transfers money is still exploitable.
- **Client-side CSRF.** Requests sent by your own JavaScript are same-site, so SameSite does nothing when attacker input steers that code.
- **Old or unusual clients** may not honour the attribute.

OWASP treats SameSite as a defence-in-depth layer to combine with tokens (or Fetch Metadata checks, next unit) in most deployments. It allows SameSite alone only in narrow cases: no untrusted hosts on the same registrable domain, no state-changing GETs, Strict (or carefully audited Lax with `__Host-`) cookies, and origin checks as an extra layer.

## Key takeaways
- Strict withholds cookies on all cross-site requests; Lax still sends them on top-level safe navigations.
- None needs Secure and is still subject to other cookie policy.
- A missing SameSite attribute is not the same as explicit Lax: defaults vary by browser, and Chromium's Lax+POST exception applies only to missing ones.
- SameSite does not stop same-site sibling attackers, client-side CSRF or state-changing GETs, so keep a CSRF token or equivalent check.

## Further reading
- [Cookies: HTTP State Management Mechanism (6265bis draft)](https://httpwg.org/http-extensions/draft-ietf-httpbis-rfc6265bis.html)
- [Chromium SameSite guidance](https://www.chromium.org/updates/same-site/)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
