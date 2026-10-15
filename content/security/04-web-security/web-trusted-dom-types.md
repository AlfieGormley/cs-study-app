---
id: web-trusted-dom-types
title: Trusted Types and XSS blast radius
level: intermediate
minutes: 3
sourceLesson: web-xss
summary: Audit Trusted Types policies and retain protection beyond direct cookie readability.
---

The preceding units covered output encoding, sanitisation and CSP script permissions. Trusted Types concentrates review at DOM injection policy boundaries; cookie flags and content-origin separation limit different parts of the damage.

### Trusted Types

For DOM XSS, the CSP directive `require-trusted-types-for 'script'` enforces Trusted Types at covered injection sinks in supporting browsers. Without an applicable default Trusted Types policy, ordinary strings passed to innerHTML are rejected. A default policy may instead convert strings. TrustedHTML is only as safe as the policy that creates it; restrict policy creation and audit policies, callers and downstream transformations. A sanitizer may need its own documented internal Trusted Types policy; if policy creation is restricted, review and allow the required names deliberately. Covered sinks can include script text and script URLs as well as HTML insertion. Chromium-based browsers have supported it since 2020; check current support in other browsers.

## Limiting the blast radius

- **HttpOnly cookies** stop script reading the session cookie. Useful, but the attacker's script can still make requests *as* the user from inside the page, so XSS remains critical.
- **Separate origins** for user-uploaded content (Google uses `googleusercontent.com`) mean script in an uploaded file runs in a throwaway origin.
- The old `X-XSS-Protection` header is obsolete; modern browsers removed the filter it controlled. Don't rely on it.

> [!note] Evidence limits
> The historical worm’s exact infection count and time are omitted because no independent measurement was established here. Framework protections and browser CSP/Trusted Types support depend on version and configuration; no complete cross-browser compatibility or exploit-success claim is supplied.

## Key takeaways
- Trusted Types enforcement rejects ordinary strings at covered sinks when no default policy converts them.
- TrustedHTML safety depends on the policy and every later transformation.
- HttpOnly hides a cookie from script but does not prevent same-origin authenticated actions.
- Separate untrusted content origins and retire obsolete XSS-filter assumptions.

## Further reading
- [Trusted Types specification](https://www.w3.org/TR/trusted-types/)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
