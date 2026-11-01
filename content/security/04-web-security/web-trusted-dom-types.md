---
id: web-trusted-dom-types
title: Trusted Types and XSS blast radius
level: intermediate
minutes: 3
sourceLesson: web-xss
summary: Audit Trusted Types policies and retain protection beyond direct cookie readability.
---

Output encoding, sanitisation and CSP each cover part of the XSS problem. This unit adds a browser feature aimed at DOM XSS, then looks at ways to limit the damage when XSS happens anyway.

## Trusted Types

DOM XSS happens when some line of client code passes an attacker-influenced string to a sink such as `innerHTML`. In a large app there can be hundreds of such lines, and reviewing each one is hard.

**Trusted Types** turns that around. With the CSP directive `require-trusted-types-for 'script'`, a supporting browser refuses plain strings at covered sinks: HTML insertion such as `innerHTML`, script text, and script URLs. Those sinks then accept only typed objects, such as `TrustedHTML`, which can be created only by a named **policy**: a small function, usually wrapping a sanitiser such as DOMPurify.

- **Without a default policy**, assigning a plain string to a covered sink throws a `TypeError`.
- **With a default policy**, the browser passes plain strings through that policy instead, so its code decides what happens.
- **Review moves to the policies.** A `TrustedHTML` value is only as safe as the policy that made it, so restrict which policy names may be created (the `trusted-types` directive) and audit those policies and their callers. A sanitiser library may need its own named policy allowed deliberately.

Trusted Types does not sanitise anything by itself; it forces every risky value through code you chose. MDN lists it as supported across current major browsers since February 2026 (it shipped in Chromium-based browsers in 2020). Older browsers ignore the directive, so it must not be your only defence.

> [!analogy] Real-world analogy: cheques need a countersignature
> A bank teller who will pay any handwritten note is easy to fool. A teller who pays only cheques stamped by the firm's finance desk forces every payment through one checkpoint.
>
> **How it maps:** The teller is a DOM sink, the handwritten note is a plain string, and the stamp is a `TrustedHTML` object that only a policy (the finance desk) can issue. Reviewers can then audit the desk rather than every teller.
>
> **Where it stops:** The stamp is only as good as the desk's checks: a policy that returns its input unchanged stamps anything. And a default policy is like a desk that stamps every note automatically, so its checks must be strict.

## Limiting the blast radius

- **HttpOnly cookies** stop script reading the session cookie. Useful, but the attacker's script can still send requests *as* the user from inside the page, with the cookie attached automatically, and read the replies. XSS remains critical.
- **Separate origins** for user-uploaded content (Google uses `googleusercontent.com`) mean script in an uploaded file runs in a throwaway origin with nothing to steal.
- The old `X-XSS-Protection` header is obsolete; modern browsers removed the filter it controlled. Don't rely on it.

## Key takeaways
- Enforced Trusted Types rejects plain strings at covered sinks unless a default policy converts them.
- A `TrustedHTML` value is only as safe as its policy; restrict and audit policy creation.
- HttpOnly hides a cookie from script but does not stop injected script acting as the user.
- Host untrusted uploads on a separate origin, and do not rely on obsolete XSS filters.

## Further reading
- [Trusted Types specification](https://www.w3.org/TR/trusted-types/)
- [MDN: Trusted Types API](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
