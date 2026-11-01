---
id: web-cors-credential-allowlists
title: Credentialed CORS and exact allowlists
level: intermediate
minutes: 4
sourceLesson: web-sop-cors
summary: Cookie eligibility, exact allowed origins and cache variation are separate checks.
---

This unit looks at an API that shares *user-specific* responses with a few named front-end origins. That is where CORS mistakes do the most damage, because the replies contain private data. The Python snippets are fragments of a Flask app, shown only to study the response headers; they are not complete authentication or preflight handlers.

### Credentials

By default, a cross-origin `fetch` sends no cookies. Setting `credentials: "include"` lets the browser attach cookies, but only those that its cookie rules allow (SameSite, third-party-cookie blocking and so on).

To let the page *read* a credentialed response, the server must say so explicitly:

- It must send `Access-Control-Allow-Credentials: true`.
- `Access-Control-Allow-Origin` must name the exact origin. The CORS wildcard `*` is **not allowed** with credentials; the browser treats the response as a CORS failure.

This rule exists so that nobody can accidentally say "any site may read this user's private data".

## The classic CORS misconfiguration

Because `*` cannot be combined with credentials, developers sometimes "fix" the error by echoing back whatever `Origin` arrives. That is a credentialed wildcard in disguise. If a victim's cookies are sent and the endpoint returns their data, any site the victim visits can read it.

Vulnerable Flask hook (assume `app` and `request` are provided; do not deploy it):

```python
@app.after_request
def cors(resp):
    o = request.headers.get("Origin")
    # BAD: grants read access to any origin
    resp.headers[
        "Access-Control-Allow-Origin"] = o
    resp.headers[
        "Access-Control-Allow-Credentials"
    ] = "true"
    return resp
```

Fixed hook with an exact allowlist (same setup assumptions):

```python
ALLOWED = {
    "https://a.test",
    "https://admin.example",
}

@app.after_request
def cors(resp):
    o = request.headers.get("Origin")
    # Share only with a known app origin.
    if o in ALLOWED:
        resp.headers[
          "Access-Control-Allow-Origin"] = o
        resp.headers[
          "Access-Control-Allow-Credentials"
        ] = "true"
    # caches must key on Origin
    resp.vary.add("Origin")
    return resp
```

A request from `https://evil.example` now gets no allow-origin header, so its page cannot read the reply. The server still runs the handler, which is why the endpoint also needs its own authentication, authorisation and CSRF protection.

> [!analogy] Real-world analogy: a door with a guest list
> A private party has a guest list at the door. A lazy doorman, asked to "only let in people on the list", instead asks each visitor their name and writes it on the list before checking it.
>
> **How it maps:** The list is the set of allowed origins and the visitor's name is the `Origin` header. Echoing `Origin` back is the lazy doorman: every visitor passes. A real allowlist compares the name with a list written in advance.
>
> **Where it stops:** Unlike a spoken name, `Origin` is set by the browser, and a web page cannot change it. (A non-browser client can send any value, but it does not carry the victim's cookies.) So the danger is not lying but *which* sites are on the list: any listed origin, even a compromised one, gets in.

## Other common mistakes

For the subdomain example below, cross-site scripting (XSS) means an attacker's script running inside a trusted page's origin; the later XSS units examine that bug.

- **Sloppy matching.** Checking `origin.endswith("example.com")` also accepts `https://evilexample.com`. A regular expression without anchors or with an unescaped `.` has the same problem. Compare complete origins exactly.
- **Trusting `null`.** Sandboxed iframes, `file:` pages and some redirects send `Origin: null`. Any website can create a sandboxed iframe, so an attacker can produce `null` on demand. Never allowlist it.
- **Trusting every subdomain.** If `*.example.com` is allowed and one forgotten subdomain has an XSS bug, the attacker reads your API through it.
- **Missing `Vary: Origin`.** When the allow-origin header depends on the request, a shared cache may store the response for one origin and serve it to another. `Vary: Origin` tells caches to keep them apart. Private per-user data also needs suitable `Cache-Control` so shared caches do not store it at all.

## Key takeaways
- `credentials: "include"` still obeys the browser's cookie rules.
- Sharing a credentialed response needs an exact named origin plus `Access-Control-Allow-Credentials: true`.
- Compare complete origins against a fixed list; echoing, suffix checks, `null` and broad subdomain trust all weaken the boundary.
- Add `Vary: Origin` when the header depends on the request, and keep private responses out of shared caches.

## Further reading
- [Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [PortSwigger original CORS research](https://portswigger.net/research/exploiting-cors-misconfigurations-for-bitcoins-and-bounties)
