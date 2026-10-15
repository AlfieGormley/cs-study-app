---
id: web-csp-script-trust
title: Script trust with a strict CSP
level: intermediate
minutes: 3
sourceLesson: web-xss
summary: A nonce policy and strict-dynamic constrain script execution without repairing unsafe output.
---

An encoding mistake can survive review. Content Security Policy adds browser enforcement around script execution. This unit explains the policy and its Flask header hook; the next unit checks nonce randomness and reuse.

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
3. In a supporting browser, matching nonces permit inline or external script elements. Under this policy, unapproved parser-inserted scripts, inline event handlers and javascript URLs are blocked; strict-dynamic also permits eligible non-parser-inserted script elements, including dynamically created inline scripts under the current CSP3 matching algorithm. Trusted-code gadgets or nonce leakage can still defeat the intended boundary.
4. `'strict-dynamic'` permits eligible non-parser-inserted script elements and ignores host/scheme allowlists in supporting implementations. The current CSP3 inline matching algorithm also permits a non-parser-inserted script’s inline text. This does not enable eval or string-valued timers; those have separate checks. Audit loaders and script-building code so neither URLs nor source text are attacker-controlled.
5. `object-src 'none'` blocks browser plugins; `base-uri 'none'` stops an injected `<base>` tag re-pointing relative script URLs.

```python
import secrets
# Fragment: app and g are Flask objects.

@app.after_request
def csp(resp):
    # Match this response’s script nonces.
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
    # New random bytes for this response.
    g.csp_nonce = secrets.token_urlsafe(16)
```

The template must put the same generated value in each intended script element. The shown r4nd0mB64 string is only a placeholder; the Python code generates 16 random bytes per request. Registration must happen before serving requests.

## Key takeaways
- CSP is an additional execution boundary; context-aware encoding remains necessary.
- A matching nonce permits its script, while strict-dynamic can permit eligible non-parser-inserted script elements, including inline text.
- Generate a fresh nonce per response and place its matching value in header and intended script elements.

## Further reading
- [Content Security Policy Level 3](https://www.w3.org/TR/CSP3/)
- [Google: strict CSP](https://web.dev/articles/strict-csp)
