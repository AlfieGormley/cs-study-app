---
id: wm-cellular-radio-states
title: Radio connection states and promotion costs
level: intermediate
minutes: 3
summary: Idle and connected are protocol states rather than literal fixed power levels.
sourceLesson: wm-cellular
---

This unit focuses on radio connection states and promotion costs. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Radio power states and application traffic

Radio activity can contribute substantially to energy use, depending on the device and workload. **RRC** (Radio Resource Control) manages connection states:

```
           ordinary setup path
 RRC_IDLE ----------------> RRC_CONNECTED
 (no RRC      setup:        (RRC context;
  connection) signalling     scheduling
     ^       exchanges        and DRX)
     |                          |
     +--- configured release ---+
          simplified two-state view
```

- **Idle**: the UE has no active RRC connection, but can perform paging monitoring, measurements, reselection and other procedures. It is not powered off.
- **Connected**: RRC context supports scheduled communication; grants and discontinuous reception (DRX) still affect timing and power. Connected does not mean continuously transmitting or always at maximum power.
- NR **RRC_INACTIVE** retains access-stratum context and can make resuming a connection less work than starting from idle. Its supported use is release/deployment-specific; related LTE suspension and newer inactive-state data features make “all packets always need full promotion” too broad.

Two costs follow:

1. **Promotion latency.** When ordinary user-plane transfer requires an idle UE to establish an RRC connection, random access, RRC setup and associated signalling add delay. A quiet period alone does not establish that this transition is required. The delay depends on radio state, procedures, release, coverage and load; no fixed millisecond value is guaranteed.
2. **Tail energy.** Activity can leave the radio in a higher-energy state after payload transfer ends. Timers, DRX and other state transitions determine the cost. Bursts can overlap or share radio activity; connected time is not identical to measured energy.

## Reading an application trace

Suppose the trace explicitly records RRC setup before a first request and no setup before subsequent requests. That observation supports a contribution from connection establishment to the first request’s delay. It does not identify a fixed setup cost or prove that server work and packet loss contributed nothing. Compare radio events with the application’s own timestamps and end-to-end deadline. A later request sent after a quiet interval might use retained context or a different procedure, so infer the state from evidence rather than from the interval alone.

## Key takeaways
- Idle and connected are protocol states rather than literal fixed power levels.
- A measured transition can explain added setup delay; a quiet interval alone does not establish a full promotion.

## Further reading
- [Radio Resource Control — Wikipedia](https://en.wikipedia.org/wiki/Radio_Resource_Control)
- [Android: Optimise network access and radio use](https://developer.android.com/develop/connectivity/network-ops/network-access-optimization)
