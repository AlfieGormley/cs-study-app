---
id: cs2-ticket-booking-waiting-seat-map
title: Waiting-room admission and seat maps
level: advanced
minutes: 3
summary: Meter the crowd into measured downstream capacity while serving availability views cheaply.
sourceLesson: cs2-ticket-booking
---

## Deep dive 2: the virtual waiting room

Without a queue, 2 M people hammer the booking API. The database melts, everyone gets errors, and bots that retry fastest win. A waiting room turns a **thundering herd into a metered stream**.

### How it works
1. Before the sale, fans land on a **static waiting page** served from the CDN.
2. Under this illustrative fairness policy, everyone already waiting receives a **random position** at on-sale time. This removes the incentive to refresh at exactly 10:00:00.000. Later arrivals join the back in arrival order.
3. An **admission controller** releases users at a rate matched to downstream capacity, for example 2,000 per minute, adjusted from live booking latency and error rates.
4. An admitted user receives a **signed, short-lived access token** (a JWT carrying user id, event id and expiry). The booking API and the edge verify it statelessly, with issuer, audience, event, expiry and user/session binding checked. Restrict direct-origin access too; a signature alone does not prevent token sharing or replay.
5. Queue status polling ("you are number 48,213, about 24 min") is answered at the edge from a periodically published counter, not by origin per user.

Cloudflare Waiting Room and Queue-it are commercial versions of this pattern.

### Adjusting the admission rate
Little’s law links long-run average occupancy, arrival rate and residence time. Use it to understand the direction of load changes, then enforce measured capacity and live feedback.

If shoppers remain inside longer, the same admission rate builds a larger active population. Reduce admissions when checkout slows; use observed concurrency and downstream health rather than treating a long-run average as a hard capacity bound.

Little's law gives a long-run average; keep a safety margin and adapt the rate to bursts and to live latency and error rates.

### Bots and fairness
- Pre-registration plus lottery ("Verified Fan"), so only vetted accounts enter the queue.
- One queue position per account, card and device fingerprint.
- CAPTCHA or proof-of-work at the queue entrance, not at checkout, which is too late.
- Per-account ticket limits enforced in the hold transaction.

## Deep dive 3: the seat map

In a read-heavy ticketing workload, seat-map reads can greatly outnumber inventory writes. Serve it from a cache (Redis, or a per-section document) refreshed every 1–2 s from the inventory database or its change stream. It *will* sometimes show a seat as available that was just taken. That's fine, because the hold's conditional update is the real check, and the UI handles the 409 gracefully ("someone just grabbed that one").

For huge on-sales, offer **"best available"** instead of free picking. The server chooses contiguous seats from a pre-computed list, which can reduce contention when a coordinated allocator spreads requests among distinct eligible blocks. The list alone does not prevent concurrent allocators choosing the same block.

## Key takeaways
- Serve waiting pages and queue status at the edge.
- Bind signed admission tokens to the event, audience and shopper; prevent origin bypass.
- Cache seat maps and handle allocation conflicts, or offer best-available seats to cut contention.

## Further reading
- [Cloudflare Waiting Room (developer docs)](https://developers.cloudflare.com/waiting-room/)
- [Building Cloudflare Waiting Room (Cloudflare blog)](https://blog.cloudflare.com/cloudflare-waiting-room/)
- [Explicit locking (PostgreSQL docs)](https://www.postgresql.org/docs/current/explicit-locking.html)
