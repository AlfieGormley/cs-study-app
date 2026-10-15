---
id: app-cookie-scope-and-lifetime
title: "Cookie scope, lifetime and script access"
level: basic
minutes: 3
sourceLesson: app-http-wire
summary: "Omitting Domain creates a host-only cookie; deleting a cookie must match its stored scope."
---

## Cookies: state on a stateless protocol

HTTP is a stateless protocol at the level of its semantics; applications and connections can still maintain state. **HTTP cookies** ([RFC 6265](https://www.rfc-editor.org/rfc/rfc6265), being revised as "6265bis") add state: the server sets a name/value pair, and the browser sends it back on later requests.

```
HTTP/1.1 200 OK
Set-Cookie: sid=a3f9; Path=/; Secure;
  HttpOnly; SameSite=Lax; Max-Age=3600
```

(Shown wrapped; on the wire it is one line.) Later requests carry only the name/value pairs, never the attributes:

```
Cookie: sid=a3f9; theme=dark
```

One quirk: combining repeated field lines is allowed only when the field definition permits it. `Set-Cookie` **must not be folded into one comma-separated field**, because cookie dates (`Expires=Wed, 21 Oct...`) contain commas. Each cookie needs its own `Set-Cookie` line.

### The attributes

| Attribute | Effect |
|---|---|
| `Expires` / `Max-Age` | Lifetime; none means session cookie |
| `Domain` | Widen scope to subdomains |
| `Path` | Only send under this path |
| `Secure` | Send only over connections the browser considers secure |
| `HttpOnly` | Exclude from non-HTTP cookie APIs such as document.cookie |
| `SameSite` | Control cross-site sending |
| `Partitioned` | Add a top-level-site partition key in supporting browsers; requires Secure |

**Lifetime.** `Max-Age` (seconds) takes precedence over `Expires` (a date) if both appear. With neither, the cookie is a *session cookie*, deleted when the browser session ends (though "restore tabs" features often keep them). To delete a cookie, set it again with `Max-Age=0` and matching name, domain/host-only scope and path, in the same partition if applicable.

**Domain.** If you *omit* `Domain`, the cookie is **host-only**: set by `app.example.com`, it goes only to `app.example.com`. Setting `Domain=example.com` allows host matching for `example.com` *and its subdomains*, subject to path, security, SameSite and browser policy. The setting host must domain-match that Domain value. Counter-intuitively, omitting `Domain` is the stricter choice. Public-suffix rejection prevents a tenant from setting a parent-suffix cookie for other tenants. The algorithm has a host-only exception when the setting host itself equals the suffix; lists and browser policy matter.

**Path** limits which URLs receive the cookie, but it is **not a security boundary**: same-origin script may access a matching-path document, subject to framing policy. Path does not isolate mutually distrustful applications on one origin; HttpOnly separately restricts script cookie access.

**Secure** normally requires HTTPS; browsers may treat localhost as a trusted exception. **HttpOnly** stops script from reading the cookie through document.cookie and similar non-HTTP APIs. It does not guarantee that XSS cannot expose a token through another vulnerable application feature, and injected script can still make authenticated requests.

## Key takeaways
- Omitting Domain creates a host-only cookie; deleting a cookie must match its stored scope.
- Path controls sending, while HttpOnly restricts non-HTTP cookie APIs; neither supplies complete XSS protection.

## Further reading
- [RFC 6265](https://www.rfc-editor.org/rfc/rfc6265)
- [Cookie revision draft](https://httpwg.org/http-extensions/draft-ietf-httpbis-rfc6265bis.html)
