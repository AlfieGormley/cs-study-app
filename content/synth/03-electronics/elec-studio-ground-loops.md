---
id: elec-studio-ground-loops
sourceLesson: elec-noise-grounding
title: "Finding ground loops in a studio"
level: advanced
minutes: 3
summary: "Map every ground path, including USB and audio."
---

Map every ground path, including USB and audio.

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

Stray magnetic fields from mains wiring and transformers induce a current around this loop, and the two earth points may also sit at slightly different potentials. As Rane's note puts it, the hum appears "when this current flows through a unit's audio signal ground". In an **unbalanced connection** the cable's shield *is* the signal return, so the voltage drop along it adds straight to the audio.

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
3. **Use balanced connections** where both ends support them. Hum that appears equally on both conductors is largely rejected by a balanced input, within its common-mode limits.
4. **Break the loop with a device made for it:** an audio isolation transformer (DI box or ground-loop isolator) in the audio line, or a USB isolator on the USB connection. Use only devices documented to suit the signal level, impedances, bandwidth and required isolation. A USB isolator must support the required USB speed and power arrangement; its data and power paths must actually break the unwanted ground route. An active DI box is not automatically transformer-isolated. Keep every protective earth intact.
5. **Design it out:** in your own build, give the synth one clear ground reference and avoid creating extra ground paths.

DIN MIDI is designed this way already: the receiving end uses an **opto-isolator**, so a MIDI cable doesn't join the grounds of the two devices. The MIDI module covers the circuit.

## Key takeaways

- Map every ground path, including USB and audio.
- Use documented signal isolation and preserve every protective earth.

## Further reading

- [RaneNote 110: system interconnection](https://www.ranecommercial.com/legacy/note110.html)
- [Analog Devices MT-031: converter grounding](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf)
