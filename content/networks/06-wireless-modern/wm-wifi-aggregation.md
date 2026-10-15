---
id: wm-wifi-aggregation
title: Frame aggregation and airtime efficiency
level: basic
minutes: 3
summary: A fixed channel-access cost overwhelms a short frame but can be shared by an aggregate.
sourceLesson: wm-wifi
---

This unit focuses on frame aggregation and airtime efficiency. It builds on the earlier units in this module; the examples below state their additional assumptions.

## 2. MAC overhead

Every transmission pays a fixed cost in airtime: DIFS, average backoff, the PHY preamble, SIFS and the acknowledgement. For the calculation below, assume 200 µs per channel access and omit per-MPDU delimiters, padding and variable protocol costs. This is a supplied teaching value, not a universal measured overhead.

The fraction of airtime that carries data is the efficiency:

```formula
T_data = (nL) / R
η = T_data / (T_data + T_oh)
n = 1: T_data = 12,000 bit / 720 Mbit/s
T_data ≈ 16.67 µs
η = 16.67 µs / (16.67 µs + 200 µs)
η ≈ 8%
n = 64: T_data = 64 × 16.67 µs ≈ 1067 µs
η = 1067 µs / (1067 µs + 200 µs) ≈ 84%
where
T_data: the airtime spent sending the frames' data, in microseconds (µs)
n: the number of frames sent in one channel access (aggregated together as an A-MPDU when more than one)
L: the size of one frame in bits; 1,500 bytes × 8 = 12,000 bits
R: the PHY rate, 720 Mbit/s here; dividing bits by Mbit/s gives microseconds
η: eta, the airtime efficiency: the fraction of airtime carrying data, between 0 and 1
T_oh: the fixed overhead per channel access, 200 µs in this teaching model
bit: one binary digit
Mbit/s: megabits per second, one million bits per second
µs: microsecond, one millionth of a second
≈: approximately equal to
In words: a fixed 200 µs cost swamps one short frame, but becomes small when many frames share one access.
```

**Frame aggregation** amortises access costs; Block Ack can acknowledge multiple MPDUs. It is an important efficiency mechanism, but no single TCP/PHY efficiency percentage holds for every link.

## Key takeaways
- A fixed channel-access cost overwhelms a short frame but can be shared by an aggregate.
- The supplied 200-microsecond model omits variable per-frame overhead and is not a measured efficiency guarantee.

## Further reading
- [WiFi — High Performance Browser Networking](https://hpbn.co/wifi/)
- [Cisco: Wi-Fi throughput validation and PHY-rate tables](https://www.cisco.com/c/en/us/support/docs/wireless-mobility/wireless-lan-wlan/212892-802-11ac-wireless-throughput-testing-and.html)
