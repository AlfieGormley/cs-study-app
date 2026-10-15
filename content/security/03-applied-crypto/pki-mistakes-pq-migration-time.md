---
id: pki-mistakes-pq-migration-time
title: Planning for harvest now, decrypt later
level: advanced
minutes: 2
sourceLesson: pki-mistakes-pq
summary: Secrecy lifetime and migration duration must both enter a quantum-risk planning scenario.
---

Cryptographic security depends on the complete construction and its implementation, including key generation, message authentication and correct nonce handling.

### When to care: harvest now, decrypt later

Nobody knows when, or whether, a cryptographically relevant quantum computer will arrive. A reliable arrival date cannot be supplied here; planning uses explicit scenarios rather than a forecast. The decision rule, often called **Mosca's inequality**, is:

```formula
x + y > z
where
x: how many years the data must stay secret (its shelf life)
y: how many years it will take to migrate your systems to post-quantum cryptography
z: how many years until a cryptographically relevant quantum computer exists; an estimate, since nobody knows
>: is greater than
In words: if the data's secrecy period plus your migration time is longer than the time until quantum computers arrive, data encrypted near the end of your migration will still need to be secret when it can be broken, so you are already late.
```

For example, with a hypothetical planning scenario of records that must stay secret for 10 years, a 5-year migration and a 12-year quantum estimate:

```formula
x + y = 10 + 5 = 15
15 > 12 = z
where
x: the secrecy period, 10 years
y: the migration time, 5 years
z: the assumed time until a quantum computer, 12 years
>: is greater than
In words: 15 years of exposure against 12 years of safety means traffic recorded in the last few years could still be sensitive when it becomes decryptable.
```

The inequality is a planning model, not a forecast: all three numbers are estimates, and z is the most uncertain.

Recorded traffic whose confidentiality depends on classical RSA or DH key establishment can become decryptable with a sufficiently capable quantum computer. This motivates early **key-exchange** migration for records with long confidentiality requirements. **Signatures** also need early migration planning: long-lived devices, software-update trust anchors and archived signatures can outlast a transition. Recorded-traffic confidentiality and future authentication are distinct risks; one universal priority order is inappropriate.

## Key takeaways
- Secrecy lifetime and migration duration must both enter a quantum-risk planning scenario.
- Mosca’s inequality compares estimates rather than forecasting a quantum computer’s arrival.
- Recorded confidentiality and future signature authenticity require distinct prioritisation.

## Further reading
- [Cryptographic storage guidance — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [NIST post-quantum project](https://csrc.nist.gov/projects/post-quantum-cryptography)
