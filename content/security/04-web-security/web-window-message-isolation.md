---
id: web-window-message-isolation
title: Cross-origin messages and isolation headers
level: intermediate
minutes: 3
sourceLesson: web-sop-cors
summary: Window messages need explicit sender checks; isolation headers control different relationships.
---

Including a cross-origin *script* runs its code inside your origin. Embedding a cross-origin *page* in an iframe is different: the frame keeps its own origin, and neither side can read the other's DOM. When they need to talk, they use a deliberate messaging channel.

## postMessage

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

- **Sender:** name the exact target origin. With `"*"`, the message goes to whatever page is currently loaded in that window, which may have navigated somewhere hostile.
- **Receiver:** any window holding a reference to yours can send it messages. Check `e.origin` against the exact expected origin, check `e.source` is the window you expect, and validate the message's shape.
- **Payload:** even from a trusted sender, treat the data as untrusted input. Passing it to `innerHTML` or `eval` turns a messaging bug into XSS (a later unit).

## Isolation headers

Side-channel attacks such as Spectre showed that a page might read memory belonging to cross-origin resources loaded into the same process. Newer response headers let a site ask for stronger isolation. Each one controls a different relationship:

| Header | Controls |
|---|---|
| `Cross-Origin-Resource-Policy` (CORP) | Which origins or sites may load this resource in no-cors mode (for example as an image or script) |
| `Cross-Origin-Opener-Policy` (COOP) | Whether cross-origin pages that open this one (or that it opens) share its browsing context group |
| `Cross-Origin-Embedder-Policy` (COEP) | What this page may embed: `require-corp` loads only resources that allow it via CORS or CORP; `credentialless` loads no-cors resources without credentials |

You may also see the old `document.domain` trick, where two subdomains both set `document.domain = "example.com"` to become same-origin. It weakens isolation, and modern Chrome makes the setter do nothing by default. Don't build on it.

Behaviour of these headers and of `document.domain` still varies by browser version, so test against the browsers you support.

## Key takeaways
- postMessage crosses origin boundaries on purpose: name the target origin when sending, and check origin, source window and payload when receiving.
- Third-party scripts run in the including page's origin, while a cross-origin iframe's DOM stays isolated.
- CORP, COOP and COEP constrain different relationships: who may embed a resource, who shares a window group, and what a page may embed.

## Further reading
- [HTML Standard: origins](https://html.spec.whatwg.org/multipage/browsers.html#origins)
- [HTML Standard: cross-document messaging](https://html.spec.whatwg.org/multipage/web-messaging.html#web-messaging)
