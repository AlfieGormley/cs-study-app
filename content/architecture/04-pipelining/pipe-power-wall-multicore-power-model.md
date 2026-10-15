---
id: pipe-power-wall-multicore-power-model
sourceLesson: pipe-power-wall
title: Compare two slower cores with one faster core
level: advanced
minutes: 3
summary: Estimate relative throughput and switching power under explicit parallel-work assumptions.
---

The earlier switching-power unit squared voltage and multiplied by clock frequency. Here the same relationship compares alternative core organisations. The workload is CPU-bound and perfectly parallel in the example; a serial thread would receive only one core’s throughput. Nothing here sets a safe voltage for real hardware.

## Why more cores instead?

For a hypothetical CPU-bound workload, hold per-core activity, capacitance, IPC and work per instruction fixed; ignore shared-system power, communication and leakage. Take one core as the reference operating point. Now build two otherwise identical cores, each at 85% of that core’s frequency and voltage:

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

## Key takeaways
- Two cores help a single job only if suitable work can run concurrently.
- Multiply per-core switching power by core count; do not count one slowed core as the total.
- Frequency/voltage extrapolations are hypothetical ratios rather than feasible operating points.

## Further reading
- [Texas Instruments: CMOS power consumption](https://www.ti.com/lit/an/scaa035b/scaa035b.pdf)
- [Esmaeilzadeh et al.: dark silicon (original 2011 paper)](https://www.cs.cmu.edu/~18742/papers/Esmaeilzadeh2011.pdf)
- [Dennard et al.: constant-field scaling (original 1974 paper)](https://stanford.edu/class/cs114/readings/dennard.pdf)
