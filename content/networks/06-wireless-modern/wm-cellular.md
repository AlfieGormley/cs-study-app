---
id: wm-cellular
title: 4G and 5G networks, and what they mean for apps
level: intermediate
minutes: 14
summary: How a phone's packets travel through the radio network and the mobile core, how the radio's power states affect latency and battery use, and how to write apps that behave well on cellular.
---

Cellular systems centrally schedule much of their radio traffic, unlike basic Wi-Fi contention. This is a distinction in access mechanisms, not a guarantee of collision-free radio or predictable latency: random access, interference, coverage and load still matter. Cellular deployments can use licensed, shared or unlicensed spectrum; Wi-Fi also has scheduled multi-user modes.

For applications, mobile paths introduce changing capacity, radio-state transitions, possible address changes and provider-specific translation or filtering. Design for interruption and measure the devices and networks you support.

## The big picture

Every cellular network has three parts: the phone (the **UE**, user equipment), the **radio access network** (RAN) of base stations, and the **core network** that handles identity, sessions and the gateway to the Internet.

```
 UE ~~radio~~ eNodeB/gNodeB
                 |  (backhaul)
     +-----------+----------+
     | Core                 |
     |  control: MME / AMF  |
     |  sessions: SMF       |
     |  user plane:         |
     |  S-GW+P-GW / UPF ----+--> Internet
     +----------------------+
```

| Part | 4G (LTE / EPC) | 5G (NR / 5GC) |
|---|---|---|
| Base station | eNodeB | gNodeB |
| Attach, mobility | MME | AMF |
| Session control | distributed across MME and gateway control functions | SMF |
| Packet gateway | S-GW + P-GW | UPF |
| Subscriber data / authentication | HSS with associated authentication functions | UDM/UDR for subscriber data; AUSF for authentication |

The 5G core defines **service-based** control-plane functions with HTTP-based service interfaces. Not every interface is HTTP/2: user-plane tunnels and control interfaces such as N4 use other protocols. Functions can be virtualised; earlier generations also support virtualisation, so “5G software versus 4G fixed boxes” is misleading.

### Tunnels keep your IP address still

For an IP session, session establishment selects/allocates addressing and user-plane resources. LTE uses EPS bearers with a P-GW anchor. In 5G, the SMF manages the PDU session and address allocation, potentially using a UPF or external allocation mechanism; a session-anchor UPF forwards user traffic. Not every PDU session carries IP: Ethernet and unstructured types also exist. Relevant radio-to-core user-plane interfaces use **GTP-U**, whose registered destination UDP port is 2152.

The gateway is the **anchor**: to the Internet, your phone lives at the gateway. During a supported handover that preserves the session anchor/address, user-plane paths can be updated while the application retains its IP address. Connections can survive, but radio interruption, loss, session changes or timeout can still break them; no particular vehicle speed guarantees continuity.

Moving to an independently addressed Wi-Fi path commonly changes the effective endpoint address. Keeping the old path alive, provider-integrated access, tunnels or mobility-capable transports can change the outcome.

## Scheduled radio access

LTE and NR use OFDM-based downlink resource allocation. A resource block spans **12 subcarriers**; the number of active subcarriers depends on the channel configuration. In the conventional LTE example, 15 kHz spacing gives 180 kHz per resource block and a 1 ms subframe scheduling interval. Later features and specialised modes qualify a universal 1 ms rule. LTE uplink commonly uses DFT-spread OFDM (SC-FDMA), rather than simply the same downlink waveform.

For dynamically scheduled uplink data without an existing grant, a connected UE can request resources and receive an uplink grant. Existing/configured grants and random-access procedures mean a fresh request/grant is not required for every packet. Scheduling coordinates access but does not eliminate random-access collisions or inter-cell interference; fairness is a scheduler policy, not an automatic guarantee.

5G NR adds flexible **numerology**. Common examples use 15, 30, 60 or 120 kHz spacing. This is not the complete set in later releases. For normal cyclic prefix, the corresponding full-slot duration is `1 ms / 2^μ` with spacing `15 × 2^μ kHz`; mini-slot transmission need not occupy a full slot:

| Spacing | Slot length | Typical use |
|---|---|---|
| 15 kHz | 1 ms | low band, wide coverage |
| 30 kHz | 0.5 ms | mid band (e.g. 3.5 GHz) |
| 120 kHz | 0.125 ms | mmWave |

### Spectrum: coverage versus capacity

NR specifications define release-specific frequency ranges, with different supported bandwidths and spacings:

- **FR1** includes low and mid bands. Lower frequencies often aid coverage, while wider available allocations can provide capacity; actual range depends on power, antennas and surroundings. A 3.5 GHz deployment is an illustrative mid-band case, not a universal regional allocation.
- **FR2** covers higher-frequency NR bands, commonly called mmWave in the industry, and has release-specific subdivisions. Wide channels and beamforming can support high capacity, but blockage and link budget matter. A fixed “few hundred metres” coverage rule is not reliable for every deployment.

