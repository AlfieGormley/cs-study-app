---
id: web-origin-boundaries
title: Origins, sites and readable data
level: basic
minutes: 3
sourceLesson: web-sop-cors
summary: Origins isolate reads; cross-origin requests can still reach a server.
---

You are logged into your bank in one tab and reading a dodgy blog in another. Your browser holds the bank's session cookie. If the blog's JavaScript could simply `fetch("https://bank.example/api/balance")` and read the reply, every site you visited could read every other site you were logged into.

The **same-origin policy** (SOP) is the browser rule that stops this. It is the foundation that almost all of web security sits on, so the rest of this module keeps coming back to it.

## What an origin is

For ordinary HTTP(S) URLs, a **web origin** compares the normalised **scheme, host and port**; an explicit default port and its omitted form are equivalent. Documents can instead have opaque origins, including sandboxed documents without same-origin permission. Identical `null` serialisations do not make distinct opaque origins equal.

| URL (vs `https://shop.example`) | Same origin? |
|---|---|
| `https://shop.example/cart` | Yes (path ignored) |
| `http://shop.example` | No: scheme |
| `https://api.shop.example` | No: host |
| `https://shop.example:8443` | No: port |

The path, query string and fragment play no part. A subdomain is a different origin, even though it feels like "the same site".

For the domain-based HTTP(S) examples here, a looser idea, the **schemeful site**, is the scheme plus the *registrable domain* (the "eTLD+1", such as `shop.example` or `example.co.uk`). `https://api.shop.example` and `https://www.shop.example` are **cross-origin but same-site**. Origins govern who can *read* what; sites govern when cookies are sent (the later SameSite cookie unit). Keep the two apart.

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

- **Writes are usually allowed.** Links, redirects and HTML form submissions can target any origin. This is why CSRF (the later CSRF units) is possible.
- **Embedding is usually allowed.** `<img>`, `<script src>`, `<link rel=stylesheet>`, `<video>` and `<iframe>` can load cross-origin resources. The kind of resource, CORS mode, CSP, CORP/COEP, framing policy and other checks affect loading. Classic scripts differ from module scripts, which require CORS for cross-origin loading. Successful embedding alone does not grant unrestricted response-byte access.
- **Reads are blocked.** Without the applicable permission, script cannot read a cross-origin `fetch` response or iframe DOM. Drawing an image without the required CORS permission can taint a canvas and prevent pixel readback. CORS-approved images can preserve readback.

> [!warning] The SOP is not server-side protection
> A simple request can reach the server even when its response is unreadable. A failed required preflight can prevent the actual request; other browser policies can block sending too. The browser just hides the reply from the calling page. Tools like `curl` ignore the SOP completely. Never rely on it to protect an endpoint; that is the job of authentication and authorisation.

### A note on embedding scripts

`<script src="https://other.example/lib.js">` runs that file *with the including page's origin*. That is why including third-party scripts is a big trust decision: the script can do anything your own code can. It is also why old APIs that returned sensitive data as runnable JavaScript (JSONP) leaked it to any site that included them.

## Key takeaways
- For HTTP(S) URLs compare normalized scheme, host and port; paths do not affect origin.
- A schemeful site is a different boundary used by cookie policies.
- Read restrictions do not replace server authentication, authorisation or CSRF checks.

## Further reading
- [HTML Standard: origins](https://html.spec.whatwg.org/multipage/browsers.html#origins)
- [Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
