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

For each IP address, every new failed login moves a **sliding window** of the last 60 seconds forwards and counts what is inside it:

```formula
t_cut = t_now − W
N > L
t_cut = 50 s − 60 s = −10 s
N = 6 > 5
where
t_cut: the cut-off: failed logins at or before this time drop out of the window, in seconds (s)
t_now: the timestamp of the failed login that has just arrived, in seconds
W: the window length, 60 s (WINDOW in the code)
N: the number of failed logins from this IP after t_cut, up to and including t_now (len(q) in the code)
L: the limit, 5 (LIMIT in the code)
s: seconds
In words: the rule fires when more than L failures from one IP fall inside the last W seconds; with failures at 0, 10, 20, 30, 40 and 50 s, the one at 50 s leaves all six in the window, and 6 > 5 raises an alert.
```

The code keeps each IP's recent timestamps in a queue, drops from the front everything at or before *t_cut*, then compares how many are left, *N*, with *L*:

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

## Further reading
- [Python deque](https://docs.python.org/3/library/collections.html#collections.deque)
- [Sigma security detection rules](https://github.com/SigmaHQ/sigma)
- [OWASP logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
