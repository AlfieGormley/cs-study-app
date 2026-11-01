---
id: sepr-team-knowledge
title: Shape ownership and write useful documentation
level: advanced
minutes: 5
summary: Spread critical knowledge and separate design decisions from task guides and reference material.
sourceLesson: sepr-teams
---

As a team grows, many of its hardest problems stop being purely technical. An engineer who leaves no documentation, blocks every review and burns out on call can end up worth less to the team than a merely good engineer who makes everyone around them faster.

This lesson covers team responsibilities, shared knowledge and documentation. The next lessons cover review, sustainable on-call and learning from incidents. (The System Design module covers SLOs, error budgets and service-level incident response; here the focus is the team.)

## Teams shape systems
**Conway's law** (Melvin Conway, 1968): organisations that design systems "are constrained to produce designs which are copies of the communication structures of these organizations". Eric Raymond's tongue-in-cheek restatement: "If you have four groups working on a compiler, you'll get a 4-pass compiler."

It works in both directions:

- If two teams must coordinate on every change to a shared module, consider whether module boundaries or team responsibilities create avoidable coordination. Some coordination may be inherent in the domain.
- The **inverse Conway manoeuvre** deliberately shapes teams to match the architecture you want. Align team ownership with business capabilities and appropriate service boundaries; a team can own several services, and organisation alone does not guarantee independence.

The **bus factor** (or truck factor) is the number of people who would have to disappear before a project stalls. A bus factor of one is a single point of failure: holidays, illness or a resignation stop work, and that person cannot take a real break. Raise it deliberately with pairing, rotating ownership, documentation and review.

## Writing things down
Spoken knowledge does not scale and does not survive staff changes. Good teams write.

### Design docs

Before building anything substantial, write a short **design doc** and have it reviewed. The goal is to find the expensive mistakes while they are still cheap to fix: on paper, not in production. A common structure, used widely at Google and elsewhere:

1. **Context and scope**: what problem, for whom, and why now.
2. **Goals and non-goals**: non-goals are as important; they stop scope creep and endless debate.
3. **The design**: APIs, data model, key flows, a diagram.
4. **Alternatives considered**: and why they lost. This is often the most valuable section for future readers.
5. **Cross-cutting concerns**: security, privacy, observability, migration, cost.

Keep it as short as the problem allows. A two-page doc that people actually read beats a 30-page doc that they skim. Once decided, record significant choices as Architecture Decision Records (covered in the architecture module) so the *why* outlives the meeting.

### The four kinds of documentation

The **Diátaxis** framework points out that documentation serves four different needs, and mixing them makes each worse:

| Kind | Reader wants to |
|---|---|
| Tutorial | Learn by doing |
| How-to guide | Achieve a specific task |
| Reference | Look up facts |
| Explanation | Understand why |

A README that mixes a walkthrough, exhaustive API details and a long architecture essay can make each task harder. A short overview can still link to those distinct resources. Separate them, and keep docs next to the code (**docs as code**) so they are reviewed and updated in the same pull request as the behaviour they describe.

> [!analogy] Real-world analogy: four kinds of cookery writing
> Diátaxis itself uses this comparison. Teaching a child to cook is a lesson: what matters is what they learn, not the dish. A recipe gets a specific dish made by someone who can already cook. The label on a food packet lists facts you look up. A book on food history and science explains why we cook the way we do, and you read it away from the stove.
>
> **How it maps:** The cooking lesson is a tutorial, the recipe a how-to guide, the packet label reference, and the history book explanation. Each disappoints if you hand it to someone wanting another: nobody in the middle of cooking wants the history of the dish.
>
> **Where it stops:** Software docs change with the code, so unlike a printed cookbook they must be kept up to date, and one page can sensibly link to all four kinds.

**Runbooks** are a special case of how-to guide: step-by-step instructions for operational tasks and alerts. Every alert that can page someone should link to a runbook that says what it means, how to check impact and what to try first.

## Pitfalls
- **Docs written once and never updated.** Outdated instructions can mislead responders at the worst moment. Keep docs near the code, change them in the same PR as the behaviour they describe, and mark anything you are unsure of.
- **Hero culture.** Celebrating the person who fixes everything at 2 a.m. rewards the bus factor of one that caused the problem.

## Key takeaways
- Team communication and system boundaries influence each other; organisation alone does not guarantee independence.
- Raise the bus factor through collective code ownership, pairing, review and maintained documentation.
- Separate tutorials, how-to guides, reference and explanation; record goals, non-goals and alternatives in design docs.

## Further reading
- [Conway’s original observation](https://www.melconway.com/Home/Conways_Law.html)
- [Design Docs at Google — Malte Ubl](https://www.industrialempathy.com/posts/design-docs-at-google/)
- [Diátaxis documentation framework](https://diataxis.fr/)
- [Docs as Code — Write the Docs](https://www.writethedocs.org/guide/docs-as-code/)
