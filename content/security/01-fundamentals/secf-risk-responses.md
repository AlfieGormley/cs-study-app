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

To prioritise, teams assess **likelihood and impact** with explicit assumptions. A common rule of thumb combines the two into a single score. OWASP's Risk Rating Methodology starts from this same "standard risk model", although it then rates each factor from 0 to 9 and combines LOW/MEDIUM/HIGH bands in a lookup table rather than multiplying; the 1-to-5 scales below are an illustrative simplification:

```formula
R = L × I
R = 4 × 2 = 8
where
R: the risk score, used only to rank threats against each other; it has no unit
L: likelihood: how probable it is that this threat is carried out successfully, on an agreed ordinal scale (here 1 = rare to 5 = almost certain)
I: impact: how bad the consequences would be if it happened, on the same kind of scale (here 1 = negligible to 5 = severe)
In words: a threat that is both likely and damaging ranks highest; here a likely (4) but low-impact (2) threat scores 8 out of a possible 25.
```

On these 1-to-5 scales a rare but severe threat scores 5, below the example above at 8, even though its worst case is far worse. That is the main limit of the formula: likelihood and impact are ordinal judgements, not measured quantities, so the product is a ranking aid, not a real probability or a cost in pounds. Write down the scale and the assumptions behind each score, and let someone review the outliers rather than trusting the arithmetic.

CVSS describes vulnerability severity; a Base score alone is not an organisation's complete risk assessment. Historical popularity claims about DREAD are omitted because this review did not establish reliable comparative evidence.

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
- [FIRST CVSS v3.1 specification](https://www.first.org/cvss/v3.1/specification-document)
