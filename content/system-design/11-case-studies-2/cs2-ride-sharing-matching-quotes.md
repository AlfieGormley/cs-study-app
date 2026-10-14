---
id: cs2-ride-sharing-matching-quotes
title: Matching, offers and price quotes
level: intermediate
minutes: 4
summary: Coordinate driver reservations while treating location and surge signals as separate policies.
sourceLesson: cs2-ride-sharing
---

## Deep dive 3: matching

### Candidate generation and ranking
1. Use a cell neighborhood large enough for the intended search area; a fixed graph radius is only an approximation to a metric radius. Expand candidates as needed and filter/rank by actual distance or ETA.
2. Filter to `status = available` and to the right vehicle type.
3. Ask the **ETA service** (routing on a road graph with live traffic) for the top ~10 by straight-line distance.
4. Rank by ETA, plus factors such as acceptance rate and keeping drivers' earnings fair.

### Offering without double-booking
The crucial correctness property is that **a driver holds at most one offer or trip**. Make driver state an explicit state machine with a compare-and-set:

This SQL fragment uses driver ID and version parameters bound by the application. The surrounding transaction must coordinate the corresponding trip reservation.

```sql
-- Compete only for this available version.
UPDATE drivers
SET state='offered', state_version=:v+1
WHERE driver_id=:driver
  AND state='available'
  AND state_version=:v;
```

Only one dispatcher can win that CAS. The offer goes out with a TTL (say 15 s). Bind the offer to a unique offer ID and epoch. A timeout may release only that same still-pending offer; it must not undo a later acceptance or offer. Acceptance must atomically validate and update the driver reservation and trip, or use a recoverable protocol preserving both invariants. Two unrelated CAS operations alone are insufficient.

### Greedy versus batched matching
Greedy matching (each request immediately takes the nearest driver) is locally optimal but globally poor. Two riders a block apart can each grab the driver better suited to the other. An illustrative **batched matching** design collects requests for a short window (say 1–2 s), build a cost matrix of ETAs, and solve the assignment problem (for example, Hungarian-style algorithms). The cost is a little extra latency in exchange for lower average pickup times across the city.

## Deep dive 4: surge pricing

Surge balances the market. Higher prices can influence supply and demand; the size and timing of the response are empirical and market-dependent.

1. A stream job (Flink or Kafka Streams) consumes ride requests (demand) and available-driver pings (supply).
2. Every ~1 minute, per H3 cell (around resolution 7–8), compute demand/supply over an overlapping stream time window.
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

> **Content gap:** no end-to-end dispatch benchmark, exact failover bound or measured matching/surge improvement is supplied. Batch windows, location intervals and price-hold rules here are design assumptions, not verified current Uber/Lyft internals.

## Key takeaways
- Fence offers and atomically coordinate authoritative driver and trip acceptance.
- Batched matching trades a small wait for better fleet-wide assignment.
- A validated unexpired quote preserves the offered price while surge changes asynchronously.

## Further reading
- [H3: hexagonal hierarchical geospatial indexing (docs)](https://h3geo.org/docs/)
- [Optimistic concurrency control (Wikipedia)](https://en.wikipedia.org/wiki/Optimistic_concurrency_control)
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
