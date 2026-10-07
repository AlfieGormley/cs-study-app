---
id: wm-wifi
title: Wi-Fi and 802.11
level: basic
minutes: 14
summary: How Wi-Fi shares the air with CSMA/CA, why hidden terminals need RTS/CTS, how channels interfere, what Wi-Fi 4 to 7 changed, and why advertised aggregate PHY rates differ from application throughput.
---

Switched Ethernet commonly gives each device a dedicated wired link. Wi-Fi stations share radio resources, but not every station can hear every other. Modern multi-user techniques allow coordinated simultaneous transmissions, and spatial reuse can allow concurrent transmissions in different coverage areas. Radio conditions change with interference, motion and obstacles.

Almost everything distinctive about Wi-Fi follows from that: how devices take turns, why they cannot detect collisions, how a slow active client can consume airtime needed by another client, and why a product’s aggregate advertised PHY rates do not predict one client’s application throughput.

## The 802.11 generations

Wi-Fi is the Wi-Fi Alliance's brand for the IEEE **802.11** standards. In 2018 the Alliance introduced generation numbers so people did not need to remember letters.

| Name | Standard | Bands | Key additions |
|---|---|---|---|
| Legacy | 802.11b/a/g | b/g: 2.4; a: 5 GHz | b up to 11 Mbit/s; a/g up to 54, with OFDM for a/g |
| Wi-Fi 4 | 802.11n (2009) | 2.4, 5 GHz | MIMO, 40 MHz, aggregation |
| Wi-Fi 5 | 802.11ac (2013) | 5 GHz | 80/160 MHz, 256-QAM, DL MU-MIMO |
| Wi-Fi 6 | 802.11ax; certification began 2019 | 2.4, 5 GHz | OFDMA, 1024-QAM, TWT |
| Wi-Fi 6E | 802.11ax | adds 6 GHz | additional spectrum, subject to local rules |
| Wi-Fi 7 | 802.11be; certification began 2024 | 2.4, 5, 6 GHz | 320 MHz, 4096-QAM, MLO |

What each change buys:

- **MIMO** (multiple-input multiple-output): several antennas send independent **spatial streams** on the same frequency at once. Two streams roughly double the rate. The usable count depends on both endpoints and the radio channel; antenna count alone does not establish it.
- **Wider channels**: rate scales roughly with width, so 80 MHz carries about four times a 20 MHz channel.
- **Denser modulation (QAM)**: 256-QAM carries 8 bits per symbol, 1024-QAM 10, 4096-QAM 12. Each step needs a much cleaner signal, so achievable modulation depends on signal quality, interference and hardware, not a fixed distance boundary.
- **OFDMA** (Wi-Fi 6): the channel is split into **resource units**, so the AP can send to or receive from several clients in one transmission instead of one at a time. This can reduce per-client access overhead, depending on scheduling, compatible clients and workload.
- **Target Wake Time** (Wi-Fi 6): devices negotiate when to wake, saving battery for phones and IoT sensors.
- **6 GHz** (Wi-Fi 6E and 7): additional spectrum for capable devices, subject to national power, indoor/outdoor and coexistence rules. It is not interference-free. Country allocations change: for example, Ofcom published a July 2026 upper-6-GHz sharing decision, so an undated “UK has only 500 MHz” statement is inadequate.
- **Multi-Link Operation** (Wi-Fi 7): coordinates multiple links; concurrent transmission/reception depends on the MLO mode and hardware. It does not require every device to transmit on three bands simultaneously.

## Sharing the air: CSMA/CA

Classic shared Ethernet used **CSMA/CD**: listen before sending, and if you *detect a collision* while transmitting, stop, jam and back off. Wi-Fi cannot do the "CD" part:

1. Ordinary Wi-Fi radios do not implement Ethernet-style collision detection while sending; their own transmit signal makes simultaneous sensing of weak incoming signals difficult.
2. A collision may happen at the receiver but not be audible at the sender at all (see hidden terminals below).

