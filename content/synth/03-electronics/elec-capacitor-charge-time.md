---
id: elec-capacitor-charge-time
sourceLesson: elec-components
title: "Capacitor charging and RC time"
level: intermediate
minutes: 3
summary: "More capacitance slows voltage change for the same current."
---

More capacitance slows voltage change for the same current.

A capacitor stores charge between conductors separated by an insulating dielectric. Capacitance is measured in farads; practical parts span picofarads to thousands of microfarads. The following model assumes ideal capacitance and a fixed charging current where a finite voltage-change per unit time is calculated.

### Behaviour
- An ideal capacitor **blocks steady DC current** once charged; a steady voltage can remain across it. Real capacitors have leakage and other losses.
- It **passes changes**, since current flows while its voltage is changing. This is why it can remove a DC offset from an audio signal or short fast noise to ground.
- Its voltage **can't jump instantly**. It changes at a rate set by the current:

```formula
ΔV / Δt = I / C
ΔV / Δt = 0.001 A / 0.000001 F
ΔV / Δt = 1000 V/s = 1 V/ms
where
ΔV: the change in the capacitor's voltage, in volts (V)
Δt: the time over which that change happens, in seconds (s)
Δ: delta, "the change in"
I: the current flowing into the capacitor, in amperes (A)
C: the capacitance, in farads (F)
A: amperes, the unit of current
F: farads, the unit of capacitance
V/s: volts per second
V/ms: volts per millisecond; 1 ms = 0.001 s
In words: the voltage rises faster with more current and slower with a bigger capacitor. 1 mA into 1 µF raises it by 1 V every millisecond. An instant jump would need infinite current, which is why it can't happen.
```

### The RC time constant
For an initially discharged ideal capacitor charged through a fixed resistor by a DC voltage step, the charging curve is exponential: fast at first, then slower and slower as it nears the supply. The **RC time constant** sets how long that takes:

```formula
τ = RC
τ = 10,000 Ω × 0.0000001 F = 0.001 s
where
τ: tau, the time constant, in seconds (s)
R: the resistance the capacitor charges through, here 10 kΩ = 10,000 ohms (Ω)
C: the capacitance, here 100 nF = 0.0000001 farads (F)
Ω: ohms, the unit of resistance
F: farads, the unit of capacitance
s: seconds; ohms × farads comes out in seconds
In words: a 10 kΩ resistor charging a 100 nF capacitor has a time constant of 1 millisecond. A bigger resistor or a bigger capacitor makes it slower.
```

The time constant is the unit of time for the charging curve:

```formula
V_C(t) = V_final(1 − e^{−t/τ})
V_C(τ) = V_final(1 − e^{−1})
V_C(τ) ≈ V_final × 0.632
where
V_C(t): the capacitor's voltage at time t, in volts (V)
t: the time since charging started, in seconds (s)
V_final: the voltage it is charging towards, in volts
e: Euler's number, about 2.718, the base of natural exponential growth and decay
e^{−t/τ}: e raised to the power minus t ÷ τ; it starts at 1 and falls towards 0
τ: tau, the time constant R × C, in seconds
≈: approximately equal to
In words: after one time constant the capacitor has covered about 63.2% of the way to its final voltage. Each further time constant covers 63.2% of what is left.
```

After five time constants it's within 1% of the final voltage (99.3%). The curve assumes an ideal capacitor and a steady source. When the source is removed and it discharges through a resistor, the remaining capacitor voltage decays exponentially, approaching 0 V.

```python
import math

tau = 10e3 * 100e-9    # 10 kΩ, 100 nF
for n in (1, 2, 3, 5):
    # Charge after n time constants.
    pct = 100 * (1 - math.exp(-n))
    ms = n * tau * 1e3
    t = f"{n} tau = {ms:.1f} ms"
    print(f"{t}: {pct:.1f}%")
```

```
1 tau = 1.0 ms: 63.2%
2 tau = 2.0 ms: 86.5%
3 tau = 3.0 ms: 95.0%
5 tau = 5.0 ms: 99.3%
```

## Key takeaways

- More capacitance slows voltage change for the same current.
- An ideal RC step reaches about 63.2% after one time constant.

## Further reading

- [OpenStax: ideal RC circuits](https://openstax.org/books/university-physics-volume-2/pages/10-5-rc-circuits)
