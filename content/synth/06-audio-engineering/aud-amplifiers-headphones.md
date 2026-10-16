---
id: aud-amplifiers-headphones
title: Match a headphone output to its load
level: advanced
minutes: 4
summary: Required voltage and current depend on headphone impedance and sensitivity.
sourceLesson: aud-amplifiers
---

## headphone drive stages

Headphones need far less power than speakers, but they vary enormously in impedance (roughly 16 Ω to several hundred ohms) and sensitivity:

- **Low-impedance headphones** need current; **high-impedance** ones need voltage. 10 mW is 0.57 V RMS into 32 Ω but 1.73 V RMS into 300 Ω (worked out below).
- A headphone drive stage should have a **low output impedance**, much lower than the headphones'. A high output impedance forms a divider with the headphones' frequency-varying impedance and changes their frequency response.
- Laptop and phone outputs can struggle with some headphones; compare required voltage/current and sensitivity with the source’s rated capabilities. A suitable dedicated amp or interface can help.

The voltage needed for a given power comes from rearranging the power formula:

```formula
V_rms = √(PR)
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
V_hp = V_src Z_hp / (Z_out + Z_hp)
V_hp = V_src × 32 Ω / (10 Ω + 32 Ω)
V_hp ≈ 0.76V_src  (≈ −2.4 dB)
V_hp = V_src × 64 Ω / (10 Ω + 64 Ω)
V_hp ≈ 0.86V_src  (≈ −1.3 dB)
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
> Headphone amps can produce hearing-damaging levels very easily (the hearing units). Turn the level down before plugging in or switching sources.

> [!note] Verification gap
> The earlier historical headphone-output standard recommendation and broad output-impedance range are omitted because their original standard text and representative measurement basis were not reliably verified. Use the actual product specifications.

## Key takeaways
- Required voltage and current depend on headphone impedance and sensitivity.
- Source and load impedances form a voltage divider.
- A varying load can colour frequency response when source impedance is significant.

## Further reading
- [Headphone amplifier load and output impedance — Texas Instruments, TIDUAW1](https://www.ti.com/lit/ug/tiduaw1/tiduaw1.pdf)
- [Amplifier principles and ratings — Crown](https://www.crownaudio.com/en-US/faq_categories/1)
- [Loudspeaker loads and damping — Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