> [!note] Why "5G" on your phone may be mostly 4G
> A common **NSA option 3** deployment uses LTE/EPC as the master/core with NR as secondary access. **SA option 2** connects NR to the 5G core. “NSA” has broader architectural usage, and a status icon alone does not prove which capabilities are active. Feature availability depends on release, configuration, device and operator support.

ITU IMT-2020 evaluation requirements include a 20 Gbit/s peak downlink data rate and 4 ms eMBB / 1 ms URLLC user-plane latency targets under their defined conditions. The latency measure is one-way radio user-plane latency, not an Internet ping RTT; the peak rate is not a per-user service guarantee. Scheduling, backhaul, core routing, server work and other path segments contribute to application latency.

## Radio power states and application traffic

Radio activity can contribute substantially to energy use, depending on the device and workload. **RRC** (Radio Resource Control) manages connection states:

```
            data to send
 RRC_IDLE ----------------> RRC_CONNECTED
 (no radio  promotion:      (scheduled,
  resources) signalling      fast, power
     ^       round trips      hungry)
     |                          |
     +--- inactivity timer -----+
          (the "tail")
```

- **Idle**: the UE has no active RRC connection, but can perform paging monitoring, measurements, reselection and other procedures. It is not powered off.
- **Connected**: RRC context supports scheduled communication; grants and discontinuous reception (DRX) still affect timing and power. Connected does not mean continuously transmitting or always at maximum power.
- NR **RRC_INACTIVE** retains access-stratum context and can reduce resumption work relative to idle. Its supported use is release/deployment-specific; related LTE suspension and newer inactive-state data features make “all packets always need full promotion” too broad.

Two costs follow:

1. **Promotion latency.** When ordinary user-plane transfer requires an idle UE to establish an RRC connection, random access, RRC setup and associated signalling add delay. A quiet period alone does not establish that this transition is required. The delay depends on radio state, procedures, release, coverage and load; no fixed millisecond value is guaranteed.
2. **Tail energy.** Activity can leave the radio in a higher-energy state after payload transfer ends. Timers, DRX and other state transitions determine the cost. Bursts can overlap or share radio activity; connected time is not identical to measured energy.

### Worked example: polling versus batching

Use a toy model: instantaneous requests each add an interval `[t, t + 10)` of activity. Count the union of those intervals. Ignore promotion time, transfers, DRX, other applications and observation-window clipping:

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
            on += tail  # new promotion
        else:
            on += t + tail - until  # extend
        until = t + tail
    return on

