---
id: crypto-password-peppers
sourceLesson: crypto-passwords-kdfs
title: Keep a pepper outside the password database
level: advanced
minutes: 3
summary: A pepper protects a stolen database only while its separate secret remains unavailable.
---

Password hashing assumes a stolen database can be attacked offline. A separately held pepper adds a secret dependency, but also creates key-management obligations: the pepper must be backed up, protected and rotated safely.

## Peppers and other defences

A **pepper** is a secret key applied to every password, for example an HMAC of the password keyed with the pepper, computed before Argon2id. The stored record is then the Argon2id hash of that peppered value, with the usual per-user salt:

```formula reference
x = HMAC(K_pep, P)
h = Argon2id(x, S)
where
x: the peppered password
HMAC: HMAC-SHA256, keyed with its first argument
K_pep: the pepper, a secret key kept outside the database
P: the user's password
h: the stored password hash
Argon2id: the slow, memory-hard password hash, with its usual parameters
S: the user's random salt, stored next to h
In words: mix in a secret the database never holds, then hash slowly with a per-user salt as usual.
```

Unlike the salt it is *not* stored in the database: it lives in a secrets manager or HSM. If attackers steal only the database (say, through SQL injection), a strong unavailable pepper prevents ordinary offline password-only verification. It does not help if they can guess the pepper or use a compromised application as an oracle. The cost is operational: lose or rotate the pepper carelessly and nobody can log in.

> [!analogy] Real-world analogy: Deposit boxes that also need the bank's key
> A bank's deposit boxes each need two keys: the customer's own key and a guard key that never leaves the vault office. A burglar who empties the customers' key drawer still cannot open a single box without the guard key.
>
> **How it maps:** The key drawer is the stolen password database (salted hashes), and the guard key is the pepper held in a secrets manager or HSM. Offline guessing needs the pepper for every guess, so a database-only theft cannot even start.
>
> **Where it stops:** A burglar who takes over the vault office itself, which here means compromising the running application, can use the guard key just as staff do. And if the bank loses its only guard key, no customer can open their box: losing the pepper locks every user out.

Password hashing is the last line of defence. It slows cracking after a breach; it doesn't stop weak passwords from being guessed online. Combine it with rate limiting, checks against known-breached passwords, and multi-factor authentication.

## Key takeaways
- A pepper protects a stolen database only while its separate secret remains unavailable.
- Combine password hashing with online rate limits, breached-password checks and multi-factor authentication.

## Further reading
- [OWASP: Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [RFC 9106: Argon2](https://www.rfc-editor.org/rfc/rfc9106)
