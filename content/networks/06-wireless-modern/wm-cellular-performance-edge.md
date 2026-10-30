---
id: wm-cellular-performance-edge
title: Mobile performance, slicing and edge computing
level: intermediate
minutes: 3
summary: Measure varying capacity, queueing and interruptions rather than assigning fixed cellular timings.
sourceLesson: wm-cellular
---

Mobile paths change capacity from second to second, hide some losses behind link-layer retries, and can queue data deeply under load. Apps that assume a steady fast connection feel broken on a train; apps designed for variation feel fine.

## Performance characteristics to design for

- **Bandwidth varies wildly**: with coverage, scheduling, congestion, device capabilities and backhaul. Use adaptive bitrate streaming and responsive images rather than assuming a speed.
- **Deep buffers**: large persistent queues on a mobile path can add substantial latency under load (bufferbloat); measure the location and size rather than assuming a particular base station buffer. BBR is model-based, using delivery-rate and RTT estimates; it is not simply delay-based and does not universally outperform CUBIC. CUBIC can also react to ECN rather than waiting only for loss.
- **Loss is mostly hidden**: HARQ and, where configured, acknowledged-mode RLC can recover some radio losses before TCP sees them. Retry limits and unacknowledged modes mean not every loss is hidden.
- **Handovers** can cause interruption or loss of varying duration. Design UIs that tolerate a request taking several seconds occasionally.

> [!warning] Testing only on office Wi-Fi
> An app that feels instant on a fast Wi-Fi network can be painful on a train. Use network link conditioners (Xcode's Network Link Conditioner, Android emulator network profiles) to test with high latency, low bandwidth and loss.

## Network slicing and edge computing

With standalone 5G, an operator can create **network slices**: logical networks with selected capabilities and policies; actual end-to-end guarantees require provisioned resources, isolation, admission control and an enforceable service agreement, for example one for low-latency industrial control and one for ordinary broadband, on the same infrastructure.

**Multi-access edge computing** (MEC) can place application compute nearer access networks, potentially reducing the path to a distant cloud region. Placement is not necessarily beside a UPF, and a nearby server alone does not guarantee low latency for the application.

> [!note] Evidence limits
> Fixed handover success speeds, radio-state timings, spectrum-wide range figures, operator market shares and guaranteed energy/latency improvements are omitted because no deployment evidence establishes them here. Complete release-specific band tables and advanced inactive-state data procedures are outside this lesson. No cellular modem or operator-network experiment was run.

## Key takeaways
- Measure varying capacity, queueing and interruptions rather than assigning fixed cellular timings.
- A slice or nearby compute placement needs resources and path engineering to achieve a service guarantee.

## Further reading
- [Mobile Networks — High Performance Browser Networking](https://hpbn.co/mobile-networks/)
- [Optimizing for Mobile Networks — High Performance Browser Networking](https://hpbn.co/optimizing-for-mobile-networks/)
- [ETSI: Multi-access Edge Computing](https://www.etsi.org/technologies/multi-access-edge-computing)
