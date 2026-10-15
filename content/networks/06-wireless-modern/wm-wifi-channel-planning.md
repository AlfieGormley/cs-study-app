---
id: wm-wifi-channel-planning
title: Channels, interference and radio propagation
level: basic
minutes: 5
summary: Start with a permitted, surveyed channel plan; overlapping energy and coordinated co-channel sharing differ.
sourceLesson: wm-wifi
---

This unit focuses on channels, interference and radio propagation. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Channels and interference

**2.4 GHz** has channels only 5 MHz apart, but each transmission is about 20 MHz wide. Neighbouring channels therefore overlap, and **1, 6 and 11** is a conventional conservative 20 MHz plan where those channels are permitted. Available channels, PHY spectral masks and interference determine other viable plans; this is not the only possible set worldwide.

The centre frequency of each 2.4 GHz channel follows a simple rule (channels 1 to 13; Japan's channel 14 is a special case):

```formula
f_c = 2407 MHz + 5 MHz × n
f_1 = 2407 MHz + (5 MHz × 1) = 2412 MHz
f_6 = 2407 MHz + (5 MHz × 6) = 2437 MHz
f_11 = 2407 MHz + (5 MHz × 11)
f_11 = 2462 MHz
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
L_fs = 20 log_10((4πdf) / c)
(4π × 10 m × 2.437 GHz) / c ≈ 1022
L_{2.4} = 20 × log_10(1022) ≈ 60.2 dB
(4π × 10 m × 5.5 GHz) / c ≈ 2305
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

So at 10 m the 5.5 GHz signal arrives about 7 dB weaker, roughly one fifth of the power, than the 2.4 GHz one. Wall losses depend on material, construction, angle and frequency; the free-space equation does not predict them. Actual coverage also depends on permitted power, antenna patterns, wall materials, bandwidth and receiver sensitivity; a frequency label alone does not establish range or throughput. Other things share 2.4 GHz too: Bluetooth, microwave ovens and baby monitors.

## Key takeaways
- Start with a permitted, surveyed channel plan; overlapping energy and coordinated co-channel sharing differ.
- Free-space path loss compares frequencies under fixed gains and distance, not arbitrary indoor coverage.

## Further reading
- [List of WLAN channels — Wikipedia](https://en.wikipedia.org/wiki/List_of_WLAN_channels)
- [Ofcom: 6 GHz spectrum sharing decisions](https://www.ofcom.org.uk/spectrum/innovative-use-of-spectrum/consultation-expanding-access-to-the-6-ghz-band-for-commercial-mobile-and-wi-fi-services)
