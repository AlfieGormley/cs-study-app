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

The offset calculation assumes the outbound and return trips take **equal** time. If they don't, the estimate is biased by half the difference between them. Suppose the request takes 5 ms but the reply takes 35 ms, for example because of congestion on the return path. The round trip is 40 ms, and the offset comes out 15 ms too low: the client appears 15 ms further ahead of the server than it really is.

```formula essential
ε = (d_out − d_back) / 2
|ε| ≤ δ / 2
where
ε: epsilon, the error in the offset estimate caused by unequal paths, in milliseconds (ms)
d_out: the one-way time from client to server, in ms
d_back: the one-way time from server back to client, in ms
δ: delta, the measured round-trip network delay, in ms
|ε|: the size of the error, ignoring its sign
≤: is at most
ms: milliseconds, thousandths of a second
In words: unequal paths shift the offset by half their difference, and that shift can never be bigger than half the round trip.
```

The four timestamps alone cannot tell this bias apart from a real clock offset. The bound assumes nonnegative delays and otherwise ideal timestamps. Low-delay samples reduce the bound but do not prove symmetry; multiple sources and filtering can help reject bad measurements.

### Disciplining the clock

Clock-discipline behaviour depends on implementation and configuration. Wall-clock steps can disrupt duration calculations and timestamp ordering:

- **Slewing**: run the clock slightly fast or slow until the offset is gone. The time needed is the offset divided by the slew rate: at an illustrative 500 ppm (half a millisecond per second), correcting a 1-second offset takes about 33 minutes. This is not a universal Linux limit: chrony supports higher slew rates on Linux.
- **Stepping the clock**: set the time directly when policy permits. Classic ntpd uses a 128 ms step threshold with state-machine safeguards; stepping is not inherently restricted to boot. Large offsets are usually stepped because slewing them would take too long.

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
