---
id: cs2-ride-sharing
title: Ride-sharing (Uber / Lyft)
level: intermediate
minutes: 16
summary: Design a ride-hailing backend, covering high-rate driver location ingestion, geospatial indexing with geohash, quadtrees, S2 and H3, rider-driver matching, and surge pricing.
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

Uber reported nearly 11.3 billion trips for 2024, about 31 M a day, but that figure includes Uber Eats deliveries, so rides alone are a good deal fewer. Design for a large ride-hailing platform:

```
Trips:      20 M/day
  avg  20e6 / 86,400  = ~230/s
  peak (5x, Friday evening) = ~1,200/s
Online drivers at peak: 2 M
Location update every 4 s:
  2e6 / 4 = 500,000 writes/s
Payload ~100 B (id, lat, lng,
  heading, speed, ts, status)
  500k x 100 B = 50 MB/s ingest
```

What matters:

- **500 k writes/s** of location, each overwriting the previous one. A rebuildable in-memory index is a useful design option; durable stores can also handle high write rates when partitioned and provisioned appropriately.
- The latest-location state is tiny: 2 M drivers × ~100 B = **200 MB**. That is raw payload only: geospatial indexes, identifiers, object overhead and replication increase memory. Sharding choices need measured memory and throughput.
- Trip writes are modest (around a thousand a second), but they must be transactional.
- Location history for trip receipts and analytics: 500 k/s × 100 B × 86,400 = about **4.3 TB/day**, streamed to cheap storage.

## API design

```
// driver app (persistent connection)
WS  /v1/driver/stream
  -> {lat, lng, heading, ts}   every 4 s
  <- {type:"offer", trip_id, pickup, ttl}

POST /v1/driver/offers/{trip_id}/accept

// rider app
GET  /v1/quotes?pickup=..&dropoff=..
  -> {quote_id, price, surge, expires_at}
POST /v1/trips
  {quote_id, pickup, dropoff}
  Idempotency-Key: <uuid>
  -> {trip_id, status:"matching"}
GET  /v1/trips/{id}   (or subscribe via WS)
```

The **quote** locks the price, including surge, for a few minutes. That way the rider pays what they were shown, even if surge changes a second later. The **idempotency key** on `POST /trips` stops a flaky network retry from booking two cars.

## Data model

```
// in-memory, sharded by geo cell
driver_loc: driver_id -> {lat,lng,ts,
                          status,cell}
cell_index: cell_id -> set(driver_id)

// durable (sharded SQL / document DB)
trips(trip_id PK, rider_id, driver_id,
      status, quote_id, pickup, dropoff,
      fare, version, created_at)
drivers(driver_id PK, vehicle, rating,
        state, state_version)
```

Trips are sharded by `trip_id` (or by city, for locality). The trip row carries a `version` used for optimistic concurrency on state transitions.

## High-level architecture

```
 Driver app          Rider app
     |                   |
     v                   v
+-----------------------------+
|  Edge / WebSocket gateway   |
+-----------------------------+
   |            |          |
   v            v          v
+--------+ +----------+ +-------+
|Location| | Dispatch | | Trip  |
|service | | /matching| |service|
+--------+ +----------+ +-------+
   |   \        |          |
   v    \       v          v
+------+ \  +-------+  +-------+
| Geo  |  ->| Kafka |  |Trip DB|
|index |    +-------+  +-------+
|(RAM) |        |
+------+        v
          +-----------+
          |Surge, ETA,|
          | analytics |
          +-----------+
```

## Deep dive 1: ingesting locations

Drivers keep a persistent connection (WebSocket, gRPC stream, or MQTT) to a gateway. Persistent streams reduce per-message headers. HTTP keep-alive or HTTP/2 can also reuse TLS connections, so each HTTP update need not incur a handshake.

For each update, the location service:

1. Validates it (drops GPS jumps of 5 km in 4 s, and out-of-order timestamps).
2. Computes the driver's **cell id** at the indexing resolution.
3. Updates `driver_loc`. If the cell changed, it moves the driver between `cell_index` sets.
4. Publishes the update to Kafka for surge, ETA models, fraud checks and trip trails.

The in-memory index is **sharded by cell**, with neighbouring cells grouped onto the same shard where possible. Uber's dispatch system famously sharded geo-state across a consistent-hash ring (their open-source Ringpop library, using SWIM gossip for membership). Historical Ringpop is an example, not a claim about the current entire Uber stack. For this soft-state index, fresh connected-driver pings can rebuild locations after routing recovers. Four seconds is the nominal update interval, not a failover bound; disconnected drivers remain missing. This is a deliberate choice: **soft state** you can afford to lose.

