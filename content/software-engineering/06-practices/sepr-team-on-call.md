---
id: sepr-team-on-call
title: Design sustainable on-call
level: advanced
minutes: 5
summary: Size a rotation, know what the minimum leaves out, and keep pages actionable.
sourceLesson: sepr-teams
---

Running a service includes looking after the people who respond when it fails. A simple staffing rule gives a minimum team size, but a sustainable rotation also needs a manageable incident load, clear policies and regular review.

## On-call that people can sustain
If your team runs production services, someone needs to respond when they break at 3 a.m. Done badly, on-call burns people out and drives them away. Done well, it is a manageable part of the job that also teaches people how the system really behaves.

### Rotation design

Google's SRE book gives concrete guidelines worth knowing:

- No more than about **25%** of an engineer's time should be spent on call.
- With a primary and a secondary on call around the clock and week-long shifts, the ideal coverage calculation gives **eight engineers** for a single-site team, before leave and other resilience needs. Google separately recommends about **six per site** for dual-site teams, considering both coverage and critical team mass.
- Google reports around **6 hours** of work per incident in its experience, including diagnosis and follow-up, and uses at most **2 incidents per 12-hour shift** as a workload guideline. This is not a universal incident-duration estimate.
- Response expectations cited by Google: about **5 minutes** for user-facing, time-critical services, about **30 minutes** for less time-sensitive ones.

These are Google's guidelines for its own SRE teams, not an industry standard; other organisations choose different limits. They are still a useful, well-reasoned starting point.

Where does eight come from? Two seats (primary and secondary) must be filled every hour of every week, and nobody may sit in either seat more than a quarter of the time. So each seat needs four people taking turns, eight in all: with week-long shifts, each engineer is on call, as primary or secondary, one week in every four.

The incident limit follows similar reasoning: if each incident takes about 6 hours of work, two of them fill a 12-hour shift, and a third leaves no time to handle any of them properly.

What these figures do not tell you:

- **Eight is a floor, not a staffing plan.** It assumes nobody is ever on leave, ill or in training. Real teams need more.
- **It says nothing about load.** Eight people facing five incidents a shift will burn out however fairly the rota is shared; the incident guideline is a separate constraint, and Google aims for paging so evenly spread that the median day has no incidents at all.

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

Page on symptoms users feel (errors, latency, imminent exhaustion that needs a human), not on every internal cause. High CPU alone need not page; a disk that will fill in two hours with no automatic fix does.

**Alert fatigue** is dangerous: when most pages are noise, people stop treating them as urgent, and the real one gets missed. Review every page from the last rotation in a weekly meeting and ask "was this worth waking someone for?".

## Key takeaways
- Two duty roles with nobody on call more than 25% of the time need at least eight people at one site.
- That minimum ignores leave, illness and training, and says nothing about incident load or recovery.
- Page for urgent actionable threats to users and use runbooks, escalation and alert review.

## Further reading
- [Being On-Call — Google SRE book](https://sre.google/sre-book/being-on-call/)
- [Monitoring Distributed Systems — Google SRE book](https://sre.google/sre-book/monitoring-distributed-systems/)
