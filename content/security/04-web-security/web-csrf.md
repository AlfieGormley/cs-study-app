---
id: web-csrf
title: CSRF and SameSite
level: intermediate
minutes: 13
summary: Why browsers will happily send your users' cookies on requests that another site started, and the layered defences (tokens, SameSite cookies, Origin and Fetch Metadata checks) that stop it.
---

The same-origin policy generally prevents a hostile page reading another origin’s responses, but does not prevent ordinary cross-origin form submissions. **Cross-site request forgery** (CSRF) exploits exactly that gap. The attacker can't see your bank's responses, but they don't need to. They only need the bank to *act* on a request.

## The attack

You are logged in to `bank.example`, which uses a session cookie. You visit `evil.example`, which contains a hidden form:

```
<form action=
  "https://bank.example/transfer"
  method="POST">
  <input name="to" value="attacker">
  <input name="amount" value="500">
</form>
<script>
  document.forms[0].submit()
</script>
```

The browser submits the form to the bank. If cookie scope, SameSite and other browser policies permit the session cookie, it accompanies the submission. A vulnerable endpoint accepts the predictable fields without an independent CSRF check or confirmation and performs the transfer.

```
 evil.example     browser         bank
     |  form       |                |
     |------------>|                |
     |             | POST /transfer |
     |             | Cookie: sid=.. |
     |             |--------------->|
     |             |     200 OK     |
     |             |<---------------|
                          money moves
```

The root cause: **possession of the session cookie does not establish user intent**. A server relying on that cookie alone cannot distinguish these requests.

### What CSRF can and cannot do

- It can trigger authorised actions when the attacker can construct accepted parameters and the endpoint lacks effective CSRF checks or additional confirmation.
- In the classic attack it is **blind**: SOP prevents reading the response. A separate CORS flaw, XSS or information leak can change that assumption.
- Classic authenticated CSRF exploits **ambient credentials** such as cookies sent automatically. An API accepting only a JavaScript-supplied bearer token avoids that mechanism if there is no ambient-authentication alternative. However, **client-side CSRF** can trick the legitimate application’s JavaScript into issuing an authenticated request using attacker-controlled input. Login CSRF also need not start with a logged-in victim.

> [!example] Login CSRF
> A twist: the attacker logs the victim into the *attacker's* account. The victim then saves a card or searches for something, and the attacker later sees it in their own account history. Login forms need CSRF protection too.

## Rule zero: GET must be safe

If `GET /transfer?to=attacker&amount=500` moves money, a link the victim clicks (or a redirect) is enough, and SameSite Lax won't help, because Lax still sends cookies on top-level GET navigations (see below). An image request can also trigger an unsafe GET if the browser sends eligible credentials. HTTP defines GET, HEAD and OPTIONS as **safe**: their requested semantics must not perform the user’s state-changing operation. Incidental logging is permitted. Use POST, PUT, PATCH or DELETE for such operations, with CSRF protection.

## Defence 1: anti-CSRF tokens

The **synchroniser token** pattern gives the legitimate page a secret that the attacker's page can't know:

1. When the session is created, the server generates a random token (a CSPRNG value, 128+ bits) and stores it in the session.
2. Legitimate state-changing forms and JS requests to the protected application include it in a hidden field or custom header. Never send it to an untrusted destination.
3. On every state-changing request, the server checks the submitted token matches the session's.

The attacker can make the browser send the cookie, but can't read your page to learn the token (the SOP blocks that read), so their forged request fails.

Vulnerable:

```python
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
    if "csrf" not in session:
        session["csrf"] = \
            secrets.token_urlsafe(32)
    return session["csrf"]

@app.before_request
def check_csrf():
    if request.method in (
            "GET", "HEAD", "OPTIONS"):
        return
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
    if not hmac.compare_digest(sent, want):
        abort(403)
```

`hmac.compare_digest` avoids content-dependent short-circuit comparison; type or length differences may still affect timing. Its string inputs must be ASCII, so the hook rejects non-ASCII input rather than raising an exception. Django’s generated project enables `CsrfViewMiddleware`; Spring Security enables CSRF protection by default for unsafe methods. Check the framework integration and configuration used by your application.

### Double-submit cookies

If you can't keep server-side session state, the **double-submit** pattern puts the token in a cookie *and* in the request body or header, and checks they match. The attacker can't read the cookie to copy it into the form.

The naive version has a weakness: an attacker who controls any sibling subdomain (or a man-in-the-middle on plain HTTP) may be able to *set* a cookie for your domain, choosing both values. OWASP recommends the **signed** variant: bind a fresh random value and session-specific data into an HMAC with a server secret, and verify the signature as well as the submitted value. A valid token for another session must not work. In browsers enforcing cookie prefixes, `__Host-` forbids `Domain` and requires `Secure` and `Path=/`, preventing a sibling subdomain from planting that named parent-domain cookie. This does not isolate different ports on the same host.

## Defence 2: SameSite cookies

The `SameSite` cookie attribute tells the browser not to send a cookie on **cross-site** requests. Recall from lesson 1 that *site* means scheme + registrable domain, so `app.example.com` and `api.example.com` are same-site.

The following is a `Set-Cookie` value wrapped for display; join its lines with a space into one HTTP field value.

