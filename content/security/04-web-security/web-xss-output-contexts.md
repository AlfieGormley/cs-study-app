---
id: web-xss-output-contexts
title: Output contexts and framework escape hatches
level: intermediate
minutes: 3
sourceLesson: web-xss
summary: Choose validation and encoding for the actual destination of each untrusted value.
---

The preceding unit traced source-to-sink bugs. The next step is choosing the right treatment for each sink: a value safe as HTML text is not automatically safe as a URL, script or style value.

## Context-aware output encoding

The right encoding depends on *where* in the document the value lands. HTML escaping helps in ordinary HTML text and safe quoted attributes, but is not a universal encoder.

```
<p>HERE</p>          HTML body
<input value="HERE"> quoted attribute
<a href="HERE">      URL attribute
<script>x = HERE     JavaScript
<style>... HERE      CSS
```

- **Ordinary HTML text and safe quoted attributes**: HTML-escape. Event-handler attributes, style, srcdoc and URL values need their own restrictions; quoting alone does not make their semantics safe. Always quote attributes; an unquoted attribute can be broken out of with a space.
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

Rich-text comments or a WYSIWYG editor need *some* HTML. Escaping would display that markup as literal text rather than preserve its formatting, so you **sanitise** instead: parse the HTML and keep only an allowlist of tags and attributes. Use a maintained library (DOMPurify in the browser, `nh3` in Python) and never a home-made regex. Sanitise as close to output as possible, since what is safe depends on where it is used.

## Key takeaways
- HTML text escaping does not validate URL schemes or serialize inline JavaScript.
- Use safe JSON serialization for script data and quoted escaped attributes for data attributes.
- Review bypass APIs and sanitise allowed rich HTML with a maintained parser-based library.

## Further reading
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [Jinja: tojson](https://jinja.palletsprojects.com/en/stable/templates/#jinja-filters.tojson)
