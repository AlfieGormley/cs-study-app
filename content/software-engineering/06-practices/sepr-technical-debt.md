---
id: sepr-technical-debt
title: Technical debt
level: basic
minutes: 11
summary: Where the debt metaphor comes from, Fowler's four kinds of debt, how to find the debt that is actually costing you, and how to pay it down and argue for it with the business.
---

Every codebase has parts the team wishes were different: a module everyone is scared to touch, a dependency three major versions behind, a test suite that takes 40 minutes. **Technical debt** is the name for the gap between the code you have and the code that would make today's work easy.

The phrase is useful because it is a metaphor the whole business understands. It is also widely misused, so it is worth knowing what it originally meant.

## The original metaphor

Ward Cunningham coined it in a 1992 experience report about a financial product called WyCash:

> Shipping first time code is like going into debt. A little debt speeds development so long as it is paid back promptly with a rewrite... The danger occurs when the debt is not repaid. Every minute spent on not-quite-right code counts as interest on that debt.

Three ideas are packed in there:

- **Principal**: the work needed to bring the code up to the design you now know you want.
- **Interest**: the extra time every future change costs because you have not done that work.
- **Borrowing can be smart.** Shipping early to learn from real users is valuable. The mistake is never repaying.

Cunningham later stressed that he meant code written with your best current understanding, which becomes "debt" as you learn more about the problem. He did not mean permission to write sloppy code.

## Fowler's debt quadrant

Martin Fowler sorted debt along two axes: was it **deliberate** or **inadvertent**, and was it **prudent** or **reckless**?

| | Reckless | Prudent |
|---|---|---|
| Deliberate | "We don't have time for design." | "Ship now, deal with the consequences." |
| Inadvertent | "What's layering?" | "Now we know how we should have done it." |

- **Prudent, deliberate**: a conscious trade-off with a repayment plan. Hitting a trade-show deadline with a hard-coded config, ticketed for next sprint.
- **Reckless, deliberate**: skipping tests and design because of pressure, knowing better. The timing and size of the cost depend on the project.
- **Reckless, inadvertent**: the team did not know good practice. Training and review fix the cause.
- **Prudent, inadvertent**: unavoidable. Even excellent teams only learn the best design by building the thing. This is Cunningham's original sense.

The quadrant matters because the response differs. Prudent debt needs a repayment plan; reckless debt needs a change in how the team works.

## Kinds of debt

Debt is not only messy code:

| Kind | Example |
|---|---|
| Code | Copy-pasted logic, 500-line functions |
| Design | Wrong module boundaries |
| Test | Missing or flaky tests |
| Dependency | Libraries years out of date |
| Infrastructure | Hand-built servers |
| Documentation | Runbooks nobody updated |
| Knowledge | Only one person understands it |

**Dependency debt** compounds silently. Regular small upgrades can reduce accumulated migration work, though even a minor release can require investigation and testing. Skipping five years of versions means a migration project, often forced at the worst moment by a security vulnerability or an end-of-life date. Python 2 reached end of life in January 2020, and many organisations spent years paying that bill at once.

## The interest is what matters

Not all ugly code is costly debt. Frequent changes expose design costs, but unchanged code can also incur incident response, security maintenance, runtime cost and knowledge risk. Compare those costs as well as change friction.

A worked example makes the trade-off concrete:

> [!example] Is it worth paying down?
> The checkout module's structure adds about 2 extra days to each feature that touches it. The team ships 8 such features a quarter, so the interest is about **16 days a quarter**. A restructure is estimated at **20 days**. It pays for itself in under two quarters, and keeps paying after that.
>
> A legacy reporting module also adds 2 days per change, but changes once a year. Interest: **2 days a year**. Ignoring other costs, a 20-day fix takes ten years to repay through change savings alone. Deferring it may make sense if security, operational and knowledge risks are also acceptable.

This is why "the code is ugly" is a weak argument and "this costs us 16 days a quarter" is a strong one.

### Finding hotspots

Adam Tornhill's **hotspot** analysis combines two signals you already have: how often a file changes (from version control) and how complex it is (lines of code or a complexity metric). Files that are both complex and frequently changed are where interest is being paid.

Change frequency from git:

```
git log --since="12 months ago" \
  --format=format: --name-only \
  | grep -v '^$' | sort | uniq -c \
  | sort -rn | head -20
```