So Wi-Fi tries to **avoid** collisions instead, and uses missing expected acknowledgments as an indication of failure; not every frame is individually acknowledged. The following is a simplified **DCF** contention example for acknowledged unicast using 5 GHz OFDM timings. Modern QoS traffic commonly uses EDCA with access-category parameters; broadcast/multicast and scheduled multi-user exchanges differ:

1. **Carrier sense.** Listen. If the channel is busy, wait until it goes idle.
2. **Wait DIFS.** After the channel goes idle, wait a fixed gap (34 µs on 5 GHz).
3. **Random backoff.** Pick a random number of slots in `[0, CW]` (9 µs slots; CW starts at 15). Count down only while the channel stays idle; freeze the counter if someone else starts sending.
4. **Transmit** when the counter hits zero.
5. **ACK.** The receiver replies after a shorter gap, SIFS (16 µs). The shorter gap gives priority over compliant contenders that sense this exchange; interference and hidden terminals can still corrupt the ACK.
6. **No ACK?** Assume a collision or corruption, grow CW as `min(2 × (CW + 1) − 1, CWmax)` (here 15, 31, 63 ... up to 1023) and try again. After a retry limit, drop the frame.

```
busy |DIFS| backoff |  DATA  |SIFS|ACK|
-----+----+---------+--------+----+---+
      34us  k x 9us           16us
```

There is also **virtual carrier sense**: eligible frames carry Duration/ID information that can reserve remaining exchange time. Stations update their **NAV** (network allocation vector) according to protocol rules. Some fields are zero or have other meanings; physical carrier sensing still applies.

> [!note] Why the random backoff matters
> If two stations both wait for a busy channel to end and then send immediately, they can collide when their transmissions overlap at the receiver. The random countdown spreads them out, and the doubling makes stations back off harder when the channel is congested.

## The hidden terminal problem and RTS/CTS

Carrier sense only works if every station can hear every other. Often they cannot.

```
  (A) ~~~~~~ [AP] ~~~~~~ (C)
   A hears AP, C hears AP,
   A and C cannot hear each other
```

A and C both sense an idle channel and transmit at once. Their frames can interfere **at the AP**, causing missing ACKs and retries. Capture effects or different timings can allow some frames to succeed; throughput need not collapse in every such topology.

**RTS/CTS** can mitigate this when the relevant contenders receive the protection frames:

1. A sends a short **Request To Send** to the AP, with the duration of the exchange.
2. The AP replies **Clear To Send**, also carrying the duration.
3. C cannot hear A's RTS, but it *can* hear the AP's CTS, so it sets its NAV and stays quiet.
4. A sends its data; the AP ACKs.

This reduces the chance of wasting a long data transmission on a hidden-terminal collision. Missed CTS frames, other interferers and overlapping reservations still permit data/ACK loss. The cost is two extra frames and gaps per exchange, so implementations can select protection using an **RTS threshold** and other policies; defaults are device-specific. Wi-Fi 6 also uses RTS/CTS-style protection automatically in some situations, such as before multi-user transmissions.

The mirror image is the **exposed terminal**: a station that hears a nearby transmission and defers, even though its own transmission would not have interfered at its intended receiver. RTS/CTS does not fix this; it is one reason dense networks waste airtime.

## Channels and interference

**2.4 GHz** has channels only 5 MHz apart, but each transmission is about 20 MHz wide. Neighbouring channels therefore overlap, and **1, 6 and 11** is a conventional conservative 20 MHz plan where those channels are permitted. Available channels, PHY spectral masks and interference determine other viable plans; this is not the only possible set worldwide.

```
ch  1     6     11
  [====][====][====]
     [====]
    ch 3 overlaps both 1 and 6
```

Two kinds of interference behave very differently:

