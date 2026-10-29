---
id: emb-platform-comparison-score-sensitivity
sourceLesson: emb-platform-comparison
title: "Test the decision against its weights"
level: advanced
minutes: 2
summary: "A weighted total makes priorities explicit but inherits the quality of its inputs."
---

## A score expresses priorities

Apply must-haves as pass/fail before scoring. For each surviving option, give each criterion a score with a sentence of evidence. Weight it according to how much that criterion matters, then add the weighted scores. A spreadsheet can do the arithmetic; the important work is justifying the evidence and priorities.

Suppose placeholder option X has stronger audio and debugging support, while Y has stronger beginner documentation. These are invented scores to illustrate the method, not measurements of any board:

| Weights (audio, debug, docs) | X total | Y total |
|---|---|---|
| 3, 2, 1: audio and debugging first | 23 | 18 |
| 1, 1, 3: documentation first | 17 | 20 |

The placeholder scores out of five are X: audio 4, debugging 4, documentation 3; Y: audio 3, debugging 2, documentation 5.

The same underlying scores can produce opposite winners when priorities change. A total is not a hardware benchmark, and a high score elsewhere cannot rescue a failed must-have.

## Test whether the result is robust

Try a small, defensible change to each weight. If the order reverses, identify the criterion driving the change. Gather evidence that could settle it: for example, try a minimal debugging workflow or measure a prototype voice on available hardware.

Do not adjust weights merely to make your favourite board win. Record the original rationale, the sensitivity result and any experiment. A robust score is still only as reliable as its evidence; missing compatibility or timing measurements remain gaps.

## Key takeaways
- A weighted total makes priorities explicit but inherits the quality of its inputs.
- If defensible weights reverse the result, gather decisive evidence.

## Further reading
- [Daisy Seed hardware page — Electro-Smith](https://docs.daisy.audio/hardware/Seed/)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Teensy 4.1 — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Audio adaptor boards for Teensy — PJRC](https://www.pjrc.com/store/teensy3_audio.html)
- [Teensy Audio Library — PJRC](https://www.pjrc.com/teensy/td_libs_Audio.html)
- [Raspberry Pi 5 product brief — Raspberry Pi](https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf)
- [Raspberry Pi audio boards overview — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/accessories/audio/introduction.adoc)
- [Raspberry Pi audio boards configuration — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/accessories/audio/configuration.adoc)
- [GPIO on Raspberry Pi — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/gpio-on-raspberry-pi.adoc)
- [Raspberry Pi models and their ports (Pi 5 lists no 3.5 mm jack) — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/introduction.adoc)
