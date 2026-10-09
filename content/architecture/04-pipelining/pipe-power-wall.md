---
id: pipe-power-wall
title: The power wall and multicore
level: advanced
minutes: 13
summary: Why power constraints slowed clock scaling, the physics of dynamic power and Dennard scaling, and how the industry turned to multicore, frequency scaling, heterogeneous cores and specialisation.
---

Clock increases and microarchitectural improvements contributed to rapid single-thread performance growth before the mid-2000s. Power and thermal constraints made continuing that trend harder and encouraged multicore designs. Clock rates and single-core performance did not stop improving, and there is no universal 3–4 GHz ceiling.

> [!note] Evidence limits
> Universal cooling wattages, voltage floors, current limits on clock rate and specific cancelled-product explanations are omitted because they need product- and process-specific evidence. The power examples below are models, not operating advice or measured processor specifications.

## Dynamic power

CMOS circuits use energy charging and discharging capacitances. A common approximation for average capacitive switching power is:

```formula
P_dyn = a × C × V^2 × f
where
P_dyn: the dynamic (switching) power, in watts (W)
a: the activity factor: average charging activity per clock cycle, consistently defined for the capacitances included in C; not simply an unweighted fraction of transistors; between 0 and 1
C: the switched capacitance represented by the activity model, in farads (F); equivalently, sum each node’s activity × capacitance
V: the supply voltage, in volts (V); of the order of 1 V in a modern processor core, and changed at run time as the operating point changes
f: the clock frequency, in hertz (Hz): cycles per second
W: watts, joules of energy per second
In words: switching power grows in proportion to how much switches, how much capacitance it charges, the clock rate, and the square of the voltage.
```

At fixed activity and capacitance, power is linear in frequency and quadratic in voltage. Higher frequencies may require higher voltage, but **V is not universally proportional to f**. A cubic frequency rule follows only if voltage also scales proportionally over the modelled range. Total chip power includes leakage, other switching effects and other components.

### What 15% less frequency buys

Drop V and f by 15% each, keeping activity and capacitance unchanged. Because the voltage is squared, the power ratio is:

```formula
r = (V_2 / V_1)^2 × (f_2 / f_1)
r = 0.85^2 × 0.85 = 0.85^3 ≈ 0.61
where
r: the new dynamic power divided by the old, with activity and capacitance unchanged
V_1, V_2: the supply voltage before and after; V_2 = 0.85 × V_1
f_1, f_2: the clock frequency before and after; f_2 = 0.85 × f_1
≈: approximately equal to (rounded)
In words: cutting voltage and frequency by 15% each leaves about 61% of the switching power, a saving of roughly 39%.
```

With unchanged activity and capacitance, capacitive switching power falls about 39%. Performance falls 15% only if throughput is proportional to frequency; total energy and total system power need separate accounting.

There is also **static (leakage) power**: current that trickles through transistors even when they are not switching. It depends on voltage, temperature and transistor design, and cannot be inferred from transistor dimensions alone.

## Dennard scaling and its end