The output is a count per file, most-changed first. Cross-check the top entries with complexity, bug reports and the files developers complain about. You usually find that a small fraction of files accounts for most of the pain.

Other useful signals: lead time for changes in an area, how often a module appears in incident reports, and how long reviews take for PRs touching it.

## Paying it down

There is no single right approach; most teams combine several.

1. **Continuous cleanup.** Refactor as part of every feature that touches the area (the preparatory refactoring from the previous lesson). This keeps interest low and needs no permission because it is just how features are built.
2. **Reserved capacity.** A fixed share of each sprint (for example, a locally chosen 10–20%; illustrative, not an established industry rate) goes to debt items. It stops the work being permanently pushed back by features.
3. **Targeted projects.** For a big structural problem (splitting a module, replacing a framework), a planned project with a clear goal and an end date. Use branch by abstraction or strangler fig so value arrives incrementally.
4. **Deliberate debt with a plan.** When you choose to borrow, record it: a ticket with the shortcut, why it was taken, the trigger for repaying it ("before we onboard a second customer") and an owner.

```python
# DEBT(PAY-412): fictional flat surcharge.
# Owner: billing team; extend before a
# second surcharge policy is introduced.
SURCHARGE_RATE = 0.20
```

A comment linking to a ticket survives; a bare `# TODO: fix` rarely gets fixed, because nobody owns it.

### Things that do not work well

- **The "tech debt sprint" once a year.** Debt accumulates daily. A yearly cleanup is too little, too late, and tends to be cut when deadlines loom.
- **A debt backlog with hundreds of vague items.** Nobody can prioritise "clean up utils". Each item needs a location, a cost (interest) and a rough fix size.
- **Rewriting from scratch** to escape the debt. Rewrites have their own debt from day one and lose the hidden knowledge in the old code. Incremental replacement is almost always safer.

## Talking to the business

Product managers and executives do not want to hear "the code is bad". They do respond to:

- **Speed**: "Features in billing take three times longer than elsewhere; this would bring them closer to average."
- **Risk**: "This library is out of security support; one CVE and we are doing an emergency upgrade under pressure."
- **Reliability**: "Four of last quarter's six incidents came from this module."
- **Options**: "We cannot launch in the EU until VAT handling is generalised."

Fowler's **design stamina hypothesis** gives the long-run picture: with little attention to design, a team is faster at first, but there is a point (Fowler judges it can arrive within weeks, but explicitly calls its position a judgement rather than a measured universal bound) after which the team with better internal quality delivers more. Debt is a choice to move faster now and slower later. Make the choice consciously and know when "later" arrives.

## Pitfalls

- **Calling every disagreement "debt".** If you would design it differently but it costs nothing to work with, it is a preference, not debt.
- **Ignoring interest.** Prioritise by cost of carrying the debt, not by how ugly it looks.
- **Borrowing without recording it.** Deliberate debt that is not written down becomes inadvertent debt for the next person.
- **Hero repayments.** One engineer quietly rewriting a module over a weekend creates a knowledge silo, which is itself debt.

> [!note] Evidence gap
> A universal time until debt becomes costly and a measured industry-wide percentage of capacity reserved for debt are not included: this review did not establish reliable evidence for those population claims. The examples are illustrative.

## Key takeaways
- Technical debt is the extra cost future changes pay because the code is not in the shape you now know it should be.
- Fowler's quadrant splits debt into deliberate or inadvertent and prudent or reckless; each needs a different response.
- Prioritise complex code that changes often, while also accounting for operational, security and knowledge costs.
- Pay down continuously, reserve some capacity, and record deliberate debt with an owner and a trigger.
- Argue for repayment in terms of speed, risk, reliability and options, not code aesthetics.

## Further reading
- [The WyCash Portfolio Management System — Ward Cunningham (1992)](http://c2.com/doc/oopsla92.html)
- [Technical Debt — Martin Fowler](https://martinfowler.com/bliki/TechnicalDebt.html)
- [Technical Debt Quadrant — Martin Fowler](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html)
- [Design Stamina Hypothesis — Martin Fowler](https://martinfowler.com/bliki/DesignStaminaHypothesis.html)
- [Is High Quality Software Worth the Cost? — Martin Fowler](https://martinfowler.com/articles/is-quality-worth-cost.html)
- [Technical debt — Wikipedia](https://en.wikipedia.org/wiki/Technical_debt)
