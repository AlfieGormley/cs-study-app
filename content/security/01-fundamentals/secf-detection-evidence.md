---
id: secf-detection-evidence
title: Dwell time, indicators and tested detection
level: advanced
minutes: 3
sourceLesson: secf-kill-chain
summary: Dwell time is an evidence-dependent incident interval.
---

## Dwell time and why speed matters

**Dwell time** measures the interval between initial compromise and detection, subject to the evidence available. Mandiant's M-Trends 2025 reports a global median of **11 days for its 2024 investigations**, compared with 10 days for 2023. This is a historical incident-response sample, not a live estimate for every organisation or a safe log-retention target. The source reports five days for adversary-notified cases in that sample.

The shape of the kill chain explains why dwell time matters: the further along the chain you detect, the more the attacker already has. Stopping a malicious delivery can avoid compromise, while detection after destructive impact may require extensive recovery. Actual response cost is not a fixed function of stage.

## The Pyramid of Pain

David Bianco's **Pyramid of Pain** (2013) ranks indicators by how much pain it causes the attacker when you detect and block them:

```
        /\     TTPs        (tough)
       /  \    Tools
      /    \   Host/network artefacts
     /      \  Domain names
    /        \ IP addresses
   /__________\Hash values (trivial)
```

Changing a file generally changes its cryptographic hash, so exact-hash blocking can be evaded by a functional variant. An IP change need not require a new server. Robust behavioural detection can impose more adaptation effort, but the Pyramid of Pain is a heuristic: effectiveness depends on telemetry, rule coverage and attacker options.

This is why mature detection programmes map to ATT&CK techniques rather than relying only on **indicators of compromise (IoCs)**.

## Putting it together

| Model | Best for |
|---|---|
| Kill chain | Planning controls per stage |
| ATT&CK | Detection coverage, shared vocabulary |
| Pyramid of Pain | Choosing which indicators to invest in |
| STRIDE (earlier lesson) | Design-time threat finding |

They complement each other. STRIDE finds weaknesses in what you build; ATT&CK describes what attackers actually do to systems like it; the kill chain reminds you that every step is a chance to stop them.

## Pitfalls

1. **Perimeter-only thinking.** An entry-control failure can expose later weaknesses. Limit subsequent access and invest in detection beyond initial delivery.
2. **Chasing IoCs.** Indicator and behavioural rules both need validation and maintenance; neither has a fixed useful lifetime.
3. **Coverage theatre.** A matrix coloured green because a rule exists isn't coverage unless the rule is tested (purple teaming, attack simulation).
4. **Ignoring identity.** Many modern intrusions use valid accounts end to end. Authentication logs are as important as endpoint logs.
5. **Unprotected backups.** If compromised credentials permit backup deletion, ransomware operators can target those copies before or during the attack. Keep independently protected offline or immutable copies and test restoration.

> [!note] Evidence limits
> Timelines and detection examples are illustrative, not executed intrusion exercises. No production SIEM, EDR or backup system was tested. Dwell-time figures are tied to the named historical report; they are not current universal benchmarks.

## Key takeaways
- Dwell time is an evidence-dependent incident interval.
- The Pyramid of Pain is an adaptation-cost heuristic.
- A rule existing is not evidence that a relevant test will be detected.

## Further reading
- [Mandiant M-Trends 2025](https://cloud.google.com/blog/topics/threat-intelligence/m-trends-2025)
- [David Bianco: Pyramid of Pain](https://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html)
- [MITRE ATT&CK Enterprise tactics](https://attack.mitre.org/tactics/enterprise/)
