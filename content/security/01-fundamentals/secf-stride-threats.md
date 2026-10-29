---
id: secf-stride-threats
title: Use STRIDE to find threats
level: basic
minutes: 3
sourceLesson: secf-threat-modelling
summary: STRIDE prompts six kinds of failure.
---

## Step 2: STRIDE

**STRIDE** was created at Microsoft in 1999 by Loren Kohnfelder and Praerit Garg. Each letter is a category of threat, and each is the violation of a security property you met in the CIA and AAA lesson.

| Threat | Violates | Example |
|---|---|---|
| Spoofing | Authentication | Forged session cookie |
| Tampering | Integrity | Edited price field |
| Repudiation | Non-repudiation | "I never sent that" |
| Info disclosure | Confidentiality | Verbose error page |
| Denial of service | Availability | Huge upload |
| Elevation of privilege | Authorisation | User reaches admin API |

The mnemonic prompts consideration of different failure modes, including repudiation and denial of service, alongside disclosure.

### STRIDE per element

Microsoft's classic **STRIDE-per-element** mapping focuses questions on particular elements. It is a modelling heuristic, not proof that other threat categories cannot matter; consider endpoints, supporting processes and the chosen level of abstraction:

| Element | Applicable threats |
|---|---|
| External entity | S, R |
| Process | S, T, R, I, D, E |
| Data store | T, I, D (R if it holds logs) |
| Data flow | T, I, D |

Processes get all six because they are where code makes decisions. For the shop diagram in the previous lesson (browser, web app, orders database, queue and email worker), walking the elements produces a list like this:

- **Browser (S, R)**: can someone log in as another user? Can a user deny placing an order?
- **Browser to web app flow (T, I, D)**: does correctly validated TLS protect the intended connection endpoints, and where does TLS terminate? Can the link be flooded?
- **Web app (all six)**: SQL injection (T, I), missing ownership checks (E), stack traces in errors (I).
- **Orders DB (T, I, D)**: who else has credentials? Are backups encrypted? What if the disk fills?
- **Queue to worker (T, I, D)**: who may publish, can messages be altered or disclosed, and can flooding or queue failure prevent delivery?

### Other frameworks

Other approaches include:

- **LINDDUN** focuses on privacy threats (linkability, identifiability, and so on).
- **PASTA** is a seven-stage, risk-centric process that ties threats to business impact.
- **Kill chains and MITRE ATT&CK** (a later lesson) model how real attackers progress, useful for detection.

## Key takeaways
- STRIDE prompts six kinds of failure.
- STRIDE-per-element focuses review without ruling other threats out.
- Privacy methods and attacker-behaviour models answer related questions.

## Further reading
- [Microsoft Threat Modeling Tool threats](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
