---
id: secp-containment-and-evidence
title: Responding, containing and preserving evidence
level: intermediate
minutes: 4
sourceLesson: secp-detection-response
summary: Choose incident-specific containment while preserving useful evidence where feasible.
---

Detection starts a response, not a fixed script. Responders need roles, a timeline and a view of ongoing harm before choosing containment and incident-recovery steps.

## Incident response

**NIST SP 800-61 Revision 3** (April 2025) is NIST's current incident-response guidance. It replaces the older Revision 2 four-phase cycle (preparation; detection and analysis; containment, eradication and recovery; post-incident activity) with a model built on the six **CSF 2.0** Functions:

```
 Govern · Identify · Protect
 (preparation: broad risk management)
        │
        v
 Detect ─> Respond ─> Recover
 (the incident response itself)
        │
        v
 Improvement (ID.IM): lessons from
 every Function feed back into all
```

The change in emphasis is that incident response is part of everyday risk management, and lessons are learned all the time, not only in a meeting after the incident. The familiar Revision 2 phase names remain a useful vocabulary, and NIST maps them onto the Functions; the sections below use them.

### Preparation (Govern, Identify, Protect)

Done before anything happens: an IR plan, named roles (incident commander, communications, scribe), on-call rotas, contact lists for legal and regulators, logging already set up, and **practice** through tabletop exercises.

### Detection and analysis (Detect)

Confirm it is real, establish scope (which systems, accounts, data) and severity. Start a timeline and a written log of every action taken.

### Containment, eradication and incident recovery (Respond and Recover)

**Containment** stops the incident spreading: isolate hosts, disable accounts, revoke credentials, block domains. There is a real tension:

- Contain prematurely and noisily, and a sophisticated attacker realises they are seen, changes tactics or triggers destructive actions.
- Contain too late, and they keep stealing data.

For a commodity ransomware infection, contain immediately. For a stealthy, persistent intruder, teams sometimes scope quietly first, then evict the attacker everywhere at once.

**Preserve evidence** before you wipe anything. Collect in **order of volatility** (RFC 3227): prioritise the most volatile relevant evidence, such as CPU registers and caches, memory contents, network connections and running processes, before less volatile storage. The order depends on the system, including temporary filesystems and remote logs. Rebooting usually destroys volatile evidence and may leave persistent malware intact. Balance evidence collection with urgent containment and safety; do not delay essential protective action merely to preserve evidence.

> [!analogy] Real-world analogy: footprints in the snow
> Police arriving at a break-in photograph footprints in the snow before they melt, then dust for fingerprints, which will keep. But if the house is on fire, they put the fire out first.
>
> **How it maps:** Melting footprints are volatile evidence such as memory, running processes and network connections; the fingerprints are disk images and stored logs. Photographing first is collecting in order of volatility, and the fire is ongoing harm, such as active encryption or data theft, that justifies containing at once.
>
> **Where it stops:** Photographing snow does not change it, but collecting from a live computer does change its state a little, and an attacker may be watching and change course. Responders weigh that, and the risk of tipping the attacker off, in a way a police photographer does not.

**Eradication** removes the attacker's footholds: malware, backdoor accounts, persistence mechanisms, exploited vulnerabilities, compromised credentials and any others the investigation identifies as exposed (revoke or rotate them). **Incident recovery** restores service, often by rebuilding from known-good images rather than cleaning; check backups for signs of compromise before restoring from them, and monitor closely for the attacker's return.

## Key takeaways
- Prepare plans, roles, contact routes, telemetry and rehearsal before an incident.
- Containment timing depends on harm, evidence and operational safety; coordinated eviction is not a reason for indefinite delay.
- Rebooting can destroy volatile evidence while leaving persistence intact.
- Eradicate footholds, verify restoration sources and restore trusted service while monitoring for return.
- NIST SP 800-61 Rev. 3 frames response with the CSF 2.0 Functions and continuous improvement.

## Further reading
- [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
- [Historical NIST SP 800-61 Rev. 2](https://csrc.nist.gov/pubs/sp/800/61/r2/final)
- [RFC 3227 evidence collection](https://www.rfc-editor.org/rfc/rfc3227)
