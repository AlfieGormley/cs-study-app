---
id: secf-threat-modelling
title: Threat modelling with STRIDE and attack trees
level: basic
minutes: 11
summary: A structured way to ask "what can go wrong?" before attackers do, using data-flow diagrams, STRIDE per element and costed attack trees.
---

Security problems can arise from overlooked assumptions: an internal API that turned out to be reachable from the internet, an admin endpoint with no check, a log file with tokens in it. **Threat modelling** is the habit of thinking about those things on purpose, early, while they are still cheap to fix.

It doesn't need special tools or a security team. At its simplest it is a whiteboard, the people who built the system and an hour of structured questioning.

## The four questions

Adam Shostack, who led threat modelling work at Microsoft, reduces the whole discipline to four questions:

1. **What are we working on?** Draw the system.
2. **What can go wrong?** Find threats, using a framework such as STRIDE.
3. **What are we going to do about it?** Decide a response for each threat.
4. **Did we do a good enough job?** Check the model and the fixes.

Everything else (diagrams, mnemonics, scoring) is a way to answer one of those questions more reliably.

## Step 1: draw a data-flow diagram

A **data-flow diagram (DFD)** uses four kinds of element, plus the lines that matter most:

| Element | Meaning | Example |
|---|---|---|
| External entity | Outside the modelled system | User, partner API |
| Process | Code that runs | Web app, worker |
| Data store | Data at rest | Postgres, S3 |
| Data flow | Data moving | HTTPS request |

The extra ingredient is the **trust boundary**: a line where the level of trust changes. Crossing a trust boundary is a useful prompt to check assumptions about identity, permissions and input. Threats can also originate inside a boundary.

```
       trust boundary (internet)
 - - - - - - - - - - - - - - - - - -
[Browser]
    | HTTPS
 - -|- - - - - - - - - - - - - - - -
    v
 (Web app) --SQL--> [= Orders DB =]
    |
    | queue msg
 - -|- - - - - - - - - - - - - - - -
    v        trust boundary (VPC)
 (Email worker) --SMTP--> [Mail provider]
```

The browser is outside your control, so everything it sends is untrusted. The email worker trusts messages from the queue; if an attacker can write to the queue, that trust is misplaced.

> [!tip] Draw what is, not what should be
> The most useful threat-modelling sessions find that the diagram people *thought* was true isn't. "Wait, the worker also talks to the old billing database?" is a finding.

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

Processes get all six because they are where code makes decisions. For the diagram above, walking the elements produces a list like this:

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

## Attack trees

STRIDE is good at breadth: finding many threats. **Attack trees**, popularised by Bruce Schneier in 1999, are good at depth: analysing one goal in detail.

The root is the attacker's goal. Children are ways to achieve it. An **OR** node succeeds if any child does; an **AND** node needs all children.

```
Read another customer's invoice (OR)
+- Guess invoice URL (IDOR)       2
+- Take over their account (OR)
|  +- Credential stuffing         3
|  +- Phish password AND OTP (AND)
|     +- Phishing page             2
|     +- Real-time OTP relay       4
+- Steal DB backup (AND)
   +- Find public bucket           5
   +- Decrypt backup               9
```

The numbers are invented additive cost units for this exercise, not measured difficulty or ordinal 1-to-10 ratings. Assume costs do not overlap, all steps are feasible and attackers choose the cheapest route. Under those assumptions:

- **OR node**: the attacker picks the cheapest child, so take the **minimum**.
- **AND node**: the attacker must do every child, so take the **sum**.

Working up: phishing costs 2 + 4 = 6. Account takeover is min(3, 6) = 3. The backup route is 5 + 9 = 14. The root is min(2, 3, 14) = **2**, via the IDOR.

In this model, removing the IDOR path raises the minimum from 2 to 3. Strengthening a cost-14 path alone leaves that minimum unchanged. Real prioritisation also needs impact, likelihood, mitigation cost and interactions between paths; these invented numbers cannot rank a real deployment.

```python
def cost(node):
    kids = node.get("children")
    if not kids:
        return node["cost"]
    costs = [cost(c) for c in kids]
    if node["type"] == "AND":
        return sum(costs)
    return min(costs)  # OR
```

Other annotations need their own aggregation rules. For this additive cost model use minimum/sum; for "requires special equipment?", OR requires it only when every feasible alternative does, while AND requires it when any required step does. Probabilities require explicit dependence assumptions and must not simply be added like costs.

> [!warning] Trees are only as good as their leaves
> An attack tree can't show a path nobody thought of. Use STRIDE (breadth) to populate the tree, and the tree (depth) to prioritise.

## Step 3: decide what to do

Each threat gets one of four responses:

| Response | Meaning | Example |
|---|---|---|
| Mitigate | Add a control | Ownership check |
| Eliminate | Remove the feature | Drop the export API |
| Transfer/share | Allocate some consequences or responsibility | Insurance or a service agreement; residual risk remains |
| Accept | Live with it, on record | Low-impact info leak |

"Accept" is legitimate, but it should be a decision made by someone with the authority to accept the risk, written down with a review date. "We didn't get round to it" is not acceptance.

To prioritise, teams assess **likelihood and impact** with explicit assumptions. CVSS describes vulnerability severity; a Base score alone is not an organisation's complete risk assessment. Historical popularity claims about DREAD are omitted because this review did not establish reliable comparative evidence.

## Step 4: check your work

- Every element on the diagram has been walked through STRIDE.
- Every threat has a response and an owner, tracked like any other ticket.
- Mitigations have tests (for example, an automated test that user A gets `403` for user B's invoice).
- The model is revisited when the design changes: new trust boundary, new data store, new third party.

## When and how

- **Early.** Design-time review can expose issues before deployment; neither review duration nor a later incident is guaranteed.
- **Small and often.** A short model per feature beats one huge document that is out of date by the next sprint.
- **With the builders.** The engineers who wrote the code know where the shortcuts are.

## Pitfalls

1. **Modelling the attacker, not the system.** Debating whether a nation state cares about you is less useful than listing what can go wrong at each boundary.
2. **Ignoring insiders and partners.** External entities include your own support staff and your vendors.
3. **Forgetting non-functional flows**: backups, logs, CI/CD pipelines, admin consoles and monitoring agents are all part of the system.
4. **A list with no owners.** Findings without tickets don't get fixed.
5. **Treating it as a one-off.** Architecture drifts; the model must drift with it.

## Key takeaways
- Threat modelling answers four questions: what are we building, what can go wrong, what will we do, did we do enough.
- Data-flow diagrams with trust boundaries show where untrusted data enters.
- STRIDE maps each threat category to a violated property; STRIDE-per-element focuses which apply where.
- In the additive toy model, OR takes minimum cost and AND takes the sum. Use real evidence and impact to prioritise actual risks.
- Every threat needs a response (mitigate, eliminate, transfer, accept) and an owner.

## Further reading
- [Threat Modeling Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [STRIDE model — Wikipedia](https://en.wikipedia.org/wiki/STRIDE_model)
- [Attack Trees — Bruce Schneier (1999)](https://www.schneier.com/academic/archives/1999/12/attack_trees.html)
- [Microsoft Threat Modeling Tool threats](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [Threat Modeling Manifesto](https://www.threatmodelingmanifesto.org/)
