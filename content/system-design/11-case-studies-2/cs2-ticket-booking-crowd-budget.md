---
id: cs2-ticket-booking-crowd-budget
title: Ticket demand and admission capacity
level: advanced
minutes: 5
summary: Compare scarce inventory with crowd size and separate edge reads from booking writes.
sourceLesson: cs2-ticket-booking
---

Ticket booking combines two problems that pull in opposite directions. **Correctness**: at most one active booking owns seat 14F for an event. **Extreme, spiky load**: millions of fans arrive in the same minute for 60,000 seats. This is an illustrative workload, not a reconstruction of a particular ticketing incident.

The interview insight is that you **don't** scale the booking core to millions of visitors. You **shape the traffic** so the core only ever sees what it can handle, and make that core strictly correct.

## Requirements

### Functional
- Browse events and view the seat map with live-ish availability.
- Select seats and **hold** them for a few minutes while paying.
- Pay and confirm. Tickets are issued.
- Holds expire automatically and seats return to the pool.
- For on-sales, a fair **queue** decides who gets to shop, and in what order.

### Non-functional
- **No double-booking, ever.** This is the hard constraint.
- Browsing can be eventually consistent (a seat map a few seconds stale is fine). Holding and booking must be strongly consistent.
- Survive **100x+** normal traffic for an hour, without collapse.
- Fairness and bot resistance.
- Booking p99 latency of a second or two. Payment latency is mostly outside our control.

## Supply is fixed; admission is a control

In an illustrative 60,000-seat event with average four-seat orders, only about 15,000 orders can succeed. Millions of interested shoppers cannot all buy. A faster system can allocate the same seats more efficiently, but cannot remove the need for fair rejection and clear sold-out feedback.

Separate three loads:

| Visitors | Work they create |
|---|---|
| Waiting fans | Static pages and approximate queue status |
| Admitted shoppers | Seat-map reads and hold attempts |
| Checking-out buyers | Authorisation, capture and durable inventory transitions |

Keep waiting traffic away from the inventory database. If every waiting-page refresh queries the booking core, the waiting room merely renames the overload. Use an edge-friendly status path with authenticated queue identity and controlled admission.

## Size the admitted work, then adjust it

Admitted concurrency and user behaviour determine map and hold traffic. Some shoppers leave quickly; others retry conflicting seats or remain through slow payment. Benchmark these behaviours under contention, not just an evenly spread write load.

A slow payment provider can become the binding limit even when the API has spare CPU. Reduce admission as latency, errors or pending checkouts grow. Scaling stateless servers cannot remove a hot inventory row or a downstream quota.

These workload assumptions describe a hypothetical ticketing service. Set concurrency and rate limits from measured dependencies, and make queue position, access-token expiry and sold-out behaviour part of the product contract.

## Key takeaways
- Oversubscription makes fair rejection a central product requirement.
- Admitted concurrency determines map and hold traffic reaching the core.
- Capacity assumptions need contention benchmarks rather than a promise about one shard.

## Further reading
- [Cloudflare Waiting Room (developer docs)](https://developers.cloudflare.com/waiting-room/)
- [Building Cloudflare Waiting Room (Cloudflare blog)](https://blog.cloudflare.com/cloudflare-waiting-room/)
- [Ticketmaster system design breakdown (Hello Interview)](https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster)
