---
id: web-cors-credential-allowlists
title: Credentialed CORS and exact allowlists
level: intermediate
minutes: 3
sourceLesson: web-sop-cors
summary: Cookie eligibility, exact allowed origins and cache variation are separate checks.
---

A successful preflight is only one condition. This unit looks at an API sharing user-specific responses with named application origins. The hooks are fragments for studying response sharing, not complete authentication or preflight implementations.

### Credentials

By default, cross-origin `fetch` does not send cookies. `credentials: "include"` permits eligible cookies, but SameSite rules and browser third-party-cookie policies can still prevent sending them. To expose a credentialed response to JavaScript, the server must also explicitly allow it:

- It must send `Access-Control-Allow-Credentials: true`.
- `Access-Control-Allow-Origin` must name the exact origin. The CORS wildcard `*` is **not allowed** with credentials; the browser rejects the response.

This rule exists precisely so that nobody can accidentally say "any site may read this user's private data".

## The classic CORS misconfiguration

Because `*` cannot be combined with credentials, developers sometimes "fix" it by echoing back whatever `Origin` arrives. That is equivalent to a credentialed wildcard: an attacker-controlled origin can read a sensitive response if credentials are actually eligible and sent and the endpoint returns the data.

Vulnerable Flask hook fragment (assume `app` and `request` are provided; do not deploy it):

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

Response-sharing hook with an exact allowlist (same setup assumptions; this is not a complete authentication or preflight handler):

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

Cross-site scripting (XSS) means unwanted script running inside a page’s origin; the later XSS units examine that bug. For the subdomain example below, assume the attacker already runs script on the trusted sibling origin.

Other common mistakes:

- **Sloppy matching.** Checking `origin.endswith("example.com")` also accepts `https://evilexample.com`. A regex without anchors or with an unescaped `.` has the same problem. Compare exact strings.
- **Trusting `null`.** Sandboxed iframes, `file:` pages and some redirects send `Origin: null`. An attacker can produce it on demand, so never allowlist it.
- **Trusting every subdomain.** If `*.example.com` is allowed and one forgotten subdomain has an XSS bug, the attacker reads your API through it.
- **Missing `Vary: Origin`.** A shared cache may store a response with one origin's header and serve it to another.

## Key takeaways
- Credentials mode include still obeys cookie eligibility and browser policy.
- Credentialed response sharing requires an exact named origin and allow-credentials true.
- Compare complete allowlisted origins; null and broad subdomain trust weaken the boundary.
- Vary on Origin when selecting the response header dynamically, and separately protect private caching.

## Further reading
- [Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [PortSwigger original CORS research](https://portswigger.net/research/exploiting-cors-misconfigurations-for-bitcoins-and-bounties)