## Deep dive 2: geospatial indexing

The query is "the K nearest available drivers within R km of the rider". A lexicographic B-tree on `(lat,lng)` is not a general efficient radius index. Spatial trees, database spatial indexes or cell mappings can support 2D searches.

### Geohash

Geohash interleaves latitude and longitude bits and base-32 encodes them. Shared prefixes mean nearby cells.

| Length | Approx. width × height near equator |
|---|---|
| 5 | 4.9 km × 4.9 km |
| 6 | 1.2 km × 0.6 km |
| 7 | 153 m × 153 m |

- **Pros**: simple, works as a string key in any KV store or DB. Redis `GEOSEARCH` uses a 52-bit geohash in a sorted set.
- **Cons**: the **edge problem**. Two points a metre apart across a cell boundary can share no prefix, so a radius search must cover every cell intersecting the search area and then filter by exact distance. The centre cell plus eight neighbours is sufficient only when the chosen cell size and search radius justify that coverage. Cells are also rectangles that distort with latitude.

### Quadtree

Recursively split a region into four until each leaf holds at most N points (say 100).

- **Pros**: adapts to density. Central London gets tiny cells and the countryside gets huge ones, which can help manage local density. Query work still depends on radius and the number of results.
- **Cons**: it's an in-memory structure that must be rebalanced as points move. With 500 k moves a second, splitting and merging nodes gets expensive, so it suits slow-changing data (restaurants, shops) better than moving cars.

### S2 (Google)

S2 projects the sphere onto a cube and orders cells along a **Hilbert curve**, which preserves locality better than geohash's Z-order. Cells have 64-bit ids across 31 levels. A circle can be **covered** by a small set of cells at mixed levels, giving a handful of id ranges to scan. Uber's early dispatch sharded by S2 cell.

### H3 (Uber)

H3 tiles the world in **hexagons** across 16 resolutions (0 to 15). Each step down is roughly 7 times smaller in area. Average cell sizes from the H3 docs:

| Resolution | Avg area | Avg edge |
|---|---|---|
| 7 | ~5.2 km² | ~1.4 km |
| 8 | ~0.74 km² | ~530 m |
| 9 | ~0.11 km² | ~200 m |

These are averages: because H3 projects from an icosahedron, hexagon area at one resolution varies by up to about 2x across the globe (excluding the smaller pentagons), though neighbouring cells in one city are very close in size. A sphere can't be tiled with hexagons alone, so each resolution also has 12 pentagons.

- A regular planar hexagon has six equally spaced neighbours. H3 approximates this geometry on a sphere; actual centre distances vary with projection distortion and pentagon boundaries. A square has edge neighbours and corner neighbours at different distances. This makes "k-ring" searches (all cells within k steps) and smoothing across neighbours clean.
- Uber built H3 specifically for surge pricing and supply/demand analysis.

> [!tip] What to say in the interview
> "I'd index drivers by H3 cell at about resolution 8 in an in-memory sharded store. For a request, I take a k-ring around the rider's cell, gather the available drivers, then rank them by road-network ETA, not straight-line distance." That names a real scheme, handles the edge problem, and shows you know crow-flies distance is misleading (think of a river with no bridge).

## Deep dive 3: matching

### Candidate generation and ranking
1. Use a cell neighborhood large enough for the intended search area; a fixed graph radius is only an approximation to a metric radius. Expand candidates as needed and filter/rank by actual distance or ETA.
2. Filter to `status = available` and to the right vehicle type.
3. Ask the **ETA service** (routing on a road graph with live traffic) for the top ~10 by straight-line distance.
4. Rank by ETA, plus factors such as acceptance rate and keeping drivers' earnings fair.

### Offering without double-booking
The crucial correctness property is that **a driver holds at most one offer or trip**. Make driver state an explicit state machine with a compare-and-set:

```
UPDATE drivers
SET state='offered', state_version=v+1
WHERE driver_id=? AND state='available'
  AND state_version=v
```

Only one dispatcher can win that CAS. The offer goes out with a TTL (say 15 s). Bind the offer to a unique offer ID and epoch. A timeout may release only that same still-pending offer; it must not undo a later acceptance or offer. Acceptance must atomically validate and update the driver reservation and trip, or use a recoverable protocol preserving both invariants. Two unrelated CAS operations alone are insufficient.

