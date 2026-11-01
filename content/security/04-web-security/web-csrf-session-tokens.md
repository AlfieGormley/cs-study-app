---
id: web-csrf-session-tokens
title: Session-bound CSRF tokens and cookie injection
level: intermediate
minutes: 4
sourceLesson: web-csrf
summary: Reject missing tokens and bind double-submit validation to the authenticated session.
---

The previous unit showed that a session cookie alone proves no user intent. The classic fix adds a second value that the browser does *not* attach automatically and that a hostile site cannot read: an anti-CSRF token. The Flask hooks below are illustrations; in production, use your framework's maintained CSRF protection.

## Defence 1: anti-CSRF tokens

The **synchroniser token** pattern gives the legitimate page a secret that the attacker's page can't know:

1. The server generates a random token (from a CSPRNG, at least 128 bits) and stores it in the user's session.
2. Every legitimate state-changing form or JavaScript request includes it, in a hidden field or a custom header. Never send it to other sites.
3. On every state-changing request, the server checks that the submitted token matches the session's copy, and rejects the request if it is missing or wrong.

The attacker can make the browser send the cookie, but cannot read your page to learn the token (the SOP blocks that read), so their fake request fails.

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

Illustrative hook (assumes `app`, `session`, `request` and `abort` are set up). Render `csrf_token()` into protected forms, and issue a new session and token when the user logs in. Note that Flask's default session is a signed cookie stored in the browser, not a server-side session store.

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

Three details matter here:

- **Missing must mean reject.** If both the session and the request lack a token and the code defaults both to `""`, an empty-equals-empty comparison would pass.
- **`hmac.compare_digest`** compares without stopping at the first different character, so response timing does not reveal how much of a guess was right. It accepts only ASCII strings, so the hook rejects other input instead of crashing.
- **Size:** `token_urlsafe(32)` draws 32 random bytes, which is 256 bits, double the usual 128-bit minimum. Guessing is hopeless; practical attacks instead steal or *plant* a token, which a longer token does nothing to stop.

Frameworks usually do all of this for you: Django's generated projects enable `CsrfViewMiddleware`, and Spring Security enables CSRF protection for unsafe methods by default. Check that yours is switched on and configured.

## Double-submit cookies

If you can't keep server-side session state, the **double-submit** pattern puts the token in a cookie *and* in the request body or a header, and checks they match. The attacker can't read the cookie to copy it into their form.

The naive version has a weakness: an attacker who can *write* cookies for your domain can choose both values. That includes anyone controlling a sibling subdomain, or a network attacker injecting cookies over plain HTTP. OWASP therefore recommends the **signed double-submit** variant: the token combines a random value with session-specific data under an HMAC keyed with a server secret, and the server checks the HMAC against the *current* session. A token minted for another session (such as the attacker's own) then fails.

Two more layers help against planting:

- A cookie named with the `__Host-` prefix must be `Secure`, have `Path=/` and have no `Domain` attribute. Supporting browsers then refuse to let a sibling subdomain set it. (It does not separate different ports on the same host.)
- HTTPS everywhere, with HSTS, stops network attackers injecting cookies over plain HTTP.

## Key takeaways
- Every state-changing request needs an independently checked token; reject a missing or empty one before comparing.
- Token length defeats guessing, not theft or planting.
- Bind a double-submit token to the session with an HMAC; equality of two attacker-chosen values proves nothing.
- `__Host-` cookies and HTTPS with HSTS reduce cookie injection, without replacing token validation.

## Further reading
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [Python hmac.compare_digest](https://docs.python.org/3/library/hmac.html#hmac.compare_digest)
- [Flask sessions](https://flask.palletsprojects.com/en/stable/quickstart/#sessions)
