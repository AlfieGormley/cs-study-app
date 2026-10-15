---
id: secp-containment-and-evidence
title: Responding, containing and preserving evidence
level: intermediate
minutes: 3
sourceLesson: secp-detection-response
summary: Choose incident-specific containment while preserving useful evidence where feasible.
---

Detection starts a response, not a fixed script. Responders need roles, a timeline and a view of ongoing harm before choosing containment and recovery steps. The lifecycle below distinguishes a familiar historical teaching diagram from NIST's current guidance.

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

**Eradication** removes the attacker's footholds: malware, backdoor accounts, persistence mechanisms, compromised credentials and any others the investigation identifies as exposed (revoke or rotate them). **Recovery** restores service, often by rebuilding from known-good images rather than cleaning, and monitors closely for return.

## Key takeaways
- Prepare plans, roles, contact routes, telemetry and rehearsal before an incident.
- Containment timing depends on harm, evidence and operational safety; coordinated eviction is not a reason for indefinite delay.
- Rebooting can destroy volatile evidence while leaving persistence intact.
- Eradicate footholds and restore trusted service while monitoring for return.

## Further reading
- [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
- [Historical NIST SP 800-61 Rev. 2](https://csrc.nist.gov/pubs/sp/800/61/r2/final)
- [RFC 3227 evidence collection](https://www.rfc-editor.org/rfc/rfc3227)
