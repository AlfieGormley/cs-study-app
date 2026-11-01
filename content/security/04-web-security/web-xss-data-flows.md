---
id: web-xss-data-flows
title: XSS from persisted input and DOM sources
level: intermediate
minutes: 5
sourceLesson: web-xss
summary: Keep attacker-influenced text from becoming executable page structure.
---

The same-origin policy protects one origin from another. **Cross-site scripting** (XSS) sidesteps it completely: the attacker gets their script to run *inside your origin*. From there it can do anything your own JavaScript can do: read the page, call your APIs with the user's cookies, change their email address, or show a fake login form on your real domain.

The OWASP Top 10:2025 files XSS under **A05 Injection**, alongside SQL injection. At heart they are the same bug: untrusted data is pasted into code, and some of it is read as code.

## The core bug

A web page is code (HTML, and JavaScript inside it). If you build that code by pasting in untrusted strings, those strings can change its structure.

```python
@app.get("/search")
def search():
    q = request.args.get("q", "")
    # BAD: q is pasted into HTML
    return f"<h1>Results for {q}</h1>"
```

If `q` is `shoes`, the page says "Results for shoes". If `q` contains a `<script>` element, the browser cannot tell that this part was meant to be text. It parses the value as markup and, unless a separate control such as CSP blocks it, runs the script.

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

`escape` turns `<` into `&lt;`, `>` into `&gt;`, `&` into `&amp;` and both quote characters into HTML entities. The browser now *displays* the angle brackets instead of parsing them. In practice a template engine does this automatically (next unit).

### Why HTML gets encoding, not placeholders

For SQL injection, the best fix is a **parameterised query**: the query text and the data travel separately, so the database never parses the data as SQL. OWASP strongly discourages escaping as a substitute there, because escaping rules vary between databases and settings.

HTML has no equivalent placeholder for a server-built page: the browser receives one stream of text and parses all of it. So for HTML the defence is to encode each value correctly for where it lands, ideally via an auto-escaping template, or to insert it through a DOM API that never parses it as HTML (such as `textContent`, below). Validating input on arrival helps, but it cannot know every place a value will later be shown, so it does not replace output encoding.

> [!analogy] Real-world analogy: a mail-merge letter
> A company prints letters from a template: "Dear NAME, your order has shipped." A customer registers with the name "Sam. Please also refund £500 to account 1234". The printed letter now contains an instruction the company never wrote, and a staff member who follows the letter might act on it.
>
> **How it maps:** The template is your page's code and the name is untrusted data. XSS happens when the browser (the reader) cannot tell where the data ends and the template resumes. Output encoding is like printing the name in quotation marks that the reader is trained to treat as "just a name".
>
> **Where it stops:** A page mixes several languages (HTML, URLs, JavaScript, CSS), each with its own "quotation marks". Quoting that is correct for one is wrong for another, which is why encoding must match the context.

## Three flavours

Two separate questions describe an XSS bug: where the payload is kept (in the request, or stored), and what inserts it into the page (the server, or client-side JavaScript). The common names mix the two:

| Type | Payload lives in | Inserted by |
|---|---|---|
| Reflected | The request (URL) | Server |
| Stored | Persisted data, e.g. database | Server or client JS |
| DOM-based | URL, storage, etc. | Client JS |

These overlap: stored data inserted unsafely by client JavaScript is both stored and DOM-based.

### Reflected XSS

The malicious input is part of the request and is echoed straight back in the response, as in the search example. The attacker delivers it with a crafted link, form or other request; nothing is stored.

### Stored XSS

The input is saved (a comment, a display name, a support ticket) and served to everyone who views it. No crafted link is needed and it can spread. The **Samy worm** of 2005 was stored XSS in MySpace profiles: the script copied itself into the profile of each user who viewed an infected one.

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

The URL fragment (the part after `#`) is not sent to the server in an ordinary request. Here it travels from the address bar to the sink entirely inside the browser, so escaping on the server cannot fix it. Fix the client-side sink.

Common sources and sinks:

| Sources | Dangerous sinks |
|---|---|
| `location.hash` / `.search` | `innerHTML`, `outerHTML` |
| `document.referrer` | `document.write` |
| `postMessage` data | `eval`, `setTimeout(str)` |
| `localStorage` | `el.href = ...` (URLs) |

A detail people trip on: inserting a `<script>` element via `innerHTML` does **not** run it, but inserting an element with an event-handler attribute (such as an `onerror` on an image that fails to load) does, unless a policy such as CSP blocks inline handlers. "We use innerHTML but scripts don't execute" is not a defence.

## Key takeaways
- XSS is injection: untrusted data parsed as page code. Stored versus reflected, and server versus DOM insertion, are separate axes.
- Encode output for its HTML context (best done by an auto-escaping template); SQL's answer, parameterised queries, has no direct HTML equivalent.
- For plain text in the DOM use `textContent`; server escaping cannot repair a client-side sink.

## Further reading
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP DOM XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)
- [OWASP Top 10:2025 A05 Injection](https://owasp.org/Top10/2025/A05_2025-Injection/)
