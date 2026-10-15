---
id: secf-security-tradeoffs
title: Security trade-offs and evidence
level: basic
minutes: 3
sourceLesson: secf-cia-aaa
summary: Controls can reduce one risk while creating another.
---

## The properties pull against each other

Disconnecting a server can reduce remote exposure while taking its service offline. It does not prevent physical access or disclosure of existing copies. Real design evaluates the risks to each property.

- **Encryption** improves confidentiality but adds a key that, if lost, makes data permanently unavailable.
- **Account lockout** after failed logins protects confidentiality, but lets an attacker lock out every user on purpose (an availability attack).
- **Backups** protect availability, but each copy is another place the data can leak from.
- **Fail-closed** behaviour (deny on error) can protect confidentiality and integrity while blocking legitimate use; **fail-open** (allow on error) can preserve access while bypassing a control. Choose based on the failure and threat model.

> [!example] Which property matters most?
> Priorities depend on the system and threat model. For example:
> - Password reset tokens: confidentiality, plus integrity of the account binding and expiry checks.
> - A public software update channel: integrity and authenticity, so devices reject unauthorised releases.
> - A time-critical operational display: availability and integrity can both be essential.
> - A medical record: privacy, correct handling of changes and timely access all matter.

### Beyond three letters

The triad is a starting point, not the whole story. Commonly added properties:

- **Non-repudiation**: evidence that supports attribution of an action and helps resolve a later dispute. Individual credentials, protected records and signatures can contribute; no mechanism alone guarantees attribution to a person or a legal outcome.
- **Authenticity**: as above, the origin is genuine.
- **Privacy**: about people, not just data, including consent and purpose (GDPR territory).

The VERIS framework uses paired attributes from the **Parkerian hexad**: confidentiality/possession, integrity/authenticity and availability/utility. Losing control of an encrypted drive can affect possession without exposing its plaintext; losing its only decryption key affects utility.

## Key takeaways
- Controls can reduce one risk while creating another.
- Authenticity, privacy and non-repudiation add questions beyond the CIA triad.
- Priorities follow the threat model; they are not universal rankings.

## Further reading
- [NIST FIPS 199: security objectives](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.199.pdf)
- [VERIS security attributes](https://verisframework.org/attributes.html)
- [NIST SP 800-63B-4: authentication](https://pages.nist.gov/800-63-4/sp800-63b.html)
