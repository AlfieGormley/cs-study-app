---
id: secp-detection-response
title: Logging, detection and incident response
level: intermediate
minutes: 14
summary: What to log and how to keep it trustworthy, how detection rules and alerting work (and fail), and how to run an incident from first alert to blameless postmortem, with SolarWinds and Log4Shell as case studies.
---

Prevention eventually fails. A zero-day, a phished password or a poisoned dependency gets someone in. What separates a minor incident from a catastrophe is usually **how quickly you notice and how well you respond**.

Security people measure this as **dwell time**: how long an attacker is inside before being detected.

```formula
T_dwell = t_detect − t_in
T_dwell = 14 − 0 = 14 days
where
T_dwell: dwell time, in days
t_detect: when defenders first detect the intrusion (an alert, a user report or an outside notification), counted in days from the break-in
t_in: when the attacker first got in, here day 0; usually only worked out afterwards from logs and forensics
days: calendar days
In words: dwell time is the gap between the break-in and its discovery; an attacker who got in on day 0 and was found on day 14 had 14 days inside.
```

Dwell time stops at detection: containment and recovery come later and are measured separately. Mandiant's M-Trends 2026 reports a 14-day global median for the 2025 investigations in its dataset, up from 11 days for 2024. These are incident-response sample statistics, not a measurement of every intrusion. Changes in detection, attacker behavior and case mix can affect the result; the trend alone does not prove one cause.

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

### Keep logs trustworthy

A capable intruder deletes logs to cover their tracks (MITRE ATT&CK technique T1070, *Indicator Removal*). So:

- **Ship logs off the host quickly** to a central store the host cannot modify.
- Use **append-only or write-once** storage (for example S3 Object Lock) for critical audit trails.
- **Synchronise clocks** (NTP); correlating events across systems with skewed clocks is miserable.
- Set **log retention** to match how long incidents take to find. With 7-day retention and a 10-day intrusion, early evidence may be lost even though later events remain. Log retention should reflect investigation needs, risk, cost and data-protection requirements, not only a population median.

How much of an intrusion has already aged out of your logs is a subtraction:

```formula
t_lost = T_dwell − R   when T_dwell > R
t_lost = 10 − 7 = 3 days
where
t_lost: how many days at the start of the intrusion have already been deleted by the time you detect it, in days
T_dwell: dwell time: how long the attacker was inside before detection, in days
R: the retention period: how many days logs are kept before they are deleted
days: calendar days
In words: if attackers were inside longer than you keep logs, the earliest part of the intrusion, often the break-in itself, is gone; with 7-day retention and a 10-day intrusion, the first 3 days are lost.
```

This assumes logs are deleted exactly *R* days after they are written and nothing was archived elsewhere. If *T_dwell* is shorter than *R*, nothing is lost.

## From logs to detections

A **SIEM** (security information and event management system, such as Splunk, Elastic Security, Microsoft Sentinel or Google SecOps) collects logs centrally, normalises them and runs **detection rules** over them.

A simple in-memory rule alerts after more than 5 failed logins from one IP in a 60-second window. It assumes nondecreasing event timestamps per IP and a trusted clock. Production detection needs late-event handling, bounded/expired per-IP state, rate controls and deduplication; this sketch deliberately omits them.

For each IP address, every new failed login moves a **sliding window** of the last 60 seconds forwards and counts what is inside it:

