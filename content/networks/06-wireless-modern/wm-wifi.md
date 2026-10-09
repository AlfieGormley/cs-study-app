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
| Wi-Fi 4 | 802.11n (2009) | 2.4, 5 GHz | MIMO, 40 MHz, frame aggregation |
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

### Why denser modulation needs a cleaner signal

A QAM symbol is one of M possible points (amplitude-and-phase combinations). The number of bits one symbol carries is the base-2 logarithm of the number of points:

```formula
b = log_2(M)
b = log_2(1024) = 10
where
b: the number of bits carried by one QAM symbol on one subcarrier
M: the number of distinct points in the QAM constellation, e.g. 256, 1024 or 4096
log_2: the base-2 logarithm: the power you must raise 2 to in order to get the number, so log_2(1024) = 10 because 2^10 = 1024
In words: every doubling of the number of constellation points adds just one bit per symbol.
```

So 256-QAM carries 8 bits (eight doublings of 1 give 256), 1024-QAM 10 bits and 4096-QAM 12 bits. Going from 1024 to 4096 points adds only 2 bits (+20%), but squeezes four times as many points into the same space, so the receiver must tell apart points that sit much closer together. Noise that a 256-QAM receiver shrugs off makes a 4096-QAM receiver pick the wrong point.

The **Shannon–Hartley theorem** sets the theoretical ceiling on any channel, whatever the modulation. It applies to a channel disturbed by random (Gaussian) noise:

```formula
C = B × log_2(1 + S / N)
C = 20 MHz × log_2(1 + 1000)
C ≈ 20 MHz × 9.97 ≈ 199 Mbit/s
where
C: the channel capacity: the highest error-free data rate theoretically possible, in bits per second (bit/s)
B: the channel bandwidth, in hertz (Hz); here a 20 MHz Wi-Fi channel
S: the received signal power, in watts (W)
N: the noise power in the same channel, in watts (W)
S / N: the signal-to-noise ratio (SNR) as a plain ratio; 1000 here, which is 30 dB
log_2: the base-2 logarithm (log_2(1024) = 10)
MHz: megahertz, one million hertz
Hz: hertz, cycles per second
Mbit/s: megabits per second, one million bits per second
≈: approximately equal to
In words: capacity grows in proportion to bandwidth, but only with the logarithm of signal quality, so doubling channel width roughly doubles capacity while doubling signal power adds only about 1 bit/s per hertz once the signal is already well above the noise.
```

At 30 dB SNR the ceiling is about 10 bits per second per hertz, which is why 1024-QAM (10 bits per symbol) needs an excellent signal and is used only close to the AP. SNR is usually quoted in decibels:

```formula
SNR_dB = 10 × log_10(S / N)
SNR_dB = 10 × log_10(1000) = 30 dB
where
SNR_dB: the signal-to-noise ratio expressed in decibels (dB)
S: the received signal power, in watts (W)
N: the noise power, in watts (W)
log_10: the base-10 logarithm, so log_10(1000) = 3 because 10^3 = 1000
dB: decibel, a logarithmic unit for a power ratio: +10 dB means ten times the power, +3 dB about double
In words: every extra 10 dB of SNR means the signal is ten times stronger relative to the noise.
```

Real radios fall short of the Shannon limit and also lose rate to coding and guard intervals, so the table of rates later in this lesson sits below it.

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
6. **No ACK?** Assume a collision or corruption, grow CW (here 15, 31, 63 ... up to 1023) and try again. After a retry limit, drop the frame.

The contention window roughly doubles after each failure, capped at a maximum:

```formula
CW_new = min(2 × (CW_old + 1) − 1, CW_max)
CW = 15 → 31 → 63 → 127 … → 1023
T_backoff = k × t_slot
where
CW_old: the contention window before the failed attempt, in slots; 15 for a first attempt in this example
CW_new: the contention window for the next attempt, in slots
CW_max: the cap on the contention window, 1023 slots here
CW: the contention window: the highest backoff count a station may draw
min: the minimum function: whichever of its values is smaller
→: "becomes, after the next failure"
…: the pattern continues in the same way
T_backoff: the idle time a station counts down before transmitting, in microseconds (µs)
k: the random whole number of slots the station draws, anywhere from 0 to CW inclusive
t_slot: the slot time, 9 µs for 5 GHz OFDM
µs: microsecond, one millionth of a second
In words: every failure roughly doubles the range of random waits, so stations on a congested channel spread their retries ever more widely, up to the cap.
```

