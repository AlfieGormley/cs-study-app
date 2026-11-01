---
id: secp-audit-events-and-dwell
title: Dwell time and structured security events
level: intermediate
minutes: 3
sourceLesson: secp-detection-response
summary: Understand discovery delay and record useful events without logging credentials.
---

Prevention can fail through an unknown vulnerability, a phished password or a poisoned dependency. **How quickly you notice and how well you respond** can materially affect the outcome, alongside attacker access, system design and operational impact.

Security people measure this as **dwell time**: how long an attacker is inside before being detected. If forensics shows a break-in on 3 March and the first alert, user report or outside notification came on 17 March, dwell time was 14 days. The break-in date is usually worked out only afterwards, from logs and forensic evidence, which is one reason good logging matters.

Dwell time stops at detection: containment and incident recovery come later and are measured separately. Mandiant's M-Trends 2026 reports a 14-day global median for the 2025 investigations in its dataset, up from 11 days for 2024. These are incident-response sample statistics, not a measurement of every intrusion. Changes in detection, attacker behavior and case mix can affect the result; the trend alone does not prove one cause.


## What to log

Missing telemetry limits retrospective detection; live monitoring, user reports and external notifications can also reveal incidents. Useful security events include:

| Category | Examples |
|---|---|
| Authentication | Logins, failures, MFA changes |
| Authorisation | Access denied, privilege changes |
| Admin actions | User created, config changed |
| Data access | Exports, bulk reads, downloads |
| Infrastructure | Cloud API calls, DNS, egress |

Each event needs **who** (user, service, source IP), **what** (action, resource), **when** (UTC timestamp, synchronised clocks), **where** (host, service) and **outcome** (success or failure).

Log in a **structured** format so machines can query it:

```python
import json
import logging
import time

logging.basicConfig(level=logging.INFO,
                    format="%(message)s")
log = logging.getLogger("audit")

def audit(event, user, ip, **fields):
    # Later fields protect the core identity
    # keys from extra-field overrides.
    log.info(json.dumps({
        **fields,
        "ts": time.time(),
        "event": event,
        "user": user,
        "src_ip": ip,
    }))

audit("login_failed", "alice",
      "203.0.113.7", reason="bad_mfa",
      outcome="failure")
```

> [!warning] Don't log secrets
> Never log passwords, session tokens, API keys or full card numbers. Log4Shell attackers used lookups such as `${env:AWS_SECRET_ACCESS_KEY}` precisely because logs and environments are full of them. Avoid passing secrets to logging APIs and apply central redaction as an additional safeguard; redaction cannot reliably infer every secret.

## Key takeaways
- Dwell time ends at detection, before containment and incident recovery.
- Incident-response sample medians describe the sampled investigations, not every intrusion.
- Record who, what, when, where and outcome in machine-readable events.
- Keep secrets out of logging calls and treat redaction as an additional safeguard.

## Further reading
- [OWASP logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [Mandiant M-Trends 2026](https://cloud.google.com/blog/topics/threat-intelligence/m-trends-2026/)
