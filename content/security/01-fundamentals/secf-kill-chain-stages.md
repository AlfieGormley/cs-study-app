---
id: secf-kill-chain-stages
title: The kill chain and its limits
level: advanced
minutes: 3
sourceLesson: secf-kill-chain
summary: The model has seven named stages.
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

- the attacker uses **valid accounts** (phished or bought credentials) and never installs malware;
- the attack is an **insider**;
- the target is **cloud** infrastructure, where "installation" may mean creating an access key;
- the attack loops (privilege escalation and lateral movement repeat many times inside the network).

Later models address this. The **Unified Kill Chain** (Paul Pols, 2017) combines the kill chain with ATT&CK into 18 phases grouped as getting in, getting through and getting out.

## Key takeaways
- The model has seven named stages.
- Interrupting a necessary step can stop that path, while alternatives remain.
- Identity, insider and cloud attacks can depart from the original sequence.

## Further reading
- [Cyber Kill Chain — Lockheed Martin](https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html)
- [Hutchins, Cloppert and Amin: intelligence-driven defence](https://www.lockheedmartin.com/content/dam/lockheed-martin/rms/documents/cyber/LM-White-Paper-Intel-Driven-Defense.pdf)
- [Unified Kill Chain](https://www.unifiedkillchain.com/)
