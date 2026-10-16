---
id: aud-sound-systems-coverage-and-delay
title: Audience coverage and delay alignment
level: advanced
minutes: 4
summary: main speakers, subs, fills, delays and monitors serve different coverage needs.
sourceLesson: aud-sound-systems
---

## PA design

A typical live PA has several systems, each with its own job:

- **main speakers (front of house).** Left/right or mono speakers covering the audience, flown or on stands. Larger venues use **line arrays**: vertical columns of boxes that control vertical coverage and lose level more slowly with distance over part of their range.
- **Subwoofers.** Below about 80–120 Hz. Usually on the ground. Several subs can be arranged (end-fire, cardioid, arc) to steer low frequencies away from the stage.
- **Stage monitor loudspeakers.** What performers hear: **floor wedges** aimed up at each performer, side fills, or **in-ear monitors (IEMs)**. Fed from **pre-fader aux** mixes.
- **Front fills.** Small speakers along the stage lip for the front rows, who are below the main speakers' coverage.
- **Delay speakers.** Further back in large venues, where the main speakers have lost too much level.

### Delay speakers, worked

At a chosen listener position, compare the path from the main speaker with the path from the delay speaker. Sound from the main speakers has further to travel, so without an electronic delay the delay speaker's copy would arrive first and pull the sound image towards it. The delay to dial in is the extra travel time, plus any difference in processing latency between the two paths:

```formula
D = d_main − d_delay
t_align = D / c + t_lat
t_align = 40 m / (343 m/s) + 0
t_align ≈ 0.117 s = 117 ms
where
D: the path difference, in metres (m): how much further the listener is from the main speaker than from the delay speaker
d_main: the distance from the main speaker to the chosen listener position, in metres (m)
d_delay: the distance from the delay speaker to the same listener position, in metres (m)
t_align: the electronic delay to apply to the delay speaker so the two arrivals line up, in seconds (s)
c: the speed of sound in air, about 343 metres per second (m/s)
t_lat: main-path processing latency minus delay-speaker-path processing latency, in seconds (s); taken as 0 here. A negative total delay requires changing the other path or the design
m: metres
m/s: metres per second
s: seconds
ms: milliseconds, thousandths of a second
In words: delay the delay speaker by the time sound takes to cover the extra distance from the main speakers, so both arrive together at the listener.
```

If the main speakers path is **40 m longer**, about 117 ms aligns arrivals in this simplified example. It only holds exactly at the chosen position; listeners nearer or further away see a different path difference. A designer may choose an additional offset to favour the main speakers as the first arrival, but no universal 10–20 ms setting guarantees fusion or stage localisation. Those depend on signal, relative level, geometry and reflections; measure and listen throughout the overlap region. Exact universal precedence offsets are absent because reliable evidence for such a guarantee was not established.

## Studio vs live

| | Studio | Live |
|---|---|---|
| Goal | Accurate monitoring | Coverage, level |
| Listeners | One position | Whole audience |
| Speakers | Near-field monitors | PA, subs, wedges |
| Feedback | Rarely an issue | Constant concern |
| Room | Treated (the room-acoustics units) | Take what you get |

In a studio the monitors must tell the truth, so you can make decisions that translate to other systems. In a live system the goal is even, intelligible, sufficiently loud coverage for everyone, with controlled exposure and compliance with applicable venue limits. WHO’s 100 dB LAeq,15 min ceiling is one part of its safe-listening venue standard, not a guarantee that a whole event is safe at that level (the hearing units).

## Key takeaways
- main speakers, subs, fills, delays and monitors serve different coverage needs.
- Align a fill using acoustic-path and processing-latency differences.
- Verify timing, localisation, overlap and exposure throughout the audience area.

## Further reading
- [Setting system level controls — Rane](https://www.ranecommercial.com/legacy/note135.html)
- [Acoustic feedback — Rane](https://www.ranecommercial.com/legacy/note158.html)
- [Keyboard stage connections — Radial](https://www.radialeng.com/blog/how-to-manage-any-keyboard-setup-on-stage)
