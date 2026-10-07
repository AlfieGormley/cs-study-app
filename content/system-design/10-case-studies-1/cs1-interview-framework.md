---
id: cs1-interview-framework
title: A framework for system design interviews
level: basic
minutes: 14
summary: A repeatable seven-step method for a 45-minute design interview, how to spend the time, what interviewers actually score, and the mistakes that sink candidates.
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

The ranges add up to 34–48 minutes, so in a 45-minute slot you will be at the bottom of most of them. These aren't rigid. A senior candidate should spend *less* time on steps 1–5 and more on deep dives, because that's where seniority shows.

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

## Step 2: Back-of-the-envelope estimates

Estimates tell you which problems are real. A write count alone does not determine capacity: transaction complexity, indexes, contention, durability, hardware and latency targets matter. Don't compute to three significant figures. Round aggressively and keep powers of ten.

Numbers worth memorising:

- 1 day = 86,400 s ≈ **10^5 s** (use 100k for mental maths; it understates rates by 13.6%, which rarely matters).
- 1 million requests/day ≈ **12 per second**. 1 billion/day ≈ 12,000/s.
- Use **2–3x** as an explicit illustrative peak assumption if no traffic profile is supplied; campaigns and diurnal skew can produce much higher ratios.
- 1 million × 1 KB = 1 GB; 1 billion × 1 KB = 1 TB. Most storage sums reduce to this.

> [!note] Content gap: universal capacity and latency numbers
> No reproducible benchmark supports a universal database writes/s, Redis operations/s, app-server throughput or hardware/network latency for this scenario. Those values are omitted. Use measured workload capacity or explicitly supplied hypothetical inputs when sizing.

A worked example, for a service with 100M daily active users who each make 10 reads and 1 write per day:

```
Writes: 100M x 1 / 10^5 s  = 1,000/s
Reads:  100M x 10 / 10^5 s = 10,000/s
Peak (x3): 3k writes/s, 30k reads/s
Storage: 100M writes/day x 1 KB
       = 100 GB/day = ~36 TB/year
```

(Dividing by the exact 86,400 gives about 1,160 writes/s and 11,600 reads/s; the shortcut is close enough.)

Now you know: reads dominate 10:1 (cache them), 3k writes/s is a target to test against the chosen primary (and a partitioning strategy is useful if tests reveal a limit), and storage grows by tens of terabytes a year.

Say what the numbers *imply*. "36 TB a year, nearly 200 TB over five years before replication, requires a storage, backup and recovery plan; I will evaluate partitioning, tiering and sharding against those constraints" is worth far more than the arithmetic itself.

> [!example] From QPS to machines
> Divide peak load by what one unit handles, then add headroom. 30k reads/s at peak with a 90% cache hit rate leaves 3k reads/s for the database: the required replica count still depends on measured query capacity. If each app server handles an assumed 1,000 req/s, 33k total requests/s needs ~35 servers, with three evenly sized zones, 54 servers leave 36 after losing one zone, above the rounded 35-server requirement. Add further headroom for deploys, uneven traffic and measurement error.

## Step 3: API design

Define the contract between clients and your system. Usually a handful of REST endpoints is enough:

```
POST /v1/links  {longUrl, alias?, ttl?}
  -> 201 {shortUrl}
GET  /{code}    -> 302 Location: longUrl
```

Things to mention: authentication (API keys or OAuth tokens), pagination (cursor-based, not offset), idempotency keys for writes that might be retried, and rate limits. For real-time features say *how* the client connects (WebSocket, Server-Sent Events, long polling) and why.

## Step 4: Data model

Name the core entities, their key fields and, crucially, the **access patterns**: what you look up by what. The access pattern drives the choice of store and the partition key.

- "Look up a link by its short code" means a key-value lookup; any store works, and the partition key is the code.
- "Get a user's last 50 messages in a conversation" means a range scan ordered by time within a partition; a wide-column store such as Cassandra with partition key `conversation_id` and clustering key `message_id` fits well.

Justify SQL vs NoSQL by the access pattern and scale, not by fashion. "Relational, because we need transactions across the order and payment tables" is a good reason. "NoSQL because it scales" is not.

## Step 5: High-level design

Draw the boxes and arrows that satisfy the functional requirements end to end. Start simple:

```
 Client
   |
   v
 Load balancer
   |
   v
 App servers (stateless) --> Cache
   |
   v
 Database (primary + replicas)
```

Then walk a request through it: "A redirect hits the load balancer, an app server checks Redis, on a miss reads the database, and returns a 302." Walking requests through the diagram catches gaps (where does the ID come from?) before the interviewer does.

Only add components when a requirement or an estimate demands them. Every box should have a reason. A message queue appears because you need to absorb bursts or decouple a slow step, not because big systems have queues.

