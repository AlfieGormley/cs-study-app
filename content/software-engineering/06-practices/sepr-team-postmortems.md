---
id: sepr-team-postmortems
title: Turn incidents into tracked improvements
level: advanced
minutes: 4
summary: Write blameless incident reviews and make owned prevention work part of normal delivery.
sourceLesson: sepr-teams
---

The previous lesson covered responding to incidents. This one covers learning from them, so the same failure does not happen again.

## Postmortems: learning, not blame
After a significant incident, the team writes a **postmortem**: what happened, the impact, the timeline, contributing factors and follow-up actions. The service-level mechanics (severity levels, incident command, SLO triggers) are in the System Design reliability module. What matters at team level is the culture around it.

A postmortem is **blameless**. It assumes everyone acted reasonably given what they knew at the time, and asks why the system made the mistake easy. "Alice ran the wrong migration" leads nowhere; "the migration tool runs against production by default with no confirmation" leads to a fix.

> [!analogy] Real-world analogy: an air accident investigation
> When an aircraft has a serious incident, investigators such as the UK's Air Accidents Investigation Branch explain what happened and why, without attributing blame. Pilots and engineers can describe their mistakes openly, and the report recommends changes to aircraft, procedures and training. The Google SRE book notes that blameless culture grew out of aviation and healthcare.
>
> **How it maps:** The postmortem is the investigation report, the timeline is the flight-recorder data, and the action items are the safety recommendations. Asking "why did the system make this mistake easy?" is the investigator's question, not the prosecutor's.
>
> **Where it stops:** Air accident investigators are independent of the airline and operate under legal rules, while a postmortem is written by the team itself inside the company that employs everyone involved. That makes genuine protection from blame a management choice that has to be demonstrated, not a legal guarantee.

Blamelessness is not about being nice. It is practical: if people are punished for honest mistakes, they hide them, and the organisation stops learning. Amy Edmondson's research on **psychological safety** (a shared belief that it is safe to admit mistakes and take interpersonal risks) found an association with team learning (not a guarantee of causation in every team), and Google's internal Project Aristotle study of team effectiveness reported it as the most important factor of the five it identified.

What makes a postmortem worth writing:

- **Action items with owners and dates**, tracked like any other work. Untracked actions can create false confidence and leave preventable risks unaddressed.
- **Contributing factors, not a single root cause.** Real incidents usually involve several: a bug, a missing alert, a confusing dashboard.
- **Sharing.** Other teams learn from your failures cheaply. Many companies hold a regular postmortem review.

## Pitfalls
- **Root cause: human error.** A review that stops at "the engineer made a mistake" has stopped too early. Ask what made the mistake easy and what would have caught it.
- **Untracked actions.** Action items kept in the postmortem document, rather than in the team's normal work tracker, tend to be forgotten until the same incident happens again.
- **Blameless in name only.** If a postmortem's real outcome is someone being quietly sidelined, the next incident will be reported later and less honestly.

## Key takeaways
- A blameless review explains decisions using the information available at the time.
- Record impact, timeline, contributing conditions and concrete preventive actions.
- Assign owners and track completion in the ordinary work system so the review changes practice.

## Further reading
- [Postmortem Culture — Google SRE book](https://sre.google/sre-book/postmortem-culture/)
