---
id: net-rendering-error-layers
title: "Extra origins and request failures"
level: basic
minutes: 3
summary: "Relate rendering requests and error symptoms to the layer that needs investigation."
sourceLesson: net-request-lifecycle
---
Receiving HTML is the start of rendering, not the end of the page’s network activity. Each unrelated origin repeats the connection setup from the earlier lessons, and when something fails, the shape of the error tells you which layer to investigate.

## Rendering and the requests it triggers

The browser parses the HTML and discovers more resources: CSS, JavaScript, images, fonts and API calls. A page may make many additional requests; the count depends on the page. Many go to the same origin and reuse the connection; others go to new origins (a CDN, an analytics domain), each paying its own DNS + TCP + TLS cost.

Setup for different origins can run in parallel, so extra origins don't simply add their costs end to end. But the browser only starts that setup once it discovers the resource while parsing, so the setup often lands on the critical path. This is why front-end engineers use hints like `<link rel="preconnect">` (start setup early) and why consolidating origins (reuse a warm connection) can help.

## Failure modes along the path

Every hop can fail, and each failure looks different to the user:

- **DNS failure:** "server not found" (`NXDOMAIN` or timeout). The 2016 Dyn attack took down Twitter, GitHub and others this way.
- **TCP failure:** "connection refused" (the host answered with a reset because nothing is listening on that port) or a timeout (a firewall silently dropping packets, or a dead host). Refused is fast; a timeout can hang for many seconds, which is why client connect timeouts matter.
- **TLS failure:** certificate warnings, often from an expired certificate.
- **HTTP failure:** a `502 Bad Gateway` reports an invalid upstream response; a `504 Gateway Timeout` reports an upstream timeout. Inspect backend health, the network and proxy configuration; the status alone does not prove which component is faulty.

Knowing which layer produced an error is the first step in debugging production incidents.

## Key takeaways

- Resources on new unrelated origins may each require fresh DNS, TCP and TLS setup.
- A refused connection and a silent timeout suggest different transport failure behaviours.
- A 502 identifies an invalid upstream response; it does not prove which backend or proxy is faulty.

## Further reading

- [How browsers work (MDN)](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work)
- [HTTP semantics: 502 and 504 (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110)
