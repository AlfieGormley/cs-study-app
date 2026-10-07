---
id: aud-amplifiers
title: Power amplifiers
level: advanced
minutes: 18
summary: What a power amplifier does, voltage gain versus power, classes A, AB and D with their efficiency and trade-offs, honest power ratings (and why PMPO is meaningless), load impedance and matching an amp to a speaker, damping factor, clipping and tweeter damage, and headphone amplifiers. Conceptual only, with no opening of mains equipment.
---

Your synth's line output can swing a volt or two into 10 kΩ or more (module 5). A loudspeaker needs tens of volts into a few ohms: amps of current and tens or hundreds of watts. A **power amplifier** bridges that gap.

> [!warning] Safety: conceptual lesson only
> Power amplifiers contain **mains wiring** and, inside, **high-voltage supply rails and large capacitors** that can stay charged after unplugging. Valve (tube) amps run at hundreds of volts. Speaker terminals on a large amp can carry voltages that are dangerous to touch at full power. This lesson is about understanding and choosing amplifiers. **Don't open, modify or build mains-powered amplifiers.** Connect speakers with the amp switched off and the volume down, and leave repairs to qualified technicians.

## What a power amp does

A power amp is a **voltage amplifier with a very low output impedance** that can deliver large currents:

- It multiplies the input voltage by a fixed **voltage gain**.
- It holds that output voltage steady whatever the speaker's impedance does (within its limits), by supplying whatever current the load demands.
- Power is a *result*: for a resistive load, average P = Vrms² / R. A real speaker has complex impedance, so sinusoidal real power also depends on the voltage–current phase difference. The amp sets the voltage; the speaker's impedance decides the current and so the power.

### Voltage gain vs power

Amplifier gain is usually quoted in dB (voltage), or as **input sensitivity**: the input voltage that produces full rated output.

```python
import math

gain_db = 26
gain = 10 ** (gain_db / 20)        # x20
v_in = 0.7746 * 10 ** (4 / 20)     # +4 dBu
v_out = v_in * gain
print(f"gain x{gain:.1f}")
print(f"out {v_out:.1f} V rms,"
      f" {v_out**2 / 8:.0f} W into 8 ohm")

# input needed for 100 W into 8 ohm:
print(round(math.sqrt(100 * 8) / gain, 2))
```

```
gain x20.0
out 24.5 V rms, 75 W into 8 ohm
1.42
```

So an amp with 26 dB gain fed a +4 dBu signal gives about 24.5 V RMS: 75 W into 8 Ω. Gain and maximum output power are separate specifications. Higher power may require greater voltage swing, greater current capacity or both; different models may also have different gain. (26 dB is used here as an illustration: real amps range widely, and many quote sensitivity instead. Read the manual.)

## Amplifier classes

The **class** describes how the output transistors (or valves) conduct over the signal cycle. It's a broad guide to efficiency and linearity.

### Class A

The output devices conduct over the **whole** cycle, biased at a high standing current even with no signal.

- Very linear: no switching between devices, so no crossover distortion.
- **Inefficient**: the ideal sine-wave output-stage efficiency depends on topology: 25% for a simple resistively loaded stage, and up to 50% in suitable inductively coupled or push-pull designs. Real designs at typical listening levels are far lower. Most of the power drawn from the mains becomes heat, all the time.

### Class B and AB

A **push-pull** pair: one device handles the positive half of the waveform, the other the negative.

- Class B (each device conducts exactly half the cycle) has a maximum theoretical efficiency of **π/4 ≈ 78.5%**, but suffers **crossover distortion** where one device hands over to the other.
- **Class AB** adds a small bias current so both devices conduct briefly around the handover, removing most crossover distortion. Efficiency sits just below class B's. It's been the standard design for linear hi-fi and PA amps for decades.

### Class D

The output devices act as **switches**, fully on or fully off, switching far above the audio band (often at hundreds of kilohertz). The audio is encoded in the switching pattern (for example pulse-width modulation), and in conventional designs an **output low-pass filter** attenuates the switching carrier. Some low-power filterless designs instead use suitable modulation and the speaker’s electrical/mechanical filtering; external filtering and wiring constraints depend on the device.

