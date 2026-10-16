---
id: midi-audio-levels-connection-families
title: Choose the right audio input
level: intermediate
minutes: 3
sourceLesson: midi-audio-levels
summary: Match signal level and load requirements from documentation before connecting outputs to inputs.
---

MIDI tells your synth what to play. This lesson is about the other cable: the **audio** that leaves your synth and goes into the audio interface. Getting it wrong gives you noise, hum, distortion, a quiet signal or, at worst, damaged equipment. Getting it right is mostly a matter of knowing the level conventions and a few circuit principles.

> [!warning] Safety boundaries
> Everything here concerns low-voltage signal connections. Don't open mains-powered gear, and never "fix" hum by removing a mains earth. Before connecting a home-built circuit to the interface, check the interface manual's maximum input level and connect with the gain turned down.

## The level hierarchy

Audio connections come in families with very different voltages and impedances:

| Level | Typical source | Goes into |
|---|---|---|
| Mic | Microphone | Mic preamp |
| Instrument | Guitar pickup | Hi-Z input |
| Line | Synth, mixer, DAC | Line input |
| Headphone | Headphone amp | Headphones |
| Speaker | Power amplifier | Passive speaker |

- **Mic level** is weak and varies widely between microphones (it is sometimes quoted as around −60 dBV). The required preamp gain depends on the microphone, source and distance; this quoted level is an illustration, not a fixed mic-level standard.
- **Passive-pickup output** comes from sources like guitar pickups that can supply very little current. "Hi-Z" instrument inputs present a high input impedance chosen for the pickup; consult the instrument and interface documentation so as not to load them.
- **Line level** is the level synths, mixers and interfaces use between each other. It is where your synth's output belongs.
- **Headphone outputs** are amplifiers designed for a specified range of headphone loads; check the supported impedance and output ratings.
- **Speaker level** outputs from power amplifiers drive passive loudspeakers (usually 4–8 Ω) with much higher voltages and currents.

These are **not interchangeable**. A speaker output into a line input can overload or damage it. A line output into a speaker is nearly a short circuit for the line driver: very weak sound and a possibly damaged output. A headphone output can sometimes feed a line input with a suitable stereo-to-mono breakout and conservative level, but check both manuals: a stereo headphone TRS output is not balanced mono, and its peak voltage can overload an input.

## Key takeaways
- Match signal level and load requirements from documentation before connecting outputs to inputs.

## Further reading
- [Line level — Wikipedia](https://en.wikipedia.org/wiki/Line_level)
- [Nominal level — Wikipedia](https://en.wikipedia.org/wiki/Nominal_level)
- [Impedance bridging — Wikipedia](https://en.wikipedia.org/wiki/Impedance_bridging)
- [Balanced audio — Wikipedia](https://en.wikipedia.org/wiki/Balanced_audio)
- [Capacitive coupling (coupling capacitors and their high-pass effect) — Wikipedia](https://en.wikipedia.org/wiki/Capacitive_coupling)
- [Phantom power — Wikipedia](https://en.wikipedia.org/wiki/Phantom_power)
- [Single-supply biasing (op amps biased at half supply, coupling capacitors) — LibreTexts, from J. Fiore's op amp textbook](https://eng.libretexts.org/Workbench/Introduction_to_Circuit_Analysis/05%3A_Advanced_Topic-_Operational_Amplifiers/5.10%3A_Basic_Op_Amp_Circuits/5.10.03%3A_Single_Supply_Biasing)
- [Single-Supply Op Amp Design Techniques (SLOA030) — Texas Instruments](https://www.ti.com/lit/an/sloa030a/sloa030a.pdf)
- [PCM5102A data sheet (ground-centred 2.1 V RMS output) — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm5102a.pdf)
- [Digitakt II user manual, technical information — Elektron](https://www.elektron.se/wp-content/uploads/2026/10/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf)
- [Passive magnetic pickup sources and Hi-Z inputs — Lehle P-Split II manual](https://manuals.lehle.com/web/1015/Lehle-P-Split-II_Manual_EN.pdf)