hour = 3600
poll = list(range(0, hour, 30))
batch = list(range(0, hour, 300))
print(radio_on(poll), radio_on(batch))
# 1200.0 120.0
```

In this model, the supplied one-hour schedules produce 1,200 and 120 seconds of interval coverage. This is not a prediction of battery energy on a real phone. Nearby requests share intervals: `radio_on([0, 4, 8, 50])` returns 28 seconds, not 40.

> [!tip] Practical rules for mobile apps
> - Batch and prefetch: grouping delay-tolerant work can reduce repeated radio activity; avoid downloading unnecessary data.
> - Use the platform push service (APNs, FCM) instead of your own polling or keepalive. Platform-managed delivery can share infrastructure across apps; delivery timing and energy are not free or guaranteed.
> - Defer non-urgent uploads (analytics, logs) until the radio is already active or the device is on Wi-Fi and charging.
> - Expect the first request after idle to be slow; choose measured end-to-end deadlines and retry behaviour rather than assuming a constant first-request cost.

## Addresses, NAT and IPv6

**Carrier-grade NAT** (CGNAT) lets an operator share public IPv4 addresses among many subscribers. The number sharing one address and availability of public addressing vary. Possible consequences:

- Unsolicited inbound IPv4 connections are commonly restricted without suitable mappings/policies. Peer-to-peer applications can use ICE with STUN and, when needed, TURN relays; STUN itself is not a relay.
- NAT mappings expire after a period of idleness, according to protocol and operator policy. Long-lived idle TCP connections can silently die, which is one more reason to use the platform push service.
- Rate-limiting by public IP can group unrelated subscribers; combine appropriate account/token and abuse controls rather than treating an address as one person.

Operators can provide **IPv6-only** access with NAT64/DNS64 or **464XLAT** to reach IPv4 services. 464XLAT combines client-side stateless translation with network-side stateful translation. Apple’s IPv6-only compatibility guidance recommends hostnames and system APIs; some system APIs can synthesise an IPv6 destination even from an IPv4 literal. Raw IPv4-only socket code without translation/synthesis is a different case.

## Mobility between networks

If an application loses its cellular path and must use an independently addressed Wi-Fi path, ordinary TCP cannot simply change its endpoint tuple. Joining Wi-Fi alone does not necessarily close every existing cellular connection.

Ways to cope:

- **Retry idempotent requests** and make uploads resumable.
- **QUIC** identifies connections by a connection ID rather than the 4-tuple, so eligible client migration can preserve a confirmed connection when permitted and the new path works; validation and other conditions still apply.
- **Multipath TCP** can carry one connection over multiple subflows, for example Wi-Fi and cellular, when endpoints and policies support it. It improves mobility options without guaranteeing uninterrupted service.
- Use the OS's path monitoring (`NWPathMonitor` on iOS, `ConnectivityManager` on Android) to react to changes and to check whether the path is **expensive** or **constrained** under the platform’s definitions; these flags are not interchangeable with a simple cellular-versus-Wi-Fi test before downloading large media.

## Performance characteristics to design for

- **Bandwidth varies wildly**: with coverage, scheduling, congestion, device capabilities and backhaul. Use adaptive bitrate streaming and responsive images rather than assuming a speed.
- **Deep buffers**: large persistent queues on a mobile path can add substantial latency under load (bufferbloat); measure the location and size rather than assuming a particular base station buffer. BBR is model-based, using delivery-rate and RTT estimates; it is not simply delay-based and does not universally outperform CUBIC. CUBIC can also react to ECN rather than waiting only for loss.
- **Loss is mostly hidden**: HARQ and, where configured, acknowledged-mode RLC can recover some radio losses before TCP sees them. Retry limits and unacknowledged modes mean not every loss is hidden.
- **Handovers** can cause interruption or loss of varying duration. Design UIs that tolerate a request taking several seconds occasionally.

> [!warning] Testing only on office Wi-Fi
> An app that feels instant on a fast Wi-Fi network can be painful on a train. Use network link conditioners (Xcode's Network Link Conditioner, Android emulator network profiles) to test with high latency, low bandwidth and loss.

## Network slicing and edge computing

With standalone 5G, an operator can create **network slices**: logical networks with selected capabilities and policies; actual end-to-end guarantees require provisioned resources, isolation, admission control and an enforceable service agreement, for example one for low-latency industrial control and one for ordinary broadband, on the same infrastructure.

**Multi-access edge computing** (MEC) can place application compute nearer access networks, potentially reducing the path to a distant cloud region. Placement is not necessarily beside a UPF, and a nearby server alone does not guarantee low end-to-end latency.

## Key takeaways
- Cellular separates user equipment, radio access and core functions. Session anchoring can preserve addresses across supported handovers.
- Scheduled data access coexists with random access, configured grants and interference; cellular is not universally collision-free.
- NR numerology, architecture options and state behaviour are release- and configuration-dependent.
- Batching can reduce radio activity, but a fixed-tail model measures interval coverage, not battery energy.
- Plan for changing capacity, addressing, translation and interruptions. Migration-capable transports also have prerequisites.

> [!note] Evidence limits
> Fixed handover success speeds, radio-state timings, spectrum-wide range figures, operator market shares and guaranteed energy/latency improvements are omitted because no deployment evidence establishes them here. Complete release-specific band tables and advanced inactive-state data procedures are outside this lesson. No cellular modem or operator-network experiment was run.

## Further reading
- [Mobile Networks — High Performance Browser Networking](https://hpbn.co/mobile-networks/)
- [Optimizing for Mobile Networks — High Performance Browser Networking](https://hpbn.co/optimizing-for-mobile-networks/)
- [5G System Overview — 3GPP](https://www.3gpp.org/technologies/5g-system-overview)
- [5G NR — Wikipedia](https://en.wikipedia.org/wiki/5G_NR)
- [System Architecture Evolution (the LTE core) — Wikipedia](https://en.wikipedia.org/wiki/System_Architecture_Evolution)
- [Radio Resource Control — Wikipedia](https://en.wikipedia.org/wiki/Radio_Resource_Control)
- [464XLAT — Wikipedia](https://en.wikipedia.org/wiki/464XLAT)
- [Supporting IPv6-only networks — Apple Developer](https://developer.apple.com/support/ipv6/)

- [Android: Optimise network access and radio use](https://developer.android.com/develop/connectivity/network-ops/network-access-optimization)
- [RFC 6877: 464XLAT](https://www.rfc-editor.org/rfc/rfc6877)
- [3GPP TS 38.211 Release 17: NR physical channels and modulation](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/17.06.00_60/ts_138211v170600p.pdf)
- [ITU-R M.2410: IMT-2020 evaluation requirements](https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-M.2410-2017-PDF-E.pdf)
- [3GPP TS23.501 Release17: 5G system architecture](https://www.etsi.org/deliver/etsi_ts/123500_123599/123501/17.09.00_60/ts_123501v170900p.pdf)
