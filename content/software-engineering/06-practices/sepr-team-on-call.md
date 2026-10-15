---
id: sepr-team-on-call
title: Design sustainable on-call
level: advanced
minutes: 5
summary: Plan rotation capacity, actionable alerts, escalation and recovery for responders.
sourceLesson: sepr-teams
---

Running a service includes supporting the people who respond when it fails. Staffing arithmetic is a starting constraint; sustainable workload requires explicit policies and regular review.

## On-call that people can sustain
If your team runs production services, someone needs to respond when they break at 3 a.m. Done badly, on-call burns people out and drives them away. Done well, it is a manageable part of the job that also teaches people how the system really behaves.

### Rotation design

Google's SRE book gives concrete guidelines worth knowing:

- No more than about **25%** of an engineer's time should be spent on call.
- With a primary and a secondary on call around the clock and week-long shifts, the ideal coverage calculation gives **eight engineers** for a single-site team, before leave and other resilience needs. Google separately recommends about **six per site** for dual-site teams, considering both coverage and critical team mass.
- Google reports around **6 hours** of work per incident in its experience, including diagnosis and follow-up, and uses at most **2 incidents per 12-hour shift** as a workload guideline. This is not a universal incident-duration estimate.
- Response expectations cited by Google: about **5 minutes** for user-facing, time-critical services, about **30 minutes** for less time-sensitive ones.

Where does eight come from? Two roles must be filled at every moment, and nobody may spend more than a quarter of their time in either of them:

```formula
E_min = R / f_max
E_min = 2 / 0.25
E_min = 8
where
E_min: the smallest team that can staff the rotation, in engineers
R: the number of on-call roles filled at all times: a primary and a secondary, so 2
f_max: the largest fraction of time one engineer may spend on call: 25%, which is 0.25
In words: two seats must always be filled and each person may sit in one only a quarter of the time, so you need four people per seat, eight in all.
```

With week-long shifts, each of the eight is on call (primary or secondary) for one week in every four, as the SRE book puts it. Real teams need more, to cover leave, illness and training.

The incident limit follows the same kind of reasoning:

```formula
H = k × t
H = 2 × 6 h = 12 h
where
H: the incident work generated during one shift, in hours (h)
k: the number of incidents in the shift; Google's guideline maximum is 2
t: the average hours of work per incident in Google's experience (root-cause analysis, remediation, and follow-up such as writing the postmortem and fixing bugs), about 6 h
h: hours
In words: two incidents of about six hours' work each fill a whole 12-hour shift, so more than two leaves no time to handle them properly.
```

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

## Key takeaways
- Two simultaneous duty roles at a 25% duty fraction require at least eight people in the simplified single-site model.
- That arithmetic excludes leave and says nothing about incident volume or recovery needs.
- Page for urgent actionable threats to users and use runbooks, escalation and alert review.

## Further reading
- [Being On-Call — Google SRE book](https://sre.google/sre-book/being-on-call/)
- [Monitoring Distributed Systems — Google SRE book](https://sre.google/sre-book/monitoring-distributed-systems/)
