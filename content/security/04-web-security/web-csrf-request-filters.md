---
id: web-csrf-request-filters
title: Request provenance, JSON types and framing
level: intermediate
minutes: 3
sourceLesson: web-csrf
summary: Use request-context filters and strict API parsing alongside tokens, then block unwanted framing.
---

The token and SameSite units addressed request secrets and cookie context. Origin and Fetch Metadata add browser-provided context checks; strict parsing closes a different request-shape gap. Framing-based clickjacking needs its own embedding policy.

## Defence 3: checking where the request came from

Browsers add headers the attacker's page cannot fake:

- **`Origin`** is supplied for many relevant requests, but can be absent or serialise as `null`. Validate an exact trusted origin and define a safe policy for missing/opaque origins, using independent CSRF protection.
- **`Sec-Fetch-Site`** in supporting browsers reports `same-origin`, `same-site`, `cross-site` or `none` (for example, address-bar or bookmark navigation). Whether it is sent depends on the client and context. Arbitrary non-browser clients can fake these headers; they are not authentication.

```python
SAFE = {"GET", "HEAD", "OPTIONS"}

@app.before_request
def fetch_metadata():
    site = request.headers.get(
        "Sec-Fetch-Site")
    if site is None:
        return  # still require token
    if request.method in SAFE:
        return
    # Do not trust sibling sites by default.
    if site not in ("same-origin",
                    "none"):
        abort(403)
```

This rejects many cross-site unsafe browser requests, but does not prevent same-origin XSS or client-side CSRF. Keep the token hook active independently, including when the Fetch Metadata headers are missing or `none`; the metadata policy is an additional filter.

## JSON APIs

A common belief is "our API takes JSON, so it's immune". It depends:

- If the server *requires* `Content-Type: application/json`, a cross-site request with that type is non-simple, so it is preflighted, and without permissive CORS the browser never sends it.
- If the server parses the body as JSON **regardless** of content type, an attacker can send a form with `enctype="text/plain"` crafted so the body happens to be valid JSON. That can be a simple request, delivered with any cookies allowed by browser policy.

So: check `Content-Type` strictly, or require a custom header such as `X-Requested-With` (which requires CORS preflight permission), and keep CORS tight.

## Related: clickjacking

Instead of faking a request, the attacker loads your real page in an invisible iframe and tricks the user into clicking a button on it. Tokens don't help, because the click happens on your genuine page. Prevent this framing with the `Content-Security-Policy` response header containing this policy value:

```
frame-ancestors 'none'
```

`frame-ancestors` is a CSP directive, not a standalone header. `X-Frame-Options: DENY` provides a legacy alternative. These controls address framing-based clickjacking; they do not prevent every form of deceptive UI.

## Evidence limits

A full browser/version compatibility matrix and live cross-browser attack testing are absent from this lesson. Browser-specific defaults must be checked for the supported clients; examples assume the credential and policy conditions stated above.

## Key takeaways
- Browser-provided provenance headers are a filter, not authentication for arbitrary clients.
- Require tokens even when Fetch Metadata is missing or none.
- JSON-only content-type enforcement and custom headers depend on restrictive CORS.
- CSP frame-ancestors controls embedding; tokens do not prevent a genuine framed-page click.

## Further reading
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [Fetch Metadata specification](https://www.w3.org/TR/fetch-metadata/)
- [OWASP clickjacking prevention](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html)
