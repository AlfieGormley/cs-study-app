---
id: wm-cellular-radio-states
title: Radio connection states and promotion costs
level: intermediate
minutes: 3
summary: Idle and connected are protocol states rather than literal fixed power levels.
sourceLesson: wm-cellular
---

A phone's cellular radio is not simply on or off. It moves between protocol states that trade responsiveness against battery life, and those transitions explain why the first request after a quiet spell is often slow and why chatty background traffic drains batteries.

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

> [!analogy] Real-world analogy: Calling a taxi and keeping it waiting
> If no taxi is waiting, you phone for one and wait for it to arrive before your trip can start. After dropping you off, the driver may wait outside with the meter running for a while in case you need another trip, then leaves.
>
> **How it maps:** Phoning and waiting is promotion from idle to connected (random access and RRC setup), which delays the first request. The taxi waiting with the meter running is the tail: the radio stays in a higher-energy state after the transfer ends, costing battery even though nothing is sent. A second trip during the wait starts immediately, as later requests do while the radio is still connected.
>
> **Where it stops:** The network, not the user, sets how long the radio "waits", and discontinuous reception lets a connected radio sleep in short bursts, so the meter does not run at a constant rate. An idle phone still listens for paging; it is not switched off like a taxi that has driven away.

## Reading an application trace

Suppose the trace explicitly records RRC setup before a first request and no setup before subsequent requests. That observation supports a contribution from connection establishment to the first request’s delay. It does not identify a fixed setup cost or prove that server work and packet loss contributed nothing. Compare radio events with the application’s own timestamps and end-to-end deadline. A later request sent after a quiet interval might use retained context or a different procedure, so infer the state from evidence rather than from the interval alone.

## Key takeaways
- Idle and connected are protocol states rather than literal fixed power levels.
- A measured transition can explain added setup delay; a quiet interval alone does not establish a full promotion.

## Further reading
- [Radio Resource Control — Wikipedia](https://en.wikipedia.org/wiki/Radio_Resource_Control)
- [Android: Optimise network access and radio use](https://developer.android.com/develop/connectivity/network-ops/network-access-optimization)
