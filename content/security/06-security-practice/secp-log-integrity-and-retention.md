---
id: secp-log-integrity-and-retention
title: Trustworthy logs and retention
level: intermediate
minutes: 3
sourceLesson: secp-detection-response
summary: Separate protected evidence storage from source truthfulness and match retention to how long intrusions go unnoticed.
---

A security event is useful only if responders can still access and interpret it. Central collection and protected retention help preserve records after host compromise, while clock synchronisation helps correlate them. They do not guarantee that a compromised source reports every event truthfully.

### Keep logs trustworthy

An intruder may delete or alter logs to cover their tracks. MITRE ATT&CK v20 files this in two places: quietly removing or editing selected entries so activity blends in is technique T1070, *Indicator Removal*, under the Stealth tactic; clearing whole logs or switching logging off is T1685, *Disable or Modify Tools*, under the Defense Impairment tactic. Either way:

- **Ship logs off the host quickly** to a central store the host cannot modify.
- Use **append-only or write-once** storage (for example S3 Object Lock) for critical audit trails.
- **Synchronise clocks** (NTP); correlating events across systems with skewed clocks is miserable.
- Set **log retention** to match how long incidents take to find. Log retention should reflect investigation needs, risk, cost and data-protection requirements, not only a population median.

The retention gap is a simple comparison. If attackers were inside for 10 days before detection and logs are kept for 7, the first 3 days, often including the break-in itself, have already been deleted when the investigation starts. If the intrusion is shorter than the retention period, nothing has aged out yet. This assumes logs are deleted exactly on schedule and nothing was archived elsewhere; other causes of missing telemetry remain possible.

A practical consequence: when an investigation starts, extend retention or snapshot the relevant logs immediately, before the scheduled deletion removes more of the timeline.

## Key takeaways
- Send logs to a separately protected collector and monitor gaps.
- Configure appropriate storage immutability and access policy.
- Retention must reflect investigation needs, risk, cost and data-protection requirements.
- An intrusion longer than the retention period has already lost its earliest evidence; preserve logs as soon as an investigation starts.

## Further reading
- [OWASP logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [MITRE Indicator Removal](https://attack.mitre.org/techniques/T1070/)
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
