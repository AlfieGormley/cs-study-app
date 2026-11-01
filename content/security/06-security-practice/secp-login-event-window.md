---
id: secp-login-event-window
title: A sliding-time login detector
level: intermediate
minutes: 3
sourceLesson: secp-detection-response
summary: Trace event-window boundaries and distinguish a teaching sketch from a production detector.
---

A SIEM turns collected telemetry into queries and alerts. Here the detector maintains recent failed-login times separately for each source IP. Its exact boundary and repeated-alert behaviour matter; the queue alone is not a complete production detection service.

## From logs to detections

A **SIEM** (security information and event management system, such as Splunk, Elastic Security, Microsoft Sentinel or Google SecOps) collects logs centrally, normalises them and runs **security detection rules** over them.

A simple in-memory rule alerts after more than 5 failed logins from one IP in a 60-second window. It assumes nondecreasing event timestamps per IP and a trusted clock. Production detection needs late-event handling, bounded/expired per-IP state, rate controls and deduplication; this sketch deliberately omits them.

For each IP address, every new failed login moves a **sliding window** of the last 60 seconds forwards. Failures at or before the cut-off (the new event's time minus 60 seconds) drop out; the rule fires when more than 5 remain. With failures at 0, 10, 20, 30, 40 and 50 seconds, the one at 50 s leaves all six inside the window, so it alerts.

The code keeps each IP's recent timestamps in a queue, drops old ones from the front, then compares how many are left with the limit:

```python
from collections import defaultdict, deque

WINDOW = 60   # seconds
LIMIT = 5

recent = defaultdict(deque)

def on_failed_login(ip, ts):
    # Each source gets its own event queue.
    q = recent[ip]
    q.append(ts)
    # Drop events at or before the cutoff.
    while q and q[0] <= ts - WINDOW:
        q.popleft()
    # Repeat alerts while above LIMIT.
    # The local harness supplies alert().
    if len(q) > LIMIT:
        alert(ip, len(q))
```

Think about what this rule cannot see. An attacker who tries one common password against many accounts from hundreds of addresses (password spraying), or who stays at four failures a minute, never crosses a per-IP threshold. Production detections therefore also count failures per account and across the whole service, and look for a success after many failures.

**Sigma** provides a common detection-rule format. Conversion requires a supported backend and correct log-source/field mapping; not every rule maps automatically to every SIEM:

```
title: JNDI lookup in web request
logsource:
  category: webserver
detection:
  keywords:
    - '${jndi:'
  condition: keywords
level: high
```

## Key takeaways
- Events at or before the cutoff are removed; events after it remain.
- The sketch alerts on every event while the retained count exceeds five.
- Nondecreasing trusted timestamps are an explicit assumption.
- Production use also needs bounded state, late-event policy, rate controls and deduplication.
- Per-IP counting misses spraying from many addresses and slow attempts; count per account and service-wide too.

## Further reading
- [Python deque](https://docs.python.org/3/library/collections.html#collections.deque)
- [Sigma security detection rules](https://github.com/SigmaHQ/sigma)
- [OWASP logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
