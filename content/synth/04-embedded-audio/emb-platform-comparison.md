---
id: emb-platform-comparison
title: Comparing synth platforms
level: advanced
minutes: 16
summary: A method for evaluating a Daisy Seed, a Teensy 4.x with its audio adaptor and a Raspberry Pi with an audio HAT against the project's own criteria, using only official documentation, with model, revision and date recorded. A comparison approach, not a recommendation.
---

The diy-synth project deliberately leaves the board open. This lesson does not choose one. It gives you a repeatable method for comparing candidates, demonstrates it with facts taken only from the manufacturers' current documentation, and shows where the evidence runs out.

> [!warning] Re-verify before buying
> Every product fact below was checked on **2026-10-04** against the named official source and model or revision. Boards change revision, codecs get substituted (the Daisy Seed has had three), and products move between manufacturers. Treat this lesson as a snapshot. Re-check each fact against the current official page before you spend money, and record your own check date.

## Step 1: write the criteria before looking at boards

Looking at spec sheets first makes the biggest numbers feel important. Start from the project instead. The project brief and the hardware-options checklist give these criteria:

**Must-haves** (pass/fail):

- Audio output suitable for an audio interface's line input.
- A control connection an external device (the Digitakt) can drive.
- Enough inputs for the planned buttons and knobs.
- A C++ toolchain that works on the development computer.
- A documented way to flash, and to recover a broken board.
- Low-voltage power only.

**Weighted criteria** (scored):

- Beginner documentation and working audio examples.
- Debugging workflow and extra equipment needed.
- CPU, RAM and flash headroom for the intended synth.
- Total prototype cost: board plus audio board, MIDI circuit, power, cables, tools.
- Soldering and construction effort.
- Availability, revision stability, maintenance.
- Fit with the learning goals (C++, DSP, embedded).

Decide the weights *before* scoring, and write down why.

## Step 2: define exact configurations

"Teensy" is not a configuration. Compare complete, buildable systems:

| Label | Configuration |
|---|---|
| A | Daisy Seed, Rev 7 |
| B | Teensy 4.1 + audio adaptor Rev D2 |
| C | Raspberry Pi 5 + Raspberry Pi DAC+ |

Each still needs a DIN MIDI interface circuit (or another agreed control link), power, cables, and possibly a debug probe. List those per configuration; they are part of the cost and the build effort. (Pi alternatives include the DAC Pro or the Codec Zero, which differ in outputs and inputs.)

## Step 3: gather evidence from official sources only

Below is what the official sources state, checked 2026-10-04.

### A: Daisy Seed (Rev 7)

Sources: Electro-Smith Daisy Seed page and datasheet v1.2.0 (18 March 2026); libDaisy documentation.

- Arm Cortex-M7 at 480 MHz; 64 MB SDRAM; 8 MB flash (external QSPI; internal flash is 128 KB).
- 96 kHz / 24-bit stereo audio in and out (PCM3060 codec on Rev 7); line-level output, 0 dBFS at 1 V RMS, 100 Ω output impedance.
- 31 GPIO, 12 × 16-bit ADC inputs, 2 × 12-bit DAC outputs; SPI, UART, I2S, I2C.
- Micro USB port, plus USB pins for OTG host and device.
- Power: VIN 5–17 V. Most GPIO 5 V tolerant; five listed pins are 3.3 V only.
- Flashing: DFU via BOOT + RESET, or a web programmer; debugging with an ST-Link V3 Mini (recommended in the getting-started guide).
- Software: libDaisy and DaisySP in C++; the datasheet also lists Arduino and Max/MSP Gen~. Default audio block 48 samples at 48 kHz.

### B: Teensy 4.1 + audio adaptor Rev D2

Sources: PJRC Teensy 4.1 page; PJRC audio adaptor page; Teensy Audio Library source.

- Arm Cortex-M7 at 600 MHz; 1,024 KB RAM (512 KB tightly coupled); 7,936 KB flash; pads for extra PSRAM or flash chips.
- 55 I/O pins (42 breadboard-accessible); 18 analogue inputs (10-bit default, "only up to 10 bits are normally usable due to noise"); 8 serial, 3 SPI, 3 I2C, 2 I2S/TDM ports.
- Pins are 3.3 V and not 5 V tolerant; recommended maximum output current 4 mA.
- USB device port (with class-compliant USB MIDI and USB audio options) and a separate USB host port.
- Audio adaptor: SGTL5000 codec, 16-bit 44.1 kHz; headphone and line out; line in or mic in; controlled over I2C.
- Audio Library default: 128-sample blocks at 44.1 kHz, 16-bit integer processing.
- Flashing: Teensy Loader via the Arduino IDE with the Teensy boards add-on (Teensyduino), PlatformIO or Makefiles; recovery via the Program button. PJRC does not document a probe-based debugging header.
- Revision notes: PJRC's page lists component changes for boards made after 2022 (for example, the bootloader chip U2 became a GD32E230F8 from June 2022), so record when your board was made.
- PJRC's pages note that SparkFun now manufactures Teensy products.

### C: Raspberry Pi 5 + DAC+

Sources: Raspberry Pi 5 product brief; Raspberry Pi audio boards documentation.

