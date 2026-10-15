---
id: pipe-power-wall-switching-power
sourceLesson: pipe-power-wall
title: Estimate capacitive switching power
level: advanced
minutes: 3
summary: Separate voltage, frequency and activity effects without confusing switching power with total energy.
---

Clock increases and microarchitectural improvements contributed to rapid single-thread performance growth before the mid-2000s. Power and thermal constraints made continuing that trend harder and encouraged multicore designs. Clock rates and single-core performance did not stop improving, and there is no universal 3–4 GHz ceiling.

> [!note] Evidence limits
> Universal cooling wattages, voltage floors, current limits on clock rate and specific cancelled-product explanations are omitted because they need product- and process-specific evidence. The power examples below are models, not operating advice or measured processor specifications.

## Dynamic power

CMOS circuits use energy charging and discharging capacitances. A common approximation for average capacitive switching power is:

```formula
P_dyn = aCV^2f
where
P_dyn: the dynamic (switching) power, in watts (W)
a: the dimensionless activity factor: capacitance-weighted mean charging events per cycle; this single-transition teaching model uses values from 0 to 1 and neglects extra intra-cycle glitches
C: the total capacitance represented by this model, in farads (F); a is its capacitance-weighted charging activity, so aC represents the activity-weighted capacitance
V: the supply voltage, in volts (V); the model assumes a supported operating point, not a universal processor voltage
f: the clock frequency, in hertz (Hz): cycles per second
W: watts, joules of energy per second
F: farads, coulombs of electric charge per volt
Hz: hertz, cycles per second
In words: switching power grows in proportion to how much switches, how much capacitance it charges, the clock rate, and the square of the voltage.
```

At fixed activity and capacitance, power is linear in frequency and quadratic in voltage. Higher frequencies may require higher voltage, but voltage is not universally proportional to clock frequency. A cubic frequency rule follows only if voltage also scales proportionally over the modelled range. Total chip power includes leakage, other switching effects and other components.

### What 15% less frequency buys

Drop voltage and frequency by 15% each, keeping activity and capacitance unchanged. Because the voltage is squared, the power ratio is:

```formula
r = (V_2 / V_1)^2 × (f_2 / f_1)
r = 0.85^2 × 0.85 = 0.85^3 ≈ 0.61
where
r: the new dynamic power divided by the old, with activity and capacitance unchanged
V_1, V_2: the supply voltage before and after, in volts; V_2 = 0.85 × V_1
f_1, f_2: the clock frequency before and after, in hertz; f_2 = 0.85 × f_1
≈: approximately equal to (rounded)
In words: cutting voltage and frequency by 15% each leaves about 61% of the switching power, a saving of roughly 39%.
```

With unchanged activity and capacitance, capacitive switching power falls about 39%. Performance falls 15% only if throughput is proportional to frequency; total energy and total system power need separate accounting.

There is also **static (leakage) power**: current that trickles through transistors even when they are not switching. It depends on voltage, temperature and transistor design, and cannot be inferred from transistor dimensions alone.

## Key takeaways
- Capacitive switching power depends on activity, capacitance, voltage squared and frequency.
- A cubic frequency rule requires an additional proportional voltage change.
- Leakage and execution duration prevent a switching-power ratio from determining total system energy.

## Further reading
- [Texas Instruments: CMOS power consumption](https://www.ti.com/lit/an/scaa035b/scaa035b.pdf)
- [Dennard et al.: constant-field scaling (original 1974 paper)](https://stanford.edu/class/cs114/readings/dennard.pdf)
- [Intel processor technology definitions](https://www.intel.com/content/www/us/en/support/articles/000006513/processors.html)
