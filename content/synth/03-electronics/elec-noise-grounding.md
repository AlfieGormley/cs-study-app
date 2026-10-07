---
id: elec-noise-grounding
title: Noise and grounding in audio circuits
level: advanced
minutes: 15
summary: Why audio picks up hum and whine, how ground loops form in a studio, shared-impedance coupling and star grounding, keeping digital return currents out of analogue grounds, shielded cable, and why supply noise and decoupling matter.
---

A synth that works can still be unusable if it hums, buzzes or whines. Noise problems come mostly from **how currents return**, not from the parts themselves. This lesson gives you the mental model to diagnose noise in your own studio: a synth board, a Digitakt, an audio interface and a computer running Ableton.

> [!warning] Never touch the safety earth
> Some "fixes" for hum online involve removing or cutting the earth connection of mains equipment ("ground lifting" the plug). **Never do this.** The protective earth is what makes a fault safe. Rane's grounding note says: "Safety regulations require that all original grounding means provided from the factory be left intact for safe operation." Everything in this lesson works at the signal level or uses equipment designed for isolation.

## Why audio is so sensitive

Logic signals have volts of noise margin. Audio has no digital-style logic threshold: added noise can be amplified, but whether it is audible depends on gain, spectrum, masking and the listening system. Consumer line level is −10 dBV (about 0.316 V RMS). A clean system's noise sits tens of decibels below that, so a few hundred microvolts of hum can be clearly audible.

```python
import math

def db(ratio):
    return 20 * math.log10(ratio)

i_loop = 0.001    # 1 mA of 50 Hz current
r_shield = 0.1    # 100 mΩ cable shield
v_hum = i_loop * r_shield

v_sig = 10 ** (-10 / 20)  # -10 dBV line
print(f"hum: {v_hum * 1e6:.0f} uV")
print(f"signal: {v_sig:.3f} V")
print(f"S/hum: {db(v_sig / v_hum):.1f} dB")
```

```
hum: 100 uV
signal: 0.316 V
S/hum: 70.0 dB
```

The 1 mA and 100 mΩ figures are illustrative, not measured; real loop currents and shield resistances vary widely. The mechanism (loop current × shield resistance adds to the signal) is the one Wikipedia's ground-loop article derives. Hum only 70 dB below the signal is easily heard in quiet passages or with gain applied afterwards.

## Ground loops

A **ground loop** forms when two pieces of equipment are connected to each other by more than one ground path. Typically:

1. each one's mains protective earth, through the wall wiring, and
2. the shield or sleeve of the audio cable between them.

```diagram
 Device A ──cable shield── Device B
    │                         │
  earth                     earth
    │                         │
    └────── mains wiring ─────┘
       (loop encloses an area)
```

Stray magnetic fields from mains wiring and transformers induce a current around this loop, and the two earth points may also sit at slightly different potentials. As Rane's note puts it, the hum appears "when this current flows through a unit's audio signal ground". In an **unbalanced** cable the shield *is* the signal return, so the voltage drop along it adds straight to the audio.

The result is hum at the mains frequency (50 Hz in the UK) and its harmonics. A rectified-supply component at 100 Hz is also common.

### Ground loops with USB

Low-voltage gear can form loops too. A common case in a synth studio:

- The synth board is powered over USB from the computer.
- The computer connects to the audio interface over USB.
- The synth's audio output goes to the interface's input.

That's two ground paths between synth and interface: through the audio cable and through USB via the computer. Digital noise on the USB ground (from the computer's processor, display and charger) flows partly through the audio cable's shield. It's often heard as whine or buzzing that changes with computer activity.

### Diagnosing and fixing

Work from least invasive to most:

1. **Diagnose by elimination.** Disconnect cables one at a time and listen. Run the synth from a battery power bank to see whether the USB ground path is the culprit. Note whether the noise is a steady 50/100 Hz hum or a varying digital whine.
2. **Plug all mains equipment into the same outlet or power strip,** so the earth paths are short and close together. This is common studio practice.
3. **Use balanced connections** where both ends support them. Hum that appears equally on both conductors is rejected by a balanced input.
4. **Break the loop with a device made for it:** an audio isolation transformer (DI box or ground-loop isolator) in the audio line, or a USB isolator on the USB connection. Each keeps every device's safety earth intact.
5. **Design it out:** in your own build, give the synth one clear ground reference and avoid creating extra ground paths.

DIN MIDI is designed this way already: the receiving end uses an **opto-isolator**, so a MIDI cable doesn't join the grounds of the two devices. The MIDI module covers the circuit.

## Shared impedance and star grounding

Ground loops are one mechanism. The other, inside your own circuit, is **shared-impedance coupling**. Every ground wire or track has resistance (and inductance). If a noisy current, such as an LED being multiplexed, a processor, or a display, returns through the same piece of ground wire as an audio signal's reference, its I × R voltage appears in the audio.

```diagram
 BAD: daisy-chained ground
 audio ──┬── LEDs ──┬── MCU ──┬── supply −
         └ shared wire carries all returns

 GOOD: star ground
          audio   LEDs    MCU
            │       │      │
            └───────┼──────┘
                    ● star point
                    │
                supply −
```

**Star grounding** (single-point grounding) at an introductory level means:

- Each sub-circuit has its own return wire to one common point.
- High-current and noisy returns don't share wire with sensitive audio returns.
- The star point is usually at the power entry or where the audio reference is defined.

