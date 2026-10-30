---
id: wm-cellular-batching-model
title: Batching requests and radio-tail models
level: intermediate
minutes: 3
summary: Count the union of request-tail intervals so overlapping activity is counted once.
sourceLesson: wm-cellular
---

Because each burst of network activity keeps the radio awake for a tail afterwards, *when* an app sends data matters as much as *how much* it sends. A simple model shows why batching and push notifications save battery.

## A toy model: polling versus batching

Assume each request keeps the radio active from its arrival until 10 seconds later. Ignore promotion time, transfer time, DRX and other apps. Requests close together share one active period: a request that arrives while the radio is still active only extends the period, while a request after the period has ended starts a whole new 10 seconds. In other words, each request adds either a full tail or just the gap since the previous request, whichever is smaller.

```
10 s tail after each request (# = active)

poll every 30 s:
##########....................##########...
active about 1/3 of the time

batch every 300 s:
##########..............(290 s idle)...
active about 1/30 of the time
```

Over one hour:

- **Polling every 30 s**: 120 requests, each gap longer than the tail, so each pays a full 10 s. The radio is active for about 1,200 s, a third of the hour.
- **Batching every 5 minutes**: 12 requests, so about 120 s active, a tenth as much.
- **Clustering**: requests at 0, 4 and 8 s, then one at 50 s, give 18 s of activity for the cluster plus 10 s for the straggler: 28 s, not 40.

The amount of data hardly matters in this model: a 50-byte heartbeat costs the same tail as a larger upload. What matters is how many separate bursts there are and how far apart they fall.

This is a model of active time, not a prediction of battery energy on a real phone. Real radios use timers set by the network, DRX sleep cycles and different power levels, but the direction of the effect is the same: fewer, grouped bursts mean fewer tails.

> [!tip] Practical rules for mobile apps
> - Batch and prefetch: grouping delay-tolerant work can reduce repeated radio activity; avoid downloading unnecessary data.
> - Use the platform push service (APNs, FCM) instead of your own polling or keepalive. Platform-managed delivery can share infrastructure across apps; delivery timing and energy are not free or guaranteed.
> - Defer non-urgent uploads (analytics, logs) until the radio is already active or the device is on Wi-Fi and charging.
> - Expect the first request after idle to be slow; choose measured end-to-end deadlines and retry behaviour rather than assuming a constant first-request cost.

## Key takeaways
- Requests that fall inside an existing tail share it; isolated requests each pay a full tail.
- Reduced interval coverage is a model result; real energy depends on radio procedures, workload and hardware.

## Further reading
- [Optimizing for Mobile Networks — High Performance Browser Networking](https://hpbn.co/optimizing-for-mobile-networks/)
- [Android: Optimise network access and radio use](https://developer.android.com/develop/connectivity/network-ops/network-access-optimization)
