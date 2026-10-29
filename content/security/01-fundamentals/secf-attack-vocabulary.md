---
id: secf-attack-vocabulary
title: ATT&CK and initial-access defences
level: advanced
minutes: 3
sourceLesson: secf-kill-chain
summary: Tactics describe goals; techniques describe methods.
---

## MITRE ATT&CK

**MITRE ATT&CK** is a public knowledge base of adversary behaviour built from real incident reports. Instead of a strict sequence, it is a matrix:

- **ATT&CK tactics** are the *why*: the attacker's goal for an activity. The Enterprise tactics page (ATT&CK v20, checked October 2026) lists 15; counts and names change between versions.
- **ATT&CK techniques** (and sub-techniques) are the *how*, at a level of abstraction that is useful to defenders, each with an ID such as T1078 (Valid Accounts).
- Technique entries can link procedure examples, mitigations and detection guidance. Available coverage varies; a listed technique does not imply complete detection.

The v20 Enterprise list below is a taxonomy, not a required chronological sequence:

```
Reconnaissance
Resource Development
Initial Access
Execution
Persistence
Privilege Escalation
Stealth
Defense Impairment
Credential Access
Discovery
Lateral Movement
Collection
Command and Control
Exfiltration
Impact
```

ATT&CK gives defenders a shared vocabulary. A threat-intelligence report can say "this group uses T1566 Phishing for initial access and T1021 Remote Services for lateral movement", and a detection team can check: do we have detections for those techniques? Teams often colour an ATT&CK matrix by detection coverage to find gaps.

## Common techniques, from the defender's side

Here are the patterns that appear again and again in incident reports, and what breaks each link.

### Initial access

- **Phishing**: an email persuading someone to open a file, enter credentials or approve an MFA prompt. Defences: mail filtering, phishing-resistant MFA, user reporting buttons, and making it easy to report mistakes without blame.
- **Exploiting public-facing applications**: unpatched VPN appliances, file-transfer servers and web apps. Defences: an accurate asset inventory, fast patching of internet-facing systems, a WAF as one layer.
- **Valid accounts**: credentials from breaches, infostealer malware or access brokers. Defences: MFA everywhere, breached-password checks, removing dormant accounts.
- **Supply chain**: compromising a vendor or software dependency to reach many victims (SolarWinds, 2020). Defences are covered in the security practice module.

## Key takeaways
- Tactics describe goals; techniques describe methods.
- ATT&CK is a changing taxonomy rather than an obligatory sequence.
- Initial access can involve valid accounts and dependencies as well as malware.

## Further reading
- [MITRE ATT&CK Enterprise tactics](https://attack.mitre.org/tactics/enterprise/)
- [CISA StopRansomware guide](https://www.cisa.gov/stopransomware/ransomware-guide)
