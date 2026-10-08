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

Numbers worth memorising. The first one turns "so many per day" into "so many per second", which is how almost every estimate in this module starts, because servers and databases are sized by their per-second load:

```formula
s_day = 24 × 60 × 60 = 86,400 s
s_day ≈ 10^5 s
rate = N_day / s_day
where
s_day: the number of seconds in one day
N_day: how many events (requests, posts, messages) happen in one day
rate: the average number of events per second, often called QPS (queries per second)
s: seconds, the unit of time
10^5: ten to the power 5, a 1 followed by five zeros, which is 100,000
≈: approximately equal to (the value has been rounded)
In words: to get an average per-second rate, divide the daily total by the number of seconds in a day, and round that to 100,000 so the sum is easy to do in your head.
```

Rounding 86,400 up to 100,000 makes every rate about 13.6% too low (86,400 / 100,000 = 0.864), which rarely changes a design decision. Two anchors to remember:

```formula
rate = 1,000,000 / 86,400 s ≈ 12/s
rate = 1,000,000,000 / 86,400 s ≈ 12,000/s
where
rate: the average number of events per second
s: seconds
/s: "per second"
≈: approximately equal to (rounded)
In words: one million events a day is about 12 a second; one billion a day is about 12,000 a second.
```

The rate above is an *average*. Traffic is not flat: it rises in the daytime and falls at night (diurnal skew), and campaigns or news events cause spikes. Capacity has to cover the busiest moment, so multiply the average by a peak factor:

```formula
rate_peak = rate_avg × k_peak
where
rate_peak: the requests per second at the busiest time, which is what you size for
rate_avg: the average requests per second over the day
k_peak: the peak factor, peak divided by average; use 2–3 as an explicit illustrative assumption when no traffic profile is given
In words: the busiest second is several times the average one, so plan for the average times a peak factor that you state out loud.
```

Real peak factors can be much higher than 3 (a push campaign or a sports final), so treat 2–3 as a placeholder until real traffic data exists.

Storage works the same way: count times size. Using decimal units, where each step is a factor of 1,000:

```formula
storage = N × size
10^6 × 1 KB = 10^6 × 10^3 B = 10^9 B = 1 GB
10^9 × 1 KB = 10^12 B = 1 TB
where
storage: total bytes needed
N: the number of records stored
size: the size of one record
B: bytes; one byte is 8 bits, enough for one plain English character
KB: kilobyte, 1,000 bytes (10^3 B)
GB: gigabyte, 1,000,000,000 bytes (10^9 B)
TB: terabyte, 10^12 bytes, a thousand gigabytes
10^6: a million; 10^9: a billion; 10^12: a trillion
In words: a million 1 KB records is 1 GB and a billion of them is 1 TB; most storage sums reduce to this.
```

(Some tools count a kilobyte as 1,024 bytes instead. At estimation precision the difference, 2.4% per step, doesn't matter.)

> [!note] Content gap: universal capacity and latency numbers
> No reproducible benchmark supports a universal database writes/s, Redis operations/s, app-server throughput or hardware/network latency for this scenario. Those values are omitted. Use measured workload capacity or explicitly supplied hypothetical inputs when sizing.

### A worked estimate

Take a service with 100M (100 million) daily active users (DAU) who each make 10 reads and 1 write per day. First the rates:

```formula
writes = 100M × 1 / 10^5 s = 1,000/s
reads = 100M × 10 / 10^5 s = 10,000/s
peak writes = 1,000/s × 3 = 3,000/s
peak reads = 10,000/s × 3 = 30,000/s
where
writes, reads: average write and read requests per second
peak writes, peak reads: the same rates at the busiest time, using an assumed peak factor of 3
M: million (10^6); 100M is 100,000,000 users
10^5: 100,000, the rounded number of seconds in a day
s: seconds; /s means per second
In words: 100 million users doing one write a day is about a thousand writes a second, ten times that for reads, and three times both at peak.
```

(Dividing by the exact 86,400 gives about 1,160 writes/s and 11,600 reads/s; the shortcut is close enough.)

Then storage, assuming each write stores about 1 KB:

```formula
daily = 100M × 1 KB = 100 GB
yearly = 100 GB × 365 ≈ 36 TB
where
daily, yearly: new data stored per day and per year, before replication
M: million (10^6)
KB: kilobyte, 1,000 bytes
GB: gigabyte, 10^9 bytes
TB: terabyte, 10^12 bytes (1,000 GB)
≈: approximately equal to (36.5 rounded down)
In words: 100 million 1 KB writes a day is 100 GB a day, which adds up to about 36 TB a year.
```

Now you know: reads dominate 10:1 (cache them), 3k writes/s is a target to test against the chosen primary (and a partitioning strategy is useful if tests reveal a limit), and storage grows by tens of terabytes a year.

Say what the numbers *imply*. "36 TB a year, nearly 200 TB over five years before replication, requires a storage, backup and recovery plan; I will evaluate partitioning, tiering and sharding against those constraints" is worth far more than the arithmetic itself.

### From QPS to machines

To turn a load into a machine count, divide peak load by what one unit handles, then add capacity headroom (spare capacity for failures and spikes). A cache in front of the database means only the misses reach it:

```formula
db reads = reads × (1 − h)
db reads = 30,000/s × (1 − 0.9)
db reads = 3,000/s
where
db reads: reads per second that reach the database
reads: peak reads per second arriving at the service
h: the cache hit rate, the fraction of reads answered by the cache, between 0 and 1; here 90% = 0.9
/s: per second
In words: with a 90% hit rate only one read in ten reaches the database, so 30,000 reads a second becomes 3,000.
```

How many database replicas that needs still depends on measured query capacity. For the app servers, assume each handles 1,000 requests a second (an assumption you would measure):

```formula
servers = load / capacity
servers = 33,000/s / 1,000/s = 33
total = 35 × Z / (Z − 1)
total = 35 × 3 / 2 = 52.5 → 54
where
load: peak requests per second for the app tier, here 30,000 reads + 3,000 writes = 33,000/s
capacity: requests per second one server handles, here an assumed 1,000/s
servers: servers needed at peak with nothing broken: 33, rounded up to 35 for a little slack before the zone sum
Z: the number of availability zones (separate data-centre sites) the fleet is spread over, here 3
total: servers to run so that losing one whole zone still leaves enough
→: "round up to", here to 54 so the three zones get 18 each
/s: per second
In words: 33 servers' worth of load, rounded to 35, spread over three zones needs about 54 servers so that if one zone fails, the remaining 36 can still carry the peak.
```

The reasoning behind the *Z / (Z − 1)* factor: if one of *Z* equal zones fails, only (*Z* − 1)/*Z* of the fleet survives, so the fleet must be that much bigger. With three zones, two thirds survive, so you need 1.5 times the bare requirement. Add further headroom for deploys, uneven traffic and measurement error.

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

For each deep dive, show **options and trade-offs**, then choose. "We could hash the URL, use a counter, or use Snowflake IDs. Hashing needs collision handling; a counter needs coordination; Snowflake IDs need clock discipline. I'll use a counter with range allocation because..."

Also cover failure: what happens when this node dies, this region goes dark, this queue backs up? Senior engineers think about failure modes by reflex.

A useful checklist of probes that come up in almost every design, so you can raise them before you're asked:

- **Hot keys and skew**: one celebrity, one viral link, one huge group chat.
- **Retries and duplicates**: what is idempotent, and where is the dedup key?
- **Data consistency**: which reads can be stale, and for how long?
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