```
sid=abc; Secure; HttpOnly;
SameSite=Lax; Path=/
```

| Value | Cross-site requests that get the cookie |
|---|---|
| `Strict` | None at all |
| `Lax` | Top-level navigations with safe methods (clicking a link, a GET redirect) |
| `None` | SameSite imposes no restriction; other cookie policies still apply, and `Secure` is required |

So with `Lax`, the hidden-form POST from `evil.example` arrives **without** the session cookie, and the user appears logged out. With `Strict`, an initial navigation from a cross-site webmail page omits the cookie, so cookie-authenticated users can appear logged out on arrival; a common pattern is a `Lax` session cookie plus a `Strict` cookie required for sensitive actions.

### Browser defaults

Since 2020, Chrome (and other Chromium browsers) treat cookies **without** a `SameSite` attribute as `Lax`. Two caveats:

- To avoid breaking some single sign-on flows, Chrome makes an exception: a cookie without an explicit `SameSite` that is under **two minutes old** is still sent on top-level cross-site POSTs ("Lax+POST").
- Exact defaults and compatibility behavior are browser/version dependent. A verified Firefox/Safari version matrix is absent here; this lesson does not assert their current defaults.

So **set `SameSite` explicitly** rather than relying on the default.

```python
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
```

### Why SameSite alone isn't enough

- **Same-site attackers.** A compromised or taken-over subdomain (`old-blog.example.com`) is same-site with your app, so SameSite does nothing against it.
- **State-changing GETs.** `Lax` sends cookies on top-level GET navigations, so a GET that transfers money is still exploitable.
- **Old or unusual clients** may not honour the attribute.

OWASP recommends explicit CSRF protection in most deployments, with SameSite as another layer. Its guidance describes constrained cases where SameSite can serve as the primary defence; those require careful conditions rather than a universal guarantee.

## Defence 3: checking where the request came from

Browsers add headers the attacker's page cannot forge:

- **`Origin`** is supplied for many relevant requests, but can be absent or serialise as `null`. Validate an exact trusted origin and define a safe policy for missing/opaque origins, using independent CSRF protection.
- **`Sec-Fetch-Site`** in supporting browsers reports `same-origin`, `same-site`, `cross-site` or `none` (for example, address-bar or bookmark navigation). Availability depends on the client and context. Arbitrary non-browser clients can forge these headers; they are not authentication.

```python
SAFE = {"GET", "HEAD", "OPTIONS"}

@app.before_request
def fetch_metadata():
    site = request.headers.get(
        "Sec-Fetch-Site")
    if site is None:
        return  # still require token
    if request.method in SAFE:
        return
    if site not in ("same-origin",
                    "none"):
        abort(403)
```

This rejects many cross-site unsafe browser requests, but does not prevent same-origin XSS or client-side CSRF. Keep the token hook active independently, including when metadata is missing or `none`; the metadata policy is an additional filter.

## JSON APIs

A common belief is "our API takes JSON, so it's immune". It depends:

- If the server *requires* `Content-Type: application/json`, a cross-site request with that type is non-simple, so it is preflighted, and without permissive CORS the browser never sends it.
- If the server parses the body as JSON **regardless** of content type, an attacker can send a form with `enctype="text/plain"` crafted so the body happens to be valid JSON. That can be a simple request, delivered with any cookies allowed by browser policy.

So: check `Content-Type` strictly, or require a custom header such as `X-Requested-With` (which requires CORS preflight permission), and keep CORS tight.

## Related: clickjacking

Instead of forging a request, the attacker loads your real page in an invisible iframe and tricks the user into clicking a button on it. Tokens don't help, because the click happens on your genuine page. Prevent this framing with the `Content-Security-Policy` response header containing this policy value:

```
frame-ancestors 'none'
```

`frame-ancestors` is a CSP directive, not a standalone header. `X-Frame-Options: DENY` provides a legacy alternative. These controls address framing-based clickjacking; they do not prevent every form of deceptive UI.

## Evidence limits

A full browser/version compatibility matrix and live cross-browser attack testing are absent from this lesson. Browser-specific defaults must be checked for the supported clients; examples assume the credential and policy conditions stated above.

## Key takeaways
- Classic authenticated CSRF exploits eligible ambient credentials on attacker-triggered requests; SOP normally blocks response reads. Login CSRF and client-side CSRF require attention too.
- Keep GET safe. Protect every state-changing request, including login.
- Primary defence: framework anti-CSRF tokens (synchroniser, or signed double-submit). Compare in constant time.
- Set `SameSite=Lax` (or `Strict`) explicitly; it doesn't stop same-site attackers or unsafe GETs.
- Check `Origin` or `Sec-Fetch-Site` as a cheap stateless layer. Require `application/json` or a custom header on APIs, and block framing with `frame-ancestors`.

## Further reading
- [Cross-Site Request Forgery Prevention Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [SameSite cookies explained — web.dev](https://web.dev/articles/samesite-cookies-explained)
- [Set-Cookie: SameSite — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie)
- [Protect your resources with Fetch Metadata — web.dev](https://web.dev/articles/fetch-metadata)
- [Cross Site Request Forgery protection — Django docs](https://docs.djangoproject.com/en/stable/ref/csrf/)
- [Clickjacking Defense Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html)
