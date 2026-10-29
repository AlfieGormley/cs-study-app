---
id: secf-system-boundaries
title: Draw the system and its trust boundaries
level: basic
minutes: 3
sourceLesson: secf-threat-modelling
summary: Model processes, stores, entities and flows, including operational paths.
---

Security problems can arise from overlooked assumptions: an internal API that turned out to be exposed to the internet, an admin endpoint with no check, a log file with tokens in it. **Threat modelling** is the habit of thinking about those things on purpose, early, while they are still cheap to fix.

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

> [!analogy] Real-world analogy: airport security
> An airport screens passengers and bags where the public landside meets the restricted airside. Staff entrances, catering deliveries and cargo also cross into airside, and each needs its own check.
>
> **How it maps:** The screening point is a trust boundary. Passengers and bags are data flows crossing it. The staff door and cargo route are the easily forgotten flows, such as the queue, a backup job or a partner feed, that also cross a boundary.
>
> **Where it stops:** Airside is not automatically safe, and neither is the inside of a software boundary: threats can start there too. A software trust boundary is also only a line on your diagram; nothing is checked there unless the design adds a control.

> [!tip] Draw what is, not what should be
> The most useful threat-modelling sessions find that the diagram people *thought* was true isn't. "Wait, the worker also talks to the old billing database?" is a finding.

## Key takeaways
- Model processes, stores, entities and flows, including operational paths.
- A trust boundary prompts checks of identity, authority and input.
- Internal queues and partners also need explicit trust assumptions.

## Further reading
- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [Threat Modeling Manifesto](https://www.threatmodelingmanifesto.org/)
