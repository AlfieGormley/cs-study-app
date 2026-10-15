---
id: web-csp-nonce-entropy
title: Nonce randomness, text length and reuse
level: intermediate
minutes: 3
sourceLesson: web-xss
summary: Random bytes establish nonce unpredictability; Base64 text length adds no entropy.
---

The previous unit generated one CSP nonce with secrets.token_urlsafe(16) and placed it into the policy and script tags. Here we inspect that size, its encoded representation and the effects of reuse.

Why 16 bytes? A nonce only protects you if an attacker cannot guess it, and CSP Level 3 recommends at least 128 bits before encoding for a nonce source. Each byte holds 8 bits, so:

```formula
b = 8n_bytes
b = 16 × 8
b = 128 bits
P_guess = 1 / 2^b
P_guess = 1 / 2^128
P_guess ≈ 2.9 × 10^{-39}
where
b: the nonce's size in bits: how many independent random yes/no choices it contains
n_bytes: how many random bytes the generator produces; here 16, from secrets.token_urlsafe(16)
8: the number of bits in one byte
P_guess: the probability that a single random guess matches the nonce, between 0 and 1
2^b: 2 raised to the power b, the number of different possible nonces
≈: approximately equal to (the result is rounded)
bits: the unit of information; one bit is a single 0 or 1
In words: 16 random bytes make a 128-bit nonce, and a single guess is right with probability about 3 in 10 to the power 39, under the uniform independent-guess model; exposure or reuse is a different risk.
```

The same bytes are then written as text. `token_urlsafe` uses URL-safe Base64, which turns every 3 bytes into 4 characters and drops the `=` padding:

```formula
n_chars = ⌈(4n_bytes) / 3⌉
n_chars = ⌈4 × 16 / 3⌉
n_chars = ⌈21.3⌉
n_chars = 22
where
n_chars: the number of characters in the nonce text that goes in the header and the script tags
n_bytes: the number of random bytes; here 16
4 / 3: Base64 writes 4 characters for every 3 bytes, because each character carries 6 bits and 3 × 8 = 4 × 6
⌈ ⌉: the ceiling: round up to the next whole number, because a part-used character still has to be written
In words: a 16-byte nonce appears as a 22-character string; the longer string carries no extra randomness.
```

The earlier policy’s r4nd0mB64 is a 9-character placeholder, far shorter than the generated 22-character value. The randomness comes from the 16 bytes, not from the length of the text.

> [!warning] Common CSP mistakes
> - A **static nonce** reused on every response is just a password printed on the page. Generate it per response.
> - Adding unsafe-inline without an effective nonce/hash weakens inline-script protection. Unsafe-eval separately enables string-to-code execution; neither means every other directive disappears.
> - Reusing cached HTML/header nonce pairs makes that nonce reusable across those responses. Use a suitable hash-based CSP for static content or generate matching fresh headers and HTML per response.

Roll out with `Content-Security-Policy-Report-Only` first: the browser does not enforce that report-only policy; configured reporting may deliver violations, so you can find legitimate inline scripts before enforcing.

## Key takeaways
- Sixteen uniformly random bytes provide 128 random bits.
- URL-safe Base64 writes those bytes in 22 characters without adding randomness.
- Do not reuse a fixed nonce or cached nonce/header pair; report-only policies do not enforce blocking.

## Further reading
- [Content Security Policy Level 3](https://www.w3.org/TR/CSP3/)
- [Python secrets](https://docs.python.org/3/library/secrets.html)
- [RFC 4648: Base64](https://www.rfc-editor.org/rfc/rfc4648)
