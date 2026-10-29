---
id: secf-password-policy
title: Password policy and online attack limits
level: intermediate
minutes: 3
sourceLesson: secf-authentication
summary: NIST distinguishes requirements from recommendations.
---

Online password policy shapes both resistance to guessing and whether people can use the service. Apply the requirements in the named NIST revision to its stated authentication context, then assess the remaining attack paths.


## Modern password policy (NIST SP 800-63B)

NIST SP 800-63B-4, the 2025 revision (checked October 2026), distinguishes mandatory requirements (SHALL) from recommendations (SHOULD). The following concerns centrally verified passwords, not local device-unlock PINs:

- **Length over complexity.** At least **15 characters** when the password is the only factor; at least 8 when it's part of MFA. Permitting at least 64 characters, printable ASCII and spaces, and Unicode are SHOULD recommendations.
- **No composition rules.** Don't demand "one uppercase, one symbol".
- **No periodic forced changes.** Force a change only on evidence of compromise.
- **Blocklist check.** Compare the entire proposed password against a blocklist of common, expected or compromised passwords. Do not reject a passphrase just because it contains a dictionary word as a substring.
- **Rate limiting.** Unless the authenticator type specifies otherwise, no more than 100 consecutive failures using a specific authenticator on one account before disabling that authenticator; in practice, use throttling and back-off well before that.
- **Managers and paste.** Verifiers SHALL allow password managers and autofill; they SHOULD permit paste when autofill APIs are unavailable.

> [!warning] Lockout is an availability trade-off
> Locking an account after 5 failures stops guessing, but lets anyone lock out your CEO, or every user, on purpose. Prefer progressive delays, per-IP and per-account throttling, and risk signals. A stuffing campaign may try only one or a few credentials per account across many accounts, so per-account thresholds alone can miss it.

## Key takeaways
- NIST distinguishes requirements from recommendations.
- Length, whole-password blocklists and usable managers replace composition rules.
- Per-account limits alone miss distributed credential stuffing.

## Further reading
- [NIST SP 800-63B-4: authentication](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
