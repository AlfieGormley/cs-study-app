---
id: web-sop-cors
title: The same-origin policy and CORS
level: basic
minutes: 12
summary: Why your browser stops one site reading another site's data, exactly what counts as an origin, and how CORS grants controlled access and how misconfiguration exposes data.
---

You are logged into your bank in one tab and reading a dodgy blog in another. Your browser holds the bank's session cookie. If the blog's JavaScript could simply `fetch("https://bank.example/api/balance")` and read the reply, every site you visited could read every other site you were logged into.

The **same-origin policy** (SOP) is the browser rule that stops this. It is the foundation that almost all of web security sits on, so the rest of this module keeps coming back to it.

## What an origin is

For ordinary HTTP(S) URLs, an **origin** compares the normalised **scheme, host and port**; an explicit default port and its omitted form are equivalent. Documents can instead have opaque origins, including sandboxed documents without same-origin permission. Identical `null` serialisations do not make distinct opaque origins equal.

| URL (vs `https://shop.example`) | Same origin? |
|---|---|
| `https://shop.example/cart` | Yes (path ignored) |
| `http://shop.example` | No: scheme |
| `https://api.shop.example` | No: host |
| `https://shop.example:8443` | No: port |

The path, query string and fragment play no part. A subdomain is a different origin, even though it feels like "the same site".

For the domain-based HTTP(S) examples here, a looser idea, the **schemeful site**, is the scheme plus the *registrable domain* (the "eTLD+1", such as `shop.example` or `example.co.uk`). `https://api.shop.example` and `https://www.shop.example` are **cross-origin but same-site**. Origins govern who can *read* what; sites govern when cookies are sent (the SameSite rules in lesson 3). Keep the two apart.

## What the SOP actually blocks

A common misconception is that the SOP stops cross-origin *requests*. Mostly it does not. It stops cross-origin *reads*.

```
evil.example page            bank.example
      |  fetch(/api/balance)      |
      |-------------------------->|  request
      |   (cookies attached)      |  is SENT
      |<--------------------------|
      |  response arrives, but    |
      |  JS may NOT read it       |
```

The diagram assumes a simple request using `credentials: "include"` and a cookie eligible under SameSite and browser policy; default cross-origin `fetch` omits cookies. Roughly, cross-origin interactions fall into three groups:

- **Writes are usually allowed.** Links, redirects and HTML form submissions can target any origin. This is why CSRF (lesson 3) is possible.
- **Embedding is usually allowed.** `<img>`, `<script src>`, `<link rel=stylesheet>`, `<video>` and `<iframe>` can load cross-origin resources. Resource type, CORS mode, CSP, CORP/COEP, framing policy and other checks affect loading. Classic scripts differ from module scripts, which require CORS for cross-origin loading. Successful embedding alone does not grant unrestricted response-byte access.
- **Reads are blocked.** Without the applicable permission, script cannot read a cross-origin `fetch` response or iframe DOM. Drawing an image without the required CORS permission can taint a canvas and prevent pixel readback. CORS-approved images can preserve readback.

> [!warning] The SOP is not server-side protection
> A simple request can reach the server even when its response is unreadable. A failed required preflight can prevent the actual request; other browser policies can block sending too. The browser just hides the reply from the calling page. Tools like `curl` ignore the SOP completely. Never rely on it to protect an endpoint; that is the job of authentication and authorisation.

### A note on embedding scripts

`<script src="https://other.example/lib.js">` runs that file *with the including page's origin*. That is why including third-party scripts is a big trust decision: the script can do anything your own code can. It is also why old APIs that returned sensitive data as executable JavaScript (JSONP) leaked it to any site that included them.

## CORS: opting in to cross-origin reads

Modern apps legitimately need cross-origin reads. A single-page app on `https://a.test` calls an API on `https://b.test`. **Cross-Origin Resource Sharing** (CORS) lets the *server* tell the browser which other origins may read its responses.

A browser CORS fetch includes an `Origin` header; not every cross-origin navigation or embedding request does. The server replies with headers saying what it allows:

```
GET /v1/orders HTTP/1.1
Host: api.example
Origin: https://a.test

HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://a.test
Vary: Origin
```

For a CORS fetch, a matching allow-origin value is necessary to expose the response; `*` works only when credentials mode is not `include`. Credentialed requests also require allow-credentials. CORS failures are exposed as network errors. A required preflight additionally gates sending the actual method/headers; CORS is not server authentication.

### Simple requests and preflights

The safelist preserves forms of cross-origin traffic historically possible without CORS. A request avoiding preflight still can have harmful side effects. The following is a simplified checklist for a CORS fetch that does not otherwise require preflight:

- Method is `GET`, `HEAD` or `POST`.
- Author-set headers meet the CORS safelist, including header-specific byte, length and syntax restrictions; a safelisted name alone is insufficient.
- `Content-Type`, if set, is `application/x-www-form-urlencoded`, `multipart/form-data` or `text/plain`.

