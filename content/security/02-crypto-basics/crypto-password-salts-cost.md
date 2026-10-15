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

SHA-256 is built for speed.

> [!note] Content gap: cracking throughput
> No reproducible GPU or end-to-end password-guessing benchmark was supplied, so fixed rate claims are omitted. Quiz rates are explicitly hypothetical arithmetic inputs.

A password hash is built to be slow, with a tunable **work factor**. The arithmetic for one sequential verifier is simple:

```formula
r = 1 / t_hash
r = 1 / (0.1 s) = 10 per s
t_total = N / r
t_total = 10^6 / (10 per s) = 10^5 s
where
r: guesses checked per second by one sequential verifier
t_hash: the time for one hash, here 100 ms = 0.1 s
t_total: the time to try every candidate
N: the number of candidate passwords, here 10^6 (a million)
s: seconds; 10^5 s is about 27.8 hours
ms: milliseconds, thousandths of a second
In words: a 100 ms hash allows ten guesses a second per verifier, so a million candidates take about a day instead of a fraction of a second.
```

So a 100 ms hash means about ten sequential verifications per second on that measured setup. It does not cap an attacker at that rate: hardware, parallelism and implementation differ, and ideal identical independent workers could divide the elapsed time by their number if no shared bottleneck intervened. Real memory, bandwidth and coordination limits affect scaling. Benchmark your deployment and use memory-hard settings to raise offline attack costs.

### Memory-hardness

Attackers use GPUs and custom ASICs with thousands of cores. If a hash needs only CPU time, these cores run it massively in parallel. A **memory-hard** function uses memory as a deliberate cost resource; the amount depends on its definition and parameters. Practical password settings often allocate tens of mebibytes or more, but memory hardness alone does not impose that fixed minimum. Memory is expensive to replicate across thousands of cores, so this blunts the attacker's hardware advantage.

## Key takeaways
- Salts prevent reuse of precomputed work across distinct accounts but are not secrets.
- Tunable time and memory costs raise offline guessing costs without imposing a universal attacker rate.

## Further reading
- [OWASP: Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [RFC 9106: Argon2](https://www.rfc-editor.org/rfc/rfc9106)
