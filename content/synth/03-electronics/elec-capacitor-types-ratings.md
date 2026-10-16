---
id: elec-capacitor-types-ratings
sourceLesson: elec-components
title: "Capacitor types, component polarity and real capacitance"
level: intermediate
minutes: 2
summary: "Check component polarity and working-voltage limits for the exact part."
---

Check component polarity and working-voltage limits for the exact part.

### Types
| Type | Polarised? | Typical use |
|---|---|---|
| Ceramic (MLCC) | No | Decoupling (100 nF), small values |
| Film | No | Audio signal paths, filters |
| Ordinary aluminium electrolytic | **Yes** | Bulk supply filtering, large µF |
| Tantalum | **Yes** | Compact bulk capacitance |

Things to watch:

- **Component polarity.** Ordinary polarised aluminium electrolytic and tantalum capacitors must have their + lead at the higher voltage. Specially specified non-polarised electrolytic types also exist; use each part only as its manufacturer permits. On aluminium electrolytics a stripe marks the **negative** lead, and the negative lead is usually the shorter one. On tantalum capacitors the marking works the other way: a stripe or bar usually marks the **positive** lead. Check the datasheet. Reverse them and they can overheat, vent or burst; tantalums can fail short and catch fire. Don't use a polarised capacitor where the voltage across it can reverse, such as a plain AC audio signal with no DC bias.
- **Voltage rating.** Every capacitor has a maximum working voltage. Choose one comfortably above the highest voltage it will see. A 6.3 V capacitor on a 5 V rail leaves little margin, so 10 V or 16 V is more comfortable. Margin is a design rule of thumb; check the manufacturer's guidance for the part.
- **Ceramic DC bias.** Many high-value ceramics (X7R, X5R and similar Class 2 dielectrics) lose a significant share of their capacitance when a DC voltage is applied, sometimes well over half near the rated voltage. The effect is documented in manufacturers' DC-bias curves. The "X7R" code itself only describes temperature behaviour (±15% from −55 to +125 °C); it says nothing about voltage. C0G/NP0 (Class 1) ceramics barely change with voltage or temperature, but come in much smaller values than Class 2 types of the same size.
- **Markings.** Small ceramics often use a three-digit code: two digits, then the number of zeros, in picofarads. `104` means 10 followed by four zeros:

```formula
C = (10 × d_1 + d_2) × 10^{d_3} pF
C = 10 × 10^4 pF = 100,000 pF = 100 nF
where
C: the capacitance
d_1: the first digit (1)
d_2: the second digit (0)
d_3: the third digit, the exponent on ten (4)
10^4: ten to the power 4, which is 10,000
pF: picofarads; 1 pF = 10^{-12} farads
nF: nanofarads; 1 nF = 1000 pF
In words: 104 is 10 with four zeros after it, in picofarads: 100,000 pF, which is 100 nF.
```

## Key takeaways

- Check component polarity and working-voltage limits for the exact part.
- Use the DC-bias curve for Class 2 ceramic capacitors.

## Further reading

- [Murata: capacitance under an applied DC voltage](https://www.murata.com/en-global/support/faqs/capacitor/ceramiccapacitor/char/0005)
- [Murata: ceramic types and temperature codes](https://go.murata.com/rs/382-MEZ-125/images/AS_2015-008_Continental-2015-2_Email-Thanks_Leaflet_202.pdf)
- [Analog Devices MT-101: decoupling techniques](https://www.analog.com/media/en/training-seminars/tutorials/MT-101.pdf)
