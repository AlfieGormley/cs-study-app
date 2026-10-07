---
id: fund-approach
title: What system design is and how to approach a problem
level: basic
minutes: 9
summary: System design turns fuzzy goals into an architecture by pinning down functional requirements, non-functional requirements and constraints first.
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

## Constraints

Constraints are things you **can't change** (or can't change cheaply):

- **Team**: three engineers who know Python and Postgres.
- **Time**: must launch in four months.
- **Budget**: fixed cloud spend.
- **Regulation**: payment card data falls under PCI DSS; GDPR restricts transfers of EU personal data abroad, which many companies turn into a hard rule that EU data stays in EU regions.
- **Existing systems**: must integrate with the company's identity provider.

Constraints often rule out "textbook" answers. A team of three probably shouldn't run its own Kafka cluster and Cassandra ring; managed services are usually the right call.

## Assumptions and scale

Next, establish the numbers the design must support:

- Daily active users (DAU), and how many actions each performs.
- Read-to-write ratio (a URL shortener might be 100:1).
- Data size per item and retention period.
- Peak versus average load (peaks of 2–10x average are common).

You'll turn these into queries per second, storage and bandwidth in the estimation lesson. The point here is that **you can't choose components without them**. A Postgres primary's sustainable write rate depends on hardware, schema, batching, durability and contention. Benchmark the intended workload before treating a guessed rate as a capacity limit.

The read-to-write ratio is especially telling. At 100:1, almost all the work is reads, so caching and read replicas pay off and the write path can stay simple. A write-heavy system (logging, metrics, chat) pushes you towards partitioning writes and append-friendly storage instead.

## A repeatable approach

Most practitioners use some variant of this sequence:

```
1. Clarify requirements
   functional / non-functional / constraints
2. Estimate scale
   QPS, storage, bandwidth
3. Define the API and data model
4. High-level design
   boxes, arrows, request flow
5. Deep dive on the hard parts
   hot keys, consistency, failure
6. Identify bottlenecks and trade-offs
   what breaks first, what you'd change
```

### Step 4: the high-level design

Start with the simplest thing that meets the requirements, then evolve it.

```
 client
   |
   v
+--------+    +-----------+    +--------+
|  load  |--->|  app tier |--->|   DB   |
|balancer|    | stateless |    |primary |
+--------+    +-----------+    +--------+
                    |              |
                    v              v
                 +-----+      +--------+
                 |cache|      |replicas|
                 +-----+      +--------+
```

Walk a request through it: "A redirect hits the load balancer, goes to any app server, checks the cache, falls back to a read replica on a miss." Walking the flow catches missing pieces quickly.

### Step 5: deep dives

This is where the real design happens. Pick the parts that are hard *for this system*:

- How are short codes generated without collisions across many servers?
- What happens if the cache cluster fails? With a 95% hit rate, the database normally sees 5% of reads; if the cache vanishes it sees all of them, a 20x jump. Can it survive that?
- What's the hot-key story when one link goes viral?

Later modules cover the tools for these questions: caching, databases and partitioning, consistency and consensus, messaging, API design and reliability patterns.

## Common mistakes

> [!warning] Jumping to technology
> "We'll use Kafka, Redis and Kubernetes" before knowing the requirements is the most common failure. Technology choices should be *conclusions*, justified by requirements.

- **Designing for imaginary scale.** Planning for a billion users when you have a thousand adds cost and complexity with no benefit. Design for roughly 10x your expected load and know how you'd get to 100x.
- **Ignoring failure.** Every component fails eventually. For each box, ask "what happens when this is down or slow?"
- **Unquantified NFRs.** "It should be fast" can't drive a decision.
- **Ignoring operations.** Who deploys it, monitors it and gets paged at 3 a.m.? A design the team can't operate is a bad design.
- **One-size consistency.** Not everything needs strong consistency; not everything can tolerate eventual consistency. Decide per data type.

## A worked mini-example

> [!example] "Design a ticket-booking system for concerts"
> **Functional:** browse events, hold seats for 10 minutes, pay, receive ticket.
>
> **Non-functional:** never sell the same seat twice (strong consistency on seat state); browse page p99 < 200 ms; survive a 50x traffic spike when a big tour goes on sale.
>
> **Constraints:** payments via an existing provider; 6 engineers; launch in 6 months.
>
> **Implications:** seat inventory needs transactions or conditional writes; the browse path can be heavily cached; the on-sale spike suggests a virtual waiting room or queue in front of checkout. Already the architecture is taking shape, and we haven't drawn a single box.

## Key takeaways
- System design is choosing components, data placement and communication to meet requirements at acceptable cost.
- Functional requirements say *what* the system does; non-functional requirements say *how well*; constraints are what you can't change.
- NFRs should have verifiable acceptance criteria, often numerical (p99 latency, availability %, QPS), and may differ per path.
- Follow a repeatable sequence: requirements, estimates, API and data model, high-level design, deep dives, trade-offs.
- Start simple and evolve; justify every technology choice from a requirement.
- Always ask "what happens when this fails?" and "who operates this?"

## Further reading
- [The System Design Primer (GitHub)](https://github.com/donnemartin/system-design-primer)
- [Non-functional requirement (Wikipedia)](https://en.wikipedia.org/wiki/Non-functional_requirement)
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
