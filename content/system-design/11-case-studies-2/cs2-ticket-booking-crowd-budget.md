---
id: cs2-ticket-booking-crowd-budget
title: Ticket demand and admission capacity
level: advanced
minutes: 5
summary: Compare scarce inventory with crowd size and separate edge reads from booking writes.
sourceLesson: cs2-ticket-booking
---

Ticket booking combines two problems that pull in opposite directions. **Correctness**: at most one active booking owns seat 14F for an event. **Extreme, spiky load**: millions of fans arrive in the same minute for 60,000 seats. The famous failure was the November 2022 Taylor Swift Eras Tour presale. About 1.5 M verified fans had been sent codes, but Ticketmaster said its systems saw around 3.5 B requests, four times its previous peak. The figures come from company statements at the time, so treat them as approximate.

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

## Back-of-the-envelope

Start with supply. A stadium has 60,000 seats and the average order is 4 seats, so the number of orders that can ever succeed is:

```formula
O = S / q
O = 60,000 seats / 4 seats = 15,000
where
O: successful orders the event can sell
S: seats in the stadium; here 60,000
q: average seats per order; assumed 4
seats: individual tickets
In words: 60,000 seats sold four at a time is only 15,000 winning orders.
```

Now demand. Assume 2–14 M (2 to 14 million) fans arrive at the on-sale. Compare that with the orders available:

```formula
x = F / O
x = 2,000,000 / 15,000 ≈ 133
x = 14,000,000 / 15,000 ≈ 933
where
x: how many fans there are for each order that can succeed (the oversubscription ratio)
F: fans at the on-sale; an assumed 2 to 14 million
O: successful orders available; 15,000
≈: approximately equal to
In words: there are between about 133 and 933 fans for every order that can be sold.
```

The traffic each part of the system sees is "users × how often each one sends a request". Fans in the waiting room poll for their position every 30 seconds:

```formula
R_wait = F / i
R_wait = 2,000,000 / 30 s ≈ 67,000 req/s
where
R_wait: waiting-room status requests per second
F: fans waiting; here the low estimate, 2 million
i: polling interval, in seconds (s); here 30
s: seconds
req: HTTP requests
≈: approximately equal to
In words: 2 million fans each checking every 30 seconds is about 67,000 requests a second, all of which must be answered at the edge.
```

Only admitted shoppers reach the seat map and the holds. Assume 50,000 shoppers at a time, each refreshing the seat map every 5 seconds and trying about 2 holds a minute:

```formula
R_map = 50,000 / 5 s = 10,000 req/s
R_hold = (50,000 × 2) / (60 s)
R_hold ≈ 1,700 holds/s
where
R_map: seat-map reads per second (cacheable)
R_hold: hold attempts per second reaching the inventory database
50,000: shoppers admitted at once
5 s: seconds between one shopper's map refreshes
2: hold attempts per shopper per minute
60 s: one minute
s: seconds
req: HTTP requests
holds: hold attempts (conditional writes)
≈: approximately equal to
In words: 50,000 shoppers make about 10,000 cacheable map reads and about 1,700 hold writes every second.
```

All of these are planning assumptions, not measured Ticketmaster figures.

What matters:

- **Under the assumed four-seat order size, demand is about 133–933 times the 15,000 available orders.** Most visitors will leave without tickets. The system's job is to make that happen fairly and cheaply.
- The hold/booking core needs only **thousands of writes a second** at peak, if admissions are throttled. Whether one event partition can sustain this depends on its measured contention, transaction duration, indexes and replication.
- The waiting room has to absorb **tens of thousands of requests a second**, so serve it from the edge or CDN with almost no origin calls.

## Key takeaways
- Oversubscription makes fair rejection a central product requirement.
- Admitted concurrency determines map and hold traffic reaching the core.
- Capacity assumptions need contention benchmarks rather than a promise about one shard.

## Further reading
- [Cloudflare Waiting Room (developer docs)](https://developers.cloudflare.com/waiting-room/)
- [Building Cloudflare Waiting Room (Cloudflare blog)](https://blog.cloudflare.com/cloudflare-waiting-room/)
- [Ticketmaster system design breakdown (Hello Interview)](https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster)
- [Ticketmaster 2022 company statement](https://business.ticketmaster.com/press-release/taylor-swift-the-eras-tour-onsale-explained/)
