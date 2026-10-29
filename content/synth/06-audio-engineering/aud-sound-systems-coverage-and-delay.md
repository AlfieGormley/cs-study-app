---
id: aud-sound-systems-coverage-and-delay
title: Audience coverage and delay alignment
level: advanced
minutes: 4
summary: Main speakers, subs, fills, delays and monitors serve different coverage needs.
sourceLesson: aud-sound-systems
---

## PA design

A typical live PA has several systems, each with its own job:

- **Main speakers (front of house).** Left/right or mono speakers covering the audience, flown or on stands. Larger venues use **line arrays**: vertical columns of boxes that control vertical coverage and lose level more slowly with distance over part of their range.
- **Subwoofers.** Below about 80–120 Hz. Usually on the ground. Several subs can be arranged (end-fire, cardioid, arc) to steer low frequencies away from the stage.
- **Stage monitor loudspeakers.** What performers hear: **floor wedges** aimed up at each performer, side fills, or **in-ear monitors (IEMs)**. Fed from **pre-fader aux** mixes.
- **Front fills.** Small speakers along the stage lip for the front rows, who are below the main speakers' coverage.
- **Delay speakers.** Further back in large venues, where the main speakers have lost too much level.

### Delay speakers

At a chosen listener position, compare the path from the main speaker with the path from the delay speaker. Sound from the main speakers has further to travel, so without an electronic delay the delay speaker's copy would arrive first and pull the sound image towards it (the precedence effect, from the hearing lessons). The delay to dial in is:

- the **extra travel time** of the main speakers' sound: about 2.9 ms per metre of extra path, so a 40 m longer path is about 117 ms;
- **plus the difference in processing latency** between the two paths (main path minus delay path). If that would make the total negative, change the other path or the design instead.

The alignment holds exactly only where the path difference is the one you designed for. Behind the delay speaker, on the straight line from the main speakers through it, moving further back adds the same distance to both paths, so the difference, and the alignment, stay the same. Off that line, and especially between the stage and the delay speaker, the difference changes: there the delay speaker's sound arrives late and can be heard as an echo. This is why delay speakers are aimed away from the stage and cover only the area behind them.

A designer may choose an additional offset to favour the main speakers as the first arrival, but no universal 10–20 ms setting guarantees fusion or stage localisation. Those depend on signal, relative level, geometry and reflections; measure and listen throughout the overlap region.

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
- Main speakers, subs, fills, delays and monitors serve different coverage needs.
- Align a fill using acoustic-path and processing-latency differences.
- Verify timing, localisation, overlap and exposure throughout the audience area.

## Further reading
- [Setting system level controls — Rane](https://www.ranecommercial.com/legacy/note135.html)
- [Acoustic feedback — Rane](https://www.ranecommercial.com/legacy/note158.html)
- [Keyboard stage connections — Radial](https://www.radialeng.com/blog/how-to-manage-any-keyboard-setup-on-stage)
