---
id: secf-factors-password-failures
title: Factors and password failure modes
level: intermediate
minutes: 3
sourceLesson: secf-authentication
summary: Count factor categories rather than prompts.
---

Authentication answers one question: *is this really the account holder?* Everything else in security depends on it. If an attacker can authenticate as your administrator, your access control, encryption and audit logs are all working for them.

## The three factors

| Factor | Something you... | Examples |
|---|---|---|
| Knowledge | know | Password, PIN |
| Possession | have | Security key, phone |
| Inherence | are | Fingerprint, face |

**Multi-factor authentication (MFA)** combines factors from *different* categories. A password plus a security question is still single-factor: both are knowledge, and both can be phished or found in a data breach together.

The point of MFA is independence: stealing a password from a breach dump doesn't give the attacker your phone. Its effectiveness depends on the authenticator and attack path; account recovery and session theft need separate protection.

> [!analogy] Real-world analogy: a bank card and PIN
> A cash machine needs your card and your PIN. A pickpocket with your card lacks the PIN; someone who watched you type the PIN lacks the card.
>
> **How it maps:** The card is a possession factor and the PIN a knowledge factor. They are usually stolen in different ways, so one theft alone is not enough: that independence is the point of MFA. Asking for a PIN and then your postcode would add a prompt, not a factor.
>
> **Where it stops:** A skimmer fitted to a fake or tampered cash machine can capture the card data and the PIN in one go, much as a real-time phishing page can collect a password and a one-time code together. Independence depends on the attack path, not only on the factor labels.

> [!note] Biometrics are not secrets
> Your face is on social media and your fingerprints are on every glass you hold. Biometrics work well as a *local* unlock (the phone checks your fingerprint, then uses a key stored in secure hardware). They work badly as a password sent to a server, because you can't change them after a leak.

## Why passwords fail

Passwords are cheap and universal, but they fail in predictable ways:

- **Password reuse.** One breached site's passwords are tried on every other site. This is **credential stuffing**, and it works because a substantial fraction of people reuse passwords.
- **Guessability.** People choose `123456`, names, sports teams and keyboard walks.
- **Phishing.** A convincing fake login page collects the password directly.
- **Theft from servers.** Badly stored password databases leak in plaintext or as fast hashes.

Password reuse can permit account takeover without cracking the target service's password database.

## Key takeaways
- Count factor categories rather than prompts.
- Biometrics work as activation evidence, not replaceable secrets.
- Password reuse, guessing, phishing and server theft are different paths.

## Further reading
- [NIST SP 800-63B-4: authentication](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