- A perfect switch dissipates no power (either no voltage across it or no current through it), so class D is **very efficient**: over 80% is common and over 90% achievable with MOSFETs.
- Small, light, cool-running: the norm in powered speakers, PA amplifiers, car audio and portable devices.
- Trade-offs: the output filter's response can depend on the speaker load, the switching causes EMI that must be contained, and design quality varies. Good modern class D measures extremely well.

```python
for name, eff in (("A, typical max", 0.25),
                  ("A, transformer", 0.50),
                  ("B, max", 0.785),
                  ("D, good", 0.90)):
    heat = 100 / eff - 100
    print(f"{name:<15} {heat:5.0f} W heat")
```

```
A, typical max    300 W heat
A, transformer    100 W heat
B, max             27 W heat
D, good            11 W heat
```

Illustrative output-stage heat to deliver 100 W at the assumed efficiencies. The class D value is a practical example; these figures exclude power-supply and other losses. Heat means heatsinks, fans, weight and power bills, which is why class D dominates where size and power matter.

## Power ratings

- **Continuous (average) power**, often called **"RMS power"**, is the meaningful figure: the average power the amp can deliver continuously into a stated load, over a stated bandwidth, at a stated distortion. "RMS power" is a loose name: it's the average power calculated from RMS voltage and current, not the RMS of the power waveform.
- **Peak power.** For a sine wave, peak instantaneous power is **twice** the average. A "200 W peak" amp may be a 100 W continuous amp.
- **PMPO** ("peak music power output") has no reliable conversion to continuous power without a defined test method and conditions. Treat an unexplained PMPO number as unsuitable for comparison.

A complete specification looks like: *"100 W continuous into 8 Ω, 20 Hz–20 kHz, at 0.1% THD"*. Missing conditions usually hide something, such as a rating taken at 10% distortion or at 1 kHz only.

## Load impedance and matching amp to speaker

A solid-state amp is a voltage source, so **lower impedance draws more current and more power**:

```
100 W into 8 ohm = 28.3 V rms, 3.5 A rms
same 28.3 V into 4 ohm = 200 W, 7.1 A rms
```

That's why amps quote power at several loads ("100 W into 8 Ω, 160 W into 4 Ω"). In practice power doesn't quite double into half the impedance, because the supply sags and the output devices have current limits.

Matching rules of thumb:

- **Check the minimum load.** If an amp is rated for 4 Ω minimum, don't connect two 4 Ω speakers in parallel (2 Ω). Speakers' actual impedance dips below nominal (lesson 4), so nominal 4 Ω loads are already demanding.
- **Parallel speakers halve impedance** (two 8 Ω = 4 Ω); series doubles it.
- **Power headroom.** An amp with a continuous rating somewhat *above* the speaker's continuous rating, used with care, is often safer than an underpowered amp driven into clipping. Many manufacturers give a recommended amplifier power range; follow it.
- **Bridged (BTL) mode** drives one speaker from two channels in opposite polarity, doubling the voltage swing: in theory four times the power into the same load, but each channel sees half the load impedance, so bridging into 4 Ω asks each side to drive 2 Ω. Check the manual's bridged minimum load.

> [!tip] Valve amps are different
> Valve amps with output transformers *do* need the right load: running them with no speaker connected can damage the output transformer or valves. Always connect a speaker (or a proper load) before powering a valve guitar or hi-fi amp.

## Damping factor

**Damping factor** is the ratio of the speaker's nominal impedance to the amp's **output impedance**:

```
DF = Z_load / Z_out
```

An amp with 0.01 Ω output impedance into 8 Ω has DF = 800. A low output impedance lets the amp's back-EMF path control the driver's motion near resonance (lesson 4: the driver is also a generator). Above a modest value (tens) the audible benefit is small, because the **speaker cable** and the driver's own voice-coil resistance dominate:

