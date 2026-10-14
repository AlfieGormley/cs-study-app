---
id: cs1-interview-scope-time
title: Scope a design interview and budget the time
level: basic
minutes: 3
summary: Separate user actions from scale, latency, durability and availability requirements.
sourceLesson: cs1-interview-framework
---

A system design interview is not a test of whether you know the "right" architecture for Twitter. There isn't one. It is a test of whether you can take a vague problem, turn it into a concrete one, and reason your way to a design that works, while explaining your trade-offs out loud.

That means *process* matters as much as knowledge. Candidates with encyclopaedic knowledge still fail because they jump straight to drawing Kafka boxes. Candidates with modest knowledge pass because they ask good questions, size the problem, and make each decision for a stated reason.

This lesson proposes a practice framework, not a universal hiring rubric. Timings, seniority signals and suggested answers vary by employer and interviewer; use the actual interview brief. This lesson gives you a method. Every case study in this module follows it, so you can see it applied six times.

## The shape of the interview

For practice, assume a design round of 45 to 60 minutes. Take off five minutes of introductions and five of your questions at the end and you have about 35 to 45 minutes of actual design. That is not long. The single biggest failure mode is running out of time with half a design on the board.

A reasonable budget for a 45-minute slot:

| Step | Minutes |
|---|---|
| 1. Requirements | 5 |
| 2. Estimates | 3–5 |
| 3. API | 3–5 |
| 4. Data model | 3–5 |
| 5. High-level design | 8–10 |
| 6. Deep dives | 10–15 |
| 7. Wrap-up | 2–3 |

The ranges add up to 34–48 minutes, so in a 45-minute slot you will be at the bottom of most of them. These aren't rigid. For this practice framework, spend less time on steps 1–5 once the design is clear, leaving time to demonstrate depth. Follow the interviewer's actual guidance.

## Step 1: Clarify requirements

The prompt is deliberately vague: "Design a URL shortener." Your first job is to pin it down. Split requirements into two kinds.

**Functional requirements** are what the system does, phrased as user actions:

- Users can create a short link from a long URL.
- Visiting the short link redirects to the long URL.
- Users can optionally pick a custom alias.
- Links can expire.

**Non-functional requirements** are the qualities the system must have:

- Scale: how many users, requests per second, how much data?
- Latency: redirects under ~50 ms at p99?
- Availability vs consistency: is it worse to be down or to be briefly stale?
- Durability: can we ever lose a link? (No.)

Write them on the board. Then explicitly scope out what you won't do: "I'll skip user accounts and billing unless you want them." Interviewers like this; it shows you can prioritise.

> [!tip] Ask, then propose
> Don't interrogate the interviewer with twenty questions. Ask the three or four that change the design ("Is this read-heavy?", "Global or one region?"), then *propose* sensible defaults for the rest and ask if they're OK.

## Key takeaways

- Separate user actions from scale, latency, durability and availability requirements.
- Ask the questions that change the design and propose explicit assumptions for the rest.
- Use the time budget to finish an end-to-end design before deep dives.

## Further reading

- [Amazon: SDE interview preparation](https://amazon.jobs/content/en/how-we-hire/sde-ii-interview-prep)
- [System Design Primer: design approach](https://github.com/donnemartin/system-design-primer/blob/master/README.md)
