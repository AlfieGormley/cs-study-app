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
- Power is a *result*. The amp sets the voltage; the speaker's impedance decides the current and so the power.

For a resistive load, Ohm's law and the power formula tell you the current and power from the voltage:

```formula
I_rms = V_rms / R
P = V_rms^2 / R
I_rms = 20 V / 8 Ω = 2.5 A
P = (20 V)^2 / 8 Ω = 400 / 8 = 50 W
where
I_rms: the RMS current through the speaker, in amperes (A)
V_rms: the RMS (root-mean-square, an "effective average") output voltage, in volts (V)
R: the load resistance, in ohms (Ω); a nominal speaker is typically 4 Ω or 8 Ω
P: the average power delivered to the load, in watts (W)
A: amperes (amps), the unit of current
V: volts, the unit of voltage
Ω: ohms, the unit of resistance
W: watts, the unit of power
In words: power rises with the square of voltage, so doubling the voltage gives four times the power, and halving the resistance doubles it.
```

That's exact only for a resistor. A real speaker has complex impedance, so sinusoidal real power also depends on the voltage–current phase difference.

### Voltage gain vs power

Amplifier gain is usually quoted in dB (voltage), or as **input sensitivity**: the input voltage that produces full rated output. To use a dB gain, turn it back into a multiplier:

```formula
G = 10^{G_dB / 20}
G = 10^{26 / 20} ≈ 19.95
V_in = 0.7746 V × 10^{4 / 20} ≈ 1.228 V
V_out = V_in × G
V_out = 1.228 V × 19.95 ≈ 24.5 V
P = (24.5 V)^2 / 8 Ω ≈ 75 W
V_sens = √(P_max × R) / G
V_sens = √(100 W × 8 Ω) / 19.95 ≈ 1.42 V
where
G: the voltage gain as a plain multiplier (no unit)
G_dB: the voltage gain in decibels (dB), here 26 dB
V_in: the RMS input voltage, in volts (V); +4 dBu (professional line level) is 0.7746 V × 10^(4/20) ≈ 1.228 V
V_out: the RMS output voltage, in volts (V)
P: the average power into the load, in watts (W)
R: the load resistance, 8 ohms (Ω)
V_sens: the input sensitivity: the input voltage that gives the rated maximum power, in volts (V)
P_max: the rated maximum power, here 100 W
√: square root
≈: approximately equal to
V: volts
W: watts
Ω: ohms
dB: decibel; dividing by 20 converts a voltage decibel figure back to a ratio
In words: 26 dB is a voltage gain of about 20, so a +4 dBu line signal comes out at about 24.5 V, which is 75 W into 8 Ω; you'd need about 1.42 V in to reach 100 W.
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

- Class B (each device conducts exactly half the cycle) has a maximum theoretical efficiency of **78.5%** (see below), but suffers **crossover distortion** where one device hands over to the other.
- **Class AB** adds a small bias current so both devices conduct briefly around the handover, removing most crossover distortion. Efficiency sits just below class B's. It's been the standard design for linear hi-fi and PA amps for decades.

The class B figure comes from an ideal output stage swinging a full sine wave right up to its supply rails:

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
P_heat: the power wasted as heat in the output stage, in watts (W)
≈: approximately equal to
W: watts, the unit of power
In words: at 25 % efficiency you burn three watts of heat for every watt of sound power; at 90 % you burn about one ninth of a watt.
```

The same sum for four efficiencies, as Python:

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

Where the factor of two for peak power comes from: a sine wave's instantaneous power swings between zero and a peak, and spends as long below the halfway line as above it.

```formula
p = V_pk^2 × sin^2(2 × π × f × t) / R
p_peak = V_pk^2 / R
P_avg = V_pk^2 / (2 × R) = V_rms^2 / R
V_rms = V_pk / √2
where
p: the instantaneous power at time t, in watts (W)
V_pk: the sine wave's peak voltage, in volts (V)
sin: the sine function; sin^2 (sine squared) swings between 0 and 1 and averages exactly 0.5
f: the frequency of the sine, in hertz (Hz)
t: time, in seconds (s)
π: pi, about 3.14159
R: the load resistance, in ohms (Ω)
p_peak: the highest instantaneous power, in watts (W)
P_avg: the average (continuous) power, in watts (W)
V_rms: the RMS voltage, the peak divided by √2 (about 0.707 of the peak)
√: square root
In words: for a sine into a resistor, the average power is half the peak instantaneous power, and it equals the RMS voltage squared over the resistance.
```

