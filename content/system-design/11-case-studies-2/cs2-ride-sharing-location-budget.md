---
id: cs2-ride-sharing-location-budget
title: Ride-sharing workload and state
level: intermediate
minutes: 5
summary: Distinguish high location-write throughput from transactional trip correctness.
sourceLesson: cs2-ride-sharing
---

Ride-sharing looks like a booking app, but the core is a **real-time geospatial system**. Millions of moving points update every few seconds, and the hot query is "who is near this spot, right now?". Every trip also needs a strongly consistent state machine so a driver can't be sent to two riders.

## Requirements

### Functional
- Drivers go online and stream their location.
- Riders see nearby cars, request a ride and get a price quote.
- The system matches a rider to a driver. The driver accepts, and both see each other live.
- The trip progresses (en route → arrived → in trip → completed), then payment is taken.
- Prices surge when demand exceeds supply in an area.

### Non-functional
- **Match latency**: a driver offer within a few seconds of the request.
- **Freshness**: locations no more than about 5–10 s stale.
- **Correctness**: a driver is never assigned two trips. A trip is never lost or double-charged.
- **Availability**: the request path must keep working through a data-centre failure. A city with no dispatch is a city with no revenue.
- Location data is high volume but **ephemeral**. Only the latest position matters for matching.

## Three location budgets

Use a hypothetical peak of two million connected drivers reporting every four seconds. The resulting half-million updates per second describes **ingestion work**, not half a million trip bookings. A ping can replace a driver's previous position while a trip must preserve durable business history.

| Budget | What matters |
|---|---|
| Latest-position index | One recent position per connected driver, plus spatial-index overhead |
| Update stream | Reporting frequency, message size, validation and cell moves |
| Historical trail | All retained samples, retention duration, compression and copies |

At an illustrative 100 bytes per position, the latest raw records occupy about 200 MB before indexes, identifiers and runtime overhead. Keeping every ping grows far faster. Extending a peak ingest rate over a whole day is a stress scenario, not a measured daily volume.

## Spend precision where it matters

More frequent pings reduce nominal location age but increase network, battery and index work. They do not make GPS exact or guarantee a driver remains reachable. Use a freshness policy and exclude stale candidates. Coalesce superseded position updates where the product allows it.

Keep authoritative driver reservations and trip transitions separate from this refreshable index. A stale candidate may lead to an unsuccessful offer; it must not let two trips claim the same driver. Use atomic reservation guards and durable trip state even if the location tier favours availability during a partition.

Benchmark the busy-cell workload as well as the fleet total. A stadium can concentrate reads, pings and matching work on a few partitions even when total throughput looks healthy. Capacity planning therefore needs skew, reconnect bursts and degraded operation, not only an average number of writes.

## Key takeaways
- Latest location payload is small even when update throughput is large.
- Historical trail storage grows with all updates and needs its own retention plan.
- Peak factors and payload sizes are explicit workload assumptions.

## Further reading
- [H3: hexagonal hierarchical geospatial indexing (docs)](https://h3geo.org/docs/)
- [S2 Geometry library](https://s2geometry.io/)
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Uber full-year 2024 company results](https://s23.q4cdn.com/407969754/files/doc_earnings/2024/q4/earnings-result/Uber-Q4-24-Earnings-Press-Release.pdf)
