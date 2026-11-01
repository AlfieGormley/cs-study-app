---
id: sepr-debt-repayment
title: Make debt repayment part of delivery
level: basic
minutes: 4
summary: Record repayment triggers, choose incremental strategies and explain the business cost.
sourceLesson: sepr-technical-debt
---

The previous lesson ranked debt by how much interest it charges. This one turns that ranking into owned work, rather than a vague list of disliked code.

## Paying it down
There is no single right approach; most teams combine several.

1. **Continuous cleanup.** Refactor as part of every feature that touches the area (the preparatory refactoring from the previous lesson). This keeps interest low and needs no permission because it is just how features are built.
2. **Reserved capacity.** A fixed share of each sprint goes to debt items, chosen by the team (some pick something like 10–20%; there is no established industry figure). It stops the work being permanently pushed back by features.
3. **Targeted projects.** For a big structural problem (splitting a module, replacing a framework), a planned project with a clear goal and an end date. Use branch by abstraction or strangler fig so value arrives incrementally.
4. **Deliberate debt with a plan.** When you choose to borrow, record it: a ticket with the shortcut, why it was taken, the trigger for repaying it ("before we onboard a second customer") and an owner.

```python
# DEBT(PAY-412): fictional flat surcharge.
# Owner: billing team; extend before a
# second surcharge policy is introduced.
SURCHARGE_RATE = 0.20
```

The comment links the shortcut to owned work and a trigger; a bare `# TODO: fix` gives no such repayment mechanism.

### Things that do not work well

- **The "tech debt sprint" once a year.** Debt accumulates daily. As the only repayment strategy, a yearly cleanup can defer valuable fixes for months and may be displaced by deadlines.
- **A debt backlog with hundreds of vague items.** Nobody can prioritise "clean up utils". Each item needs a location, a cost (interest) and a rough fix size.
- **Rewriting from scratch** to escape the debt. Rewrites have their own debt from day one and lose the hidden knowledge in the old code. Incremental replacement often reduces cutover risk, but compare its compatibility and replacement effort with the specific rewrite.

## Talking to the business
Product managers and executives do not want to hear "the code is bad". They do respond to:

- **Speed**: "Features in billing take three times longer than elsewhere; this would bring them closer to average."
- **Risk**: "This library is out of security support; one CVE and we are doing an emergency upgrade under pressure."
- **Reliability**: "Four of last quarter's six incidents came from this module."
- **Options**: "We cannot launch in the EU until VAT handling is generalised."

Fowler's **design stamina hypothesis** gives the long-run picture: with little attention to design, a team is faster at first, but beyond a **design payoff line** the team with better internal quality delivers more. Fowler judges that line usually arrives within weeks, not months, but he is explicit that this is a judgement: the hypothesis has no objective proof, because neither productivity nor design quality can be measured. Debt is a choice to move faster now and slower later. Make the choice consciously, and expect "later" to come sooner than it feels.

## Pitfalls
- **Calling every disagreement "debt".** If you would design it differently but it costs nothing to work with, it is a preference, not debt.
- **Ignoring interest.** Prioritise by cost of carrying the debt, not by how ugly it looks.
- **Borrowing without recording it.** Deliberate debt that is not written down becomes inadvertent debt for the next person.
- **Hero repayments.** One engineer quietly rewriting a module over a weekend creates a knowledge silo, which is itself debt.

## Key takeaways
- Combine continuous cleanup, selected maintenance capacity and targeted incremental projects.
- Record deliberate shortcuts with a reason, owner and repayment trigger.
- Explain debt using delivery cost, risk and lost options; design stamina is a hypothesis rather than a universal timetable.

## Further reading
- [Design Stamina Hypothesis — Martin Fowler](https://martinfowler.com/bliki/DesignStaminaHypothesis.html)
- [Is High Quality Software Worth the Cost? — Martin Fowler](https://martinfowler.com/articles/is-quality-worth-cost.html)
