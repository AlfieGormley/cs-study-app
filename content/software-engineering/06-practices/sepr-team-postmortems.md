---
id: sepr-team-postmortems
title: Turn incidents into tracked improvements
level: advanced
minutes: 3
summary: Write blameless incident reviews and make owned prevention work part of normal delivery.
sourceLesson: sepr-teams
---

The on-call unit focused on response capacity. After a significant incident, use the evidence to improve both the service and the conditions in which people operate.

## Postmortems: learning, not blame
After a significant incident, the team writes a **postmortem**: what happened, the impact, the timeline, contributing factors and follow-up actions. The service-level mechanics (severity levels, incident command, SLO triggers) are in the System Design reliability module. What matters at team level is the culture around it.

A postmortem is **blameless**. It assumes everyone acted reasonably given what they knew at the time, and asks why the system made the mistake easy. "Alice ran the wrong migration" leads nowhere; "the migration tool runs against production by default with no confirmation" leads to a fix.

Blamelessness is not about being nice. It is practical: if people are punished for honest mistakes, they hide them, and the organisation stops learning. Amy Edmondson's research on **psychological safety** (a shared belief that it is safe to admit mistakes and take interpersonal risks) found an association with team learning (not a guarantee of causation in every team), and Google's internal Project Aristotle study of team effectiveness reported it as the most important factor of the five it identified.

What makes a postmortem worth writing:

- **Action items with owners and dates**, tracked like any other work. Untracked actions can create false confidence and leave preventable risks unaddressed.
- **Contributing factors, not a single root cause.** Real incidents usually involve several: a bug, a missing alert, a confusing dashboard.
- **Sharing.** Other teams learn from your failures cheaply. Many companies hold a regular postmortem review.

## Pitfalls
- **Hero culture.** Celebrating the person who fixes everything at 2 a.m. rewards the bus factor of one that caused the problem.
- **Docs written once and never updated.** Outdated instructions can mislead responders; flag uncertainty and maintain important procedures. Keep docs near the code and change them in the same PR.
- **Review as gatekeeping.** Blocking on style preferences, or leaving reviews for days, teaches people to avoid review.
- **Paging on causes rather than symptoms.** High CPU alone need not page, but imminent exhaustion that threatens users and requires urgent human action can justify a page.
- **Blameless in name only.** If a postmortem's real outcome is someone being quietly sidelined, the next incident will be reported later and less honestly.

## Key takeaways
- A blameless review explains decisions using the information available at the time.
- Record impact, timeline, contributing conditions and concrete preventive actions.
- Assign owners and track completion in the ordinary work system so the review changes practice.

## Further reading
- [Postmortem Culture — Google SRE book](https://sre.google/sre-book/postmortem-culture/)