### Greedy versus batched matching
Greedy matching (each request immediately takes the nearest driver) is locally optimal but globally poor. Two riders a block apart can each grab the driver better suited to the other. An illustrative **batched matching** design collects requests for a short window (say 1–2 s), build a cost matrix of ETAs, and solve the assignment problem (for example, Hungarian-style algorithms). The cost is a little extra latency in exchange for lower average pickup times across the city.

## Deep dive 4: surge pricing

Surge balances the market. Higher prices can influence supply and demand; the size and timing of the response are empirical and market-dependent.

1. A stream job (Flink or Kafka Streams) consumes ride requests (demand) and available-driver pings (supply).
2. Every ~1 minute, per H3 cell (around resolution 7–8), compute demand/supply over a sliding window.
3. **Smooth** across neighbouring hexagons and across time. This reduces abrupt boundary changes; it does not eliminate flicker or strategic behavior.
4. Map the ratio to a multiplier via a pricing model, capped by policy and regulation.
5. Write `cell -> multiplier` to a low-latency KV store that the quote service reads.

The quote service returns a `quote_id` holding the price. `POST /trips` honours it until expiry, which keeps pricing consistent even though surge is eventually consistent.

## Trip lifecycle and reliability

```
requested -> matching -> driver_assigned
  -> driver_arrived -> in_trip
  -> completed -> paid
(cancel possible from early states)
```

Persist every transition durably, using optimistic concurrency. Emit events (outbox pattern) so payments, receipts and notifications react asynchronously. Payment runs *after* the trip on a separate, idempotent path, which can decouple post-trip charging from dispatch. Preauthorisation, risk checks or payment eligibility may still be dependencies in another product policy.

For the live map, the rider subscribes to the driver's location, and the gateway pushes updates every few seconds over the rider's WebSocket. The client interpolates movement between points so the car glides rather than jumps.

## Bottlenecks and trade-offs

- **Hot cells**: a stadium emptying creates 50 k requests in one hexagon. Finer cells for dense areas, and batching, keep any one shard from melting.
- **Consistency vs availability**: locations are AP (stale by seconds is fine). Driver assignment and trip state are CP (they must never double-book). Mixing the two tiers deliberately is the key insight.
- **Straight-line vs ETA**: ETA calls are expensive, so pre-filter cheaply by cell and call routing only for the top candidates.
- **Mobile networks**: drivers drop out in tunnels. Treat a driver as stale after ~30 s without a ping and exclude them from matching.

## Evolving at 10x

- **5 M writes/s of location**: shard per city or region. Cities are natural failure and scaling domains, since a trip rarely spans two of them.
- **Multi-region**: active cities can be distributed among home regions with standby replicas. For each city, safe failover needs fenced ownership and a defined replication-loss policy. A driver phone may supply recovery evidence but cannot independently prove authoritative trip/payment state.
- **Richer products** (pooling, scheduled rides, deliveries) turn matching into a vehicle-routing problem. Batch windows and optimisation solvers grow in importance.
- **Edge compute**: run dispatch close to users for latency, and keep only aggregates global.

## Key takeaways
- Location ingestion is huge in writes (hundreds of thousands a second) but small in state (hundreds of MB). A sharded in-memory soft-state index is one option; evaluate durable alternatives against measured requirements.
- Map 2D space to keys. Geohash is simple but has the edge problem. Quadtrees adapt to density but suit slowly changing data. S2 and H3 are widely used alternatives with different geometry and hierarchy tradeoffs; H3 neighbor distances are not perfectly uniform on the sphere.
- Rank candidates by road-network ETA, not distance, and consider batched assignment over greedy matching.
- Use conditional state transitions with offer fencing and atomic driver/trip acceptance to prevent double-dispatch. Keep locations eventually consistent.
- Lock surge into a quote with an expiry, so prices stay consistent for the rider even though surge itself is computed asynchronously.

> **Content gap:** no end-to-end dispatch benchmark, exact failover bound or measured matching/surge improvement is supplied. Batch windows, location intervals and price-hold rules here are design assumptions, not verified current Uber/Lyft internals.

## Further reading
- [H3: hexagonal hierarchical geospatial indexing (docs)](https://h3geo.org/docs/)
- [S2 Geometry library](https://s2geometry.io/)
- [Geohash (Wikipedia)](https://en.wikipedia.org/wiki/Geohash)
- [Quadtree (Wikipedia)](https://en.wikipedia.org/wiki/Quadtree)
- [Optimistic concurrency control (Wikipedia)](https://en.wikipedia.org/wiki/Optimistic_concurrency_control)
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
