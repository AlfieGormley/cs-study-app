---
id: secp-detection-quality-and-noise
title: Behaviour detections and alert precision
level: intermediate
minutes: 4
sourceLesson: secp-detection-response
summary: Use the Pyramid of Pain and a base-rate calculation to reason about useful alerts.
---

A detector can match a particular file or infrastructure address, or it can look for how an intrusion operates. This unit compares those signals and calculates why a small false-positive rate can overwhelm a response team when harmless events greatly outnumber attacks.

### The pyramid of pain

Not all indicators are equally useful. David Bianco's **Pyramid of Pain** ranks them by how much it hurts the attacker when you detect them:

```
        /\      TTPs (behaviour)  hardest
       /  \     Tools
      /    \    Host/network artefacts
     /      \   Domain names
    /        \  IP addresses
   /__________\ File hashes       easiest
```

Changing a file usually changes its cryptographic hash; recompilation is not guaranteed to change bytes. Infrastructure addresses can also be replaced. Detecting **behaviour** ("a web server process spawned a shell", "a server made an outbound LDAP connection") can require a change in technique, but cost depends on the attacker and a particular behaviour may be avoidable.

### Alert fatigue

Many security detection rules produce false positives; their rates depend on context and tuning. A SOC drowning in thousands of low-quality alerts a day will miss the real one.

A real alert can be missed when ownership, triage or escalation fails.

> [!note] Content gap
> The detailed Target alert chronology is omitted because this review did not obtain a primary incident record establishing the claimed sequence.

Keep detections healthy:

- **Measure precision**: what fraction of alerts from each rule were real? Tune or delete rules that are always noise.
- **Add context automatically**: asset owner, user's normal location, recent changes.
- **Tier alerts**: page a human only for high-confidence, high-impact detections.
- **Test detections**: re-run known attack techniques (for example with Atomic Red Team) and check the alert fires.

**Precision** is a ratio, and it explains why noise is so hard to escape. Real attacks are rare compared with normal activity (a low **base rate**), so a rule that is wrong on only a tiny fraction of harmless events can still produce mostly false alarms. An illustrative calculation with made-up numbers: 1,000,000 harmless logins a day, 2 real attacks, and a rule that catches both attacks but misfires on 0.1 % of harmless logins:

```formula
P = TP / (TP + FP)
FP = FPR N_ok
FP = 0.001 × 1000000 = 1000
P = 2 / (2 + 1000) ≈ 0.002
where
P: precision: the fraction of a rule's alerts that were real, from 0 (all noise) to 1 (all real); 0.002 is 0.2 %
TP: true positives: alerts that fired on real malicious activity; here 2, assuming there were 2 real attacks that day and the rule caught both
FP: false positives: alerts that fired on harmless activity
FPR: false-positive rate: the fraction of harmless events the rule wrongly alerts on; here 0.001, which is 1 in 1,000
N_ok: the number of harmless events the rule examines; here 1,000,000 logins a day
≈: approximately equal to (the result is rounded)
In words: a rule that misfires on only 1 harmless login in 1,000 still raises about 1,000 false alerts a day against a million logins, so even if it catches both real attacks only about 2 alerts in 1,000 are real.
```

To raise *P*, cut *FP*: narrow the rule, add context so it fires only on unusual combinations, or tier it so low-confidence matches enrich other alerts instead of paging someone. Catching more real attacks (*TP*) barely helps while *FP* is in the thousands.

## Key takeaways
- Behavioural detections can force changes to attacker technique, although any one behaviour may be avoidable.
- Alert quality depends on context, ownership and triage.
- Precision counts real alerts among all alerts; false-positive rate counts flagged harmless events among harmless events.
- Test rules, enrich context and tune noisy paging paths.

## Further reading
- [The Pyramid of Pain, original author](https://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html)
- [Precision and false-positive rate](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall)
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)
