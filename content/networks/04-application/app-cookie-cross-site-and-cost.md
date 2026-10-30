---
id: app-cookie-cross-site-and-cost
title: "SameSite, cookie prefixes and repeated bytes"
level: basic
minutes: 4
sourceLesson: app-http-wire
summary: "SameSite uses site relationships and request context; __Host- prefixes constrain supporting browsers."
---

A cookie is a stored name/value pair with scope and security attributes. Earlier units covered host-only cookies, Domain, Path, Secure and HttpOnly. This unit adds cross-site sending rules and cookie-name prefixes, then looks at the cost of repeating cookies on every request.

### SameSite and the meaning of "site"

For these ordinary domain URLs, a **schemeful site** is the scheme plus the *registrable domain* (eTLD+1): `https://shop.example.co.uk` and `https://api.example.co.uk` are the **same site**, though different origins.

- `Strict`: sent only on same-site requests. On a cross-site navigation, that cookie is withheld from the initial request; what the user sees depends on application behaviour.
- `Lax`: also sent on **top-level navigations** with safe methods (clicking a link, a GET form). Not sent on cross-site `POST`s, iframes, images or `fetch`.
- `None`: removes the SameSite restriction and requires Secure in supporting browsers. Domain/path rules, partitioning and third-party-cookie policies still apply.

The 6265bis draft specifies Lax-style default enforcement and allows a user-agent-chosen recent-cookie exception for cookies with no explicit SameSite value. Explicit Lax excludes that exception. SameSite helps against cross-site CSRF, but does not cover same-site sibling attacks or every application workflow. Use appropriate CSRF protection for state-changing requests; GET should not perform state changes.

> [!analogy] Real-world analogy: An assistant who carries your membership card
> Your assistant automatically shows your club membership card on every errand to the club. A stranger hands the assistant a sealed note for the club saying "transfer £500". Without a rule, the assistant shows your card and the club acts on the note as if you sent it.
>
> **How it maps:** The assistant is the browser, the card is a cookie, and the stranger's note is a cross-site request. `Strict` means "show the card only on errands I started from the club's own pages". `Lax` adds "or when a stranger's link just sends you to the club's front page", which is a top-level navigation with a safe method such as GET. It still withholds the card from a cross-site POST and from requests embedded in the stranger's page, such as images or `fetch`.
>
> **Where it stops:** "Same site" means the same scheme and registrable domain, so every subdomain of the club counts as the club, including a compromised one. Browser policies also differ, so SameSite supplements CSRF protection rather than replacing it.

### Prefixes

Supporting browsers enforce cookie-name prefixes:

- `__Secure-name`: must be set with `Secure` from an HTTPS page.
- `__Host-name`: must be `Secure`, have `Path=/` and **no** `Domain`. This prevents a sibling from setting a parent-domain cookie under that prefixed name. It does not isolate ports on the same host or authenticate a Cookie header supplied by an arbitrary client.

> [!tip] A good session cookie
> `Set-Cookie: __Host-sid=<random>; Path=/; Secure; HttpOnly; SameSite=Lax`

### Limits

RFC 6265 asks browsers to support **at least** 4096 bytes per cookie, 50 cookies per domain and 3000 in total, as recommended minimum capabilities in that RFC, not universal current limits. Cookie inclusion also depends on path, security, SameSite, credentials mode and browser policy.

Because HTTP/1.1 repeats the `Cookie` header on every request, large cookies multiply. A page that makes 80 requests, each carrying 3,000 bytes of cookies, uploads about 240,000 bytes of cookie values before any other header overhead. On a slow mobile uplink that can be noticeable. Two practical fixes are keeping cookies small (a short random session ID rather than stored state) and serving static files from a host the cookies are not scoped to.

This assumes every request is eligible to carry the cookies and that nothing compresses them. Cache hits can avoid requests; HTTP/2 or HTTP/3 compression savings depend on encoder/table decisions.

## Pitfalls

- **Hand-rolled parsers.** Reading until close, ignoring `HEAD`/`304` rules or trusting chunk boundaries to match `recv` calls are classic bugs.
- **Mixed framing headers.** Any hop that accepts both `Content-Length` and `Transfer-Encoding` is a smuggling risk.
- **`Domain=` by habit.** It widens scope to every subdomain, including the forgotten staging box.
- **Treating cookie attributes as complete XSS protection.** HttpOnly is a real restriction on cookie APIs, but does not prevent injected script from making authenticated requests. Path is not an isolation boundary.

## Key takeaways
- SameSite uses site relationships and request context; __Host- prefixes constrain supporting browsers.
- Cookie-size estimates count actual eligible requests and state compression assumptions.

## Further reading
- [RFC 6265](https://www.rfc-editor.org/rfc/rfc6265)
- [Cookie revision draft](https://httpwg.org/http-extensions/draft-ietf-httpbis-rfc6265bis.html)
- [CHIPS design](https://privacysandbox.google.com/cookies/chips)
