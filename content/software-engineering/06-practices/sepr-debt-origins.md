---
id: sepr-debt-origins
title: Understand technical debt and its kinds
level: basic
minutes: 5
summary: Distinguish principal and interest, classify debt and recognise risks beyond messy code.
sourceLesson: sepr-technical-debt
---

Every codebase has parts the team wishes were different: a module everyone is scared to touch, a dependency three major release versions behind, a test suite that takes 40 minutes. **Technical debt** is the name for the gap between the code you have and the code that would make today's work easy.

The phrase is useful because it is a metaphor the whole business understands. It is also widely misused, so it is worth knowing what it originally meant.

## The original metaphor
Ward Cunningham coined it in a 1992 experience report about a financial product called WyCash:

> Shipping first time code is like going into debt. A little debt speeds development so long as it is paid back promptly with a rewrite... The danger occurs when the debt is not repaid. Every minute spent on not-quite-right code counts as interest on that debt.

Three ideas are packed in there:

- **Debt principal**: the work needed to bring the code up to the design you now know you want.
- **Debt interest**: the extra time every future change costs because you have not done that work.
- **Borrowing can be smart.** Shipping early to learn from real users is valuable. The mistake is never repaying.

In a 2009 video, Cunningham stressed that he meant code written with your best current understanding, which becomes "debt" as you learn more about the problem: "I'm never in favor of writing code poorly, but I am in favor of writing code to reflect your current understanding of a problem even if that understanding is partial." Repaying the debt means refactoring the code to match what you have since learned, which only works if the code is clean enough to refactor.

### Where the metaphor stops

Fowler points out one place the comparison breaks down: a bank charges interest as time passes, but code charges interest only when someone works on it. A tangled module nobody needs to change costs little change effort, however ugly it is. Unlike a loan, the "interest rate" is also never written down anywhere: principal and interest are estimates, not figures on a statement.

## Fowler's debt quadrant
Martin Fowler sorted debt along two axes: was it **deliberate** or **inadvertent**, and was it **prudent** or **reckless**?

| | Reckless | Prudent |
|---|---|---|
| Deliberate | "We don't have time for design." | "We must ship now and deal with consequences." |
| Inadvertent | "What's layering?" | "Now we know how we should have done it." |

- **Prudent, deliberate**: a conscious trade-off with a repayment plan. Hitting a trade-show deadline with a hard-coded config, ticketed for next sprint.
- **Reckless, deliberate**: skipping tests and design under pressure, knowing better. Fowler's point is that "quick and dirty" rarely even buys speed: people underestimate how soon poor internal quality starts slowing them down (his judgement is "usually weeks not months").
- **Reckless, inadvertent**: the team did not know good practice. Training and review fix the cause.
- **Prudent, inadvertent**: can emerge even after careful design, because even excellent teams only learn the best design by building the thing. Fowler identifies this as the kind of debt Cunningham described.

The quadrant matters because the response differs. Prudent debt needs a repayment plan; reckless debt needs a change in how the team works.

The labels are not universally accepted. In a 2009 post, Robert C. Martin ("Uncle Bob") argued that "a mess is not a technical debt": the word should be kept for reasoned trade-offs made under real project constraints, and even then the code must be kept clean. Fowler replied that asking whether a flaw "is" debt is the wrong question. A mess is reckless debt, and the useful distinction is prudent versus reckless, because the choice between paying the interest and paying down the principal applies either way.

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

## Key takeaways
- Technical debt describes costs created by a gap between current implementation and current understanding.
- Principal is repayment work; interest is the ongoing cost of carrying the debt.
- Deliberate versus inadvertent and prudent versus reckless debt need different responses.

## Further reading
- [The WyCash Portfolio Management System — Ward Cunningham](https://c2.com/doc/oopsla92.html)
- [Technical Debt Quadrant — Martin Fowler](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html)
- [Ward Explains Debt Metaphor (transcript of his video) — C2 wiki](https://wiki.c2.com/?WardExplainsDebtMetaphor)
- [Technical Debt — Martin Fowler](https://martinfowler.com/bliki/TechnicalDebt.html)
- [Sunsetting Python 2](https://www.python.org/doc/sunset-python-2/)
