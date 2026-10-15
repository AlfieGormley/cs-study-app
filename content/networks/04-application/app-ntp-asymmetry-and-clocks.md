---
id: app-ntp-asymmetry-and-clocks
title: "NTP path asymmetry, slewing and monotonic time"
level: advanced
minutes: 4
sourceLesson: app-ntp-ssh-grpc
summary: "Unequal one-way delays bias an NTP offset estimate; low delay does not prove symmetry."
---

NTP estimates server time minus client time by averaging the apparent difference in each direction. It estimates network round-trip delay by subtracting server handling time from the complete exchange. Those estimates cannot by themselves identify one-way path asymmetry.

### The symmetry assumption

The formula assumes the outbound and return trips take **equal** time. If they don't, the error in the offset is half the difference:

```formula
ε = (d_out − d_back) / 2
ε = (5 ms − 35 ms) / 2 = −15 ms
|ε| ≤ δ / 2
where
ε: epsilon, the error in the offset estimate caused by unequal paths, in milliseconds (ms)
d_out: the one-way time from client to server; here 5 ms
d_back: the one-way time from server back to client; here 35 ms, for example because of congestion on the return path
δ: delta, the measured round-trip delay, here 40 ms
|ε|: the size of the error, ignoring its sign
≤: is at most
ms: milliseconds, thousandths of a second
In words: if the reply takes 30 ms longer than the request, the offset comes out 15 ms wrong, and the error can never be more than half the round trip.
```

So in this example the offset estimate is biased by **−15 ms**. Those four timestamps alone cannot distinguish this from clock offset. With nonnegative delays and otherwise ideal timestamps, the error magnitude is at most half the measured network round-trip delay. Low-delay samples reduce that bound but do not prove symmetry; multiple sources and filtering can help reject bad measurements.

### Disciplining the clock

Clock-discipline behaviour depends on implementation and configuration. Wall-clock steps can disrupt duration calculations and timestamp ordering:

- **Slewing**: run the clock slightly fast or slow until the offset is gone. The time needed is the offset divided by the slew rate; at an illustrative 500 ppm, correcting 1 second takes 1 ÷ 0.0005 = 2,000 seconds, about 33 minutes (see the formula below). This is not a universal Linux limit: chrony supports higher slew rates on Linux.
- **Stepping the clock**: set the time directly when policy permits. Classic ntpd uses a 128 ms step threshold with state-machine safeguards; stepping is not inherently restricted to boot.

```formula
T = θ / r
T = 1 s / (500 × 10^{−6}) = 2,000 s ≈ 33 min
where
T: how long slewing takes to remove the offset, in seconds (s)
θ: theta, the offset to correct; here 1 second
r: the slew rate as a fraction; 500 parts per million (ppm) is 500 × 10^{−6} = 0.0005, so the clock gains or loses half a millisecond per second
^: "to the power of"; 10^{−6} is one millionth
≈: approximately equal to
s: seconds
min: minutes
In words: running the clock 0.05% fast takes about 33 minutes to catch up one second, which is why big offsets are usually stepped.
```

Programs should measure durations with a **monotonic clock** (`time.monotonic()` in Python), which is never stepped, and use wall-clock time only for timestamps.

**Leap seconds** add a further wrinkle. Google documents a 24-hour **leap smear** centred on a leap second; it changes the clock's rate instead of presenting an abrupt insertion. Its offset from unsmeared UTC reaches half a second. Different smear policies need not agree, so do not mix incompatible sources. CGPM Resolution 4 (2022) calls for increasing the permitted UT1−UTC difference by or before 2035, allowing much longer intervals without leap adjustments; it does not specify an unconditional permanent abolition date.

## Key takeaways
- Unequal one-way delays bias an NTP offset estimate; low delay does not prove symmetry.
- Slew and step policies differ, while duration measurements should use a monotonic clock.

## Further reading
- [RFC 5905](https://www.rfc-editor.org/rfc/rfc5905)
- [chrony configuration](https://chrony-project.org/doc/4.7/chrony.conf.html)
- [Google leap smear](https://developers.google.com/time/smear)
- [CGPM resolution 4](https://www.bipm.org/en/cgpm-2022/resolution-4)
