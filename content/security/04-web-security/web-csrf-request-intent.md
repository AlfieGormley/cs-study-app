---
id: web-csrf-request-intent
title: Cookies do not establish request intent
level: intermediate
minutes: 3
sourceLesson: web-csrf
summary: Classic CSRF depends on eligible ambient credentials and an accepted attacker-triggered action.
---

CORS and SOP control browser reads, while XSS runs inside an origin. CSRF exploits a different trust mistake: treating an automatically attached credential as proof that the user intended an action.

The same-origin policy generally prevents a hostile page reading another origin’s responses, but does not prevent ordinary cross-origin form submissions. **Cross-site request forgery** (CSRF) abuses exactly that gap. The attacker can't see your bank's responses, but they don't need to. They only need the bank to *act* on a request.

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
- In the classic form it is a **blind attack**: SOP prevents reading the response. A separate CORS flaw, XSS or information leak can change that assumption.
- Classic authenticated CSRF abuses **ambient credentials** such as cookies sent automatically. An API accepting only a JavaScript-supplied bearer token avoids that mechanism if there is no ambient-authentication alternative. However, **client-side CSRF** can trick the legitimate application’s JavaScript into issuing an authenticated request using attacker-controlled input. Login CSRF also need not start with a logged-in victim.

> [!example] Login CSRF
> A twist: the attacker logs the victim into the *attacker's* account. The victim then saves a card or searches for something, and the attacker later sees it in their own account history. Login forms need CSRF protection too.

## Rule zero: GET must be safe

If `GET /transfer?to=attacker&amount=500` moves money, a link the victim clicks (or a redirect) is enough, and SameSite Lax won't help, because Lax still sends cookies on top-level GET navigations (see below). An image request can also trigger an unsafe GET if the browser sends eligible credentials. HTTP defines GET, HEAD, OPTIONS and TRACE as **safe methods**: their requested semantics must never perform a state-changing operation for the user. Incidental logging is permitted. Use POST, PUT, PATCH or DELETE for such operations, with CSRF protection.

## Key takeaways
- SOP can hide a response while an accepted request still changes state.
- Keep requested GET semantics safe and protect login as well as authenticated actions.
- Bearer-only APIs avoid classic ambient-cookie CSRF under their stated assumptions, but client-side CSRF is a separate hazard.

## Further reading
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [HTTP semantics: safe methods](https://www.rfc-editor.org/rfc/rfc9110.html#name-safe-methods)