Example: a sine of 40 V peak into 8 Ω peaks at 1600 ÷ 8 = 200 W but averages 100 W, so "200 W peak" and "100 W continuous" can describe the same amp. This only holds for a steady sine into a resistive load.

A complete specification looks like: *"100 W continuous into 8 Ω, 20 Hz–20 kHz, at 0.1% THD"*. Missing conditions usually hide something, such as a rating taken at 10% distortion or at 1 kHz only.

## Load impedance and matching amp to speaker

A solid-state amp is a voltage source, so **lower impedance draws more current and more power**:

```formula
V_rms = √(P × R)
V_rms = √(100 W × 8 Ω) ≈ 28.3 V
I_rms = 28.3 V / 8 Ω ≈ 3.5 A
P = (28.3 V)^2 / 4 Ω ≈ 200 W
I_rms = 28.3 V / 4 Ω ≈ 7.1 A
where
V_rms: the RMS output voltage, in volts (V)
P: the average power into the load, in watts (W)
R: the load resistance, in ohms (Ω)
I_rms: the RMS current, in amperes (A)
√: square root
≈: approximately equal to
V: volts
W: watts
Ω: ohms
A: amperes
In words: the voltage that gives 100 W into 8 Ω would push twice the current, and so twice the power, into 4 Ω.
```

That's why amps quote power at several loads ("100 W into 8 Ω, 160 W into 4 Ω"). In practice power doesn't quite double into half the impedance, because the supply sags and the output devices have current limits.

Matching rules of thumb:

- **Check the minimum load.** If an amp is rated for 4 Ω minimum, don't connect two 4 Ω speakers in parallel (2 Ω). Speakers' actual impedance dips below nominal (lesson 4), so nominal 4 Ω loads are already demanding.
- **Parallel speakers halve impedance** (two 8 Ω = 4 Ω); series doubles it.
- **Power headroom.** An amp with a continuous rating somewhat *above* the speaker's continuous rating, used with care, is often safer than an underpowered amp driven into clipping. Many manufacturers give a recommended amplifier power range; follow it.
- **Bridged (BTL) mode** drives one speaker from two channels in opposite polarity, doubling the voltage swing: in theory four times the power into the same load, but each channel sees half the load impedance, so bridging into 4 Ω asks each side to drive 2 Ω. Check the manual's bridged minimum load.

The parallel and bridged rules come from these relations (for resistive loads):

```formula
R_par = (R_1 × R_2) / (R_1 + R_2)
R_par = (8 Ω × 8 Ω) / (8 Ω + 8 Ω) = 4 Ω
P_bridge = (2 × V)^2 / R = 4 × V^2 / R
R_ch = R / 2
where
R_par: the combined resistance of two loads in parallel, in ohms (Ω)
R_1: the first speaker's impedance, in ohms (Ω)
R_2: the second speaker's impedance, in ohms (Ω)
P_bridge: the power into the speaker in bridged mode, in watts (W)
V: the RMS voltage one channel can swing on its own, in volts (V)
R: the bridged speaker's impedance, in ohms (Ω)
R_ch: the load each channel effectively sees in bridged mode, in ohms (Ω)
Ω: ohms
In words: two equal speakers in parallel give half the impedance; bridging doubles the voltage, so in theory four times the power, but each channel then works as if it were driving half the speaker's impedance.
```

> [!tip] Valve amps are different
> Valve amps with output transformers *do* need the right load: running them with no speaker connected can damage the output transformer or valves. Always connect a speaker (or a proper load) before powering a valve guitar or hi-fi amp.

## Damping factor

**Damping factor** is the ratio of the speaker's nominal impedance to the amp's **output impedance**:

```formula
DF = Z_load / Z_out
DF = 8 Ω / 0.01 Ω = 800
where
DF: damping factor, a plain ratio (no unit); bigger means the amp holds the driver more firmly
Z_load: the speaker's nominal impedance, in ohms (Ω)
Z_out: the amplifier's output impedance, in ohms (Ω); typically a few hundredths of an ohm for a solid-state amp
Ω: ohms
In words: damping factor says how many times smaller the amp's own internal impedance is than the speaker's.
```

