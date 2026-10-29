---
id: aud-amplifiers-classes
title: Amplifier classes and heat
level: advanced
minutes: 5
summary: Amplifier class describes output-device conduction.
sourceLesson: aud-amplifiers
---

## Amplifier classes

The **amplifier class** describes how the output transistors (or valves) conduct over the signal cycle. It's a broad guide to efficiency and linearity.

### Class A

The output devices conduct over the **whole** cycle, biased at a high standing current even with no signal.

- Very linear: no switching between devices, so no crossover distortion.
- **Inefficient**: the ideal sine-wave amplifier power-stage efficiency depends on topology: 25% for a simple resistively loaded stage, and up to 50% in suitable inductively coupled or push-pull output-stage designs. Real designs at typical listening levels are far lower. Most of the power drawn from the mains becomes heat, all the time.

### Class B and AB

A **push-pull pair**: one device handles the positive half of the waveform, the other the negative.

- Class B (each device conducts exactly half the cycle) has a maximum theoretical efficiency of **78.5%**, but suffers **crossover distortion** where one device hands over to the other.
- **Class AB** adds a small bias current so both devices conduct briefly around the handover, removing most crossover distortion. Efficiency sits just below class B's. It's been the standard design for linear hi-fi and PA amplifiers for decades.

That 78.5 % (a quarter of pi) is the best an ideal class B stage can do while swinging a full sine wave right up to its supply rails. At lower levels, where music spends most of its time, it is much lower, so even a perfect linear amplifier turns a large share of its supply power into heat.

### Class D

The output devices act as **switches**, fully on or fully off, switching far above the audio band (often at hundreds of kilohertz). The audio is encoded in the switching pattern (for example pulse-width modulation), and in conventional designs an **output low-pass filter** attenuates the switching carrier. Some low-power filterless designs instead use suitable modulation and the speaker’s electrical/mechanical filtering; external filtering and wiring constraints depend on the device.

- A perfect switch dissipates no power (either no voltage across it or no current through it), so class D is **very efficient**: over 80% is common and over 90% achievable with MOSFETs.
- Small, light, cool-running: the norm in powered speakers, PA amplifiers, car audio and portable devices.
- Trade-offs: the output filter's response can depend on the speaker load, the switching causes EMI that must be contained, and design quality varies. Good modern class D measures extremely well.

> [!analogy] Real-world analogy: flicking a light switch fast
> Imagine controlling a lamp's brightness by flicking its switch on and off very quickly: on for most of each moment for bright, off for most of it for dim. Your eye averages the flicker. The switch itself never gets hot, because it is either fully closed (no voltage across it) or fully open (no current through it).
>
> **How it maps:** The class D output devices are the switch, the on-time pattern is the pulse-width modulation carrying the audio, and the averaging eye is the output low-pass filter (or the speaker itself in some filterless designs) removing the switching carrier.
>
> **Where it stops:** A class D amplifier switches hundreds of thousands of times a second, and real switches take a little time to change state, losing some power each time. The fast switching also radiates interference (EMI) that must be contained, which a light switch does not.

Efficiency decides how much heat the amp makes, because everything drawn from the supply that doesn't reach the speaker becomes heat. Illustrative amplifier power-stage heat while delivering 100 W:

| Power stage | Efficiency | Heat for 100 W out |
|---|---|---|
| Class A, simple resistive load | 25 % | about 300 W |
| Class A, transformer coupled | 50 % | about 100 W |
| Ideal class B at full output | 78.5 % | about 27 W |
| Good class D | 90 % | about 11 W |

The class D value is a practical example; these figures exclude power-supply and other losses. Heat means heatsinks, fans, weight and power bills, which is why class D dominates where size and power matter.

## Key takeaways
- Amplifier class describes output-device conduction.
- Ideal class-A limits depend on topology; class B reaches about 78.5 percent at full sine output.
- Class D reduces amplifier power-stage losses through switching; total system losses still matter.

## Further reading
- [Class-D LC filter design — Texas Instruments, SLOA119B](https://www.ti.com/lit/an/sloa119b/sloa119b.pdf)
- [Amplifier principles and ratings — Crown](https://www.crownaudio.com/en-US/faq_categories/1)
- [Loudspeaker loads and damping — Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Class-A power-stage efficiency — ADI university course](https://wiki.analog.com/university/courses/engineering_discovery/lab_10)
- [Class-A resistive and transformer coupling limits — ACS College of Engineering, pages 65–67](https://www.acsce.edu.in/acsce/wp-content/uploads/2020/03/Analog-Circuits-module-3.pdf)
