---
id: sepr-teams
title: Working in teams - docs, review, on-call and postmortems
level: advanced
minutes: 14
summary: The practices that let a team of engineers work as more than the sum of its parts - Conway's law and bus factor, design docs and the four kinds of documentation, effective code review, a sustainable on-call rotation, and blameless postmortems.
---

Past a certain size, the hardest problems in software are not technical. A brilliant engineer who leaves no documentation, blocks every review and burns out on call creates less value than a merely good engineer who makes the whole team faster.

This lesson covers the habits that scale knowledge and keep a team healthy: how team shape affects system shape, writing things down, reviewing code, carrying a pager sustainably, and learning from failure. (The System Design module covers SLOs, error budgets and service-level incident response; here the focus is the team.)

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

A README that is half tutorial, half API reference and half architecture essay serves nobody. Separate them, and keep docs next to the code (**docs as code**) so they are reviewed and updated in the same pull request as the behaviour they describe.

**Runbooks** are a special case of how-to guide: step-by-step instructions for operational tasks and alerts. Every alert that can page someone should link to a runbook that says what it means, how to check impact and what to try first.

## Code review

Code review catches defects, but its bigger benefits are spreading knowledge (raising the bus factor) and keeping the codebase consistent.

Google's published engineering practices give a useful standard: reviewers should favour approving a change once it **definitely improves the overall health of the code**, even if it is not perfect. Perfectionism in review slows everyone and drives people to batch work into huge, unreviewable changes.

Practical habits:

- **Small changes.** Smaller coherent changes are easier to understand and review; line counts alone do not determine review quality. Split refactoring from behaviour change (see the refactoring lesson).
- **Fast responses.** Google's guide says one business day is the maximum time to respond to a review request. Slow reviews are a hidden tax on every engineer.
- **Comment on the code, not the person.** "This loop is O(n²); a set would make it O(n)" rather than "why would you do this?".
- **Label severity.** Prefix optional suggestions with `Nit:` so the author knows what blocks approval.
- **Automate the trivial.** Formatters and linters in CI settle style, so humans spend review time on design and correctness.
- **Explain the why** in the PR description: context, approach, how it was tested, and what the reviewer should focus on.

## On-call that people can sustain

If your team runs production services, someone needs to respond when they break at 3 a.m. Done badly, on-call burns people out and drives them away. Done well, it is a manageable part of the job that also teaches people how the system really behaves.

### Rotation design

Google's SRE book gives concrete guidelines worth knowing:

- No more than about **25%** of an engineer's time should be spent on call.
- With a primary and a secondary on call around the clock and week-long shifts, the ideal coverage calculation gives **eight engineers** for a single-site team, before leave and other resilience needs. Google separately recommends about **six per site** for dual-site teams, considering both coverage and critical team mass.
- Google reports around **6 hours** of work per incident in its experience, including diagnosis and follow-up, and uses at most **2 incidents per 12-hour shift** as a workload guideline. This is not a universal incident-duration estimate.
- Response expectations cited by Google: about **5 minutes** for user-facing, time-critical services, about **30 minutes** for less time-sensitive ones.

A **follow-the-sun** rotation across suitable time zones and shift lengths can avoid night duty, with clear handovers. Check that the roster covers all 24 hours: London and San Francisco each working an ordinary eight-hour day do not provide complete coverage.

Other essentials:

- **A secondary** and a clear escalation path, so nobody is alone with a problem beyond them.
- **Handover notes** at the end of each shift: what fired, what is still open, what to watch.
- **Compensation and recovery**: pay or time off for on-call, and a lie-in after a bad night.
- **Training**: shadow shifts and practice incidents before someone carries the pager alone.

### Alert hygiene

The SRE book's test for a page: it should detect something **urgent, actionable and actively or imminently user-visible**. Every page should require human judgement; if a script could handle it, automate it.

Common failures and fixes:

| Problem | Fix |
|---|---|
| Pages on CPU > 80% without service risk | Tie pages to actionable current or imminent service risk |
| Same alert fires daily | Fix the cause; downgrade or remove only if paging is unnecessary |
| Alert with no runbook | Add a runbook; keep necessary service-risk detection |
| 20 alerts for 1 outage | Group and deduplicate |

**Alert fatigue** is dangerous: when most pages are noise, people stop treating them as urgent, and the real one gets missed. Review every page from the last rotation in a weekly meeting and ask "was this worth waking someone for?".

## Postmortems: learning, not blame

After a significant incident, the team writes a **postmortem**: what happened, the impact, the timeline, contributing factors and follow-up actions. The service-level mechanics (severity levels, incident command, SLO triggers) are in the System Design reliability module. What matters at team level is the culture around it.

A postmortem is **blameless**. It assumes everyone acted reasonably given what they knew at the time, and asks why the system made the mistake easy. "Alice ran the wrong migration" leads nowhere; "the migration tool runs against production by default with no confirmation" leads to a fix.

Blamelessness is not about being nice. It is practical: if people are punished for honest mistakes, they hide them, and the organisation stops learning. Amy Edmondson's research on **psychological safety** (a shared belief that it is safe to admit mistakes and take interpersonal risks) found an association with team learning (not a guarantee of causation in every team), and Google's internal Project Aristotle study of team effectiveness reported it as the most important factor of the five it identified.

What makes a postmortem worth writing:

- **Action items with owners and dates**, tracked like any other work. Untracked actions can create false confidence and leave preventable risks unaddressed.
- **Contributing factors, not a single root cause.** Real incidents usually involve several: a bug, a missing alert, a confusing dashboard.
- **Sharing.** Other teams learn from your failures cheaply. Many companies hold a regular postmortem review.

## Team health in general

- **Onboarding** is a test of your docs. Have every new joiner fix whatever confused them.
- **Pairing and mobbing** spread knowledge fast, especially on unfamiliar code.
- **Async by default** for things that do not need a meeting: written proposals, recorded decisions, threads rather than calls. Protect focus time.
- **Rotate ownership** of components and of on-call so expertise is not concentrated.

## Pitfalls

- **Hero culture.** Celebrating the person who fixes everything at 2 a.m. rewards the bus factor of one that caused the problem.
- **Docs written once and never updated.** Wrong documentation is worse than none. Keep docs near the code and change them in the same PR.
- **Review as gatekeeping.** Blocking on style preferences, or leaving reviews for days, teaches people to avoid review.
- **Paging on causes rather than symptoms.** High CPU alone need not page, but imminent exhaustion that threatens users and requires urgent human action can justify a page.
- **Blameless in name only.** If a postmortem's real outcome is someone being quietly sidelined, the next incident will be reported later and less honestly.

## Key takeaways
- Conway's law links team structure to system structure; design both together, and raise the bus factor deliberately.
- Write short design docs with goals, non-goals and alternatives; separate tutorials, how-tos, reference and explanation; keep docs next to code.
- Review small changes quickly, approve changes that improve code health, and automate style.
- Google’s illustrative on-call model needs at least eight people for two single-site roles at 25% duty and targets at most two incidents per 12-hour shift; adapt staffing and workload to the service, including leave, runbooks and recovery.
- Blameless postmortems with owned, tracked actions turn incidents into learning; psychological safety is what makes them honest.

## Further reading
- [Being On-Call — Google SRE book](https://sre.google/sre-book/being-on-call/)
- [Postmortem Culture: Learning from Failure — Google SRE book](https://sre.google/sre-book/postmortem-culture/)
- [Google Engineering Practices: Code Review](https://google.github.io/eng-practices/review/)
- [Design Docs at Google — Malte Ubl](https://www.industrialempathy.com/posts/design-docs-at-google/)
- [Diátaxis documentation framework](https://diataxis.fr/)
- [Conway's law — Wikipedia](https://en.wikipedia.org/wiki/Conway%27s_law)
- [Psychological safety — Wikipedia](https://en.wikipedia.org/wiki/Psychological_safety)
