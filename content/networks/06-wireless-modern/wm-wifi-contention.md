---
id: wm-wifi-contention
title: Wi-Fi contention, backoff and acknowledgments
level: basic
minutes: 4
summary: Count down backoff only while the channel is idle; failure grows the contention window up to its cap.
sourceLesson: wm-wifi
---

Wi-Fi stations on one channel share the air with no referee deciding who speaks next in the basic access mode. They take turns by listening, waiting a random time and treating a missing acknowledgment as failure. This explains why a busy channel gets slower and less predictable as more devices compete.

## Sharing the air: CSMA/CA

Classic shared Ethernet used **CSMA/CD**: listen before sending, and if you *detect a collision* while transmitting, stop, jam and back off. Wi-Fi cannot do the "CD" part:

1. Ordinary Wi-Fi radios do not implement Ethernet-style collision detection while sending; their own transmit signal makes simultaneous sensing of weak incoming signals difficult.
2. A collision may happen at the receiver but not be audible at the sender at all (covered in the next lesson).

So Wi-Fi tries to **avoid** collisions instead, and uses missing expected acknowledgments as an indication of failure; not every frame is individually acknowledged. The following is a simplified **DCF** contention example for acknowledged unicast using 5 GHz OFDM timings. Modern QoS traffic commonly uses EDCA with access-category parameters; broadcast/multicast and scheduled multi-user exchanges differ:

1. **Carrier sense.** Listen. If the channel is busy, wait until it goes idle.
2. **Wait DIFS.** After the channel goes idle, wait a fixed gap (34 µs on 5 GHz).
3. **Random backoff.** Pick a random whole-number count between zero and the current contention window, inclusive (9 µs slots; the window starts at 15). Count down only while the channel stays idle; freeze the counter if someone else starts sending.
4. **Transmit** when the counter hits zero.
5. **ACK.** The receiver replies after a shorter gap, SIFS (16 µs). The shorter gap gives priority over compliant contenders that sense this exchange; interference and hidden terminals can still corrupt the ACK.
6. **No ACK?** Assume a collision or corruption, grow the contention window (here 15, 31, 63 ... up to 1023) and try again. After a retry limit, drop the frame.

```
busy |DIFS| backoff |  DATA  |SIFS|ACK|
-----+----+---------+--------+----+---+
      34us  k x 9us           16us
```

In the timeline, k is the random number of slots the station drew.

DIFS is SIFS plus two slots (16 + 2 × 9 = 34 µs). That difference is the whole point: a receiver about to send an ACK only has to wait 16 µs, so it starts before any compliant contender that is waiting for 34 µs of silence.

## Why the window doubles

The contention window roughly doubles after each failure, up to a cap:

```formula reference
CW_new = min(2(CW_old + 1) − 1, CW_max)
where
CW_new: the contention window for the next attempt, in slots
CW_old: the contention window before the failed attempt, in slots; 15 for a first attempt in this example
CW_max: the cap on the contention window, 1023 slots here
min: the minimum function: whichever of its values is smaller
In words: every failed attempt roughly doubles the range of random waits a station chooses from, until the range reaches its cap.
```

If two stations both wait for a busy channel to end and then send immediately, they collide. The random countdown spreads them out. When failures keep happening, the channel is probably crowded, so each failing station widens its range and backs off harder. After three failures in this example, the station draws from 0 to 127 slots, up to about 1.1 ms of counted idle time, before busy periods and interframe gaps are added.

The consequences for performance follow directly:

- **More stations, more waiting.** Each extra contender adds collisions and frozen countdowns, so per-station throughput falls and delay becomes more variable.
- **Retries cost airtime.** A failed transmission still occupied the air, and the retry waits longer.
- **Latency spikes.** A frame that fails several times can wait milliseconds before it is finally sent or dropped.

> [!analogy] Real-world analogy: A group conversation with no chairperson
> In a group with no chair, people wait for a pause, then hesitate for a moment before speaking. If two start at once, both stop, and next time each waits a little longer before trying again.
>
> **How it maps:** Waiting for a pause is carrier sense and DIFS; the brief random hesitation is the backoff count; both stopping and waiting longer next time is the contention window doubling after a missing ACK. The person who was asked a question answers straight away, which is the short SIFS gap before the ACK.
>
> **Where it stops:** People in a room notice when they talk over each other. A Wi-Fi sender usually cannot: it only learns of failure when the expected ACK does not arrive, and some stations cannot hear each other at all.

There is also **virtual carrier sense**: eligible frames carry Duration/ID information that can reserve remaining exchange time. Stations update their **NAV** (network allocation vector) according to protocol rules. Some fields are zero or have other meanings; physical carrier sensing still applies.

## Key takeaways
- Count down backoff only while the channel is idle; failure grows the contention window up to its cap.
- SIFS gives immediate replies priority over ordinary DCF contention under the stated sensing assumptions.
- More contenders mean more collisions, longer backoffs and more variable delay.

## Further reading
- [Carrier-sense multiple access with collision avoidance — Wikipedia](https://en.wikipedia.org/wiki/Carrier-sense_multiple_access_with_collision_avoidance)
- [ns-3 Wi-Fi model: DCF, EDCA and protection mechanisms](https://raw.githubusercontent.com/nsnam/ns-3-dev-git/master/src/wifi/doc/source/wifi-design.rst)
