---
id: web-csrf-request-filters
title: Request provenance, JSON types and framing
level: intermediate
minutes: 4
sourceLesson: web-csrf
summary: Use request-context filters and strict API parsing alongside tokens, then block unwanted framing.
---

Tokens check a secret; SameSite controls when cookies travel. This unit adds checks on where a request came from, closes a JSON-parsing gap, and then deals with clickjacking, which no request check can stop.

## Defence 3: checking where the request came from

Browsers add headers that a web page cannot set or change:

- **`Origin`** names the requesting page's origin on CORS requests and on every request whose method is not GET or HEAD, such as a form POST. Plain GET navigations and image loads usually carry none, and it can be `null` (opaque origins, some referrer policies). Accept only exact trusted origins, and decide deliberately what to do when it is absent.
- **`Sec-Fetch-Site`** (part of **Fetch Metadata**) says how the requesting page relates to your site: `same-origin`, `same-site`, `cross-site`, or `none` (the user typed the address or used a bookmark). Browsers send it only to HTTPS (and other trustworthy) URLs. OWASP notes that all major browsers have supported it since March 2023.

These headers describe a browser's request. `curl` or a script can send any values it likes, but such a client does not carry the victim's cookies, so this matters for CSRF only as a reminder that the headers are not authentication.

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

This hook rejects cross-site and same-site unsafe requests from supporting browsers, and does not treat sibling subdomains as trusted. When the header is missing (an old client, a stripping proxy), it falls back to the token check from earlier, which stays active.

OWASP's current guidance accepts a Fetch Metadata policy like this as a main defence for sites that only target modern browsers, *provided* missing headers fall back to origin checks or tokens. Keeping tokens as well costs little. Neither check stops same-origin XSS or client-side CSRF, because those requests really do come from your own page.

## JSON APIs

A common belief is "our API takes JSON, so it's immune". It depends:

- If the server *requires* `Content-Type: application/json`, a cross-site request with that type is not a simple request. It must pass a CORS preflight, and without permissive CORS the browser never sends it.
- If the server parses the body as JSON **regardless** of content type, an attacker can submit a form with `enctype="text/plain"`, crafted so that the body happens to be valid JSON. That is a simple request, sent with whatever cookies the browser's rules allow.

So: reject requests that are not `application/json`, or require a custom header such as `X-Requested-With`, which forces a preflight. Both rely on keeping CORS tight.

## Related: clickjacking

Instead of faking a request, the attacker loads your real page in an invisible iframe and tricks the user into clicking a button on it. Tokens don't help, because the click happens on your genuine page, which includes a valid token. Prevent the framing instead, with the `Content-Security-Policy` response header containing:

```
frame-ancestors 'none'
```

Use `'self'` if you frame your own pages, or list specific partner origins. `frame-ancestors` is a CSP directive, not a header of its own. `X-Frame-Options: DENY` is the older equivalent, still useful for old browsers. These stop framing-based clickjacking; they do not prevent every kind of deceptive interface.

> [!analogy] Real-world analogy: a contract under a raffle ticket
> A con artist lays a real contract under a thin sheet printed with a raffle ticket, lining up "Sign here to win" with the contract's signature box. You think you are entering a raffle; your pen signs the contract.
>
> **How it maps:** The contract is your genuine page in a transparent iframe; the raffle sheet is the attacker's visible decoy page. The click is real, on your real button, with a valid token, which is why request checks cannot tell. `frame-ancestors` is a rule that your contract may never be placed under someone else's sheet.
>
> **Where it stops:** Nobody can stop a con artist layering paper, but a browser can refuse to render your page inside another site's frame. Some deceptive designs need no frame at all, and `frame-ancestors` does not cover those.

## Key takeaways
- Origin and Sec-Fetch-Site are browser-set filters; decide explicitly how to treat missing or `null` values, and fall back to tokens.
- A JSON API is protected only if it rejects non-JSON content types (or requires a custom header) and keeps CORS tight.
- `frame-ancestors` (or `X-Frame-Options`) prevents framing; tokens cannot stop a genuine framed click.

## Further reading
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [Fetch Metadata specification](https://www.w3.org/TR/fetch-metadata/)
- [OWASP clickjacking prevention](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html)