- Quad-core Arm Cortex-A76 at 2.4 GHz; 1–16 GB RAM options; 4 USB ports; 40-pin GPIO header; 5 V / 5 A USB-C power.
- No analogue audio output: the product brief lists none, and Raspberry Pi's model list shows a 3.5 mm audio/AV jack for earlier models but not for Pi 5. A HAT or USB interface is needed.
- DAC+: TI PCM5122, 24-bit 192 kHz, line out 0–2 V RMS on phono sockets, headphone amplifier; output only (the Codec Zero adds inputs).
- HATs are auto-detected from an on-board EEPROM, or configured with a device-tree overlay; audio runs through Linux.
- GPIO pins are 3.3 V digital I/O (Raspberry Pi's GPIO documentation describes them only as high/low inputs and outputs, with no ADC), so knobs need an external ADC chip.
- Production stated until at least January 2036 (product brief).

## Step 4: tabulate, and mark gaps honestly

| Criterion | A | B | C |
|---|---|---|---|
| Audio out | Line, 1 V RMS | Line + phones | 0–2 V RMS line |
| Audio in | Yes | Yes | No (DAC+) |
| Knob inputs | 12 ADC | 18 ADC | External ADC |
| Debug probe | ST-Link (SWD) | Not documented | Linux tools |
| Boot | Firmware | Firmware | Linux OS |
| Block default | 48 @ 48k | 128 @ 44.1k | Configurable |

Then list what the official sources **do not** tell you, and how you will find out:

- **Real CPU headroom for your synth.** Clock speeds are not workloads. Estimate from an offline prototype, then measure on the board (lesson 6).
- **Boot time** of the Linux configuration. Measure it.
- **Noise and output quality** in your studio. Listen and record.
- **Cost.** Prices change; record them on the day you buy, including shipping, headers, cables, a MIDI circuit and any probe.
- **Compatibility with your other equipment.** Check the Digitakt and audio interface manuals for ports and levels. A USB connector alone proves nothing: two USB *devices* cannot talk to each other directly; one side must be a host.

## Step 5: score, then test the scoring

Apply must-haves as pass/fail first. Then score the survivors on each weighted criterion, with a sentence of evidence per score. Then check whether the result depends on your weights.

```python
# Placeholder scores (1-5), NOT real data.
scores = {
    "X": {"audio": 4, "debug": 4,
          "docs": 3},
    "Y": {"audio": 3, "debug": 2,
          "docs": 5},
}

def rank(weights):
    total = {
        name: sum(weights[c] * s[c]
                  for c in weights)
        for name, s in scores.items()
    }
    return sorted(total.items(),
                  key=lambda kv: -kv[1])

print(rank({"audio": 3, "debug": 2,
            "docs": 1}))
print(rank({"audio": 1, "debug": 1,
            "docs": 3}))
```

```
[('X', 23), ('Y', 18)]
[('Y', 20), ('X', 17)]
```

Same scores, different weights, opposite winner. That is the point of the exercise: a weighted matrix makes your priorities explicit. If a small, defensible change of weights flips the result, the options are close, and the deciding factor should be a test, not arithmetic.

## Step 6: run the smallest decisive experiment

Before committing, try the cheapest experiment that could change your mind:

- Run your oscillator and filter code offline on the computer and count operations per sample, to estimate CPU need.
- If one board is already available, do the roadmap's stage-6 exercises: flash and recover, read a knob and button, pass audio, measure load.
- Prototype the MIDI input circuit on a breadboard from the specification, at low voltage.

## Step 7: record the decision

Write a decision record (the project has `docs/decisions/` for this) containing:

1. The criteria and weights, with reasons.
2. The exact configurations, revisions and sources, with check dates.
3. The evidence table, including gaps and how they were closed.
4. The decision, the runner-up, and what would make you revisit it.
5. A parts list with compatibility checks, produced before purchase.

## Common mistakes

- **Comparing headline numbers.** 600 MHz versus 480 MHz says little about whether your synth fits; memory placement, library efficiency and your own code matter more.
- **Forgetting the rest of the system.** The board is a fraction of the build: MIDI circuit, power, connectors and enclosure all count.
- **Trusting a forum post or an old video.** Use the official page for the exact revision, then verify on the bench.
- **Choosing for the final instrument only.** The project also values learning. A platform that hides the codec teaches less about integration but gets you to sound sooner. Decide which you want for version 1.

> [!note] Content absent pending reliable verification
> A project-specific wiring diagram, compatible bill of materials, measured voice count and end-to-end latency are not supplied here: the project has not selected its board, controls or exact interface, and no hardware bench measurements are available. Generic examples cannot reliably establish those facts. Confirm the configuration and measure it before treating any example as a build specification.

## Key takeaways
- Write criteria and weights from the project before reading spec sheets; separate must-haves from scored criteria.
- Compare exact configurations (board, revision, audio board, MIDI circuit, power, tools), not product families.
- Use only official sources, record model, revision, URL and date, and re-verify before buying.
- Mark gaps explicitly; close the important ones with measurements, not assumptions.
- Test the sensitivity of a weighted score; if small weight changes flip the result, run an experiment.

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
