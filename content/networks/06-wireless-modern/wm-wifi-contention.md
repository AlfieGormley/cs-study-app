---
id: wm-wifi-contention
title: Wi-Fi contention, backoff and acknowledgments
level: basic
minutes: 5
summary: Count down backoff only while the channel is idle; failure grows the contention window up to its cap.
sourceLesson: wm-wifi
---

This unit focuses on Wi-Fi contention, backoff and acknowledgments. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Sharing the air: CSMA/CA

Classic shared Ethernet used **CSMA/CD**: listen before sending, and if you *detect a collision* while transmitting, stop, jam and back off. Wi-Fi cannot do the "CD" part:

1. Ordinary Wi-Fi radios do not implement Ethernet-style collision detection while sending; their own transmit signal makes simultaneous sensing of weak incoming signals difficult.
2. A collision may happen at the receiver but not be audible at the sender at all (covered in the next unit).

So Wi-Fi tries to **avoid** collisions instead, and uses missing expected acknowledgments as an indication of failure; not every frame is individually acknowledged. The following is a simplified **DCF** contention example for acknowledged unicast using 5 GHz OFDM timings. Modern QoS traffic commonly uses EDCA with access-category parameters; broadcast/multicast and scheduled multi-user exchanges differ:

1. **Carrier sense.** Listen. If the channel is busy, wait until it goes idle.
2. **Wait DIFS.** After the channel goes idle, wait a fixed gap (34 µs on 5 GHz).
3. **Random backoff.** Pick a random whole-number count between zero and the current contention window, inclusive (9 µs slots; the window starts at 15). Count down only while the channel stays idle; freeze the counter if someone else starts sending.
4. **Transmit** when the counter hits zero.
5. **ACK.** The receiver replies after a shorter gap, SIFS (16 µs). The shorter gap gives priority over compliant contenders that sense this exchange; interference and hidden terminals can still corrupt the ACK.
6. **No ACK?** Assume a collision or corruption, grow CW (here 15, 31, 63 ... up to 1023) and try again. After a retry limit, drop the frame.

The contention window roughly doubles after each failure, capped at a maximum:

```formula
CW_new = min(2(CW_old + 1) − 1, CW_max)
CW = 15 → 31 → 63 → 127 … → 1023
T_backoff = k t_slot
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

For example, drawing seven slots on the first attempt gives a 63-microsecond idle countdown. After three failures the count is drawn from zero through 127, giving up to 1.143 milliseconds of counted idle slots. Busy periods and interframe waits add wall-clock time.

The interframe gaps follow the same slot arithmetic:

```formula
DIFS = SIFS + 2t_slot
DIFS = 16 µs + 2 × 9 µs = 34 µs
where
DIFS: the DCF interframe space: the idle gap a station must see before starting contention, in microseconds (µs)
SIFS: the short interframe space: the gap before an ACK or other immediate reply, 16 µs for 5 GHz OFDM
t_slot: the slot time, 9 µs for 5 GHz OFDM
µs: microsecond, one millionth of a second
In words: a station waiting to contend must stay quiet two slots longer than one sending an ACK, so a compliant contender that senses the exchange defers to the immediate reply. Hidden senders and interference can still cause failure.
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

## Key takeaways
- Count down backoff only while the channel is idle; failure grows the contention window up to its cap.
- SIFS gives immediate replies priority over ordinary DCF contention under the stated sensing assumptions.

## Further reading
- [Carrier-sense multiple access with collision avoidance — Wikipedia](https://en.wikipedia.org/wiki/Carrier-sense_multiple_access_with_collision_avoidance)
- [ns-3 Wi-Fi model: DCF, EDCA and protection mechanisms](https://raw.githubusercontent.com/nsnam/ns-3-dev-git/master/src/wifi/doc/source/wifi-design.rst)
