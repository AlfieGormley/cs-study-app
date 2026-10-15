---
id: pipe-power-wall-budgets-and-specialisation
sourceLesson: pipe-power-wall
title: Manage power budgets and specialise work
level: advanced
minutes: 4
summary: Distinguish DVFS, boost, idle, clock/power gating, heterogeneous placement and dark silicon.
---

The earlier units modelled switching power, ideal scaling and parallel speedup. Real systems also choose supported operating points and where work runs. These mechanisms cooperate under platform-specific power and thermal limits; no universal idle-power figure or accelerator efficiency multiplier follows.

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
- Power, energy and performance need workload-specific measurement.
- Clock gating reduces clock switching; power gating targets supply-domain leakage with transition costs.
- Dark silicon concerns power-constrained utilisation, and accelerators help only suitable workloads.

## Further reading
- [Linux implementation: Energy Aware Scheduling](https://kernel.org/doc/html/latest/scheduler/sched-energy.html)
- [Intel processor technology definitions](https://www.intel.com/content/www/us/en/support/articles/000006513/processors.html)
- [Esmaeilzadeh et al.: dark silicon (original 2011 paper)](https://www.cs.cmu.edu/~18742/papers/Esmaeilzadeh2011.pdf)
- [Texas Instruments: CMOS power consumption](https://www.ti.com/lit/an/scaa035b/scaa035b.pdf)
