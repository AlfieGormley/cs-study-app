---
id: elec-audio-hum-budget
sourceLesson: elec-noise-grounding
title: "Understanding an audio hum budget"
level: advanced
minutes: 2
summary: "Small return-wire voltages can matter after amplification."
---

A small unwanted voltage can matter in audio because later stages amplify it along with the wanted signal. Audibility depends on gain, frequency, masking and the listening system; there is no single voltage below which hum is always harmless.

> [!warning] Keep protective earth intact
> Never remove or bypass a mains safety earth to cure hum. Use documented signal isolation, suitable balanced connections and safe low-voltage diagnosis. This module does not cover mains wiring or modifying mains equipment.

## Follow the unwanted current
In an ordinary unbalanced connection, the cable shield is also the signal return. An unwanted current through its resistance produces a voltage drop. The receiving input measures against that return, so the drop can become part of the audio.

For scale, an illustrative 1 mA RMS hum current through a 0.1 Ω shield produces 100 µV RMS. Compared with a 0.316 V RMS signal, that is about 70 dB lower. These are model assumptions, not studio measurements, and they do not prove whether anyone will hear the hum.

## Compare like with like
The commonly used −10 dBV nominal line reference corresponds to about 0.316 V RMS. It is not every device’s actual output level or maximum safe input. Check the exact equipment manuals.

If both voltages are RMS values measured over the relevant bandwidth, this reference formula converts their ratio to a signal-to-hum figure:

```formula reference
L_SH = 20 log_10(V_sig / V_hum)
where
L_SH: signal-to-hum voltage ratio expressed in decibels (dB)
V_sig: wanted signal RMS voltage, in volts (V)
V_hum: nonzero unwanted hum RMS voltage, in volts, measured over the stated bandwidth
log_10: base-ten logarithm; the power of ten that gives its argument
20: voltage-ratio scale factor for decibels
In words: A larger wanted signal relative to the hum gives a larger signal-to-hum figure. Amplifying both equally leaves that ratio unchanged, though it can make the hum audible.
```

Turning up downstream gain raises both wanted signal and hum already present at that stage. To reduce the hum itself, investigate its current path, the impedance it crosses and how the receiver measures the signal. Do not infer an RMS hum level from an LED pulse’s peak current alone.

## Key takeaways

- Tiny return-wire drops can enter audio and be amplified.
- Noise ratios need consistent measurement conventions and bandwidth.
- A numerical hum budget helps compare designs, but does not establish a universal audibility threshold.

## Further reading

- [RaneNote 110: system interconnection](https://www.ranecommercial.com/legacy/note110.html)
- [Analog Devices MT-031: converter grounding](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf)
