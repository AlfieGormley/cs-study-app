---
id: web-xss-data-flows
title: XSS from persisted input and DOM sources
level: intermediate
minutes: 4
sourceLesson: web-xss
summary: Keep attacker-influenced text from becoming executable page structure.
---

The earlier browser-isolation units explained where an origin’s authority applies. XSS attacks that authority from inside the page’s origin rather than asking another origin for permission.

The same-origin policy (the earlier origin-boundary unit) protects one origin from another. **Cross-site scripting** (XSS) sidesteps it completely: the attacker gets their script to run *inside your origin*. From there it can do anything your own JavaScript can do: read the page, call your APIs with the user's cookies, change their email address, or show a fake login form on your real domain.

In the OWASP Top 10 2025 edition, XSS is covered by **A05 Injection**, because at heart it is the same bug as SQL injection: data is mixed into code without being kept separate.

## The core bug

A web page is code (HTML, and JavaScript inside it). If you build that code by pasting in untrusted strings, some of those strings can change its structure.

```python
@app.get("/search")
def search():
    q = request.args.get("q", "")
    # BAD: q is pasted into HTML
    return f"<h1>Results for {q}</h1>"
```

If `q` is `shoes`, the page says "Results for shoes". If `q` contains a `<script>` element, the browser has no way to know that part was meant to be text. Without an independent execution restriction such as CSP, it parses the value as markup and can run the script.

The fix is **output encoding**: encode the value for the place it is going, so that special characters become harmless text:

```python
from markupsafe import escape

@app.get("/search")
def search():
    q = request.args.get("q", "")
    # Encode for this HTML text context.
    return ("<h1>Results for "
            f"{escape(q)}</h1>")
```

`escape` turns `<` into `&lt;`, `>` into `&gt;`, `&` into `&amp;` and both quote characters into HTML entities. The browser now *displays* the angle brackets instead of parsing them. In practice you'd use a template engine that does this automatically (below).

## Three flavours

Where the payload lives (stored versus reflected) and insertion mechanism (server versus client/DOM) are different axes. Stored data can cause DOM-based XSS too. The table gives common examples, not exclusive categories.

| Type | Payload lives in | Inserted by |
|---|---|---|
| Reflected | The request (URL) | Server |
| Stored | Persisted data, e.g. database | Server or client JS |
| DOM-based | URL, storage, etc. | Client JS |

### Reflected XSS

The malicious input is part of the request and is echoed straight back in the response, as in the search example. Delivery may use a crafted link, form submission or another request trigger. The payload is reflected from that request rather than stored for later delivery.

### Stored XSS

The input is saved (a comment, a display name, a support ticket) and served to everyone who views it. No crafted link is needed and it can spread. The **Samy worm** of 2005 was stored XSS in MySpace profiles: the script could copy itself into a viewing user’s profile under the vulnerable site/browser conditions. It is a historical example of script propagation through profile content.

Stored XSS in admin tools is especially nasty: an attacker submits a "support ticket" and the script runs when a privileged employee opens it.

### DOM-based XSS

In DOM-based XSS, client-side JavaScript reads attacker-influenced data (a **DOM XSS source**) and writes it into a dangerous API (a **sink**).

```javascript
// BAD: hash flows into innerHTML
const name = decodeURIComponent(
  location.hash.slice(1));
greeting.innerHTML = "Hi " + name;
```

```javascript
// GOOD: treated as text, never parsed
greeting.textContent = "Hi " + name;
```

A URL fragment is not included in the ordinary HTTP request target. In this example it reaches the sink entirely in the client, so escaping response values on the server does not fix the flow. A page can explicitly transmit fragments later; server-supplied CSP can also limit execution. Fix the unsafe client sink.

Common sources and sinks:

| Sources | Dangerous sinks |
|---|---|
| `location.hash` / `.search` | `innerHTML`, `outerHTML` |
| `document.referrer` | `document.write` |
| `postMessage` data | `eval`, `setTimeout(str)` |
| `localStorage` | `el.href = ...` (URLs) |

For the following browser behaviour, assume no enforcing policy independently blocks the event handler.

A detail people trip on: inserting a `<script>` element via `innerHTML` does **not** run it, but inserting an element with an event-handler attribute (such as an `onerror` on an image that fails to load) does. "We use innerHTML but scripts don't execute" is not a defence.

## Key takeaways
- Stored versus reflected and DOM insertion describe different axes and can overlap.
- HTML output encoding protects the shown server text context.
- For plain DOM text use textContent; server escaping cannot repair an independent client-side sink.

## Further reading
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP DOM XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)
