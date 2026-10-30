---
id: pki-mistakes-pq-migration-time
title: Planning for harvest now, decrypt later
level: advanced
minutes: 2
sourceLesson: pki-mistakes-pq
summary: Secrecy lifetime and migration duration must both enter a quantum-risk planning scenario.
---

Quantum migration planning does not need a forecast of the arrival date. It asks whether the time your data must stay secret, plus the time your migration will take, is already longer than the time you might have.

### When to care: harvest now, decrypt later

Nobody knows when, or whether, a cryptographically relevant quantum computer will arrive. A reliable arrival date cannot be supplied here; planning uses explicit scenarios rather than a forecast. The decision rule, often called **Mosca's inequality**, is:

```formula essential
x + y > z
where
x: how many years the data must stay secret (its shelf life)
y: how many years it will take to migrate your systems to post-quantum cryptography
z: how many years until a cryptographically relevant quantum computer exists; an estimate, since nobody knows
>: is greater than
In words: if the data's secrecy period plus your migration time is longer than the time until quantum computers arrive, data encrypted near the end of your migration will still need to be secret when it can be broken, so you are already late.
```

For example, in a hypothetical planning scenario, records that must stay secret for 10 years, a 5-year migration and a 12-year quantum estimate give 15 years of required protection against 12 years of assumed safety. Traffic recorded in the last few years of the migration could still be sensitive when it becomes decryptable, so migration should already have started.

The inequality is a planning model, not a forecast: all three numbers are estimates, and z is the most uncertain.

Recorded traffic whose confidentiality depends on classical RSA or DH key establishment can become decryptable with a sufficiently capable quantum computer. This motivates early **key-exchange** migration for records with long confidentiality requirements. **Signatures** also need early migration planning: long-lived devices, software-update trust anchors and archived signatures can outlast a transition. Recorded-traffic confidentiality and future authentication are distinct risks; one universal priority order is inappropriate.

## Key takeaways
- Secrecy lifetime and migration duration must both enter a quantum-risk planning scenario.
- Mosca’s inequality compares estimates rather than forecasting a quantum computer’s arrival.
- Recorded confidentiality and future signature authenticity require distinct prioritisation.

## Further reading
- [NIST IR 8547: Transition to Post-Quantum Cryptography Standards](https://csrc.nist.gov/pubs/ir/8547/final)
- [Post-quantum cryptography — Wikipedia](https://en.wikipedia.org/wiki/Post-quantum_cryptography)