In 1974 Robert Dennard and colleagues at IBM observed how MOSFETs scale. In the ideal constant-field model, shrink dimensions by a factor k (say 0.7 per process generation) and also scale voltage by k:

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
s_P = s_C × s_V^2 × s_f
s_P = k × k^2 × (1 / k) = k^2
s_D = s_P × s_N = k^2 × (1 / k^2) = 1
where
k: the scaling factor per process generation, below 1; about 0.7 in the classic model
s_P: the factor by which power per transistor changes
s_C, s_V, s_f: the factors by which capacitance per transistor, supply voltage and clock frequency change: k, k and 1 / k
s_N: the factor by which transistors per unit area change, 1 / k^2
s_D: the factor by which power per unit area (power density) changes
In words: each transistor uses k^2 of its old power, but k^2 as much area holds it, so power per square millimetre stays the same.
```

With k = 0.7, power per transistor falls to 0.49 of its old value while about 2.04 times as many transistors fit in each square millimetre. So **power density stays constant**: each generation gives more transistors, each faster, at the same watts per square millimetre. Together with Moore's law, this is what drove decades of rising clock speeds.

Maintaining performance while reducing supply voltage puts pressure on threshold voltage and leakage. Real devices did not continue the ideal scaling relationships indefinitely. Once voltage and other properties no longer scale together, constant power density no longer follows. Power delivery and heat removal then constrain feasible operating points: the **power wall** is an engineering constraint, not a universal frequency or wattage limit.

## Why more cores instead?

For a hypothetical CPU-bound workload, hold per-core activity, capacitance, IPC and work per instruction fixed; ignore shared-system power, communication and leakage. Take one core at frequency f and voltage V, using switching power P. Now build two cores, each at 0.85 f and 0.85 V:

```formula
R_2 = 2 × 0.85 = 1.70
P_2 = 2 × 0.85^2 × 0.85 ≈ 2 × 0.614
P_2 ≈ 1.23
P_fast = 1.7^2 × 1.7 = 1.7^3 ≈ 4.9
where
R_2: the throughput of the two slower cores, relative to the single core; each runs at 0.85 of the frequency
P_2: the total switching power of the two slower cores, relative to the single core; each uses 0.85^2 (voltage, squared) × 0.85 (frequency) of its power
P_fast: the switching power of one core clocked 1.7 times faster, if it also needed 1.7 times the voltage, relative to the original core
≈: approximately equal to (rounded)
In words: two slowed-down cores give 1.7 times the throughput for about 1.23 times the power, while getting 1.7 times from one core by raising frequency and voltage together would cost about 4.9 times the power.
```

If the work splits across both cores perfectly, you get 1.7× the throughput for 1.23× the power. If a single-core 1.7× clock increase also required 1.7× voltage, this model would predict about 4.9× switching power. That hypothetical scaling is not a claim that such an operating point is feasible or universally impossible to cool.

Multicore can improve aggregate throughput per watt when work can run concurrently, including independent jobs. It does not automatically accelerate one serial task; algorithmic and single-core improvements still matter.

## Amdahl's law

The catch is that most programs are not perfectly parallel. Split a fixed-size job's single-core run time into a serial part, which still runs on one core, and a parallel part, which divides evenly over the cores. Assume unchanged serial time and no communication, scheduling, contention or other parallel overhead:

```formula
S(n) = 1 / ((1 − p) + p / n)
S_max = 1 / (1 − p)   as n → ∞
where
S(n): the speedup on n cores: the original run time divided by the new run time
n: the number of equally fast cores, at least 1
p: the parallel fraction: the share of the original single-core run time that scales perfectly over the cores, between 0 and 1
1 − p: the serial fraction, which no number of cores shortens
S_max: the ceiling the speedup approaches as cores are added, for p below 1
→: approaches, tends towards
∞: infinity: the number of cores growing without limit
In words: the new run time is the serial part plus the parallel part divided among the cores, and however many cores you add, the serial part is still left.
```

For example, with 90% parallel code on 8 cores:

```formula
S(8) = 1 / ((1 − 0.9) + 0.9 / 8)
S(8) = 1 / (0.1 + 0.1125) ≈ 4.71
S_max = 1 / (1 − 0.9) = 10
where
S(8): the speedup on 8 cores
S_max: the ceiling on speedup however many cores are added
≈: approximately equal to (rounded)
In words: the serial 10% plus one-eighth of the parallel 90% is 21.25% of the original time, a speedup of about 4.7; even infinitely many cores leave the 10%, capping the speedup at 10.
```

The same calculation in Python, for several core counts:

```python
def amdahl(p, n):
    if (not 0 <= p <= 1
            or type(n) is not int or n < 1):
        raise ValueError("bad p/n")
    return 1 / ((1 - p) + p / n)

for n in (2, 4, 8, 64, 10**9):
    print(n, round(amdahl(0.9, n), 2))
