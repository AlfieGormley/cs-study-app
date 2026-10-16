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

- Class B (each device conducts exactly half the cycle) has a maximum theoretical efficiency of **78.5%** (see below), but suffers **crossover distortion** where one device hands over to the other.
- **Class AB** adds a small bias current so both devices conduct briefly around the handover, removing most crossover distortion. Efficiency sits just below class B's. It's been the standard design for linear hi-fi and PA amplifiers for decades.

The class B figure comes from an ideal amplifier power stage swinging a full sine wave right up to its supply rails:

```formula
η = P_out / P_in
η_max = π / 4 ≈ 0.785 = 78.5 %
where
η: eta, efficiency: the fraction of the power drawn from the supply that reaches the speaker (no unit, often given as a percentage)
P_out: the audio power delivered to the speaker, in watts (W)
P_in: the power drawn from the power supply, in watts (W)
η_max: the best possible efficiency of an ideal class B stage at full sine-wave output
π: pi, about 3.14159
≈: approximately equal to
In words: even a perfect class B stage turns at least about a fifth of its supply power into heat at full output, and much more at lower levels.
```

### Class D

The output devices act as **switches**, fully on or fully off, switching far above the audio band (often at hundreds of kilohertz). The audio is encoded in the switching pattern (for example pulse-width modulation), and in conventional designs an **output low-pass filter** attenuates the switching carrier. Some low-power filterless designs instead use suitable modulation and the speaker’s electrical/mechanical filtering; external filtering and wiring constraints depend on the device.

- A perfect switch dissipates no power (either no voltage across it or no current through it), so class D is **very efficient**: over 80% is common and over 90% achievable with MOSFETs.
- Small, light, cool-running: the norm in powered speakers, PA amplifiers, car audio and portable devices.
- Trade-offs: the output filter's response can depend on the speaker load, the switching causes EMI that must be contained, and design quality varies. Good modern class D measures extremely well.

Efficiency decides how much heat the amp makes. Everything drawn from the supply that doesn't reach the speaker becomes heat:

```formula
P_in = P_out / η
P_heat = P_in − P_out
P_heat = 100 W / 0.25 − 100 W = 300 W
P_heat = 100 W / 0.90 − 100 W ≈ 11 W
where
P_in: the power drawn from the supply, in watts (W)
P_out: the audio power delivered to the speaker, here 100 W
η: eta, the efficiency as a fraction (0.25 means 25 %)
P_heat: the power wasted as heat in the amplifier power stage, in watts (W)
≈: approximately equal to
W: watts, the unit of power
In words: at 25 % efficiency you burn three watts of amplifier power-stage heat for every watt of electrical load power; at 90 % you burn about one ninth of a watt.
```

The same sum for four efficiencies, as Python:

```python
for name, eff in (("A, typical max", 0.25),
                  ("A, transformer", 0.50),
                  ("B, max", 0.785),
                  ("D, good", 0.90)):
    # Supply input minus electrical output.
    heat = 100 / eff - 100
    print(f"{name:<15} {heat:5.0f} W heat")
```

```
A, typical max    300 W heat
A, transformer    100 W heat
B, max             27 W heat
D, good            11 W heat
```

Illustrative amplifier power-stage heat to deliver 100 W at the assumed efficiencies. The class D value is a practical example; these figures exclude power-supply and other losses. Heat means heatsinks, fans, weight and power bills, which is why class D dominates where size and power matter.

## Key takeaways
- Amplifier class describes output-device conduction.
- Ideal class-A limits depend on topology; class B reaches about 78.5 percent at full sine output.
- Class D reduces amplifier power-stage losses through switching; total system losses still matter.

## Further reading
- [Class-D output filtering — Texas Instruments, SLAA701B](https://www.ti.com/lit/an/sloa119b/sloa119b.pdf)
- [Amplifier principles and ratings — Crown](https://www.crownaudio.com/en-US/faq_categories/1)
- [Loudspeaker loads and damping — Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Class-A power-stage efficiency — ADI university course](https://wiki.analog.com/university/courses/engineering_discovery/lab_10)
- [Class-A resistive and transformer coupling limits — ACS College of Engineering, pages 65–67](https://www.acsce.edu.in/acsce/wp-content/uploads/2020/03/Analog-Circuits-module-3.pdf)
