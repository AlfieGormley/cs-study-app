---
id: elec-capacitor-charge-time
sourceLesson: elec-components
title: "Capacitor charging and RC time"
level: intermediate
minutes: 3
summary: "More capacitance slows voltage change for the same current."
---

A capacitor stores energy in an electric field by separating charge across an insulating dielectric. Its capacitance, measured in farads, tells you how much charge is needed for a given voltage change.

## Voltage changes need current
An ideal capacitor carries current while its voltage changes. With the same finite charging current, a larger capacitor changes voltage more slowly; with the same capacitor, more current changes it faster. An instantaneous voltage jump would require an idealised infinite current.

At steady DC, an ideal capacitor eventually carries no current while a voltage can remain across it. Real capacitors have leakage and other losses. This makes capacitors useful for coupling changing audio while blocking steady DC, and for supplying brief local current pulses.

For a fixed-current estimate:

```formula reference
ΔV / Δt = I / C
where
ΔV: voltage change across the ideal capacitor, in volts (V)
Δt: duration of that change, in seconds (s)
Δ: change in a quantity
I: constant current entering the positive capacitor terminal, in amperes (A)
C: capacitance, in farads (F)
In words: A larger capacitor changes voltage more slowly for the same charging current. Increasing the current speeds the change; this finite-change expression assumes constant current.
```

## A resistor makes charging slow down
When a DC voltage step charges a capacitor through a resistor, current is largest initially. As the capacitor voltage approaches the supply, less voltage remains across the resistor, so current falls. The curve rises quickly at first and then approaches the final voltage gradually; it is not a straight ramp.

The RC time constant is the characteristic time of that process. Increasing resistance or capacitance makes the response slower. In the ideal initially discharged RC circuit, one time constant takes the voltage about 63.2% of the way to its final value. After five it is about 99.3% there, not exactly finished.

```formula reference
τ = RC
where
τ: tau, the RC time constant, in seconds (s)
R: resistance charging the capacitor, in ohms (Ω)
C: capacitance, in farads (F)
In words: Larger resistance or capacitance stretches the charging and discharging response in time. The product gives the time constant for this ideal RC circuit.
```

A 10 kΩ resistor and 100 nF capacitor have a 1 ms time constant. Doubling either part doubles the time taken to reach the same fraction of the final voltage, without changing that final voltage in this unloaded ideal model. Discharging through a resistor has the same slowing behaviour as the voltage approaches zero.

> [!analogy] Real-world analogy: Filling a wide tank
> At the same inflow, water level rises more slowly in a wide tank than a narrow one.
>
> **How it maps:** Current corresponds to flow rate, capacitor voltage to level, and capacitance to the tank’s capacity per change in level.
>
> **Where it stops:** A capacitor separates electric charge and stores field energy. The tank comparison does not supply a capacitor’s polarity, voltage rating or the exponential RC charging law.

## Key takeaways

- Capacitor voltage changes through current; more capacitance slows a given current’s effect.
- RC charging slows because the resistor’s voltage and current fall as the capacitor charges.
- Time constant describes response speed, not a deadline when charging suddenly stops.

## Further reading

- [OpenStax: ideal RC circuits](https://openstax.org/books/university-physics-volume-2/pages/10-5-rc-circuits)
