---
id: cs2-ticket-booking-inventory-pressure
title: Inventory pressure and scaling
level: advanced
minutes: 3
summary: Spread general-admission contention and estimate inventory tied up by abandoned holds.
sourceLesson: cs2-ticket-booking
---

### General admission
For standing tickets there are no seat ids, just a count. A single `remaining` counter row becomes a hot spot under thousands of decrements a second. **Split** the inventory into N buckets, where N is the number of bucket rows (say 50 rows of 400 tickets each), pick a random bucket and decrement it with `WHERE remaining >= :qty`, falling back to other buckets. With evenly distributed traffic, fifty buckets each receive about one fiftieth of the offered attempts; shared bottlenecks and near-empty buckets reduce the gain. Orders larger than every individual remainder may need atomic multi-bucket allocation.

## Bottlenecks and trade-offs

- **Hot partition**: one event lives on one shard by design, so everything hits that shard during its on-sale. Sub-partitioning by section can spread load, but cross-section orders then require a cross-shard protocol or a product restriction. Keep admissions within measured capacity.
- **Hold duration**: long holds feel kind but lock up inventory, causing "sold out" followed by seats reappearing later. An illustrative range is 5–10 minutes. Little's law sizes the cost: if 600 four-seat holds per minute are destined to be abandoned and each remains allocated for its entire eight-minute lifetime, then on average in steady state:

```formula
L = λW
λ = 600 holds/min × 4 seats
λ = 2,400 seats/min
L = 2,400 seats/min × 8 min = 19,200 seats
where
L: seats tied up in abandoned holds at any moment
λ: the rate seats enter abandoned holds, in seats per minute
W: how long each abandoned hold keeps its seats, in minutes (min); here the full 8-minute hold
holds: hold attempts
seats: tickets
min: minutes
In words: 2,400 seats a minute, each stuck for 8 minutes, keeps 19,200 seats unavailable on average.
```

That is nearly a third of a 60,000-seat stadium. If counting only time after abandonment, use the remaining lifetime instead. A short initial hold, extended when checkout starts, keeps that down.
- **Strict queue fairness vs throughput**: admitting in a strict global order needs an agreed ordering authority (which can be replicated). Batched admission (top 2,000 every minute) is nearly as fair and far simpler.
- **Payment provider limits**: the PSP may cap your authorisations per second. The admission rate must respect the *slowest* downstream dependency.

## Evolving at 10x

- **Pre-scale** before known on-sales. Load-test with recorded traffic shapes, and keep the edge configuration (token checks, static pages) able to serve everything if origin is struggling.
- **Lotteries instead of races** for the biggest events: register over days, draw winners, give each a time-boxed purchase window. Peak load becomes a schedule.
- **In-memory inventory**: one single-threaded actor per event section can serialize holds without database row locks. Durable acknowledgments, replicated recovery, fenced ownership and cross-section coordination remain necessary. It's the LMAX-style pattern for extreme contention.
- **Multi-region**: one option is a home write region per event with safe failover; cross-region consensus is another, while catalogue browsing and the waiting room are global.

> **Content gap:** no production ticketing benchmark or implementation is supplied. Capacity targets and timing budgets are hypothetical, and payment recovery requires the additional durable state described below.

## Key takeaways
- Bucket general-admission inventory without allowing negative authoritative allocation.
- Long abandoned holds tie up inventory according to their full or remaining lifetime model.
- Admission, regional ownership and cross-section rules must respect the slowest measured dependency.

## Further reading
- [Cloudflare Waiting Room (developer docs)](https://developers.cloudflare.com/waiting-room/)
- [Explicit locking (PostgreSQL docs)](https://www.postgresql.org/docs/current/explicit-locking.html)
- [How to do distributed locking (Martin Kleppmann)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
