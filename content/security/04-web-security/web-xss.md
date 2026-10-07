---
id: web-xss
title: XSS (stored, reflected, DOM) and CSP
level: intermediate
minutes: 14
summary: How attacker-controlled text ends up running as script in your users' browsers, why context-aware output encoding is the real fix, and how a strict Content Security Policy limits the damage when you miss one.
---

The same-origin policy (lesson 1) protects one origin from another. **Cross-site scripting** (XSS) sidesteps it completely: the attacker gets their script to run *inside your origin*. From there it can do anything your own JavaScript can do: read the page, call your APIs with the user's cookies, change their email address, or show a fake login form on your real domain.

In the OWASP Top10 2025 edition, XSS is covered by **A05 Injection**, because at heart it is the same bug as SQL injection: data is mixed into code without being kept separate.

## The core bug

A web page is code (HTML, and JavaScript inside it). If you build that code by pasting in untrusted strings, some of those strings can change its structure.

```python
@app.get("/search")
def search():
    q = request.args.get("q", "")
    # BAD: q is pasted into HTML
    return f"<h1>Results for {q}</h1>"
```

If `q` is `shoes`, the page says "Results for shoes". If `q` contains a `<script>` element, the browser has no way to know that part was meant to be text. It parses it as markup and runs it.

The fix is to **encode** the value for the place it is going, so that special characters become harmless text:

```python
from markupsafe import escape

@app.get("/search")
def search():
    q = request.args.get("q", "")
    return ("<h1>Results for "
            f"{escape(q)}</h1>")
```

`escape` turns `<` into `&lt;`, `>` into `&gt;`, `&` into `&amp;` and both quote characters into entities. The browser now *displays* the angle brackets instead of parsing them. In practice you'd use a template engine that does this automatically (below).

## Three flavours

Persistence (stored versus reflected) and insertion mechanism (server versus client/DOM) are different axes. Stored data can cause DOM-based XSS too. The table gives common examples, not exclusive categories.

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

In DOM-based XSS, client-side JavaScript reads attacker-influenced data (a **source**) and writes it into a dangerous API (a **sink**).

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

A URL fragment is not included in the ordinary HTTP request target. In this example it reaches the sink entirely in the client, so server-side escaping of response values does not fix the flow. A page can explicitly transmit fragments later; server-supplied CSP can also limit execution. Fix the unsafe client sink.

Common sources and sinks:

| Sources | Dangerous sinks |
|---|---|
| `location.hash` / `.search` | `innerHTML`, `outerHTML` |
| `document.referrer` | `document.write` |
| `postMessage` data | `eval`, `setTimeout(str)` |
| `localStorage` | `el.href = ...` (URLs) |

A detail people trip on: inserting a `<script>` element via `innerHTML` does **not** run it, but inserting an element with an event-handler attribute (such as an `onerror` on an image that fails to load) does. "We use innerHTML but scripts don't execute" is not a defence.

## Context-aware output encoding

The right encoding depends on *where* in the document the value lands. HTML escaping helps in ordinary HTML text and safe quoted attributes, but is not a universal encoder.

```
<p>HERE</p>          HTML body
<input value="HERE"> quoted attribute
<a href="HERE">      URL attribute
<script>x = HERE     JavaScript
<style>... HERE      CSS
```

