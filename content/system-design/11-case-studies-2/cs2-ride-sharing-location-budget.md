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

## Back-of-the-envelope

Uber reported nearly 11.3 billion trips for 2024, about 31 M a day, but that figure includes Uber Eats deliveries, so rides alone are a good deal fewer. Design for a large ride-hailing platform.

Trips: assume **20 M (20 million) a day**. To get a rate per second, divide by the 86,400 seconds in a day (24 hours of sixty minutes, each containing sixty seconds), then multiply by a peak factor, because demand is not spread evenly:

```formula
T_avg = T_day / 86,400 s
T_avg = 20,000,000 / 86,400 s ≈ 230/s
T_peak = 5 × T_avg ≈ 1,200/s
where
T_avg: average trip requests per second over the day
T_day: trips per day; here 20 million
T_peak: trip requests per second at the busiest time (a Friday evening), assumed 5 times the average
86,400 s: the number of seconds in a day
s: seconds
≈: approximately equal to
In words: 20 million trips a day averages about 230 a second, and about 1,200 a second at a five-times peak.
```

Locations: assume **2 M drivers online at peak**, each sending its position every 4 seconds. Each update is a payload of about 100 bytes (driver id, latitude, longitude, heading, speed, timestamp, status):

```formula
U = N / i
U = 2,000,000 / 4 s = 500,000/s
D = U × p
D = 500,000/s × 100 B = 50 MB/s
where
U: location updates arriving per second (writes per second)
N: drivers online at peak; here 2,000,000
i: interval between one driver's updates, in seconds (s); here 4
D: incoming data rate (ingest bandwidth), in megabytes per second (MB/s)
p: size of one update, in bytes (B); about 100
B: bytes
s: seconds
MB: megabytes; 1 MB = 1,000,000 bytes
In words: 2 million drivers reporting every 4 seconds is half a million writes a second, about 50 megabytes of data every second.
```

What matters:

- **500 k writes/s** of location, each overwriting the previous one. A rebuildable in-memory index is a useful design option; durable stores can also handle high write rates when partitioned and provisioned appropriately.
- The latest-location state is tiny, because each driver keeps only one current position:

```formula
M = N × p
M = 2,000,000 × 100 B = 200 MB
where
M: memory for the latest position of every driver, in megabytes (MB)
N: drivers online; here 2,000,000
p: bytes per position record (B); about 100
B: bytes
MB: megabytes; 1 MB = 1,000,000 bytes
In words: one 100-byte record for each of 2 million drivers is only 200 megabytes, which fits easily in memory.
```

That is raw payload only: geospatial indexes, identifiers, object overhead and replication increase memory. Sharding choices need measured memory and throughput.
- Trip writes are modest (around a thousand a second), but they must be transactional.
- Location history for trip receipts and analytics keeps *every* update, not just the latest, so it grows with time:

```formula
H = U × p × 86,400 s
H = 500,000/s × 100 B × 86,400 s
H = 4,320,000,000,000 B ≈ 4.3 TB/day
where
H: location history written per day, in bytes (B)
U: location updates per second; here 500,000
p: bytes per update; about 100
86,400 s: seconds in a day
s: seconds
B: bytes
TB: terabytes; 1 TB = 10^12 bytes
day: one day
≈: approximately equal to
In words: keeping every 100-byte update at half a million a second adds about 4.3 terabytes a day, which is streamed to cheap storage.
```

The 5x peak, 4-second interval and 100-byte payload are planning assumptions; real figures vary by city and app version. The 4.3 TB daily trail assumes the peak update rate persists all day, so it is a constant-peak capacity scenario rather than the average day.

## Key takeaways
- Latest location payload is small even when update throughput is large.
- Historical trail storage grows with all updates and needs its own retention plan.
- Peak factors and payload sizes are explicit workload assumptions.

## Further reading
- [H3: hexagonal hierarchical geospatial indexing (docs)](https://h3geo.org/docs/)
- [S2 Geometry library](https://s2geometry.io/)
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Uber full-year 2024 company results](https://s23.q4cdn.com/407969754/files/doc_earnings/2024/q4/earnings-result/Uber-Q4-24-Earnings-Press-Release.pdf)
