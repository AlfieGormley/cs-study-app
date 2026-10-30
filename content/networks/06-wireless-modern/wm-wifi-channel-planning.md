---
id: wm-wifi-channel-planning
title: Channels, interference and radio propagation
level: basic
minutes: 4
summary: Start with a permitted, surveyed channel plan; overlapping energy and coordinated co-channel sharing differ.
sourceLesson: wm-wifi
---

Which channel an access point uses, and how wide it is, decides who it competes with and who merely interferes with it. A good channel plan is the cheapest Wi-Fi performance fix, and radio propagation explains why the bands behave differently.

## Channels and interference

**2.4 GHz** has channels only 5 MHz apart, but each transmission is about 20 MHz wide. Neighbouring channels therefore overlap, and **1, 6 and 11** is a conventional conservative 20 MHz plan where those channels are permitted. Available channels, PHY spectral masks and interference determine other viable plans; this is not the only possible set worldwide.

Channel 1 is centred at 2412 MHz and each channel number adds 5 MHz (channels 1 to 13; Japan's channel 14 is a special case). So channels 1, 6 and 11 sit at 2412, 2437 and 2462 MHz: 25 MHz apart, more than one 20 MHz-wide transmission.

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

With antennas of fixed gain, such as the small antennas in typical clients and APs, higher frequencies lose more signal over the same distance. **Free-space path loss** is the loss between two ideal antennas with nothing in the way, so it is a best case:

```formula reference
L_fs = 20 log_10((4πdf) / c)
where
L_fs: the free-space path loss between two isotropic antennas, in decibels (dB)
d: the distance between the antennas, in metres (m)
f: the signal frequency, in hertz (Hz)
c: the speed of light, about 299,792,458 metres per second (m/s)
π: pi, about 3.14159
log_10: the base-10 logarithm
dB: decibel; every 10 dB is a factor of ten in power
In words: free-space loss rises by about 6 dB, a quarter of the received power, every time the distance or the frequency doubles.
```

At 10 m, for example, a 5.5 GHz signal arrives about 7 dB weaker than a 2.4 GHz one, roughly a fifth of the power, before any walls. Wall losses depend on material, construction, angle and frequency, and the free-space model does not predict them. Actual coverage also depends on permitted power, antenna patterns, bandwidth and receiver sensitivity; a frequency label alone does not establish range or throughput. Other things share 2.4 GHz too: Bluetooth, microwave ovens and baby monitors.

The practical consequence: as a client moves away, its signal-to-noise ratio falls, rate adaptation picks slower modulation, and each frame takes longer on air. That is why throughput falls with distance well before the connection drops, and why 5 and 6 GHz cells are usually smaller than 2.4 GHz ones.

## Key takeaways
- Start with a permitted, surveyed channel plan; overlapping energy and coordinated co-channel sharing differ.
- Free-space path loss compares frequencies under fixed gains and distance, not arbitrary indoor coverage.

## Further reading
- [List of WLAN channels — Wikipedia](https://en.wikipedia.org/wiki/List_of_WLAN_channels)
- [Ofcom: 6 GHz spectrum sharing decisions](https://www.ofcom.org.uk/spectrum/innovative-use-of-spectrum/consultation-expanding-access-to-the-6-ghz-band-for-commercial-mobile-and-wi-fi-services)