## Step 6: Deep dives

This is where you earn the senior rating. Pick the two or three hardest parts of *this* problem and go deep:

- URL shortener: unique ID generation without coordination.
- Chat: delivering to a user connected to a different server.
- News feed: the celebrity with 100M followers.

Often the interviewer will steer you here. If they don't, choose yourself: "The interesting part is fan-out; shall I go deep on that?"

For each deep dive, show **options and trade-offs**, then choose. "We could hash the URL, use a counter, or use Snowflake IDs. Hashing needs collision handling; a counter needs coordination; Snowflake needs clock discipline. I'll use a counter with range allocation because..."

Also cover failure: what happens when this node dies, this region goes dark, this queue backs up? Senior engineers think about failure modes by reflex.

A useful checklist of probes that come up in almost every design, so you can raise them before you're asked:

- **Hot keys and skew**: one celebrity, one viral link, one huge group chat.
- **Retries and duplicates**: what is idempotent, and where is the dedup key?
- **Consistency**: which reads can be stale, and for how long?
- **Backpressure**: what happens when a downstream dependency is slow, and does the queue grow without bound?
- **Fail-open or fail-closed**: when a dependency is down, do you allow the request or reject it?
- **Multi-region**: where do writes go, and what does a user see after a regional failover?

## Step 7: Wrap up and evolve

Spend the last few minutes on:

- **Bottlenecks**: what breaks first as load grows?
- **10x scale**: what would you change? (Shard further, add regions, move to async processing.)
- **Operational concerns**: monitoring, alerting, deployment, data migration.
- **Cost**: at staff level, say which component dominates the bill (often storage or egress) and one way to cut it.

Finish with a one-sentence summary of the design and its key trade-off. It leaves the interviewer with a clear picture to write up.

## A practice review checklist

Use these dimensions as a practice checklist; they are not asserted to be the scorecard of most companies:

1. **Problem navigation**: did you clarify scope, or charge off in a random direction?
2. **Solution design**: does the design actually work end to end and meet the requirements?
3. **Technical depth**: can you go deep on at least a couple of components (database internals, consistency, caching behaviour)?
4. **Trade-offs**: do you articulate alternatives and *why* you chose one?
5. **Communication**: can the interviewer follow your reasoning? Do you respond well to hints?

Seniority changes the bar. A mid-level candidate is expected to produce a working design with some guidance. A senior candidate drives the conversation, identifies the hard parts unprompted, and discusses failure modes. A staff candidate also talks about evolution, operability, cost and organisational trade-offs.

## Common mistakes

- **Jumping to the solution.** Drawing Kafka in minute two, before you know whether the system does 10 writes per second or 10 million.
- **Over-engineering.** Microservices, three caches and a service mesh for a system that fits on one database. Scale the design to the numbers.
- **Buzzword architecture.** Naming technologies without saying what they do for this problem. "I'll use Cassandra" means nothing without "because the access pattern is a partitioned time-ordered range scan and we need high write throughput".
- **Ignoring the interviewer.** If they ask "what about hot keys?" it's a hint, not small talk.
- **Silent thinking.** The interviewer can only score what they hear. Think out loud.
- **Not finishing.** A complete simple design beats a half-finished elaborate one. Get end to end first, then deepen.
- **Pretending.** If you don't know how something works, say so and reason from first principles. Bluffing is easy to spot.

> [!warning] Estimates are a tool, not a ritual
> Some candidates spend ten minutes on estimates and then never refer to them again. Only compute numbers that will change a decision, and then use them.

## Key takeaways

- Follow a fixed sequence: requirements, estimates, API, data model, high-level design, deep dives, wrap-up.
- Split requirements into functional (what it does) and non-functional (scale, latency, availability, durability), and scope things out explicitly.
- Round estimates to powers of ten; 1M requests/day ≈ 12/s and 1B × 1 KB = 1 TB. Always state what each number implies.
- Turn estimates into machine counts (peak load ÷ per-unit capacity, plus headroom) to decide what needs to scale out.
- Let access patterns choose the data store and partition key.
- Get a simple end-to-end design on the board before going deep.
- Spend most time on the two or three genuinely hard parts, showing alternatives and failure modes.
- Interviewers score navigation, design, depth, trade-offs and communication; seniority is shown by driving the conversation.

## Further reading

- [The System Design Primer: how to approach a system design interview question](https://github.com/donnemartin/system-design-primer/blob/master/README.md)
- [Latency numbers every programmer should know](https://gist.github.com/jboner/2841832)
- [Tech Interview Handbook: system design](https://www.techinterviewhandbook.org/system-design/)
- [Hello Interview: a delivery framework for system design](https://www.hellointerview.com/learn/system-design/in-a-hurry/delivery)
