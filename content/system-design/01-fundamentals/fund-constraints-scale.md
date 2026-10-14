---
id: fund-constraints-scale
title: Scope a design around constraints and load
level: basic
minutes: 3
summary: Use team, budget, regulation and traffic assumptions to rule out unsuitable architectures before drawing them.
sourceLesson: fund-approach
---

Requirements set the goal; constraints set the limits within which the team must achieve it. Traffic assumptions connect that goal to a practical capacity plan.

## Constraints

Constraints are things you **can't change** (or can't change cheaply):

- **Team**: three engineers who know Python and Postgres.
- **Time**: must launch in four months.
- **Budget**: fixed cloud spend.
- **Regulation**: payment card data falls under PCI DSS; GDPR requires safeguards for transfers of personal data outside the European Economic Area; an organisation may additionally require EU-only residency. Such a residency rule is a specified policy, not a universal GDPR requirement.
- **Existing systems**: must integrate with the company's identity provider.

Constraints often rule out "textbook" answers. A team of three probably shouldn't run its own Kafka cluster and Cassandra ring; managed services are usually the right call.

## Assumptions and scale

Next, establish the numbers the design must support:

- Daily active users (DAU), and how many actions each performs.
- Read-to-write ratio (a URL shortener might be 100:1).
- Data size per item and retention period.
- Peak versus average load (a 2–10x factor is an illustrative planning range, not a universal statistic; measure the traffic shape).

You'll turn these into queries per second, storage and bandwidth in the estimation lesson. The point here is that **you can't choose components without them**. A Postgres primary's sustainable write rate depends on hardware, schema, batching, durability and contention. Benchmark the intended workload before treating a guessed rate as a capacity limit.

The read-to-write ratio is especially telling. At 100:1, almost all the work is reads, so caching and read replicas pay off and the write path can stay simple. A write-heavy system (logging, metrics, chat) pushes you towards partitioning writes and append-friendly storage instead.

## Common mistakes

> [!warning] Jumping to technology
> "We'll use Kafka, Redis and Kubernetes" before knowing the requirements is the most common failure. Technology choices should be *conclusions*, justified by requirements.

- **Designing for imaginary scale.** Planning for a billion users when you have a thousand adds cost and complexity with no benefit. Design for roughly 10x your expected load and know how you'd get to 100x.
- **Ignoring failure.** Every component fails eventually. For each box, ask "what happens when this is down or slow?"
- **Unquantified NFRs.** "It should be fast" can't drive a decision.
- **Ignoring operations.** Who deploys it, monitors it and gets paged at 3 a.m.? A design the team can't operate is a bad design.
- **One-size consistency.** Not everything needs strong consistency; not everything can tolerate eventual consistency. Decide per data type.

## Key takeaways
- Constraints narrow the feasible design: team, time, budget, regulation and existing systems matter.
- Estimate behaviour, read/write balance, retained data and peak load before choosing components.
- Avoid imaginary scale, unmeasurable goals and systems the team cannot operate.

## Further reading
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
- [European Commission: international transfers](https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/rules-international-data-transfers_en)
