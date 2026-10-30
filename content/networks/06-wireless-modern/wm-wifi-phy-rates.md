---
id: wm-wifi-phy-rates
title: PHY rates and the number on the box
level: basic
minutes: 4
summary: An aggregate router label sums separate radios, while a single-link client uses one link at a time.
sourceLesson: wm-wifi
---

A router box says "AX3000", yet a phone in the next room measures a few hundred megabits per second. Nothing is broken: the box number is a different quantity from what one client can achieve, and seeing what goes into it explains the gap.

## What the number on the box is

The number on the box is the **maximum PHY rate**, often summed across bands. A PHY rate is the raw bit rate of one link while it is transmitting: bits per symbol, times the number of subcarriers carrying data, times the number of spatial streams, divided by how long each symbol lasts.

```formula reference
R = (N_ss N_sd b r) / T_sym
where
R: the PHY rate, in megabits per second (Mbit/s)
N_ss: the number of spatial streams, e.g. 2
N_sd: the number of data subcarriers in the channel: 234 at 20 MHz, 468 at 40 MHz, 980 at 80 MHz and 1960 at 160 MHz for Wi-Fi 6
b: bits per subcarrier per symbol, set by the modulation: 1 for BPSK, 6 for 64-QAM, 8 for 256-QAM, 10 for 1024-QAM
r: the coding rate: the fraction of transmitted bits that are real data rather than error-correction redundancy, e.g. 5/6
T_sym: the duration of one OFDM symbol including its guard interval, in microseconds (µs): 12.8 µs + 0.8 µs = 13.6 µs for Wi-Fi 6 (HE) with the shortest guard interval
In words: the rate grows with more spatial streams, a wider channel (more subcarriers), denser modulation and less error-correction redundancy, and falls if each symbol takes longer.
```

An "AX3000" Wi-Fi 6 router typically gets its name like this, assuming 1024-QAM with rate-5/6 coding and a 0.8 µs guard interval on both radios:

- the 5 GHz radio, 2 streams on a 160 MHz channel: about 2,402 Mbit/s;
- the 2.4 GHz radio, 2 streams on a 40 MHz channel: about 574 Mbit/s;
- added together: about 3,000.

A conventional single-link client uses only one of those radios at a time, so it can never see the sum. Multiple-radio devices and other link-bonding arrangements existed before Wi-Fi 7; MLO standardises coordinated multi-link operation.

## Why one client gets far less

**1. The client's link rate is lower.** Many clients cannot use, or are not offered, a 160 MHz channel, and few have a clean enough signal for 1024-QAM. **Rate adaptation** picks the modulation and coding (the **MCS**) from link feedback. For one stream on an 80 MHz Wi-Fi 6 channel with a 0.8 µs guard interval, the PHY rates are approximately:

| MCS | Modulation | 1 stream, 80 MHz |
|---|---|---|
| 0 | BPSK 1/2 | 36 Mbit/s |
| 7 | 64-QAM 5/6 | 360 Mbit/s |
| 9 | 256-QAM 5/6 | 480 Mbit/s |
| 11 | 1024-QAM 5/6 | 600 Mbit/s |

A two-stream phone at MCS 7 on 80 MHz therefore runs at about 720 Mbit/s, under a third of the box figure, before any overhead. Moving further away or behind walls pushes the MCS lower still.

**2. PHY rate is not throughput.** The PHY rate excludes channel-contention waits, interframe gaps, PHY preamble airtime, MAC acknowledgments, headers and retransmissions. Ordinary single-link uploads and downloads also share the same airtime, including TCP acknowledgments, and other active stations take their turns too. The next two lessons look at fixed per-access overhead and at sharing airtime.

> [!analogy] Real-world analogy: The top speed in the car brochure
> A brochure quotes a car's top speed; a family that owns two cars might even add both top speeds together. Your actual journey time depends on which car you took, the road you are on, junctions, traffic lights and other traffic.
>
> **How it maps:** Each car's top speed is one radio's best-case PHY rate, and adding the two cars is the "AX3000" sum. The road conditions that keep you below top speed are the lower MCS chosen for your signal quality, and the junctions and traffic are contention, overhead and other stations sharing the air.
>
> **Where it stops:** A car can hold a steady speed between junctions; rate adaptation can change a Wi-Fi link's rate from one frame to the next, and every station on the channel takes turns on the same "road" rather than driving side by side.

## Key takeaways
- An aggregate router label sums separate radios, while a single-link client uses one link at a time.
- A client's PHY rate depends on its streams, channel width and the MCS its signal supports; overhead and sharing reduce throughput further.

## Further reading
- [Cisco: Wi-Fi throughput validation and PHY-rate tables](https://www.cisco.com/c/en/us/support/docs/wireless-mobility/wireless-lan-wlan/212892-802-11ac-wireless-throughput-testing-and.html)
