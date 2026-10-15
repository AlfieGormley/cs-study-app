---
id: app-dns-poisoning-models
title: "DNS spoofing races and guessing-space models"
level: intermediate
minutes: 5
sourceLesson: app-dns-wire
summary: "Forged UDP responses must match the outstanding query and race the legitimate answer."
---

## Cache poisoning

A recursive resolver caches answers for their TTL. If an attacker gets a forged answer accepted, later matching lookups may receive poisoned cached data until expiry or replacement. Other caches, record types, validation and application authentication affect the result. That is **cache poisoning**.

For ordinary outstanding UDP queries, necessary response-matching checks include:

- the question (name, type, class),
- the transaction **ID**,
- the source IP and port it sent to, arriving at the **source port** it sent from.

An off-path attacker cannot see the query, so they must guess. With a fixed source port, if all other checked fields are known and the ID is uniform, each distinct guess has the same small chance of matching:

```formula
p_1 = 1 / 2^16 = 1 / 65,536
where
p_1: the probability that one forged response carries the right DNS transaction ID
^: "to the power of": 2^16 is 16 copies of 2 multiplied together
In words: a 16-bit ID has 65,536 possible values, so one blind guess matches once in 65,536 tries.
```

Acceptance also depends on racing the real response and passing other checks.

### The Kaminsky attack (2008)

A simple vulnerable-resolver model offers a race only when a target name's cached answer expires. Dan Kaminsky's 2008 technique avoids that wait by causing fresh lookups and attempting to replace delegation data:

1. Make the resolver look up a fresh random name unlikely to have a cached answer: `x71.bank.example`.
2. Race the real answer with a flood of forged responses with guessed IDs.
3. Each forged response says "I don't know `x71`, but the name server for **bank.example** is `ns.bank.example` at **192.0.2.66**" (attacker-controlled), in the authority and additional sections.
4. If a forged response wins and its delegation records are admitted, the vulnerable resolver caches the attacker's server for the target zone.
5. If none wins, try `x72.bank.example` immediately. There is no TTL to wait for.

Under the following deliberately simplified model, attempts succeed or fail independently, so the chance that *every* attempt fails is the per-attempt failure chance raised to the power of the number of attempts. Setting the overall success chance to one half and solving for the number of attempts gives:

```formula
p = g / 2^16
p = 100 / 65,536 ≈ 0.00153
1 − (1 − p)^n = 0.5
n = ln(0.5) / ln(1 − p)
n ≈ 453.9 ≈ 454
n ≈ 0.693 / p ≈ 454
where
p: the probability that one attempt succeeds, about 0.153%
g: the number of distinct forged IDs the attacker races in per attempt; here 100
n: the number of independent attempts needed for a 50% overall chance of success
^: "to the power of"; (1 − p)^n is n copies of (1 − p) multiplied together
ln: the natural logarithm, which turns "to the power of n" into "times n" so n can be solved for. For small p, ln(1 − p) is very close to −p, and ln(0.5) ≈ −0.693, which gives the quick estimate n ≈ 0.693 / p
≈: approximately equal to
In words: with a 0.15% chance per attempt, about 454 fresh attempts give an even chance of a successful cache poisoning.
```

This is probability arithmetic, not a measured attack duration; resolver caching and checks can change feasibility.

## Key takeaways
- Forged replies must match outstanding-query fields and beat the legitimate answer.
- The independent ID-guess model estimates attempts, not real attack duration.

## Further reading
- [RFC 5452](https://www.rfc-editor.org/rfc/rfc5452)