```formula
t_cut = t_now − W
N > L
t_cut = 50 − 60 = −10 s
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
    q = recent[ip]
    q.append(ts)
    # drop events older than the window
    while q and q[0] <= ts - WINDOW:
        q.popleft()
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

A file hash changes if the attacker recompiles; an IP changes in minutes. Detecting **behaviour** ("a web server process spawned a shell", "a server made an outbound LDAP connection") forces the attacker to change *how* they operate, which is expensive.

### Alert fatigue

Many detection rules produce false positives; their rates depend on context and tuning. A SOC drowning in thousands of low-quality alerts a day will miss the real one.

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
FP = FPR × N_ok
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

## Case study: how SolarWinds was finally caught

SUNBURST was designed to evade detection:

- It waited up to two weeks after installation before doing anything.
- Its traffic imitated the legitimate Orion Improvement Program protocol.
- It checked for security tools and stayed quiet if it found them.
- The follow-on intruders used hostnames matching the victim's naming scheme and IP addresses in the victim's own country.

The campaign spanned months, but installation, follow-on compromise and detection dates differed by organisation; a uniform nine-month dwell time for every customer is not supported. It was the security firm FireEye that eventually noticed, in late 2020, when it found it had been breached itself. In Senate testimony, Kevin Mandia confirmed that an unexpected additional authentication verifier was a tip-off. Details of a particular employee phone call are omitted here because the primary testimony checked does not establish them.

The suspicious identity event helped initiate a much broader investigation; it did not alone establish the whole campaign. FireEye disclosed it on 13 December 2020, and the US CISA issued an emergency directive ordering federal agencies to disconnect Orion.

> [!example] Lesson
> High-value detections are often about **identity and behaviour**, not malware signatures: new MFA devices, impossible travel, a service account logging in interactively, a server talking to a new external domain.

## Case study: detecting Log4Shell

Log4Shell was disclosed on 9 December 2021. Cloudflare saw the first exploitation attempt **nine minutes** later, and found scanning as early as 1 December, eight days before disclosure.

Defenders' first reflex was a rule matching `${jndi:` in request logs. Attackers adapted within hours, using Log4j's own lookup syntax to disguise the string:

```
${${lower:j}ndi:ldap://...}
${${::-j}${::-n}${::-d}${::-i}:...}
${${env:X:-j}ndi:...}
```

These examples illustrate nested/default lookups that can construct `jndi` without containing the literal `${jndi:` pattern in raw input. The environment-default example assumes X is absent; runtime configuration matters. Cloudflare's advice was to treat *any* `${` in input as suspicious. Better still were detections higher up the pyramid:

- **Egress**: unexpected outbound LDAP/RMI connections may be useful warning signs. Restrict unnecessary egress according to the application baseline; some applications legitimately use these protocols, and these blocks do not cover every exploit/exfiltration path.
- **Process behaviour**: a Java process spawning `sh`, `curl` or `powershell`.
- **DNS**: lookups of unusual subdomains from servers (many scanners used DNS callbacks).

And remember the payload can arrive through *any* logged field, not just HTTP: usernames, email subjects, even device names. String-matching on the web tier would never see those.

## Incident response

The following teaching diagram is the older **NIST SP 800-61 Revision 2** four-phase model. NIST SP 800-61 Revision 3 (April 2025) supersedes it and integrates incident response with CSF 2.0, including Govern/Identify/Protect preparation and Detect/Respond/Recover activities plus continual improvement:

```
 Preparation
     │
     v
 Detection & analysis <──┐
     │                   │
     v                   │
 Containment,            │
 eradication, recovery ──┘
     │
     v
 Post-incident activity
```

### Preparation

Done before anything happens: an IR plan, named roles (incident commander, communications, scribe), on-call rotas, contact lists for legal and regulators, logging already set up, and **practice** through tabletop exercises.

### Detection and analysis

Confirm it is real, establish scope (which systems, accounts, data) and severity. Start a timeline and a written log of every action taken.

### Containment, eradication and recovery

**Containment** stops the bleeding: isolate hosts, disable accounts, revoke credentials, block domains. There is a real tension:

- Contain prematurely and noisily, and a sophisticated attacker realises they are seen, changes tactics or triggers destructive actions.
- Contain too late, and they keep stealing data.

For a commodity ransomware infection, contain immediately. For a stealthy, persistent intruder, teams sometimes scope quietly first, then evict the attacker everywhere at once.

**Preserve evidence** before you wipe anything. Collect in **order of volatility** (RFC 3227): prioritise the most volatile relevant evidence, such as CPU registers and caches, memory contents, network connections and running processes, before less volatile storage. The order depends on the system, including temporary filesystems and remote logs. Rebooting usually destroys volatile evidence and may leave persistent malware intact. Balance evidence collection with urgent containment and safety; do not delay essential protective action merely to preserve evidence.

**Eradication** removes the attacker's footholds: malware, backdoor accounts, persistence mechanisms, stolen credentials (rotate them all). **Recovery** restores service, often by rebuilding from known-good images rather than cleaning, and monitors closely for return.

### Post-incident activity

Run a **blameless postmortem**: what happened, why, what made it worse, and what will change, with owners and dates. "Blameless" does not mean nobody is accountable; it means you assume people acted reasonably with the information they had, so they tell you the truth. Blaming individuals teaches everyone to hide mistakes.

Also consider legal duties. For a reportable personal-data breach, the UK GDPR controller must notify the ICO without undue delay and, where feasible, within 72 hours of awareness. The exception is where risk to individuals' rights and freedoms is unlikely; delayed notification needs reasons and information may be supplied in phases. EU GDPR Article 33 uses the same core rule for its competent authority. Other duties, such as processor-to-controller notice or high-risk individual notification, differ; seek jurisdiction-specific advice for an actual incident.

## Key takeaways
- Dwell time is one useful outcome metric, alongside impact, containment and recovery; logging, detection and response are how you shrink it.
- Log structured security events with who, what, when, where and outcome; never log secrets; ship logs off-host to tamper-resistant storage.
- Detect behaviour, not just indicators: hashes and IPs are cheap for attackers to change, TTPs are not.
- String-matching rules are easy to evade, as Log4Shell's obfuscated `${jndi:` payloads showed; egress and process detections were more robust.
- An anomalous authentication verifier helped trigger the investigation that uncovered the SolarWinds campaign.
- Follow a lifecycle: prepare, detect and analyse, contain and eradicate (preserving evidence), recover, then learn through blameless postmortems.

## Further reading
- [NIST SP 800-61 Rev. 3: Incident Response Recommendations](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [Sigma rules (SigmaHQ on GitHub)](https://github.com/SigmaHQ/sigma)
- [The Pyramid of Pain — David Bianco](http://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html)
- [SUNBURST backdoor analysis — Mandiant/FireEye](https://cloud.google.com/blog/topics/threat-intelligence/evasive-attacker-leverages-solarwinds-supply-chain-compromises-with-sunburst-backdoor)
- [Log4j exploitation before disclosure and WAF evasion — Cloudflare](https://blog.cloudflare.com/exploitation-of-cve-2021-44228-before-public-disclosure-and-evolution-of-waf-evasion-patterns/)
- [RFC 3227: Guidelines for Evidence Collection and Archiving](https://www.rfc-editor.org/rfc/rfc3227)
- [Postmortem culture — Google SRE book](https://sre.google/sre-book/postmortem-culture/)