- **Co-channel**: your neighbour's AP is also on channel 6. When networks can sense each other, contention helps them share airtime. Collisions, hidden terminals and decoding failures can still occur.
- **Adjacent-channel**: your neighbour is on channel 3. Overlapping energy may interfere without successful frame decoding. Energy detection can still cause deferral, depending on thresholds. The result depends on power, frequency separation, placement and equipment; it is not a universal ranking of channel plans.

> [!tip] Rule of thumb
> In a dense deployment using channels 1–11, 20 MHz with a coordinated 1/6/11 plan is a useful starting point. Check the regulatory domain and survey neighbouring use; wider channels reduce the number of separate channels available.

**5 GHz** has many more 20 MHz channels, enough for several 80 MHz channels. Some are **DFS** channels shared with radar: an AP must listen for radar before using them and vacate if it detects any, which can cause a sudden channel change.

**6 GHz** excludes older 2.4/5-GHz-only Wi-Fi clients, but compatible clients can still use low rates or consume substantial airtime. Other authorised services and neighbouring networks may share spectrum.

At fixed antenna gains and distance, free-space path loss grows with frequency. Actual coverage also depends on permitted power, antenna patterns, wall materials, bandwidth and receiver sensitivity; a frequency label alone does not establish range or throughput. Other things share 2.4 GHz too: Bluetooth, microwave ovens and baby monitors.

## Why real throughput is far below the advertised rate

The number on the box is the **maximum PHY rate**, often summed across bands. Take an "AX3000" router:

- 5 GHz: 2 streams × 160 MHz × 1024-QAM ≈ 2,402 Mbit/s
- 2.4 GHz: 2 streams × 40 MHz ≈ 574 Mbit/s
- Total on the box: ~3,000. A conventional single-link client connection does not obtain this sum. Multiple-radio devices and other aggregation arrangements existed before Wi-Fi 7; MLO standardises coordinated multi-link operation.

Now follow the losses for a real phone.

### 1. The client's link rate is lower

For an example client with two spatial streams using an 80 MHz HE channel and 0.8 µs guard interval, full-channel single-stream PHY rates are approximately:

| MCS | Modulation | 1 stream, 80 MHz |
|---|---|---|
| 0 | BPSK 1/2 | 36 Mbit/s |
| 7 | 64-QAM 5/6 | 360 Mbit/s |
| 9 | 256-QAM 5/6 | 480 Mbit/s |
| 11 | 1024-QAM 5/6 | 600 Mbit/s |

Two rooms away, the phone might negotiate MCS 7 on 2 streams: about **720 Mbit/s**. **Rate adaptation** selects rates using link feedback; the illustrated room count does not predict a particular MCS.

### 2. MAC overhead

Every transmission pays a fixed cost in airtime: DIFS, average backoff, the PHY preamble, SIFS and the acknowledgement. For the calculation below, assume 200 µs per channel access and omit per-MPDU delimiters, padding and variable protocol costs. This is a supplied teaching value, not a universal measured overhead.

```
1 frame of 1500 B at 720 Mbit/s:
  data      12000 / 720e6 ~=   17 us
  overhead                ~=  200 us
  efficiency  17 / 217    ~=   8%

64 frames aggregated (A-MPDU):
  data      64 x 16.667   ~= 1067 us
  efficiency 1067 / 1267  ~=  84%
```

**Frame aggregation** amortises access costs; Block Ack can acknowledge multiple MPDUs. It is an important efficiency mechanism, but no single TCP/PHY efficiency percentage holds for every link.

### 3. Half duplex and sharing

An ordinary single radio link cannot simultaneously transmit and receive on that link. Uploads and downloads consume radio resources; scheduling, OFDMA/MU-MIMO, spatial reuse and multiple links make modern sharing more complex than a single global turn-taking sequence.

### 4. The performance anomaly

