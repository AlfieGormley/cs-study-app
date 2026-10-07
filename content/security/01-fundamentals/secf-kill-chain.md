---
id: secf-kill-chain
title: Attacker techniques and the kill chain
level: advanced
minutes: 13
summary: How real intrusions unfold, modelled with the Lockheed Martin kill chain and MITRE ATT&CK, and how defenders use those models to detect and disrupt attacks at every stage.
---

Many intrusions involve several activities: find a way in, establish a foothold, look around, gain more privilege, move towards something valuable, then steal it, encrypt it or destroy it. Activities may leave evidence when the relevant telemetry is available.

That is good news for defenders. Interrupting a necessary step can stop a particular attack path. Attackers may skip stages or switch paths, so one blocked step does not guarantee the whole campaign has stopped. Observing activity provides an opportunity to investigate and respond. This lesson describes the models defenders use to reason about that chain. It stays at the level of what attackers achieve and how to detect and disrupt it, not how to carry it out.

## The Lockheed Martin Cyber Kill Chain

In 2011, Lockheed Martin researchers (Hutchins, Cloppert and Amin) adapted the military idea of a kill chain to intrusions. It has seven stages:

| # | Stage | Attacker goal |
|---|---|---|
| 1 | Reconnaissance | Learn about the target |
| 2 | Weaponisation | Prepare a payload |
| 3 | Delivery | Get it to the target |
| 4 | Exploitation | Make it run |
| 5 | Installation | Persist on the host |
| 6 | Command and control | Remote control channel |
| 7 | Actions on objectives | Steal, encrypt, destroy |

The paper's key insight was **intelligence-driven defence**: map what you know about an adversary onto the stages, and plan a defensive action for each. Its course-of-action matrix uses six verbs, borrowed from military doctrine: **detect, deny, disrupt, degrade, deceive, destroy**.

| Stage | Detect | Deny |
|---|---|---|
| Delivery | Mail filtering alerts | Block attachment types |
| Exploitation | EDR alerts | Patch, app allowlisting |
| Installation | New autorun entries | Least privilege |
| C2 | Unusual beaconing | Egress filtering |

> [!note] Why stages 1 and 2 are hard to defend
> Reconnaissance (reading your website, LinkedIn and public DNS) and weaponisation (building a payload on the attacker's own machines) mostly happen outside your network. You can reduce what you expose, but you rarely see these stages directly. Some reconnaissance can be detected through scanning or web telemetry; delivery is not the first possible defensive intervention.

### Criticisms

The kill chain was designed around malware delivered to a perimeter. It fits less well when:

- the attacker uses **valid credentials** (phished or bought) and never installs malware;
- the attack is an **insider**;
- the target is **cloud** infrastructure, where "installation" may mean creating an access key;
- the attack loops (privilege escalation and lateral movement repeat many times inside the network).

Later models address this. The **Unified Kill Chain** (Paul Pols, 2017) combines the kill chain with ATT&CK into 18 phases grouped as getting in, getting through and getting out.

## MITRE ATT&CK

**MITRE ATT&CK** is a public knowledge base of adversary behaviour built from real incident reports. Instead of a strict sequence, it is a matrix:

- **Tactics** are the *why*: the attacker's goal for an activity. The live Enterprise tactics page consulted for this review lists 15; counts and names are version-dependent.
- **Techniques** (and sub-techniques) are the *how*, at a level of abstraction that is useful to defenders, each with an ID such as T1078 (Valid Accounts).
- Technique entries can link procedure examples, mitigations and detection guidance. Available coverage varies; a listed technique does not imply complete detection.

The consulted Enterprise list below is a taxonomy, not a required chronological sequence:

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

### Execution, persistence and evasion

Attackers can **live off the land**: using tools already present on the system (PowerShell, WMI, remote administration tools, cloud CLIs) rather than custom malware. A malicious binary need not be installed. File-hash matching alone may miss the abuse, but antivirus can also inspect scripts, command content or behaviour; product labels do not determine detection capability.

Defenders respond by watching **behaviour**, not files: endpoint detection and response (EDR) records process trees, so "Word spawned PowerShell, which made a network connection" stands out even if every binary is legitimate.

### Privilege escalation and credential access

A foothold may not provide the access required for the objective. Attackers look for ways to become an administrator: unpatched local vulnerabilities, misconfigured services, and exposed **credentials**, such as cached admin logins, passwords in scripts, and cloud keys in environment variables.

Defences: least privilege, separate admin accounts used only from hardened workstations, no shared local admin passwords, and secrets kept in a secrets manager rather than files.

### Discovery and lateral movement

With credentials, the attacker maps the network and moves host to host towards the target, often using the same remote-administration protocols the IT team uses.

```
 workstation
  (phished)
     |
     v
 file server
  (cached admin credential)
     |
     v
 domain controller
  (full control)
```

Defences: network segmentation, so a workstation can't reach the domain controller's admin interfaces; tiered administration; and alerting on unusual authentication patterns, such as one account logging in to 40 machines in an hour.

### Actions on objectives

- **Exfiltration**: data copied out, often compressed and sent to cloud storage. Watch for unusual outbound volumes.
- **Impact**: ransomware encrypts systems. Some ransomware operations steal data and threaten publication (**double extortion**), so backups alone don't resolve the incident.

> [!example] An illustrative ransomware path
> 1. Phishing email or exploited VPN gives initial access.
> 2. Attacker harvests credentials and escalates to domain admin.
> 3. Lateral movement to file servers and backup systems.
> 4. Data exfiltrated to attacker-controlled storage.
> 5. Reachable backups are targeted, followed by encryption on systems the attacker can control.
>
> These are possible detection opportunities, not an obligatory sequence. Encryption can start earlier, and visibility depends on telemetry.

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
5. **Unprotected backups.** If backups are reachable with domain admin credentials, ransomware operators will delete them first. Keep offline or immutable copies.

## Key takeaways
- Intrusions are chains; breaking or detecting any link is an opportunity, and earlier is cheaper.
- The Lockheed Martin kill chain has seven stages, from reconnaissance to actions on objectives, each paired with defensive actions.
- ATT&CK provides versioned tactics and techniques; the consulted Enterprise page lists 15. Test detection coverage instead of inferring it from labels.
- Legitimate-tool and account abuse can evade file-hash checks; combine identity, content and behavioural evidence.
- The Pyramid of Pain motivates behaviour-focused detection, but adaptation cost and detection success require evidence.

> [!note] Evidence limits
> Timelines and detection examples are illustrative, not executed intrusion exercises. No production SIEM, EDR or backup system was tested. Dwell-time figures are tied to the named historical report; they are not current universal benchmarks.

## Further reading
- [The Cyber Kill Chain — Lockheed Martin](https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html)
- [MITRE ATT&CK Enterprise tactics](https://attack.mitre.org/tactics/enterprise/)
- [Mandiant M-Trends 2025: 2024 investigation results](https://cloud.google.com/blog/topics/threat-intelligence/m-trends-2025)
- [David Bianco: Pyramid of Pain presentation](https://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html)
- [Unified Kill Chain](https://www.unifiedkillchain.com/)
- [Indicator of compromise — Wikipedia](https://en.wikipedia.org/wiki/Indicator_of_compromise)
- [Endpoint detection and response — Wikipedia](https://en.wikipedia.org/wiki/Endpoint_detection_and_response)
