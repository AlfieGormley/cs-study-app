---
id: web-csp-nonce-entropy
title: Nonce randomness, text length and reuse
level: intermediate
minutes: 3
sourceLesson: web-xss
summary: Random bytes establish nonce unpredictability; Base64 text length adds no entropy.
---

The previous unit generated each CSP nonce with `secrets.token_urlsafe(16)` and put it in the policy and the script tags. A nonce works only while the attacker cannot know it, so two things matter: how hard it is to guess, and whether it is ever reused.

## How big is big enough?

CSP Level 3 says a nonce should contain at least 128 bits of randomness, counted *before* encoding, from a cryptographically secure generator. `token_urlsafe(16)` draws 16 random bytes, which is exactly 128 bits. There are so many possible values that a blind guess has no realistic chance of success.

Those bytes are then written as text in **URL-safe Base64**, which uses 4 characters for every 3 bytes and drops the `=` padding. So the nonce appears as a 22-character string.

```formula reference
b = 8n_bytes
n_chars = ⌈(4n_bytes) / 3⌉
where
b: the nonce's randomness in bits; one bit is a single random 0 or 1
n_bytes: how many random bytes the generator produces; 16 for token_urlsafe(16)
8: the number of bits in one byte
n_chars: how many characters the Base64 text has, without padding
4 / 3: Base64 writes 4 characters for every 3 bytes, because each character carries 6 bits
⌈ ⌉: the ceiling: round up to the next whole number, because a part-used character still has to be written
In words: 16 random bytes give 128 bits of randomness and are written as 22 Base64 characters; the longer text adds no extra randomness.
```

The randomness comes from the bytes, not from the length of the text. A 22-character nonce built from a predictable value (a timestamp, a counter) would be worthless, however long it looks. The earlier `r4nd0mB64` was only a 9-character placeholder.

## Reuse is the real danger

Guessing is not how nonces usually fail. Reuse is:

> [!warning] Common CSP mistakes
> - A **static nonce** reused on every response is just a password printed on the page. An attacker reads it from any page and puts it on their injected script tag. Generate a new one per response.
> - **Caching** a page together with its nonce header serves the same pair to many users, so the nonce becomes reusable across those responses. Either generate fresh headers and HTML per response, or use a hash-based CSP for static pages.
> - Adding `'unsafe-inline'` without an effective nonce or hash weakens inline-script protection. `'unsafe-eval'` separately allows string-to-code execution. Neither switches off the rest of the policy.

Roll out with `Content-Security-Policy-Report-Only` first. The browser does not enforce a report-only policy; it only reports what it *would* have blocked (if reporting is configured), so you can find legitimate inline scripts before you switch to enforcement.

## Key takeaways
- A nonce needs at least 128 random bits; 16 random bytes provide exactly that.
- URL-safe Base64 writes those bytes as 22 characters without adding randomness.
- Never let a nonce repeat, whether fixed in code or frozen in a cached page; report-only mode does not block anything.

## Further reading
- [Content Security Policy Level 3](https://www.w3.org/TR/CSP3/)
- [Python secrets](https://docs.python.org/3/library/secrets.html)
- [RFC 4648: Base64](https://www.rfc-editor.org/rfc/rfc4648)
