---
id: aud-amplifiers-headphones
title: Match a headphone output to its load
level: advanced
minutes: 4
summary: Required voltage and current depend on headphone impedance and sensitivity.
sourceLesson: aud-amplifiers
---

## Headphone drive stages

Headphones need far less power than speakers, but they vary enormously in impedance (roughly 16 Ω to several hundred ohms) and sensitivity:

- **Low-impedance headphones** need current; **high-impedance** ones need voltage. 10 mW is about 0.57 V RMS into 32 Ω but about 1.73 V RMS into 300 Ω: three times the voltage, but far less current.
- A headphone drive stage should have a **low output impedance**, much lower than the headphones'. A high output impedance forms a divider with the headphones' frequency-varying impedance and changes their frequency response.
- Laptop and phone outputs can struggle with some headphones; compare required voltage/current and sensitivity with the source’s rated capabilities. A suitable dedicated amp or interface can help.

The output impedance and the headphones form a **voltage divider**: the amplifier's internal voltage is shared between its own output impedance and the headphones, and only the headphones' share is heard.

```formula reference
V_hp = V_src Z_hp / (Z_out + Z_hp)
where
V_hp: the voltage that actually reaches the headphones, in volts (V)
V_src: the voltage the amp generates internally, before its own output impedance, in volts (V)
Z_hp: the headphones' impedance at a given frequency, in ohms (Ω)
Z_out: the amplifier's output impedance, in ohms (Ω)
Ω: ohms
In words: the bigger the amp's output impedance compared with the headphones', the more voltage is lost, and if the headphone impedance changes with frequency, so does the loss.
```

If the output impedance is tiny compared with the headphones' at every frequency, the headphones' share stays close to the whole voltage and the response stays flat. If it is significant, that share changes wherever the headphone impedance changes. For example, a 10 Ω output delivers about 76 % of its voltage (about −2.4 dB) into 32 Ω, but about 86 % (about −1.3 dB) where the same headphones' impedance rises to 64 Ω.

In this illustrative example, 32 Ω headphones whose impedance rises to 64 Ω at their resonance, driven from a 10 Ω output, get about 1.1 dB more level at the resonance than elsewhere. From a 1 Ω output the difference would be well under 0.3 dB. (This treats the impedances as plain resistances; real ones also have phase.)

> [!warning] Ears first
> Headphone amplifiers can produce hearing-damaging levels very easily (the hearing units). Turn the level down before plugging in or switching sources.

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
