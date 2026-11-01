---
id: secp-detection-quality-and-noise
title: Behaviour detections and alert precision
level: intermediate
minutes: 4
sourceLesson: secp-detection-response
summary: Use the Pyramid of Pain and the base-rate effect to reason about useful alerts.
---

A detector can match a particular file or infrastructure address, or it can look for how an intrusion operates. This unit compares those signals and explains why a small false-positive rate can overwhelm a response team when harmless events greatly outnumber attacks.

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

**Precision** is the fraction of a rule's alerts that were real. It explains why noise is so hard to escape. Real attacks are rare compared with normal activity (a low **base rate**), so a rule that is wrong on only a tiny fraction of harmless events can still produce mostly false alarms.

An illustrative example with made-up numbers: 1,000,000 harmless logins a day, 2 real attacks, and a rule that catches both attacks but misfires on 1 harmless login in 1,000. It raises about 1,000 false alerts and 2 real ones, so only about 2 alerts in every 1,000 are worth an analyst's time. The rule's false-positive rate sounds tiny (0.1 %), but its precision is dreadful (about 0.2 %).

```formula reference
P = TP / (TP + FP)
FP = FPR N_ok
where
P: precision: the fraction of a rule's alerts that were real, from 0 (all noise) to 1 (all real)
TP: true positives: alerts that fired on real malicious activity
FP: false positives: alerts that fired on harmless activity
FPR: false-positive rate: the fraction of harmless events the rule wrongly alerts on, for example 0.001 (1 in 1,000)
N_ok: the number of harmless events the rule examines, for example 1,000,000 logins a day
In words: precision is real alerts divided by all alerts; false alerts grow with the volume of harmless events, so a low false-positive rate applied to a huge volume still swamps a handful of real attacks.
```

To raise precision, cut false positives: narrow the rule, add context so it fires only on unusual combinations, or tier it so low-confidence matches enrich other alerts instead of paging someone. Catching more real attacks barely helps while false alerts are in the thousands.

> [!analogy] Real-world analogy: a smoke alarm above the toaster
> A kitchen smoke alarm that sounds every time someone makes toast is rarely wrong about smoke, yet after a week everyone ignores it, and on the night of a real fire nobody gets up.
>
> **How it maps:** Toast is the flood of harmless events, the fire is the rare real attack, and ignoring the alarm is alert fatigue. Moving the alarm or switching to a heat detector in the kitchen is tuning the rule or adding context so that it fires on unusual combinations.
>
> **Where it stops:** A smoke alarm watches one room for one hazard. A SOC receives thousands of rules' output, and attackers deliberately make their activity look like the toast, so tuning never ends and must be checked by re-running known attack techniques.

## Key takeaways
- Behavioural detections can force changes to attacker technique, although any one behaviour may be avoidable.
- Alert quality depends on context, ownership and triage.
- Precision counts real alerts among all alerts; false-positive rate counts flagged harmless events among harmless events.
- Test rules, enrich context and tune noisy paging paths.

## Further reading
- [The Pyramid of Pain, original author](https://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html)
- [Precision and false-positive rate](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall)
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)
