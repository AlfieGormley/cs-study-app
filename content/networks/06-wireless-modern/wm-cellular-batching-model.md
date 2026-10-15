---
id: wm-cellular-batching-model
title: Batching requests and radio-tail models
level: intermediate
minutes: 4
summary: Count the union of request-tail intervals so overlapping activity is counted once.
sourceLesson: wm-cellular
---

This unit focuses on batching requests and radio-tail models. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Worked example: polling versus batching

Use a toy model: each instantaneous request keeps the radio active from its arrival until 10 seconds later. Count the union of those intervals, so overlapping tails are counted once. Ignore promotion time, transfers, DRX, other applications and observation-window clipping. Sorting requests by time, each one adds whichever is smaller, a full tail or the gap since the previous request:

```formula
ΔT_i = min(T_tail, t_i − t_{i−1})
T_on = Σ ΔT_i
N_poll = 3600 s / 30 s = 120
T_poll = 120 × 10 s = 1,200 s
N_batch = 3600 s / 300 s = 12
T_batch = 12 × 10 s = 120 s
where
ΔT_i: delta-T-i, the extra active time added by request i, in seconds (s)
min: the minimum function: the smaller of its two values
T_tail: the tail: how long the radio stays active after a request, 10 s in this model
i: the request position in time-sorted order, beginning with 1
t_i: the time of request i, in seconds
t_{i−1}: the time of the previous request; for the very first request, ΔT_1 is a full tail
T_on: the total time the radio is active, in seconds
Σ: sigma, "the sum of": add up ΔT_i for every request
N_poll: the number of requests in one hour (3,600 s) when polling every 30 s
T_poll: the active time for polling, where every gap exceeds the tail so each request adds a full 10 s
N_batch: the number of requests in one hour when batching every 300 s
T_batch: the active time for batching
s: second
In words: a request that arrives during an existing tail only extends it; a request after the tail ends pays a whole new tail.
```

With polling every 30 s, each gap is longer than the 10 s tail, so every request pays in full. The same rule as Python:

```python
from math import isfinite

def radio_on(times, tail=10.0):
    """Union length of tail intervals."""
    times = list(times)
    if not isfinite(tail) or tail < 0:
        raise ValueError("invalid tail")
    if any(not isfinite(t) for t in times):
        raise ValueError("invalid time")
    on, until = 0.0, None
    for t in sorted(times):
        if until is None or t > until:
            # Disjoint interval: count all.
            on += tail
        else:
            # Overlap: count only extension.
            on += t + tail - until
        # Sorted arrivals move the end
        # ahead.
        until = t + tail
    return on

hour = 3600
poll = list(range(0, hour, 30))
batch = list(range(0, hour, 300))
print(radio_on(poll), radio_on(batch))
# Active seconds in the isolated model:
# 1200.0 120.0
```

In this model, the supplied one-hour schedules produce 1,200 and 120 seconds of interval coverage. This is not a prediction of battery energy on a real phone. Nearby requests share intervals: `radio_on([0, 4, 8, 50])` returns 28 seconds, not 40.

> [!tip] Practical rules for mobile apps
> - Batch and prefetch: grouping delay-tolerant work can reduce repeated radio activity; avoid downloading unnecessary data.
> - Use the platform push service (APNs, FCM) instead of your own polling or keepalive. Platform-managed delivery can share infrastructure across apps; delivery timing and energy are not free or guaranteed.
> - Defer non-urgent uploads (analytics, logs) until the radio is already active or the device is on Wi-Fi and charging.
> - Expect the first request after idle to be slow; choose measured end-to-end deadlines and retry behaviour rather than assuming a constant first-request cost.

## Key takeaways
- Count the union of request-tail intervals so overlapping activity is counted once.
- Reduced interval coverage is a model result; real energy depends on radio procedures, workload and hardware.

## Further reading
- [Optimizing for Mobile Networks — High Performance Browser Networking](https://hpbn.co/optimizing-for-mobile-networks/)
- [Android: Optimise network access and radio use](https://developer.android.com/develop/connectivity/network-ops/network-access-optimization)
