---
id: secp-log-integrity-and-retention
title: Trustworthy logs and retention
level: intermediate
minutes: 3
sourceLesson: secp-detection-response
summary: Separate protected evidence storage from source truthfulness and calculate aged-out evidence.
---

A security event is useful only if responders can still access and interpret it. Central collection and protected retention help preserve records after host compromise, while clock synchronisation helps correlate them. They do not guarantee that a compromised source reports every event truthfully.

### Keep logs trustworthy

An intruder may delete logs to cover their tracks (MITRE ATT&CK technique T1070, *Indicator Removal*). So:

- **Ship logs off the host quickly** to a central store the host cannot modify.
- Use **append-only or write-once** storage (for example S3 Object Lock) for critical audit trails.
- **Synchronise clocks** (NTP); correlating events across systems with skewed clocks is miserable.
- Set **log retention** to match how long incidents take to find. With 7-day retention and a 10-day intrusion, early evidence may be lost even though later events remain. Log retention should reflect investigation needs, risk, cost and data-protection requirements, not only a population median.

How much of an intrusion has already aged out of your logs is a subtraction:

```formula
t_lost = T_dwell − R   when T_dwell > R
t_lost = 10 days − 7 days = 3 days
where
t_lost: how many days at the start of the intrusion have already been deleted by the time you detect it, in days
T_dwell: dwell time: how long the attacker was inside before detection, in days
R: the retention period: how many days logs are kept before they are deleted
days: calendar days
In words: if attackers were inside longer than you keep logs, the earliest part of the intrusion, often the break-in itself, is gone; with 7-day retention and a 10-day intrusion, the first 3 days are lost.
```

This assumes logs are deleted exactly *R* days after they are written and nothing was archived elsewhere. If *T_dwell* is shorter than *R*, nothing has aged out under these assumptions. Other causes of missing telemetry remain possible.

## Key takeaways
- Send logs to a separately protected collector and monitor gaps.
- Configure appropriate storage immutability and access policy.
- Retention must reflect investigation needs, risk, cost and data-protection requirements.
- The retention calculation assumes exact deletion timing and no separate archive.

## Further reading
- [OWASP logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [MITRE Indicator Removal](https://attack.mitre.org/techniques/T1070/)
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