In a simplified saturated, equal-priority DCF model with comparable frame sizes, stations obtain similar access opportunities rather than equal airtime. Slow transmissions can then reduce faster stations’ throughput. QoS, aggregation, AP scheduling and airtime policies change this model.

> [!example] One slow client
> A fast client at 54 Mbit/s and a slow one at 6 Mbit/s alternate 1,500-byte frames. Ignoring overhead, a fast frame takes 222 µs and a slow one 2,000 µs. Each cycle of 2,222 µs moves one frame for each, so **both** get about 12,000 / 2,222 µs ≈ 5.4 Mbit/s. The fast client loses 90% of its throughput.

Some APs implement **airtime fairness** policies to mitigate this; capabilities and effectiveness vary. Moving compatible clients to another band can separate contention, but does not guarantee high rates there.

### 5. Loss and retries

Interference and fading cause corrupted frames. Wi-Fi retries at the link layer, which hides most loss from TCP but adds latency and jitter. Under load, large buffers in the AP add more: an illustrative loaded link might show 5 ms idle RTT and 200 ms during a download; this is not a universal measurement or unique diagnosis.

## Practical consequences
- Survey placement, interference, client capabilities and backhaul before changing settings. Wired backhaul avoids consuming wireless backhaul airtime; a dedicated radio still has coexistence and capacity constraints.
- Compare permitted bands for the actual devices and coverage needs. Extra APs need channel and power planning; more is not automatically better.
- Wired connections can remove active traffic from radio contention. An idle device’s removal need not produce a measurable improvement.
- Compare local wired and wireless tests, RSSI/SNR, negotiated rates, retries, airtime use and loaded latency to locate the bottleneck.

## Key takeaways
- Wi-Fi uses shared radio resources; modern multi-user and spatial-reuse mechanisms qualify simple one-transmitter models.
- Contention and acknowledgments reduce or reveal failures; they do not eliminate collisions.
- RTS/CTS can mitigate hidden terminals when protection is received and obeyed.
- A 1/6/11 plan is a common 2.4 GHz starting point, not a worldwide exclusivity rule.
- PHY rate, aggregate product labels and application throughput are different quantities. Rate, aggregation, scheduling, retries and backhaul all matter.

> [!note] Evidence limits
> Universal handset stream counts, fixed TCP efficiency ratios, driver defaults and guaranteed channel-plan outcomes are omitted because they need device-specific evidence. Regional spectrum rules are time-sensitive; consult the regulator before deployment. No RF, coverage, interference or throughput measurements were performed for this lesson.

## Further reading
- [IEEE 802.11 — Wikipedia](https://en.wikipedia.org/wiki/IEEE_802.11)
- [Carrier-sense multiple access with collision avoidance — Wikipedia](https://en.wikipedia.org/wiki/Carrier-sense_multiple_access_with_collision_avoidance)
- [Hidden node problem — Wikipedia](https://en.wikipedia.org/wiki/Hidden_node_problem)
- [List of WLAN channels — Wikipedia](https://en.wikipedia.org/wiki/List_of_WLAN_channels)
- [Wi-Fi 6 — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_6)
- [Wi-Fi 7 — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_7)
- [WiFi — High Performance Browser Networking](https://hpbn.co/wifi/)

- [Cisco: Wi-Fi throughput validation and PHY-rate tables](https://www.cisco.com/c/en/us/support/docs/wireless-mobility/wireless-lan-wlan/212892-802-11ac-wireless-throughput-testing-and.html)
- [Wi-Fi Alliance: Wi-Fi CERTIFIED 7 launch, January 2024](https://rss.globenewswire.com/news-release/2024/01/08/2805409/0/en/wi-fi-alliance-introduces-wi-fi-certified-7.html)
- [Ofcom: 6 GHz spectrum sharing decisions](https://www.ofcom.org.uk/spectrum/innovative-use-of-spectrum/consultation-expanding-access-to-the-6-ghz-band-for-commercial-mobile-and-wi-fi-services)