```python
rho = 1.68e-8          # copper, ohm*m
r_cable = rho * 20 / 1.5e-6  # 10 m pair
z_out = 0.01
print(f"cable {r_cable:.3f} ohm")
print(f"DF at amp   {8 / z_out:.0f}")
print(f"DF at speaker "
      f"{8 / (z_out + r_cable):.0f}")
```

```
cable 0.224 ohm
DF at amp   800
DF at speaker 34
```

Ten metres of 1.5 mm² cable (20 m of conductor) turns DF 800 into about 34. Use thicker cable for long runs, and treat very high DF claims as marketing.

## Clipping and why it can kill tweeters

An amplifier can't output more voltage than its supply rails allow. Ask for more and the output **clips**: the waveform's peaks are flattened.

```diagram
  clean:      /\      /\
             /  \    /  \
            /    \  /    \
  clipped:   ____      ____
            /    \    /    \
           /      \__/      \
```

Why that's dangerous for **tweeters**:

- **More average power.** A sine wave clipped hard towards a square wave carries up to **twice** the average power of the clean sine with the same peak voltage (a square wave of peak V gives V²/R; a sine gives V²/2R).
- **High-frequency harmonics.** A square wave contains odd harmonics at 1/3, 1/5, 1/7... of the fundamental's amplitude (−9.5, −14, −16.9 dB). Clip a loud bass or midrange note and those harmonics land in the tweeter's band. The crossover passes them straight to a driver that normally receives only a small fraction of the total power, and its small voice coil overheats.

So a small amp driven hard into clipping can destroy a tweeter that a larger amp, playing the same music cleanly, wouldn't hurt. Watch for clip indicators, leave headroom, and use limiters in PA systems.

## Headphone amplifiers

Headphones need far less power than speakers, but they vary enormously in impedance (roughly 16 Ω to several hundred ohms) and sensitivity:

- **Low-impedance headphones** need current; **high-impedance** ones need voltage. 10 mW is 0.57 V RMS into 32 Ω but 1.73 V RMS into 300 Ω.
- A headphone amp should have a **low output impedance**, much lower than the headphones'. A high output impedance forms a divider with the headphones' frequency-varying impedance and changes their frequency response.
- Laptop and phone outputs can struggle with some headphones; compare required voltage/current and sensitivity with the source’s rated capabilities. A suitable dedicated amp or interface can help.

> [!warning] Ears first
> Headphone amps can produce hearing-damaging levels very easily (lesson 2). Turn the level down before plugging in or switching sources.

> [!note] Verification gap
> The earlier historical headphone-output standard recommendation and broad output-impedance range are omitted because their original standard text and representative measurement basis were not reliably verified. Use the actual product specifications.

## Key takeaways
- A power amp is a low-output-impedance voltage amplifier; P = V²/R, so the load decides the current and power.
- Class A avoids output-device crossover distortion but has topology-dependent efficiency (25% or 50% in the ideal examples); class B reaches 78.5% theoretically, and AB is the classic compromise; class D switches and commonly exceeds 80–90%.
- Use continuous (average) power at stated load, bandwidth and distortion; peak power for a sine is twice average; an unexplained PMPO figure cannot establish continuous output.
- Lower load impedance draws more current: respect the minimum load, and remember parallel speakers halve impedance.
- Damping factor = Z_load / Z_out, but cable resistance usually dominates in practice.
- Clipping raises average power and adds high harmonics, which can overheat tweeters; headphone amps need low output impedance.

## Further reading
- [Power amplifier classes — Wikipedia](https://en.wikipedia.org/wiki/Power_amplifier_classes)
- [Audio power (continuous power, PMPO) — Wikipedia](https://en.wikipedia.org/wiki/Audio_power)
- [Damping factor — Wikipedia](https://en.wikipedia.org/wiki/Damping_factor)
- [Clipping (audio) — Wikipedia](https://en.wikipedia.org/wiki/Clipping_(audio))
- [Headphone amplifier — Wikipedia](https://en.wikipedia.org/wiki/Headphone_amplifier)
- [Loudspeaker parameters (damping factor and cable) — Purdue University](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Electrical resistivity of copper — Wikipedia](https://en.wikipedia.org/wiki/Electrical_resistivity_and_conductivity)
