---
id: fund-requirements-targets
title: Turn features into measurable requirements
level: basic
minutes: 4
summary: Distinguish observable features from numerical service targets, and let each request path have its own priorities.
sourceLesson: fund-approach
---

System design is the work of deciding *which components a system has, how they talk to each other, and where data lives*, so that the system does what users need at the scale, speed, cost and reliability the business needs.

Writing code answers "how does this function work?". System design answers bigger questions. Where does a request go first? What happens when a machine dies? How much will this cost when traffic grows ten times?

There is rarely one right answer. A good design is one whose trade-offs are **explicit and suited to the requirements**. That is why every good design starts with requirements, not boxes and arrows.

## Why requirements come first

Imagine two teams asked to "build a URL shortener".

- Team A builds for 100 internal users. A single Postgres instance and a small web app is perfect.
- Team B builds for a public service with 100 million new links and 10 billion redirects a month. They need capacity and failure-mode analysis; caching, partitioning or multiple regions may be justified by measured bottlenecks and availability/latency requirements, not traffic totals alone.

Same feature list, completely different systems. The difference is entirely in the **non-functional requirements** and **constraints**. If you skip them, you'll either over-engineer (wasting months) or under-engineer (falling over on launch day).

## Functional requirements

Functional requirements describe **what the system does**: the behaviours a user or another system can observe.

For a URL shortener:

- Given a long URL, return a short code.
- Visiting `/abc123` redirects to the original URL.
- Optionally: custom aliases, expiry dates, click analytics.

A useful habit is to write them as user stories or API calls:

```
POST /links  {url}      -> {code}
GET  /{code}            -> 301/302
GET  /links/{code}/stats -> {clicks}
```

Then **prioritise**. In an interview or a real project kickoff, agree which features are in scope for the first version. "Analytics is nice-to-have; the redirect path is the core."

Even a tiny API line hides decisions that features drive. A `301 Moved Permanently` is heuristically cacheable, so some repeat visits may bypass your servers. A `302 Found` or `307` is not heuristically cacheable, but explicit freshness headers can still permit caching. Set an appropriate cache policy (for example `Cache-Control: no-store`) when each redirect must reach the service for analytics. If click analytics is in scope, that requirement quietly decides the status code and multiplies your redirect traffic.

## Non-functional requirements

Non-functional requirements (NFRs) describe **how well** the system does those things. They are the "-ilities", and they drive most architectural decisions.

| NFR | Example target |
|---|---|
| Latency | Redirect p99 < 50 ms |
| Throughput | 100k redirects/s peak |
| Availability | 99.99% for redirects |
| Durability | Never lose a created link |
| Consistency | New link usable within 1 s |
| Scalability | 10x growth in 3 years |
| Security | Block malware URLs |
| Cost | < £5k/month infra |

Notice the targets are **numbers**. "Fast" and "highly available" are useless because nobody can test them. "p99 under 50 ms" can be measured, alerted on and designed for.

> [!tip] Make NFRs differ per path
> Different parts of a system deserve different targets. The redirect path in a URL shortener must be very fast and very available. The analytics dashboard can be slower and eventually consistent. Saying this out loud is a sign of seniority.

## Key takeaways
- Clarify what the system does before choosing technologies.
- Replace “fast” and “available” with measurable targets, separately for each path.
- Redirect analytics depend on cache policy as well as the HTTP status code.

## Further reading
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
