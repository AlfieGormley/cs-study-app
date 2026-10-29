---
id: secf-intrusion-defence
title: Detect movement, privilege abuse and impact
level: advanced
minutes: 3
sourceLesson: secf-kill-chain
summary: Legitimate tools can be used maliciously.
---

### Execution, persistence and evasion

Attackers can **live off the land**: using tools already present on the system (PowerShell, WMI, remote administration tools, cloud CLIs) rather than custom malware. A malicious binary need not be installed. File-hash matching alone may miss the abuse, but antivirus can also inspect scripts, command content or behaviour; product labels do not determine what a tool can detect.

Defenders combine file indicators with **behaviour**: endpoint detection and response (EDR) can record process trees, so "Word spawned PowerShell, which made a network connection" can prompt investigation even if every binary is legitimate. Available telemetry and detection rules depend on deployment.

> [!analogy] Real-world analogy: a burglar using the owner's ladder
> A burglar who brings no tools and instead uses the homeowner's own ladder from the shed leaves nothing unusual to find: the ladder belongs there. What gives them away is behaviour, such as the ladder against an upstairs window at 3 a.m.
>
> **How it maps:** The owner's ladder is PowerShell, WMI or a cloud CLI: legitimate tools already present. Searching for burglary tools is like matching known-malware file hashes. Noticing the ladder in an odd place at an odd time is behavioural detection, such as an unusual process tree or login.
>
> **Where it stops:** Computers can record far more detail than a householder sees, but only where telemetry is collected and someone has written and tested rules for it. Legitimate administrators also do unusual things, so behavioural alerts need investigation rather than automatic conclusions.

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

## Key takeaways
- Legitimate tools can be used maliciously.
- Protect credentials and constrain movement after a foothold.
- Backups address restoration but do not undo stolen-data exposure.

## Further reading
- [CISA: identifying and mitigating living-off-the-land techniques](https://www.cisa.gov/resources-tools/resources/identifying-and-mitigating-living-land-techniques)
- [CISA StopRansomware guide](https://www.cisa.gov/stopransomware/ransomware-guide)