You won't build perfect stars on a breadboard. Apply the principle with intent: give the audio output's ground its own wire back to the board's ground pin, and keep LED and motor returns off it.

## Analogue and digital ground

Boards with audio codecs often talk about **AGND** (analogue ground) and **DGND** (digital ground). At a conceptual level:

- Digital circuits produce large, fast, spiky return currents.
- Analogue audio needs a quiet, stable reference.
- Layout keeps noisy digital return currents away from sensitive analogue references. Often this uses careful placement over a **continuous ground plane**; a split plane or one-point join is not a universal requirement.

Two cautions:

- **Use the specified grounding topology.** AGND and DGND must have the connection required by the manufacturer, often both directly to one low-impedance plane. Splitting that plane or forcing a distant single-point join can worsen high-frequency return paths.
- **Follow the manufacturer.** If your audio board exposes separate analogue and digital ground pins, connect pots, audio jacks and analogue parts as its documentation directs. Codec datasheets specify their own grounding and layout. This is advanced material; for the first build, follow the board's guidance and keep noisy and quiet wiring physically apart.

## Shielded cable and wiring

A **shielded cable** surrounds the signal conductor(s) with a braid or foil connected to ground. The shield intercepts electric-field interference before it reaches the signal.

- **Unbalanced (TS):** one conductor plus shield. The shield is also the signal return, so ground-loop current in it adds to the signal.
- **Balanced (TRS or XLR):** two signal conductors plus shield. The shield carries no signal current, and interference common to both conductors cancels at a balanced input.
- **Twisting** a signal wire with its return reduces magnetic pickup, because each twist reverses the induced voltage.

Inside the build:

- Keep audio wires short and away from digital lines, LED wiring and power.
- Cross noisy wiring at right angles rather than running it alongside audio.
- Run each signal and its own return together.

## Power supply noise and decoupling

A synth's supply often comes from a computer's USB port or a USB charger. Both carry noise: digital load current from the computer, and ripple at the switching frequency of switch-mode chargers and regulators.

How it reaches the audio:

- Op-amps, codecs and regulators reject supply noise only partially. Their **power supply rejection ratio (PSRR)** typically falls as frequency rises, so high-frequency supply noise gets through more easily. Datasheets show this as a "PSRR vs frequency" graph; TI's OPA1612 datasheet has an example (its "CMRR and PSRR vs Frequency" figure).
- Digital chips on the same rail inject current spikes, which lesson 4's decoupling capacitors exist to contain.

Defences, in order of effort:

1. **Decouple every chip** with 100 nF close to its supply pin, plus bulk capacitance where power enters (lesson 4).
2. **Filter the analogue supply** from the digital one with a small resistor or inductor and a capacitor (an RC or LC low-pass, lesson 3).
3. **Use a dedicated low-noise linear regulator** for analogue parts, if the board design calls for it.
4. **Use a better source:** try a different USB supply or a battery bank to see whether the noise follows the supply.

Audio-focused development boards often build these measures in. Read the board's documentation before adding your own. Your main job is not to undo them with poor external wiring.

## A noise-hunting checklist

- Identify the noise: steady 50/100 Hz hum (ground loop or mains field), or whine that tracks computer, LED or processor activity (digital ground or supply noise).
- Remove connections one at a time and note what changes.
- Try battery power for the synth.
- Check that audio grounds return directly to the board's ground, not through LED or digital wiring.
- Confirm decoupling capacitors are present and close to their pins.
- Use balanced or isolated connections between devices where possible.
- Never remove a mains safety earth.

## Key takeaways

- Audio has no noise margin: tens to hundreds of microvolts can be audible.
- A ground loop is two ground paths between devices. Induced current in the shared audio return becomes 50 Hz hum and harmonics.
- USB power plus USB audio plus an audio cable is a common low-voltage ground loop. Battery power is a quick test, and a USB isolator is a fix.
- Never lift a mains earth. Use balanced connections, isolation transformers or USB isolators instead.
- Shared ground impedance couples noisy return currents into audio. Star grounding gives each sub-circuit its own return to one point.
- Keep noisy return currents away from sensitive references; use the board's documented plane or connection topology rather than assuming a one-point join.
- Shields intercept interference. In unbalanced cables they also carry the signal return.
- Supply noise reaches audio through limited PSRR. Decouple, filter and choose a clean supply.

## Further reading

- [Grounding data converters, MT-031 — Analog Devices](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf)

- [RaneNote 110: Sound system interconnection](https://www.ranecommercial.com/legacy/note110.html)
- [Ground loop (electricity) (Wikipedia)](https://en.wikipedia.org/wiki/Ground_loop_(electricity))
- [Mains hum (Wikipedia)](https://en.wikipedia.org/wiki/Mains_hum)
- [Balanced audio (Wikipedia)](https://en.wikipedia.org/wiki/Balanced_audio)
- [Shielded cable (Wikipedia)](https://en.wikipedia.org/wiki/Shielded_cable)
- [Power supply rejection ratio (Wikipedia)](https://en.wikipedia.org/wiki/Power_supply_rejection_ratio)
- [OPA1612 audio op-amp datasheet, PSRR vs frequency (Texas Instruments)](https://www.ti.com/lit/ds/symlink/opa1612.pdf)
- [Decoupling capacitor (Wikipedia)](https://en.wikipedia.org/wiki/Decoupling_capacitor)
- [Ground plane (Wikipedia)](https://en.wikipedia.org/wiki/Ground_plane)
