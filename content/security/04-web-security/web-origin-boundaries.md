---
id: web-origin-boundaries
title: Origins, sites and readable data
level: basic
minutes: 4
sourceLesson: web-sop-cors
summary: Origins isolate reads; cross-origin requests can still reach a server.
---

You are logged into your bank in one tab and reading a dodgy blog in another. Your browser holds the bank's session cookie. If the blog's JavaScript could simply `fetch("https://bank.example/api/balance")` and read the reply, every site you visited could read every other site you were logged into.

The **same-origin policy** (SOP) is the browser rule that stops this. Almost all of web security builds on it, so the rest of this module keeps coming back to it.

## What an origin is

For ordinary HTTP(S) URLs, a **web origin** is the **scheme, host and port**. Two URLs are same-origin only if all three match. A default port written out (`:443` for HTTPS) counts the same as leaving it out.

| URL (vs `https://shop.example`) | Same origin? |
|---|---|
| `https://shop.example/cart` | Yes (path ignored) |
| `http://shop.example` | No: scheme |
| `https://api.shop.example` | No: host |
| `https://shop.example:8443` | No: port |

The path, query string and fragment play no part. A subdomain is a different origin, even though it feels like "the same site".

Some documents get an **opaque origin** instead, for example a sandboxed iframe that is not granted same-origin status. An opaque origin is written as `null`, but two separately created opaque origins are not the same origin, even though both print as `null`.

A looser boundary, the **schemeful site**, is the scheme plus the *registrable domain* (the "eTLD+1", such as `shop.example` or `example.co.uk`). So `https://api.shop.example` and `https://www.shop.example` are **cross-origin but same-site**. Origins govern who can *read* what; sites govern when cookies are sent (the later SameSite unit). Keep the two apart.

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

The diagram assumes the page asked for credentials (`credentials: "include"`) and that the browser's cookie rules allow the cookie. A plain cross-origin `fetch` sends no cookies at all.

Cross-origin interactions fall roughly into three groups:

- **Writes are usually allowed.** Links, redirects and HTML form submissions can target any origin. This is why CSRF (the later CSRF units) is possible.
- **Embedding is usually allowed.** `<img>`, `<script src>`, `<link rel=stylesheet>`, `<video>` and `<iframe>` can load cross-origin resources. Other rules can still stop a load: CSP, CORP/COEP, framing policy, and module scripts, which need CORS permission to load cross-origin. Embedding a resource does not give the page its raw bytes.
- **Reads are blocked.** Without permission, script cannot read a cross-origin `fetch` response or a cross-origin iframe's DOM. Drawing a cross-origin image without CORS permission taints a canvas, so the page cannot read its pixels back.

> [!analogy] Real-world analogy: an office mailroom
> Picture an office mailroom. Staff can post letters to any address, and parcels from outside can be put on display in the lobby. But when a reply comes back from another department, the clerk will not hand you its contents unless that department has said you may see them.
>
> **How it maps:** Your page is the member of staff, the browser is the clerk, and other origins are other departments. Sending (writes) and displaying (embedding) are allowed; handing over the contents of a reply (reads) needs the other side's permission, which is what CORS provides.
>
> **Where it stops:** A real clerk might refuse to post a suspicious letter. The SOP does not: the request still reaches the server and can change things there. And anyone who skips the mailroom (a script run with `curl`) is not bound by the clerk's rules at all.

> [!warning] The SOP is not server-side protection
> A simple cross-origin request can reach the server even though the page cannot read the reply. Some requests need an approved CORS preflight first (next unit), and other browser policies can block sending, but the SOP itself only hides replies. Tools like `curl` ignore it completely. Protect every endpoint with authentication and authorisation on the server.

### A note on embedding scripts

`<script src="https://other.example/lib.js">` runs that file *with the including page's origin*. That is why including a third-party script is a big trust decision: the script can do anything your own code can. It is also why old APIs that returned sensitive data as runnable JavaScript (JSONP) leaked it to any site that included them.

## Key takeaways
- For HTTP(S) URLs, an origin is scheme, host and port; paths do not matter.
- A schemeful site (scheme plus registrable domain) is a wider boundary used by cookie rules.
- The SOP hides cross-origin replies; it does not stop requests arriving, so servers still need authentication, authorisation and CSRF checks.

## Further reading
- [HTML Standard: origins](https://html.spec.whatwg.org/multipage/browsers.html#origins)
- [Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
