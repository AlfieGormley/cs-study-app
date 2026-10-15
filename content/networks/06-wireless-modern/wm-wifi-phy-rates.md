---
id: wm-wifi-phy-rates
title: PHY rates and the number on the box
level: basic
minutes: 4
summary: An aggregate router label sums separate radios, while a single-link client uses one link at a time.
sourceLesson: wm-wifi
---

This unit focuses on PHY rates and the number on the box. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Why real throughput is far below the advertised rate

The number on the box is the **maximum PHY rate**, often summed across bands. A PHY rate is just bits per symbol, times the number of subcarriers carrying data, times the number of spatial streams, divided by how long each symbol lasts. For Wi-Fi 6 (HE, "high efficiency"):

```formula
R = (N_ss N_sd b r) / T_sym
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
R_5 = (2 × 1960 × 10 × (5/6)) / 13.6 µs
R_5 ≈ 2,402 Mbit/s
R_{2.4} = (2 × 468 × 10 × (5/6)) / 13.6 µs
R_{2.4} ≈ 574 Mbit/s
R_box = 2,402 Mbit/s + 574 Mbit/s
R_box ≈ 3,000 Mbit/s
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

PHY rate excludes channel-contention waits, interframe gaps, PHY preamble airtime, MAC acknowledgments, headers and retransmissions. Ordinary single-link uploads and downloads also consume shared airtime, including TCP acknowledgments. Other active stations share those resources. These effects explain why useful application throughput can fall below the negotiated PHY rate; the next units quantify particular simplified cases.

Now compare this model with a hypothetical phone’s negotiated PHY rate. The next units examine airtime overhead, sharing and retries.

## 1. The client's link rate is lower

For an example client with two spatial streams using an 80 MHz HE channel and 0.8 µs guard interval, full-channel single-stream PHY rates are approximately:

| MCS | Modulation | 1 stream, 80 MHz |
|---|---|---|
| 0 | BPSK 1/2 | 36 Mbit/s |
| 7 | 64-QAM 5/6 | 360 Mbit/s |
| 9 | 256-QAM 5/6 | 480 Mbit/s |
| 11 | 1024-QAM 5/6 | 600 Mbit/s |

Each row comes from the PHY-rate formula with 980 data subcarriers and a 13.6 µs symbol. For an illustrative negotiated MCS 7 on two streams, the arithmetic is:

```formula
R = (2 × 980 × 6 × (5/6)) / 13.6 µs
R ≈ 720 Mbit/s
where
R: the phone's PHY rate, in megabits per second (Mbit/s)
µs: microsecond, one millionth of a second
Mbit/s: megabits per second
≈: approximately equal to
In words: two streams of 64-QAM (6 bits) at rate 5/6 over 980 subcarriers give about 720 Mbit/s, under a third of the box figure.
```

**Rate adaptation** selects rates using link feedback; the illustrated room count does not predict a particular MCS.

## Key takeaways
- An aggregate router label sums separate radios, while a single-link client uses one link at a time.
- Compute a PHY rate from streams, data subcarriers, modulation, coding and symbol duration.

## Further reading
- [Cisco: Wi-Fi throughput validation and PHY-rate tables](https://www.cisco.com/c/en/us/support/docs/wireless-mobility/wireless-lan-wlan/212892-802-11ac-wireless-throughput-testing-and.html)
