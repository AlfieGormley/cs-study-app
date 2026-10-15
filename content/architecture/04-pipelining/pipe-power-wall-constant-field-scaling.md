---
id: pipe-power-wall-constant-field-scaling
sourceLesson: pipe-power-wall
title: Understand ideal Dennard scaling
level: advanced
minutes: 3
summary: Combine constant-field scaling factors and identify why its assumptions matter.
---

The previous unit modelled capacitive switching power using activity, capacitance, voltage squared and clock frequency. Dennard scaling combines assumptions about all of these as transistor dimensions shrink. Its factors below are ideal scaling relationships, not a guarantee about a current process node.

## Dennard scaling and its end

In 1974 Robert Dennard and colleagues at IBM observed how MOSFETs scale. In the ideal constant-field model, shrink dimensions and voltage by the same factor, 0.7 in the example. In the table and following card, k denotes that dimensionless factor, strictly between zero and one:

| Quantity | Scales by |
|---|---|
| Capacitance per transistor | k |
| Voltage | k |
| Frequency | 1 / k |
| Power per transistor | k² |
| Transistors per area | 1 / k² |
| Power per area | 1 (constant) |

Multiply the scale factors from the table to see why power density stays constant:

```formula
s_P = s_C s_V^2 s_f
s_P = k × k^2 × (1 / k) = k^2
s_D = s_P s_N = k^2 × (1 / k^2) = 1
where
k: the scaling factor per process generation, below 1; about 0.7 in the classic model
s_P: the factor by which power per transistor changes
s_C, s_V, s_f: the factors by which capacitance per transistor, supply voltage and clock frequency change: k, k and 1 / k
s_N: the factor by which transistors per unit area change, 1 / k^2
s_D: the factor by which power per unit area (power density) changes
In words: each transistor uses k^2 of its old power, but k^2 as much area holds it, so power per square millimetre stays the same.
```

With a scaling factor of 0.7, power per transistor falls to 0.49 of its old value while about 2.04 times as many transistors fit in each square millimetre. So **power density stays constant**: each generation gives more transistors, each faster, at the same watts per square millimetre. Together with Moore's law, this is what drove decades of rising clock speeds.

Maintaining performance while reducing supply voltage puts pressure on threshold voltage and leakage. Real devices did not continue the ideal scaling relationships indefinitely. Once voltage and other properties no longer scale together, constant power density no longer follows. Power delivery and heat removal then constrain feasible operating points: the **power wall** is an engineering constraint, not a universal frequency or wattage limit.

## Key takeaways
- Ideal dimension and voltage scaling can keep power density constant at fixed activity.
- Power per transistor and power per area are different quantities.
- The power wall is an operating constraint, not a universal frequency ceiling.

## Further reading
- [Dennard et al.: constant-field scaling (original 1974 paper)](https://stanford.edu/class/cs114/readings/dennard.pdf)
- [Esmaeilzadeh et al.: dark silicon (original 2011 paper)](https://www.cs.cmu.edu/~18742/papers/Esmaeilzadeh2011.pdf)
- [Texas Instruments: CMOS power consumption](https://www.ti.com/lit/an/scaa035b/scaa035b.pdf)