- **Ordinary HTML text and safe quoted attributes**: HTML-escape. Event handlers, style, srcdoc and URL values need their own restrictions; quoting alone does not make their semantics safe. Always quote attributes; an unquoted attribute can be broken out of with a space.
- **URLs** (`href`, `src`): escaping is not enough. A value starting `javascript:` contains no special HTML characters yet runs code when clicked. Parse the URL and **allowlist schemes** (`https:`, `mailto:`).
- **Inside `<script>`**: HTML escaping is the wrong encoding. Serialise as JSON with a safe encoder (Jinja's `|tojson` escapes `<`, `>` and `&` so the value cannot close the script tag), or better, put data in a `data-` attribute and read it from JS.
- **CSS and event-handler attributes**: avoid putting untrusted data there at all.

### Let the framework do it

Modern template engines auto-escape for HTML by default: Jinja2 in Flask (for `.html` templates), Django templates, React JSX, Angular and Vue all treat interpolated values as text.

```
{# Jinja2: escaped automatically #}
<p>{{ comment.body }}</p>
```

Important review points include these **escape hatches**, alongside unsafe URLs, template injection, dependencies and framework-specific behaviour:

| Framework | Escape hatch |
|---|---|
| Jinja2 | `\|safe`, `Markup(...)` |
| Django | `\|safe`, `mark_safe` |
| React | `dangerouslySetInnerHTML` |
| Vue | `v-html` |
| Angular | `bypassSecurityTrust...` |

Grep for these in code review. Each one is a claim that the value is already safe, and it should come with a reason.

### When you must accept HTML

Rich-text comments or a WYSIWYG editor need *some* HTML. Escaping would destroy it, so you **sanitise** instead: parse the HTML and keep only an allowlist of tags and attributes. Use a maintained library (DOMPurify in the browser, `nh3` in Python) and never a home-made regex. Sanitise as close to output as possible, since what is safe depends on where it is used.

## Content Security Policy

Encoding is the cure. **Content Security Policy** (CSP) is the seatbelt: a response header telling the browser which scripts it may run, so that a missed bug is much harder to exploit.

An old-style allowlist policy names domains:

```
script-src 'self' cdn.example.com
```

Google’s 2016 study found widespread bypasses in its sampled policies, including allowed hosts serving exploitable libraries or JSONP. This is a historical sample, not a current universal deployment statistic. One recommended defence is a **strict nonce-based policy**; hash-based strict policies are another option. Below is a formatted policy value, joined with spaces in one Content-Security-Policy response header, not folded HTTP wire syntax:

```
script-src 'nonce-r4nd0mB64'
  'strict-dynamic';
object-src 'none'; base-uri 'none'
```

How it works:

1. On every response, the server generates a fresh, unguessable **nonce** (at least 128 bits from a CSPRNG).
2. Each legitimate script tag carries it: `<script nonce="r4nd0mB64">`.
3. In a supporting browser, matching nonces permit inline or external script elements. Under this policy, unapproved parser-inserted scripts, inline event handlers and javascript URLs are blocked; strict-dynamic also permits eligible non-parser-inserted external scripts. Trusted-code gadgets or nonce leakage can still defeat the intended boundary.
4. `'strict-dynamic'` permits eligible non-parser-inserted external scripts and ignores host/scheme allowlists in supporting implementations. Dynamic inline code still needs applicable permission; loaders must not use attacker-controlled URLs.
5. `object-src 'none'` blocks plugins; `base-uri 'none'` stops an injected `<base>` tag re-pointing relative script URLs.

```python
import secrets
# Fragment: app and g are Flask objects.

@app.after_request
def csp(resp):
    n = g.csp_nonce  # set per request
    resp.headers[
      "Content-Security-Policy"] = (
        f"script-src 'nonce-{n}' "
        "'strict-dynamic'; "
        "object-src 'none'; "
        "base-uri 'none'")
    return resp

@app.before_request
def make_nonce():
    g.csp_nonce = secrets.token_urlsafe(16)
```

The template must put the same generated value in each intended script element. The shown r4nd0mB64 string is only a placeholder; the Python generator supplies 16 random bytes. Registration must happen before serving requests.

> [!warning] Common CSP mistakes
> - A **static nonce** reused on every response is just a password printed on the page. Generate it per response.
> - Adding unsafe-inline without an effective nonce/hash weakens inline-script protection. Unsafe-eval separately enables string-to-code execution; neither means every other directive disappears.
> - Reusing cached HTML/header nonce pairs makes that nonce reusable across those responses. Use a suitable hash policy for static content or generate matching fresh headers and HTML per response.

Roll out with `Content-Security-Policy-Report-Only` first: the browser does not enforce that report-only policy; configured reporting may deliver violations, so you can find legitimate inline scripts before enforcing.

### Trusted Types

For DOM XSS, the CSP directive `require-trusted-types-for 'script'` enforces Trusted Types at covered injection sinks in supporting browsers. Without an applicable default policy, ordinary strings passed to innerHTML are rejected. A default policy may instead convert strings. TrustedHTML is only as safe as the policy that creates it; restrict policy creation and audit policies, callers and downstream transformations. Chromium-based browsers have supported it since 2020; check current support in other browsers.

## Limiting the blast radius

- **HttpOnly cookies** stop script reading the session cookie. Useful, but the attacker's script can still make requests *as* the user from inside the page, so XSS remains critical.
- **Separate origins** for user-uploaded content (Google uses `googleusercontent.com`) mean script in an uploaded file runs in a throwaway origin.
- The old `X-XSS-Protection` header is obsolete; modern browsers removed the filter it controlled. Don't rely on it.

> [!note] Evidence limits
> The historical worm’s exact infection count and time are omitted because no independent measurement was established here. Framework protections and browser CSP/Trusted Types support depend on version and configuration; no complete cross-browser compatibility or exploit-success claim is supplied.

## Key takeaways
- XSS lets attacker script run in your origin, defeating the SOP from inside.
- Stored/reflected describe persistence; DOM-based describes a client-side source-to-sink flow. These categories can overlap, and DOM sources need not be invisible to the server.
- The fix is context-aware encoding: HTML-escape for ordinary HTML text and safe quoted attributes, allowlist URL schemes, JSON-encode for scripts.
- Use auto-escaping templates and review every escape hatch (`|safe`, `dangerouslySetInnerHTML`, `v-html`). Sanitise with a library when you must allow HTML.
- A strict nonce-based CSP with `'strict-dynamic'`, plus Trusted Types, is defence in depth, not a replacement for encoding.

## Further reading
- [Cross Site Scripting Prevention Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [DOM based XSS Prevention Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)
- [Mitigate XSS with a strict CSP — web.dev](https://web.dev/articles/strict-csp)
- [Content Security Policy (CSP) — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [CSP Is Dead, Long Live CSP! (Google research, ACM CCS 2016)](https://research.google/pubs/csp-is-dead-long-live-csp-on-the-insecurity-of-whitelists-and-the-future-of-content-security-policy/)
- [Trusted Types API — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API)