# 2 1.82
# 4 3.08
# 8 4.71
# 64 8.77
# 1000000000 10.0
```

Even with 90% parallel code, 8 cores give only 4.7×, and no number of cores gets past 10×. The serial 10% dominates. This shows why serial performance still matters for this workload. Other workloads can justify many smaller cores; the model does not prescribe one chip organisation. (Gustafson's law gives a more hopeful view when the problem size grows with the machine; that is covered in the parallel hardware module.)

## Living within a power budget

Performance per watt is one important CPU design objective, alongside latency, throughput, cost and other constraints. The main techniques:

### Dynamic voltage and frequency scaling (DVFS)

DVFS changes operating frequency and voltage at runtime within supported operating points. Lowering voltage can substantially reduce switching power; frequency changes alone are not governed by a universal cubic law. The best setting depends on workload demands and total energy, including how long execution lasts.

### Turbo boost

Supported processors can raise frequency above a specified base level when power, current, thermal and other limits allow. The available boost depends on the processor and active-core configuration; boost can involve multiple or all active cores, and idle cores need not all be power-gated. Maximum advertised boost is not a guarantee for every workload.

### Race to idle

Sometimes it is better to run fast and then enter a lower-power idle state, because completing work can permit more components to become idle. Whether racing or pacing wins depends on how much static power the rest of the system burns while the work is running.

### Power gating and clock gating

Clock gating suppresses clock transitions and associated switching activity; it does not remove leakage or necessarily prevent every data-driven transition. Power gating disconnects selected supply domains to reduce leakage, with transition costs and possible state-retention requirements. Neither implies that the whole system consumes zero power.

### Heterogeneous cores

Heterogeneous processors combine cores with different performance and energy characteristics. An energy-aware scheduler can use workload demand and an energy model to choose placement, subject to affinity, ISA compatibility, policy and available capacity. A background task is not guaranteed to consume less energy on any core simply labelled “efficient”; evaluate the actual workload and system.

## Dark silicon

**Dark silicon** describes a power-constrained inability to use all available circuitry simultaneously at full performance. The 2011 study by Esmaeilzadeh and colleagues modelled such limits; its projections are not measurements of every current chip or proof that a fixed fraction must be physically powered off at every instant.

Specialised units can perform supported workloads with less instruction-processing overhead or more suitable data paths than general-purpose cores. Benefits depend on utilisation, data movement, programmability and implementation. Idle units may be gated; no universal efficiency multiplier or idle-power figure is established here.

## The bigger picture

Clock frequency, IPC, parallel execution and specialised hardware all contribute to performance. Their importance varies by workload. More cores or an accelerator help only when software and data movement can use them effectively.

> [!warning] Power is a software problem too
> Busy-waiting, polling loops and unnecessary wake-ups keep cores out of their low-power states. On battery-powered devices and in data centres (where electricity and cooling are a large part of running costs), efficient code is measured in watts as well as seconds.

## Key takeaways
- Capacitive switching power is approximately proportional to activity, capacitance, the square of the supply voltage and the clock frequency; cubic frequency scaling requires an extra voltage-frequency assumption.
- Ideal Dennard scaling keeps power density constant; its breakdown increases the importance of power and thermal budgets.
- Multicore can improve throughput for concurrent work, without automatically speeding up a serial job.
- Fixed-work Amdahl speedup approaches one divided by the serial fraction; a fully parallel job has no finite ceiling in that ideal model.
- DVFS, boost, gating, heterogeneous placement and specialisation have workload-dependent power and energy tradeoffs.

## Further reading
- [Dennard scaling — Wikipedia](https://en.wikipedia.org/wiki/Dennard_scaling)
- [The Free Lunch Is Over, by Herb Sutter](http://www.gotw.ca/publications/concurrency-ddj.htm)
- [Dark silicon — Wikipedia](https://en.wikipedia.org/wiki/Dark_silicon)
- [Processor power dissipation — Wikipedia](https://en.wikipedia.org/wiki/Processor_power_dissipation)
- [Amdahl's law — Wikipedia](https://en.wikipedia.org/wiki/Amdahl%27s_law)
- [ARM big.LITTLE — Wikipedia](https://en.wikipedia.org/wiki/ARM_big.LITTLE)

- [CMOS Power Consumption (Texas Instruments)](https://www.ti.com/lit/an/scaa035b/scaa035b.pdf)
- [Dark Silicon and the End of Multicore Scaling (original 2011 paper)](https://www.cs.cmu.edu/~18742/papers/Esmaeilzadeh2011.pdf)
- [Intel processor technology definitions](https://www.intel.com/content/www/us/en/support/articles/000006513/processors.html)
- [Linux Energy Aware Scheduling](https://kernel.org/doc/html/latest/scheduler/sched-energy.html)
- [Original Dennard et al. scaling paper (1974)](https://stanford.edu/class/cs114/readings/dennard.pdf)
