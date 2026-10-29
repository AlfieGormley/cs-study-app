---
id: secf-risk-responses
title: Respond to threats and revisit the model
level: basic
minutes: 4
sourceLesson: secf-threat-modelling
summary: Give each threat a response and an accountable owner.
---

## Step 3: decide what to do

Each threat gets one of four responses:

| Response | Meaning | Example |
|---|---|---|
| Mitigate | Add a control | Ownership check |
| Eliminate | Remove the feature | Drop the export API |
| Transfer/share | Allocate some consequences or responsibility | Insurance or a service agreement; residual risk remains |
| Accept | Live with it, on record | Low-impact info leak |

"Accept" is legitimate, but it should be a decision made by someone with the authority to accept the risk, written down with a review date. "We didn't get round to it" is not acceptance.

> [!analogy] Real-world analogy: looking after a house
> A homeowner repairs a leaking roof, removes a rotten tree that could fall on the house, buys fire insurance and decides to live with a scuffed doorstep.
>
> **How it maps:** Repairing the roof is mitigation. Removing the tree is elimination: the hazard is gone. Insurance is transfer: it pays for some consequences but does not stop the fire. Living with the scuff is acceptance of a low-impact risk.
>
> **Where it stops:** A homeowner can usually decide alone. In an organisation, acceptance must come from someone with authority to own the risk, recorded with a review date. Insurance can also exclude some losses, and reputational harm is hard to transfer at all.

To prioritise, teams assess **likelihood and impact** with explicit assumptions. A common rule of thumb combines the two into a single score. OWASP's Risk Rating Methodology starts from this same "standard risk model", although it then rates each factor from 0 to 9 and combines LOW/MEDIUM/HIGH bands in a table rather than multiplying; the 1-to-5 scales below are an illustrative simplification:

```formula essential
R = L × I
where
R: the risk score, used only to rank threats against each other; it has no unit
L: likelihood: how probable it is that this threat is carried out successfully, on an agreed ordinal scale (here 1 = rare to 5 = almost certain)
I: impact: how bad the consequences would be if it happened, on the same kind of scale (here 1 = negligible to 5 = severe)
In words: multiply the two ratings, so a threat that is both likely and damaging ranks highest. The product only orders threats; it is not a probability or a cost.
```

For example, a likely (4) but low-impact (2) threat scores 8 out of a possible 25. On the same scales a rare but severe threat scores 5, below that example, even though its worst case is far worse. That is the main limit of the formula: likelihood and impact are ordinal judgements, not measured quantities, so the product is a ranking aid, not a real probability or a cost in pounds. Write down the scale and the assumptions behind each score, and let someone review the outliers rather than trusting the arithmetic.

CVSS (version 4.0, published by FIRST in November 2023) describes vulnerability severity. Its specification asks users to enrich the Base score with threat and environmental information, so a Base score alone is not an organisation's risk assessment.

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
- Give each threat a response and an accountable owner.
- Ordinal risk-score products are ranking aids, not measured probabilities.
- Test mitigations and update the model when the system changes.

## Further reading
- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [OWASP Risk Rating Methodology](https://community.owasp.org/OWASP_Risk_Rating_Methodology)
- [FIRST CVSS v4.0 specification](https://www.first.org/cvss/v4.0/specification-document)
