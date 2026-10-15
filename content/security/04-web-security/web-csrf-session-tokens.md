---
id: web-csrf-session-tokens
title: Session-bound CSRF tokens and cookie injection
level: intermediate
minutes: 4
sourceLesson: web-csrf
summary: Reject missing tokens and bind double-submit validation to the authenticated session.
---

The previous unit established that a session cookie alone proves no user intent. Token checks add a value that a hostile origin cannot normally read. These illustrative Flask hooks assume registered application objects and do not replace maintained framework CSRF integration.

## Defence 1: anti-CSRF tokens

The **synchroniser token** pattern gives the legitimate page a secret that the attacker's page can't know:

1. When the session is created, the server generates a random token (a CSPRNG value, 128+ bits) and stores it in the session.
2. Legitimate state-changing forms and JS requests to the protected application include it in a hidden field or custom header. Never send it to an untrusted destination.
3. On every state-changing request, the server checks the submitted token matches the session's.

The attacker can make the browser send the cookie, but can't read your page to learn the token (the SOP blocks that read), so their faked request fails.

Vulnerable:

```python
# BAD: login does not establish intent.
@app.post("/transfer")
@login_required
def transfer():
    do_transfer(current_user,
                request.form["to"],
                request.form["amount"])
    return "ok"
```

Illustrative Flask hook (assumes `app`, `session`, `request` and `abort` are imported/configured). Render `csrf_token()` into protected forms and rotate the session/token at authentication boundaries. Flask’s default session is a signed client cookie, not a server-side session store. Prefer a maintained CSRF integration in production.

```python
import hmac, secrets

def csrf_token():
    # Retain a token for this session.
    if "csrf" not in session:
        session["csrf"] = \
            secrets.token_urlsafe(32)
    return session["csrf"]

@app.before_request
def check_csrf():
    if request.method in (
            "GET", "HEAD", "OPTIONS"):
        return
    # Prefer the form token, else a header.
    sent = (request.form.get("csrf")
        or request.headers.get(
            "X-CSRF-Token", ""))
    want = session.get("csrf")
    # no token in session: reject too,
    # or "" == "" would pass
    if (not isinstance(want, str)
            or not want
            or not want.isascii()
            or not sent.isascii()):
        abort(403)
    # ASCII, non-empty expected token above.
    if not hmac.compare_digest(sent, want):
        abort(403)
```

`hmac.compare_digest` avoids content-dependent short-circuit comparison; type or length differences may still affect timing. Its string inputs must be ASCII, so the hook rejects non-ASCII input rather than raising an exception. Django’s generated project enables `CsrfViewMiddleware`; Spring Security enables CSRF protection by default for unsafe methods. Check the framework integration and configuration used by your application.

How big is the token in this hook? `secrets.token_urlsafe(32)` draws 32 random bytes, and each byte is 8 bits:

```formula
b = 8n_bytes
b = 32 × 8
b = 256 bits
256 bits ≥ 128 bits
where
b: the token's size in bits: how many independent random yes/no choices it contains
n_bytes: how many random bytes the generator draws; here 32
8: the number of bits in one byte
≥: is greater than or equal to
bits: the unit of information; one bit is a single 0 or 1
In words: 32 random bytes give a 256-bit token, twice 128 bits; guessing resistance assumes uniformly generated secret bytes and appropriate online controls.
```

Practical attacks may instead bypass guessing entirely: it is stealing or planting a token, which is what the next section is about. A longer token does nothing against those.

### Double-submit cookies

If you can't keep server-side session state, the **double-submit** pattern puts the token in a cookie *and* in the request body or header, and checks they match. The attacker can't read the cookie to copy it into the form.

The naive version has a weakness: an attacker who controls any sibling subdomain (or a man-in-the-middle on plain HTTP) may be able to *set* a cookie for your domain, choosing both values. OWASP recommends the **signed double-submit** variant: bind a fresh random value and session-specific data into an HMAC with a server secret, and verify the HMAC as well as the submitted value. A valid token for another session must never work. In browsers enforcing cookie prefixes, `__Host-` forbids `Domain` and requires `Secure` and `Path=/`, preventing a sibling subdomain from planting that named parent-domain cookie. This does not isolate different ports on the same host.

## Key takeaways
- A protected state-changing request needs an independently checked token.
- Reject absent/empty session tokens before comparing ASCII values.
- A signed double-submit token must bind to session-specific data; equality alone does not prevent planting.
- Host-prefixed cookies and HTTPS/HSTS address scoped injection threats, without replacing token validation.

## Further reading
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [Python hmac.compare_digest](https://docs.python.org/3/library/hmac.html#hmac.compare_digest)
- [Flask sessions](https://flask.palletsprojects.com/en/stable/quickstart/#sessions)