So an amp with 0.01 Ω output impedance into 8 Ω has a damping factor of 800. A low output impedance lets the amp's back-EMF path control the driver's motion near resonance (lesson 4: the driver is also a generator). Above a modest value (tens) the audible benefit is small, because the **speaker cable** and the driver's own voice-coil resistance dominate. The cable's resistance adds to the amp's output impedance:

```formula
R_c = ρ × L_w / A_w
R_c = (1.68 × 10^{-8} Ω·m × 20 m)
      / (1.5 × 10^{-6} m^2)
R_c ≈ 0.224 Ω
DF_spk = Z_load / (Z_out + R_c)
DF_spk = 8 Ω / (0.01 Ω + 0.224 Ω) ≈ 34
where
R_c: the resistance of the speaker cable (both conductors), in ohms (Ω)
ρ: rho, the resistivity of the conductor material, in ohm-metres (Ω·m); copper is about 1.68 × 10^−8 Ω·m
L_w: the total length of conductor the current flows through (out and back), in metres (m): 20 m for a 10 m cable
A_w: the cross-sectional area of each conductor, in square metres (m^2); 1.5 mm² is 1.5 × 10^−6 m^2
DF_spk: the damping factor seen at the speaker, including the cable (no unit)
Z_load: the speaker's nominal impedance, 8 ohms (Ω)
Z_out: the amplifier's output impedance, 0.01 Ω
m: metres
Ω: ohms, the unit of resistance
≈: approximately equal to
In words: a long, thin cable adds far more resistance than a good amp's output stage, so it sets the real damping factor.
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

- **More average power.** A sine wave clipped hard towards a square wave carries up to **twice** the average power of the clean sine with the same peak voltage (worked out below).
- **High-frequency harmonics.** A square wave contains odd harmonics at 1/3, 1/5, 1/7... of the fundamental's amplitude (about −9.5, −14 and −16.9 dB, worked out below). Clip a loud bass or midrange note and those harmonics land in the tweeter's band. The crossover passes them straight to a driver that normally receives only a small fraction of the total power, and its small voice coil overheats.

A square wave sits at its peak voltage all the time, while a sine only touches its peak briefly:

```formula
P_sine = V_pk^2 / (2 × R)
P_square = V_pk^2 / R = 2 × P_sine
L_n = 20 × log_10(1 / n)
L_3 = 20 × log_10(1/3) ≈ −9.5 dB
L_5 = 20 × log_10(1/5) ≈ −14 dB
L_7 = 20 × log_10(1/7) ≈ −16.9 dB
where
P_sine: the average power of a clean sine wave, in watts (W)
P_square: the average power of a square wave with the same peak voltage, in watts (W)
V_pk: the peak voltage, in volts (V)
R: the load resistance, in ohms (Ω)
L_n: the level of the nth harmonic relative to the square wave's fundamental, in decibels (dB)
n: the harmonic number (3, 5, 7 ...): the multiple of the fundamental frequency; a square wave has only odd ones
L_3: the 3rd harmonic's level
L_5: the 5th harmonic's level
L_7: the 7th harmonic's level
log_10: the base-10 logarithm
≈: approximately equal to
dB: decibel, the unit of level ratio
In words: hard clipping can double the average power at the same peak voltage, and pushes strong harmonics at three, five and seven times the note's frequency into the tweeter's range.
```

For example, a 1.5 kHz note clipped to a square wave puts its 3rd harmonic at 4.5 kHz, its 5th at 7.5 kHz and its 7th at 10.5 kHz: all above a typical 2–3 kHz crossover.

So a small amp driven hard into clipping can destroy a tweeter that a larger amp, playing the same music cleanly, wouldn't hurt. Watch for clip indicators, leave headroom, and use limiters in PA systems.

## Headphone amplifiers

Headphones need far less power than speakers, but they vary enormously in impedance (roughly 16 Ω to several hundred ohms) and sensitivity:

- **Low-impedance headphones** need current; **high-impedance** ones need voltage. 10 mW is 0.57 V RMS into 32 Ω but 1.73 V RMS into 300 Ω (worked out below).
- A headphone amp should have a **low output impedance**, much lower than the headphones'. A high output impedance forms a divider with the headphones' frequency-varying impedance and changes their frequency response.
- Laptop and phone outputs can struggle with some headphones; compare required voltage/current and sensitivity with the source’s rated capabilities. A suitable dedicated amp or interface can help.

The voltage needed for a given power comes from rearranging the power formula:

```formula
V_rms = √(P × R)
V_rms = √(0.01 W × 32 Ω) ≈ 0.57 V
V_rms = √(0.01 W × 300 Ω) ≈ 1.73 V
where
V_rms: the RMS voltage the amp must supply, in volts (V)
P: the power wanted in the headphones, here 10 milliwatts (mW) = 0.01 watts (W)
R: the headphones' impedance, treated as a resistance, in ohms (Ω)
√: square root
≈: approximately equal to
V: volts
W: watts
Ω: ohms
In words: the same power needs about three times the voltage into 300 Ω headphones as into 32 Ω ones, but far less current.
```

The output impedance and the headphones form a voltage divider:

```formula
V_hp = V_src × Z_hp / (Z_out + Z_hp)
V_hp = V_src × 32 Ω / (10 Ω + 32 Ω)
V_hp ≈ 0.76 × V_src  (≈ −2.4 dB)
V_hp = V_src × 64 Ω / (10 Ω + 64 Ω)
V_hp ≈ 0.86 × V_src  (≈ −1.3 dB)
where
V_hp: the voltage that actually reaches the headphones, in volts (V)
V_src: the voltage the amp generates internally, before its own output impedance, in volts (V)
Z_hp: the headphones' impedance at a given frequency, in ohms (Ω)
Z_out: the amplifier's output impedance, in ohms (Ω)
≈: approximately equal to
dB: decibel, the unit of level ratio
Ω: ohms
In words: the bigger the amp's output impedance compared with the headphones', the more voltage is lost, and if the headphone impedance changes with frequency, so does the loss.
```

In this illustrative example, 32 Ω headphones whose impedance rises to 64 Ω at their resonance, driven from a 10 Ω output, get about 1.1 dB more level at the resonance than elsewhere. From a 1 Ω output the difference would be well under 0.3 dB. (This treats the impedances as plain resistances; real ones also have phase.)

> [!warning] Ears first
> Headphone amps can produce hearing-damaging levels very easily (lesson 2). Turn the level down before plugging in or switching sources.

> [!note] Verification gap
> The earlier historical headphone-output standard recommendation and broad output-impedance range are omitted because their original standard text and representative measurement basis were not reliably verified. Use the actual product specifications.

## Key takeaways
- A power amp is a low-output-impedance voltage amplifier; power is voltage squared divided by resistance, so the load decides the current and power.
- Class A avoids output-device crossover distortion but has topology-dependent efficiency (25% or 50% in the ideal examples); class B reaches 78.5% theoretically, and AB is the classic compromise; class D switches and commonly exceeds 80–90%.
- Use continuous (average) power at stated load, bandwidth and distortion; peak power for a sine is twice average; an unexplained PMPO figure cannot establish continuous output.
- Lower load impedance draws more current: respect the minimum load, and remember parallel speakers halve impedance.
- Damping factor is speaker impedance divided by amplifier output impedance, but cable resistance usually dominates in practice.
- Clipping raises average power and adds high harmonics, which can overheat tweeters; headphone amps need low output impedance.

## Further reading
- [Power amplifier classes — Wikipedia](https://en.wikipedia.org/wiki/Power_amplifier_classes)
- [Audio power (continuous power, PMPO) — Wikipedia](https://en.wikipedia.org/wiki/Audio_power)
- [Damping factor — Wikipedia](https://en.wikipedia.org/wiki/Damping_factor)
- [Clipping (audio) — Wikipedia](https://en.wikipedia.org/wiki/Clipping_(audio))
- [Headphone amplifier — Wikipedia](https://en.wikipedia.org/wiki/Headphone_amplifier)
- [Loudspeaker parameters (damping factor and cable) — Purdue University](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Electrical resistivity of copper — Wikipedia](https://en.wikipedia.org/wiki/Electrical_resistivity_and_conductivity)