Methods such as `PUT`/`DELETE`, an author-set `Authorization` header or JSON content type require preflight permission in a CORS fetch. Without a matching unexpired preflight-cache entry, the browser sends `OPTIONS` first. Streaming bodies or XHR upload listeners can require preflight too.

```
OPTIONS /v1/orders/7 HTTP/1.1
Origin: https://a.test
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: x-token

HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://a.test
Access-Control-Allow-Methods: DELETE
Access-Control-Allow-Headers: x-token
Access-Control-Max-Age: 600
```

The actual `DELETE` needs successful preflight permission. Fetch specifies a five-second default when max-age is missing or invalid, with implementation caps and possible earlier eviction. Chromium source currently uses a two-hour maximum; this is version-specific, not guaranteed retention or a cache shared with ordinary HTTP responses.

### Credentials

By default, cross-origin `fetch` does not send cookies. `credentials: "include"` permits eligible cookies, but SameSite rules and browser third-party-cookie policies can still prevent sending them. To expose a credentialed response to JavaScript, the server must also opt in:

- It must send `Access-Control-Allow-Credentials: true`.
- `Access-Control-Allow-Origin` must name the exact origin. The wildcard `*` is **not allowed** with credentials; the browser rejects the response.

This rule exists precisely so that nobody can accidentally say "any site may read this user's private data".

## The classic CORS misconfiguration

Because `*` cannot be combined with credentials, developers sometimes "fix" it by echoing back whatever `Origin` arrives. That is equivalent to a credentialed wildcard: an attacker-controlled origin can read a sensitive response if credentials are actually eligible and sent and the endpoint returns the data.

Vulnerable Flask hook fragment (assume `app` and `request` are provided; do not deploy it):

```python
@app.after_request
def cors(resp):
    o = request.headers.get("Origin")
    # BAD: trusts every origin
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

Other common mistakes:

- **Sloppy matching.** Checking `origin.endswith("example.com")` also accepts `https://evilexample.com`. A regex without anchors or with an unescaped `.` has the same problem. Compare exact strings.
- **Trusting `null`.** Sandboxed iframes, `file:` pages and some redirects send `Origin: null`. An attacker can produce it on demand, so never allowlist it.
- **Trusting every subdomain.** If `*.example.com` is allowed and one forgotten subdomain has an XSS bug, the attacker reads your API through it.
- **Missing `Vary: Origin`.** A shared cache may store a response with one origin's header and serve it to another.

## Other cross-origin channels

### postMessage

`window.postMessage` is the sanctioned way for cross-origin windows and iframes to talk. Both sides must be careful:

```javascript
// sender: name the target origin
child.postMessage(data,
  "https://widget.example");

// receiver: assume trusted parent window
addEventListener("message", (e) => {
  if (e.origin !==
      "https://a.test") return;
  if (e.source !== parent) return;
  if (typeof e.data !== "string") return;
  handle(e.data);
});
```

Using `"*"` as the target can leak data to whatever page has been loaded into that window; an unchecked handler can accept messages from an untrusted window that has a reference to it. Validate origin, expected source and message structure, and treat the payload as untrusted data.

### Isolation headers

Side-channel attacks such as Spectre showed that a page might read memory belonging to cross-origin resources loaded into the same process. Newer headers let a site ask for stronger isolation:

| Header | Purpose |
|---|---|
| `Cross-Origin-Resource-Policy` | Restricts applicable cross-origin no-cors resource loads |
| `Cross-Origin-Opener-Policy` | Controls browsing-context-group isolation for top-level documents |
| `Cross-Origin-Embedder-Policy` | Controls embedding; require-corp and credentialless have different rules |

You also may see the old `document.domain` trick, where two subdomains both set `document.domain = "example.com"` to become same-origin. It weakens isolation and modern Chrome disables it by default; don't build on it.

> [!note] Evidence limits
> Browser-specific preflight retention, third-party-cookie policy and legacy origin relaxation vary by version and configuration. A complete browser compatibility matrix and universal exploit-success rates are absent because they were not reliably established. Wire examples are abbreviated; the Flask hooks need an application, authentication, cache policy and preflight handling.

## Key takeaways
- An origin is scheme + host + port; all three must match. A site (scheme + registrable domain) is a looser idea used for cookies.
- The SOP mainly blocks cross-origin *reads*. Requests, form posts and embeds still happen, so the server must still authenticate and authorise.
- CORS controls browser response sharing and preflight permission. It does not replace server authentication, authorisation or CSRF defences.
- Non-safelisted CORS requests need preflight permission; cached permission can avoid another OPTIONS exchange.
- Never reflect arbitrary origins with credentials, never trust `null`, match exactly, and send `Vary: Origin`.

## Further reading
- [Same-origin policy — MDN](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)
- [Cross-Origin Resource Sharing (CORS) — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Fetch Standard: CORS protocol — WHATWG](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [Exploiting CORS misconfigurations — PortSwigger](https://portswigger.net/research/exploiting-cors-misconfigurations-for-bitcoins-and-bounties)
- [Window.postMessage() — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
