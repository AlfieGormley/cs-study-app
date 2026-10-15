---
id: web-window-message-isolation
title: Cross-origin messages and isolation headers
level: intermediate
minutes: 3
sourceLesson: web-sop-cors
summary: Window messages need explicit sender checks; isolation headers control different relationships.
---

Origins still matter after loading a resource. Script inclusion runs code in the including page’s origin; an embedded cross-origin page retains its own origin and needs a controlled messaging protocol.

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
  // Check shape before trusting a payload.
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
> How long each browser keeps preflight results, third-party-cookie policy and legacy origin relaxation vary by version and configuration. A complete browser compatibility matrix and universal exploit-success rates are absent because they were not reliably established. Wire examples are abbreviated; the Flask hooks need an application, authentication, cache policy and preflight handling.

## Key takeaways
- postMessage crosses origin boundaries deliberately: validate origin, expected window and payload.
- Third-party scripts run in the including page’s origin, while cross-origin iframe DOM stays isolated.
- CORP, COOP and COEP constrain different resource or window relationships.

## Further reading
- [HTML Standard: origins](https://html.spec.whatwg.org/multipage/browsers.html#origins)
- [HTML Standard: cross-document messaging](https://html.spec.whatwg.org/multipage/web-messaging.html#web-messaging)
