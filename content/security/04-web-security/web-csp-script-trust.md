---
id: web-csp-script-trust
title: Script trust with a strict CSP
level: intermediate
minutes: 4
sourceLesson: web-xss
summary: A nonce policy and strict-dynamic constrain script execution without repairing unsafe output.
---

A missed output-encoding step can survive review. **Content Security Policy** (CSP) adds a second line of defence: a response header telling the browser which scripts it may run, so that a missed bug is much harder to exploit. Encoding is the cure; CSP is the seatbelt.

## Allowlists versus nonces

An old-style **allowlist** policy names trusted hosts:

```
script-src 'self' cdn.example.com
```

The weakness is that it trusts *everything* on those hosts. If an allowed host serves a JSONP endpoint or an old library with script gadgets, an attacker who can inject HTML loads that file and steers it into running their code. Google's 2016 study of about 26,000 distinct real-world policies found that 14 of the 15 hosts most often allowlisted for scripts served such unsafe endpoints, and that about three-quarters of the policies could be bypassed through their allowlists. Those figures are a historical snapshot, but the mechanism still applies to any host allowlist.

The recommended alternative is a **strict CSP** built on nonces (a hash-based strict policy is the other option). The policy value below is wrapped for display; in the real `Content-Security-Policy` header it is one line:

```
script-src 'nonce-r4nd0mB64'
  'strict-dynamic';
object-src 'none'; base-uri 'none'
```

How it works:

1. On every response, the server generates a fresh, unguessable **nonce** (at least 128 bits from a CSPRNG).
2. Each legitimate script tag carries it: `<script nonce="r4nd0mB64">`.
3. The browser runs a script element, inline or external, only if its nonce matches. Injected `<script>` tags without the nonce, inline event handlers such as `onclick`, and `javascript:` URLs are all blocked.
4. `'strict-dynamic'` passes trust on: a trusted script may create further script elements with `document.createElement` and they run without a nonce. This keeps script loaders working. In supporting browsers it also makes the policy ignore host allowlists. It does not allow `eval` or string timers, which CSP controls separately.
5. `object-src 'none'` blocks browser plugins; `base-uri 'none'` stops an injected `<base>` tag re-pointing relative script URLs.

Limits remain. If a trusted script builds a script URL or script text from attacker-controlled data, `strict-dynamic` lets that through; audit loaders for this. A nonce that leaks to the attacker, or trusted-code gadgets, can also defeat the policy.

> [!analogy] Real-world analogy: tonight's wristband versus a company guest list
> One venue admits "anyone from Acme Ltd or Bolt Ltd". Another stamps a different coloured wristband on invited guests each night, and staff admit only that night's colour. A guest with a wristband may bring a friend in personally.
>
> **How it maps:** The company list is an allowlist CSP: anyone from an allowed host gets in, including someone that host lets through by mistake (JSONP, gadgets). The nightly wristband is a per-response nonce, and the guest bringing a friend is `strict-dynamic` trusting scripts created by an already-trusted script.
>
> **Where it stops:** Staff check only the wristband, not the person's behaviour. A nonce proves the server placed the script, not that the script is harmless, and a trusted script that "brings in" attacker-chosen code passes too.

## Setting it in Flask

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

The template must put the same value in each intended script element. The `r4nd0mB64` string above is only a placeholder; this code generates 16 fresh random bytes per request. The next unit looks at that size and at what happens when a nonce repeats.

## Key takeaways
- CSP is an extra execution boundary; context-aware encoding is still required.
- Host allowlists trust everything an allowed host serves; a nonce trusts only scripts this response marked.
- `strict-dynamic` extends trust to scripts created by trusted scripts, so loaders must not take script URLs or text from attackers.

## Further reading
- [Content Security Policy Level 3](https://www.w3.org/TR/CSP3/)
- [Google: strict CSP](https://web.dev/articles/strict-csp)
