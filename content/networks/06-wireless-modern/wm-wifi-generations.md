---
id: wm-wifi-generations
title: Wi-Fi generations and multi-user features
level: basic
minutes: 4
summary: Compare streams, channel width, modulation and scheduling as different improvements.
sourceLesson: wm-wifi
---

Switched Ethernet commonly gives each device a dedicated wired link. Wi-Fi stations share radio resources, but not every station can hear every other. Modern multi-user techniques allow coordinated simultaneous transmissions, and spatial reuse can allow concurrent transmissions in different coverage areas. Radio conditions change with interference, motion and obstacles.

Almost everything distinctive about Wi-Fi follows from that shared, changeable medium: how devices take turns, why they cannot detect collisions, how a slow active client can consume airtime needed by another client, and why a product’s aggregate advertised PHY rates do not predict one client’s application throughput.

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

Dates move: Wi-Fi Alliance certification for Wi-Fi 7 began in January 2024, before IEEE approved 802.11be (September 2024) and published it (July 2025). The next amendment, **802.11bn** ("Ultra High Reliability"), was still a draft in October 2026, with IEEE's own timeline estimating approval in 2028. Check the IEEE 802.11 timeline page for current status.

What each change buys:

- **MIMO** (multiple-input multiple-output): several antennas send independent **spatial streams** on the same frequency at once. Two streams roughly double the rate. The usable count depends on both endpoints and the radio channel; antenna count alone does not establish it.
- **Wider channels**: rate scales roughly with width, so 80 MHz carries about four times a 20 MHz channel.
- **Denser modulation (QAM)**: 256-QAM carries 8 bits per symbol, 1024-QAM 10, 4096-QAM 12. Each step needs a much cleaner signal, so achievable modulation depends on signal quality, interference and hardware, not a fixed distance boundary.
- **OFDMA** (Wi-Fi 6): the channel is split into **resource units**, so the AP can send to or receive from several clients in one transmission instead of one at a time. This can reduce per-client access overhead, depending on scheduling, compatible clients and workload.
- **Target Wake Time** (Wi-Fi 6): devices negotiate when to wake, saving battery for phones and IoT sensors.
- **6 GHz** (Wi-Fi 6E and 7): additional spectrum for capable devices, subject to national power, indoor/outdoor and coexistence rules. It is not interference-free. Country allocations change: for example, in July 2026 Ofcom decided to extend UK licence-exempt Wi-Fi from 5925–6425 MHz up to 6585 MHz, allowing Wi-Fi in the rest of the upper band only under database-controlled coordination, so an undated “UK has only 500 MHz” statement is out of date.
- **Multi-Link Operation** (Wi-Fi 7): coordinates multiple links; concurrent transmission/reception depends on the MLO mode and hardware. It does not require every device to transmit on three bands simultaneously.

## Key takeaways
- Compare streams, channel width, modulation and scheduling as different improvements.
- A generation label does not establish supported modes, spectrum permission or measured throughput.

## Further reading
- [IEEE 802.11 — Wikipedia](https://en.wikipedia.org/wiki/IEEE_802.11)
- [Wi-Fi 6 — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_6)
- [Wi-Fi 7 — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_7)
- [IEEE 802.11 working group: standards timelines](https://www.ieee802.org/11/Reports/802.11_Timelines.htm)
- [Ofcom: upper 6 GHz band decisions](https://www.ofcom.org.uk/spectrum/innovative-use-of-spectrum/consultation-expanding-access-to-the-6-ghz-band-for-commercial-mobile-and-wi-fi-services)
- [Wi-Fi Alliance: Wi-Fi CERTIFIED 7 launch, January 2024](https://rss.globenewswire.com/news-release/2024/01/08/2805409/0/en/wi-fi-alliance-introduces-wi-fi-certified-7.html)