For example, a station that draws k = 7 on its first attempt waits 7 × 9 µs = 63 µs of idle channel. After three failures it draws from 0 to 127, a wait of up to 1.143 ms.

The interframe gaps follow the same slot arithmetic:

```formula
DIFS = SIFS + 2 × t_slot
DIFS = 16 µs + 2 × 9 µs = 34 µs
where
DIFS: the DCF interframe space: the idle gap a station must see before starting contention, in microseconds (µs)
SIFS: the short interframe space: the gap before an ACK or other immediate reply, 16 µs for 5 GHz OFDM
t_slot: the slot time, 9 µs for 5 GHz OFDM
µs: microsecond, one millionth of a second
In words: a station waiting to contend must stay quiet two slots longer than one sending an ACK, so the ACK always gets in first.
```

```
busy |DIFS| backoff |  DATA  |SIFS|ACK|
-----+----+---------+--------+----+---+
      34us  k x 9us           16us
```

In the timeline, k is the random slot count from the formula above.

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

The centre frequency of each 2.4 GHz channel follows a simple rule (channels 1 to 13; Japan's channel 14 is a special case):

```formula
f_c = 2407 MHz + 5 MHz × n
f_1 = 2407 + 5 × 1 = 2412 MHz
f_6 = 2407 + 5 × 6 = 2437 MHz
f_11 = 2407 + 5 × 11 = 2462 MHz
where
f_c: the centre frequency of channel n, in megahertz (MHz)
n: the channel number, 1 to 13
f_1: the centre of channel 1
f_6: the centre of channel 6
f_11: the centre of channel 11
MHz: megahertz, one million hertz (cycles per second)
In words: each channel number moves the centre up by 5 MHz, so channels five numbers apart are 25 MHz apart, more than one 20 MHz-wide transmission.
```

Channels 1 and 3, by contrast, are only 10 MHz apart, so their 20 MHz-wide signals overlap by about half.

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

At fixed antenna gains and distance, **free-space path loss** grows with frequency. It is the loss between two ideal antennas with nothing in the way, so it is a best case:

```formula
L_fs = 20 × log_10(4 × π × d × f / c)
4 × π × 10 m × 2.437 GHz / c ≈ 1022
L_{2.4} = 20 × log_10(1022) ≈ 60.2 dB
4 × π × 10 m × 5.5 GHz / c ≈ 2305
L_{5.5} = 20 × log_10(2305) ≈ 67.3 dB
where
L_fs: the free-space path loss between two isotropic antennas, in decibels (dB)
d: the distance between the antennas, in metres (m); 10 m here
f: the signal frequency, in hertz (Hz); 2.437 GHz (channel 6) and 5.5 GHz here
c: the speed of light, about 299,792,458 metres per second (m/s)
π: pi, about 3.14159
log_10: the base-10 logarithm
L_{2.4}: the loss at 2.437 GHz over 10 m
L_{5.5}: the loss at 5.5 GHz over 10 m
m: metre
GHz: gigahertz, one billion (10^9) hertz
dB: decibel; every 10 dB is a factor of ten in power
≈: approximately equal to
In words: the loss rises 6 dB (four times less received power) every time you double the distance or double the frequency.
```

So at 10 m the 5.5 GHz signal arrives about 7 dB weaker, roughly one fifth of the power, than the 2.4 GHz one. Walls make the gap larger in practice, because they absorb higher frequencies more. Actual coverage also depends on permitted power, antenna patterns, wall materials, bandwidth and receiver sensitivity; a frequency label alone does not establish range or throughput. Other things share 2.4 GHz too: Bluetooth, microwave ovens and baby monitors.

## Why real throughput is far below the advertised rate

The number on the box is the **maximum PHY rate**, often summed across bands. A PHY rate is just bits per symbol, times the number of subcarriers carrying data, times the number of spatial streams, divided by how long each symbol lasts. For Wi-Fi 6 (HE, "high efficiency"):

```formula
R = N_ss × N_sd × b × r / T_sym
where
R: the PHY rate, in megabits per second (Mbit/s)
N_ss: the number of spatial streams, e.g. 2
N_sd: the number of data subcarriers in the channel: 234 at 20 MHz, 468 at 40 MHz, 980 at 80 MHz and 1960 at 160 MHz for Wi-Fi 6
b: bits per subcarrier per symbol, set by the modulation: 1 for BPSK, 6 for 64-QAM, 8 for 256-QAM, 10 for 1024-QAM
r: the coding rate: the fraction of transmitted bits that are real data rather than error-correction redundancy, e.g. 5/6
T_sym: the duration of one OFDM symbol including its guard interval, in microseconds (µs): 12.8 µs + 0.8 µs = 13.6 µs here
In words: rate grows with streams, channel width (more subcarriers), denser modulation and less redundancy, and falls if each symbol takes longer.
```

Take an "AX3000" router, using 1024-QAM with rate-5/6 coding and a 0.8 µs guard interval on both radios:

```formula
R_5 = 2 × 1960 × 10 × (5/6) / 13.6 µs
R_5 ≈ 2,402 Mbit/s
R_{2.4} = 2 × 468 × 10 × (5/6) / 13.6 µs
R_{2.4} ≈ 574 Mbit/s
R_box = 2,402 + 574 ≈ 3,000 Mbit/s
where
R_5: the 5 GHz radio's maximum PHY rate: 2 streams of a 160 MHz channel (1960 data subcarriers)
R_{2.4}: the 2.4 GHz radio's maximum PHY rate: 2 streams of a 40 MHz channel (468 data subcarriers)
R_box: the sum printed on the box as "3000"
µs: microsecond, one millionth of a second; bits per microsecond equal megabits per second
Mbit/s: megabits per second, one million bits per second
≈: approximately equal to
In words: "AX3000" adds the best cases of two separate radios; a conventional single-link client uses only one of them at a time.
```

A conventional single-link client connection does not obtain this sum. Multiple-radio devices and other link-bonding arrangements existed before Wi-Fi 7; MLO standardises coordinated multi-link operation.

Now follow the losses for a real phone.

### 1. The client's link rate is lower

For an example client with two spatial streams using an 80 MHz HE channel and 0.8 µs guard interval, full-channel single-stream PHY rates are approximately:

| MCS | Modulation | 1 stream, 80 MHz |
|---|---|---|
| 0 | BPSK 1/2 | 36 Mbit/s |
| 7 | 64-QAM 5/6 | 360 Mbit/s |
| 9 | 256-QAM 5/6 | 480 Mbit/s |
| 11 | 1024-QAM 5/6 | 600 Mbit/s |

Each row comes from the PHY-rate formula with 980 data subcarriers and a 13.6 µs symbol. Two rooms away, the phone might negotiate MCS 7 on 2 streams:

```formula
R = 2 × 980 × 6 × (5/6) / 13.6 µs
R ≈ 720 Mbit/s
where
R: the phone's PHY rate, in megabits per second (Mbit/s)
µs: microsecond, one millionth of a second
Mbit/s: megabits per second
≈: approximately equal to
In words: two streams of 64-QAM (6 bits) at rate 5/6 over 980 subcarriers give about 720 Mbit/s, under a third of the box figure.
```

**Rate adaptation** selects rates using link feedback; the illustrated room count does not predict a particular MCS.

### 2. MAC overhead

Every transmission pays a fixed cost in airtime: DIFS, average backoff, the PHY preamble, SIFS and the acknowledgement. For the calculation below, assume 200 µs per channel access and omit per-MPDU delimiters, padding and variable protocol costs. This is a supplied teaching value, not a universal measured overhead.

The fraction of airtime that carries data is the efficiency:

```formula
T_data = n × L / R
η = T_data / (T_data + T_oh)
n = 1:  T_data = 12,000 / 720 ≈ 17 µs
η = 17 / (17 + 200) ≈ 8%
n = 64:  T_data = 64 × 16.67 ≈ 1067 µs
η = 1067 / (1067 + 200) ≈ 84%
where
T_data: the airtime spent sending the frames' data, in microseconds (µs)
n: the number of frames sent in one channel access (aggregated together as an A-MPDU when more than one)
L: the size of one frame in bits; 1,500 bytes × 8 = 12,000 bits
R: the PHY rate, 720 Mbit/s here; dividing bits by Mbit/s gives microseconds
η: eta, the airtime efficiency: the fraction of airtime carrying data, between 0 and 1
T_oh: the fixed overhead per channel access, 200 µs in this teaching model
µs: microsecond, one millionth of a second
≈: approximately equal to
In words: a fixed 200 µs cost swamps one short frame, but becomes small when many frames share one access.
```

**Frame aggregation** amortises access costs; Block Ack can acknowledge multiple MPDUs. It is an important efficiency mechanism, but no single TCP/PHY efficiency percentage holds for every link.

### 3. Half duplex and sharing

An ordinary single radio link cannot simultaneously transmit and receive on that link. Uploads and downloads consume radio resources; scheduling, OFDMA/MU-MIMO, spatial reuse and multiple links make modern sharing more complex than a single global turn-taking sequence.

### 4. The performance anomaly

In a simplified saturated, equal-priority DCF model with comparable frame sizes, stations obtain similar access opportunities rather than equal airtime. Slow transmissions can then reduce faster stations’ throughput. QoS, frame aggregation, AP scheduling and airtime policies change this model.

> [!example] One slow client
> A fast client at 54 Mbit/s and a slow one at 6 Mbit/s alternate 1,500-byte frames, ignoring overhead. Each cycle moves one frame for each, so **both** get the same throughput, about 5.4 Mbit/s. The fast client loses 90% of its throughput.

The calculation behind the example:

```formula
T_F = L / R_F = 12,000 / 54 ≈ 222 µs
T_S = L / R_S = 12,000 / 6 = 2,000 µs
X = L / (T_F + T_S)
X = 12,000 / 2,222 µs ≈ 5.4 Mbit/s
where
T_F: the airtime of one fast-client frame, in microseconds (µs)
T_S: the airtime of one slow-client frame
R_F: the fast client's link rate, 54 Mbit/s
R_S: the slow client's link rate, 6 Mbit/s
X: the throughput each client gets, in megabits per second (Mbit/s)
L: the frame size in bits: 1,500 bytes × 8 = 12,000 bits
µs: microsecond, one millionth of a second; bits per µs equal Mbit/s
Mbit/s: megabits per second
≈: approximately equal to
In words: taking turns frame by frame means both clients move at the pace set mostly by the slow one.
```

The fast client gets 5.4 of its possible 54 Mbit/s. The model assumes both clients always have a frame waiting and get equal turns.

Some APs implement **airtime fairness** policies to mitigate this; capabilities and effectiveness vary. Moving compatible clients to another band can separate contention, but does not guarantee high rates there.

### 5. Loss and retries

Interference and fading cause corrupted frames. Wi-Fi retries at the link layer, which hides most loss from TCP but adds latency and jitter. Under load, large buffers in the AP add more: an illustrative loaded link might show 5 ms idle RTT and 200 ms during a download; this is not a universal measurement or unique diagnosis.

## Practical consequences
- Survey placement, interference, client capabilities and backhaul before changing configuration. Wired backhaul avoids consuming wireless backhaul airtime; a dedicated radio still has coexistence and capacity constraints.
- Compare permitted bands for the actual devices and coverage needs. Extra APs need channel and power planning; more is not automatically better.
- Wired connections can remove active traffic from radio contention. An idle device’s removal need not produce a measurable improvement.
- Compare local wired and wireless tests, RSSI/SNR, negotiated rates, retries, airtime use and loaded latency to locate the bottleneck.

## Key takeaways
- Wi-Fi uses shared radio resources; modern multi-user and spatial-reuse mechanisms qualify simple one-transmitter models.
- Contention and acknowledgments reduce or reveal failures; they do not eliminate collisions.
- RTS/CTS can mitigate hidden terminals when protection is received and obeyed.
- A 1/6/11 plan is a common 2.4 GHz starting point, not a worldwide exclusivity rule.
- PHY rate, aggregate product labels and application throughput are different quantities. Rate, frame aggregation, scheduling, retries and backhaul all matter.

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
