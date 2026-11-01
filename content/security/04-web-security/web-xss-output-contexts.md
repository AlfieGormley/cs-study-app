---
id: web-xss-output-contexts
title: Output contexts and framework escape hatches
level: intermediate
minutes: 4
sourceLesson: web-xss
summary: Choose validation and encoding for the actual destination of each untrusted value.
---

The previous unit traced untrusted data from a source to a sink. This one is about choosing the right treatment for each destination: a value that is safe as HTML text is not automatically safe as a URL, inside a script, or in CSS.

## Context-aware output encoding

The right encoding depends on *where* in the document the value lands. HTML escaping is correct for ordinary HTML text and quoted attribute values, but it is not a universal encoder.

```
<p>HERE</p>          HTML body
<input value="HERE"> quoted attribute
<a href="HERE">      URL attribute
<script>x = HERE     JavaScript
<style>... HERE      CSS
```

- **HTML text and ordinary quoted attributes**: HTML-escape. Always quote attributes; an unquoted attribute can be broken out of with a space.
- **URLs** (`href`, `src`): escaping is not enough. A value starting `javascript:` contains no special HTML characters yet runs code when clicked. Parse the URL and **allowlist schemes** (`https:`, `mailto:`).
- **Inside `<script>`**: HTML escaping is the wrong encoding. Serialise as JSON with an encoder that is safe inside HTML (Jinja's `|tojson` escapes `<`, `>`, `&` and `'` so the value cannot close the script tag). Better still, put the data in a `data-` attribute and read it from JS.
- **Event-handler attributes, `style`, CSS and `srcdoc`**: quoting does not make these safe, because their contents are themselves code or markup. Avoid putting untrusted data there at all.

### Let the framework do it

Modern template engines auto-escape for HTML by default: Jinja2 in Flask (for `.html` templates), Django templates, React JSX, Angular and Vue all treat interpolated values as text.

```
{# Jinja2: escaped automatically #}
<p>{{ comment.body }}</p>
```

Auto-escaping covers the HTML context only. Code review should still look for unsafe URLs, server-side template injection, vulnerable dependencies and, above all, these **escape hatches**:

| Framework | Escape hatch |
|---|---|
| Jinja2 | `\|safe`, `Markup(...)` |
| Django | `\|safe`, `mark_safe` |
| React | `dangerouslySetInnerHTML` |
| Vue | `v-html` |
| Angular | `bypassSecurityTrust...` |

Search for these in code review. Each one is a claim that the value is already safe, and it should come with a reason.

Frameworks differ in what else they catch. For example, React 19 replaces a `javascript:` URL in `href` or `src` with one that only throws an error, but older React versions did not block them. Check the version you use, and still apply your own URL scheme allowlist.

### When you must accept HTML

Rich-text comments or a WYSIWYG editor need *some* HTML. Escaping would show that markup as visible tags rather than apply its formatting, so you **sanitise** instead: parse the HTML and keep only an allowlist of tags and attributes. Use a maintained library (DOMPurify in the browser, `nh3` in Python), never a home-made regular expression. Sanitise as close to output as possible, since what is safe depends on where the HTML is used.

## Key takeaways
- HTML escaping fits HTML text and quoted attributes; it does not validate URL schemes or make data safe inside a script.
- Use a safe JSON serialiser for script data, and a scheme allowlist for URLs.
- Review every escape hatch, and sanitise rich HTML with a maintained parser-based library.

## Further reading
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [Jinja: tojson](https://jinja.palletsprojects.com/en/stable/templates/#jinja-filters.tojson)
