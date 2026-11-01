---
id: web-csrf-request-intent
title: Cookies do not establish request intent
level: intermediate
minutes: 4
sourceLesson: web-csrf
summary: Classic CSRF depends on eligible ambient credentials and an accepted attacker-triggered action.
---

CORS and the SOP control what a page can *read*, and XSS runs code inside an origin. **Cross-site request forgery** (CSRF) exploits a different mistake: treating a credential that the browser attaches automatically as proof that the user meant to act.

The SOP stops a hostile page reading another origin's responses, but it does not stop ordinary cross-origin form submissions. The attacker can't see your bank's replies, but they don't need to. They only need the bank to *act* on a request.

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

The browser submits the form to the bank. If the browser's cookie rules (SameSite and others, covered later) allow it, the session cookie goes with it. If the endpoint accepts these predictable fields with no CSRF check or extra confirmation, it performs the transfer.

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

The root cause: **possession of the session cookie does not establish user intent**. A server that relies on the cookie alone cannot tell this request from a real one.

> [!analogy] Real-world analogy: a franking machine in the post room
> An office's post room stamps every outgoing letter with the company's franking mark, automatically. The bank accepts any letter carrying that mark as a genuine company instruction. A visitor slips a fake "please pay £500" letter into the outgoing tray; it gets franked like the rest.
>
> **How it maps:** The franking mark is the session cookie, which the browser attaches to every eligible request. The fake letter is the attacker's form. The bank checks the mark, not who wrote the letter.
>
> **Where it stops:** The visitor never sees the bank's reply, matching CSRF's blindness. Real post rooms don't vary their stamping by who wrote a letter, whereas browsers can withhold cookies on cross-site requests (SameSite). The fix in both cases is a check the faker cannot copy, such as a reference number known only to genuine letters: the CSRF token of the next unit.

### What CSRF can and cannot do

- It can trigger any action the victim is allowed to take, as long as the attacker can predict the parameters and the endpoint has no effective CSRF check or extra confirmation.
- Classic CSRF is a **blind attack**: the SOP stops the attacker reading the response. A separate CORS flaw, XSS or information leak would change that.
- It rides on **ambient credentials**: cookies (or similar, such as HTTP authentication) that the browser sends automatically. An API that accepts only a bearer token added by its own JavaScript, with no ambient alternative, is not exposed to classic CSRF.
- **Client-side CSRF** is a different route: input the attacker controls (for example in the URL) tricks the legitimate app's own JavaScript into sending an authenticated request. Bearer tokens do not prevent that.

> [!example] Login CSRF
> A twist: the attacker logs the victim into the *attacker's* account. The victim then saves a card or searches for something, and the attacker later sees it in their own account history. No logged-in victim is needed, so login forms need CSRF protection too.

## Rule zero: GET must be safe

HTTP defines GET, HEAD, OPTIONS and TRACE as **safe methods**: a request with them must not ask the server to change state for the user. (Incidental effects such as logging are fine.)

If `GET /transfer?to=attacker&amount=500` moves money, a link the victim clicks, or a redirect, is enough. SameSite Lax won't help, because Lax still sends cookies on top-level GET navigations (a later unit). Where cookies are sent on subresource requests, even an `<img>` tag can trigger it. Use POST, PUT, PATCH or DELETE for state changes, with CSRF protection.

## Key takeaways
- The SOP can hide a response while an accepted request still changes state.
- A session cookie proves who the browser belongs to, not what the user intended.
- Keep GET safe, and protect login as well as authenticated actions.
- Bearer-only APIs avoid classic ambient-cookie CSRF, but client-side CSRF is a separate hazard.

## Further reading
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [HTTP semantics: safe methods](https://www.rfc-editor.org/rfc/rfc9110.html#name-safe-methods)
