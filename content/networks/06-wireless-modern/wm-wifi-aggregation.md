---
id: wm-wifi-aggregation
title: Frame aggregation and airtime efficiency
level: basic
minutes: 3
summary: A fixed channel-access cost overwhelms a short frame but can be shared by an aggregate.
sourceLesson: wm-wifi
---

Every time a Wi-Fi station wins the channel it pays a fixed cost in airtime before and after its data. At high PHY rates the data itself is so quick to send that this fixed cost dominates, which is why faster modulation alone stops helping and why Wi-Fi bundles frames together.

## The fixed cost of each channel access

Each access pays for DIFS, the average backoff, the PHY preamble, SIFS and the acknowledgment. For this lesson's illustration, assume about 200 µs per access and ignore smaller per-frame costs such as delimiters and padding. This is a teaching value, not a universal measured overhead.

At 720 Mbit/s, one 1,500-byte frame takes only about 17 µs to send. So a single frame per access spends about 17 µs on data and 200 µs on overhead: only about 8% of the airtime carries data.

The share of airtime carrying data is the **airtime efficiency**:

```formula reference
η = T_data / (T_data + T_oh)
where
η: eta, the airtime efficiency: the fraction of airtime carrying data, between 0 and 1
T_data: the airtime spent sending data in one channel access, in microseconds (µs)
T_oh: the fixed overhead per channel access, in microseconds (µs)
µs: microsecond, one millionth of a second
In words: efficiency is the data time divided by the whole time of an access; a large fixed overhead makes it small unless each access carries a lot of data.
```

Two ways to raise efficiency behave very differently:

- **A faster PHY rate** shrinks only the data part. Going from 17 µs to 8.5 µs of data per access barely changes a 217 µs access, so efficiency falls further and throughput hardly improves.
- **Sending more data per access** spreads the same overhead across more bytes. With 64 frames in one access, about 1,070 µs of data shares the 200 µs overhead, so roughly 84% of the airtime carries data.

**Frame aggregation** does the second. An **A-MPDU** packs many frames into one transmission, and a **Block Ack** acknowledges them together, so the access cost is paid once. It is one of the most important efficiency mechanisms in Wi-Fi 4 and later, but the gain depends on having enough queued data for the same receiver: sparse, latency-sensitive traffic cannot always be aggregated. No single efficiency percentage holds for every link.

> [!analogy] Real-world analogy: A car ferry with a fixed crossing time
> A ferry spends the same time docking, lowering its ramp and crossing whether it carries one car or forty; only driving the cars on and off grows with the load. Sailing with one car wastes nearly the whole trip. Hiring quicker drivers who board in half the time hardly helps, but filling the deck makes every crossing count.
>
> **How it maps:** Each crossing is one channel access, and the docking and crossing time is the fixed overhead. Driving cars on and off is the data airtime, so quicker drivers are a higher PHY rate, which shrinks only that small part. Filling the deck is frame aggregation.
>
> **Where it stops:** A ferry's crossing time does not change with traffic, but Wi-Fi's backoff and retries grow when the channel is busy. One damaged frame in an aggregate can be retransmitted on its own, whereas a ferry does not send a single car back across.

## Key takeaways
- A fixed channel-access cost overwhelms a short frame but can be shared by an aggregate.
- At high PHY rates, aggregation improves efficiency far more than an even faster rate.
- The 200-microsecond model omits variable per-frame overhead and is not a measured efficiency guarantee.

## Further reading
- [WiFi — High Performance Browser Networking](https://hpbn.co/wifi/)
- [Cisco: Wi-Fi throughput validation and PHY-rate tables](https://www.cisco.com/c/en/us/support/docs/wireless-mobility/wireless-lan-wlan/212892-802-11ac-wireless-throughput-testing-and.html)
