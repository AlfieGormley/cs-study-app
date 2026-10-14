---
id: cs2-ride-sharing-location-contracts
title: Ride location ingestion and recovery
level: intermediate
minutes: 4
summary: Stream sequenced positions into a partitioned soft-state index with durable trip contracts.
sourceLesson: cs2-ride-sharing
---

## API design

This is an illustrative endpoint contract, not a runnable HTTP request. Arrows distinguish responses from submitted fields.

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

This is a schema sketch: PK marks the primary key. It omits executable type declarations and migrations.

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

Follow the arrows as data paths; the drawing is not a deployment specification.

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

## Bottlenecks and trade-offs

- **Hot cells**: a stadium emptying creates 50 k requests in one hexagon. Finer cells for dense areas, and batching, keep any one shard from melting.
- **Consistency vs availability**: in CAP theorem terms, locations are AP, favouring availability (stale by seconds is fine). Driver assignment and trip state are CP, favouring consistency (they must never double-book). Mixing the two tiers deliberately is the key insight.
- **Straight-line vs ETA**: ETA calls are expensive, so pre-filter cheaply by cell and call routing only for the top candidates.
- **Mobile networks**: drivers drop out in tunnels. Treat a driver as stale after ~30 s without a ping and exclude them from matching.

## Evolving at 10x

- **5 M writes/s of location**: shard per city or region. Cities are natural failure and scaling domains, since a trip rarely spans two of them.
- **Multi-region**: active cities can be distributed among home regions with standby replicas. For each city, safe failover needs fenced ownership and a defined replication-loss policy. A driver phone may supply recovery evidence but cannot independently prove authoritative trip/payment state.
- **Richer products** (pooling, scheduled rides, deliveries) turn matching into a vehicle-routing problem. Batch windows and optimisation solvers grow in importance.
- **Edge compute**: run dispatch close to users for latency, and keep only aggregates global.

## Key takeaways
- Rebuild candidate locations from fresh pings while keeping trips durable.
- Atomic logical-operation deduplication prevents mobile retries from creating two trips.
- Hot-cell and region ownership plans require measured throughput and fenced recovery.

## Further reading
- [H3: hexagonal hierarchical geospatial indexing (docs)](https://h3geo.org/docs/)
- [S2 Geometry library](https://s2geometry.io/)
- [Optimistic concurrency control (Wikipedia)](https://en.wikipedia.org/wiki/Optimistic_concurrency_control)
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
