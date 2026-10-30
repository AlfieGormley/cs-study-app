---
id: crypto-password-salts-cost
sourceLesson: crypto-passwords-kdfs
title: Salts, offline guessing and memory cost
level: advanced
minutes: 4
summary: Salts prevent reuse of precomputed work across distinct accounts but are not secrets.
---

## The password problem

Human-chosen passwords are often much more guessable than uniformly random cryptographic keys. If an attacker steals your user table, they will try to recover passwords **offline**, on their own hardware, with no rate limits. Your job is to make each guess as expensive as possible.

Here is how storage has evolved:

| Storage | What goes wrong |
|---|---|
| Plaintext | One breach reveals everything |
| Encrypted | Whoever obtains or can use the decryption key can recover passwords |
| `sha256(pw)` | Fast to brute-force; rainbow tables |
| `sha256(salt + pw)` | Still deliberately fast; no password-specific work factor |
| Argon2id, scrypt, bcrypt | Each guess is slow and costly |

### Salts

A **salt** is a random value (16 bytes is typical) generated per user and stored next to the hash. It means:

- Different salts prevent direct equality matching and reuse of one computed hash across accounts. But a password learned from one account remains a valuable candidate for others.
- Precomputed **rainbow tables** (precomputed hash chains supporting time/memory trade-offs) cannot be reused directly across sufficiently large, distinct salts, because the attacker would need a separate table for every salt.

Salts are not secret. They don't make a single guess slower; they force the attacker to attack each account separately.

### Slowness (work factor)

SHA-256 is built for speed, which is exactly what an offline attacker wants: every candidate password costs them one fast hash.

A password hash is built to be slow, with a tunable **work factor**. Suppose one verification takes 100 ms on your server. One sequential verifier can then check about ten candidates a second, so a list of a million candidates takes it about 28 hours instead of a fraction of a second.

That figure is a cost per guess, not a cap on the attacker. Attackers bring their own hardware and run many guesses in parallel, so a stolen table is still attacked at whatever rate they can afford. What the work factor does is multiply the price of every guess, for every account. Benchmark on your own production hardware and choose the highest cost your login latency and capacity allow.

### Memory-hardness

Attackers use GPUs and custom ASICs with thousands of cores. If a hash needs only CPU time, these cores run it massively in parallel. A **memory-hard** function also makes each guess use a deliberate amount of memory, set by its parameters; practical password settings allocate from about 19 MiB (OWASP's Argon2id minimum) to hundreds of mebibytes per guess. Memory is expensive to replicate across thousands of cores, so this blunts the attacker's hardware advantage.

> [!analogy] Real-world analogy: A stolen crate of combination padlocks
> A thief steals a crate of thousands of combination padlocks, each set by its owner. If every lock were the same model, a pre-printed book showing what the mechanism looks like for each popular combination would let the thief read off many combinations at a glance. If each lock is a slightly different model, the same combination looks different inside each one, so the book is useless and every lock must be tried separately. If each dial is also stiff, every try costs time, and a lock that needs a full workbench per attempt limits how many tries can run side by side.
>
> **How it maps:** Each padlock is one stored password hash and its owner's combination is the password. The book is a rainbow table or any precomputed list of hashes. The model number stamped on each lock is the salt: public, but it makes the same password hash differently for every account. The stiff dial is the work factor, and the workbench each attempt needs is memory-hardness.
>
> **Where it stops:** A stolen database can be copied to thousands of machines and attacked in parallel, which a crate of physical locks cannot. And none of this helps a lock set to `1234`: a common password is tried early whatever the cost per try.

## Key takeaways
- Salts prevent reuse of precomputed work across distinct accounts but are not secrets.
- Tunable time and memory costs raise offline guessing costs without imposing a universal attacker rate.

## Further reading
- [OWASP: Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [RFC 9106: Argon2](https://www.rfc-editor.org/rfc/rfc9106)
