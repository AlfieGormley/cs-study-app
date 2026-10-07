from pathlib import Path
import json
p=Path('content/architecture/04-pipelining/pipe-power-wall.md');s=p.read_text()
s=s.replace('Why clock speeds stopped rising around 2005,', 'Why power constraints slowed clock scaling,')
a=s.index('From the 1980s');b=s.index('## Dynamic power',a)
s=s[:a]+'''Clock increases and microarchitectural improvements contributed to rapid single-thread performance growth before the mid-2000s. Power and thermal constraints made continuing that trend harder and encouraged multicore designs. Clock rates and single-core performance did not stop improving, and there is no universal 3–4 GHz ceiling.

> [!note] Evidence limits
> Universal cooling wattages, voltage floors, current clock-rate limits and specific cancelled-product explanations are omitted because they need product- and process-specific evidence. The power examples below are models, not operating advice or measured processor specifications.

'''+s[b:]
s=s.replace('Every time a transistor switches, it charges or discharges a tiny capacitance. The power this costs is:', 'CMOS circuits use energy charging and discharging capacitances. A common approximation for average capacitive switching power is:')
s=s.replace('- **a** (activity factor): the fraction of transistors switching each cycle.', '- **a** (activity factor): average charging activity per clock cycle, consistently defined for the capacitances included in C; not simply an unweighted fraction of transistors.')
s=s.replace('- **C**: the total capacitance being switched.', '- **C**: the capacitance represented by the activity model. Equivalently, sum each node’s activity × capacitance.')
a=s.index('Voltage is squared');b=s.index('> [!example]',a)
s=s[:a]+'''At fixed activity and capacitance, power is linear in frequency and quadratic in voltage. Higher frequencies may require higher voltage, but **V is not universally proportional to f**. A cubic frequency rule follows only if voltage also scales proportionally over the modelled range. Total chip power includes leakage, other switching effects and other components.

'''+s[b:]
s=s.replace('You lose 15% of performance and save about 39% of power.', 'With unchanged activity and capacitance, capacitive switching power falls about 39%. Performance falls 15% only if throughput is proportional to frequency; total energy and total system power need separate accounting.')
s=s.replace('Shrink every dimension by a factor k', 'In the ideal constant-field model, shrink dimensions by a factor k')
a=s.index('The catch is voltage.');b=s.index('## Why more cores instead?',a)
s=s[:a]+'''Maintaining performance while reducing supply voltage puts pressure on threshold voltage and leakage. Real devices did not continue the ideal scaling relationships indefinitely. Once voltage and other properties no longer scale together, constant power density no longer follows. Power delivery and heat removal then constrain feasible operating points: the **power wall** is an engineering constraint, not a universal frequency or wattage limit.

'''+s[b:]
s=s.replace('Take one core at frequency f and voltage V, using power P.', 'For a hypothetical CPU-bound workload, hold per-core activity, capacitance, IPC and work per instruction fixed; ignore shared-system power, communication and leakage. Take one core at frequency f and voltage V, using switching power P.')
s=s.replace('Getting 1.7× from a single core by raising the clock would need roughly 1.7³ ≈ 4.9× the power, which is impossible to cool.', 'If a single-core 1.7× clock increase also required 1.7× voltage, this model would predict 1.7³ ≈ 4.9× switching power. That hypothetical scaling is not a claim that such an operating point is feasible or universally impossible to cool.')
s=s.replace('That is the bargain multicore offers: **more performance per watt, but only for parallel work**. Herb Sutter\'s 2005 article *The Free Lunch Is Over* told programmers that from now on, faster software would have to be concurrent software.', 'Multicore can improve aggregate throughput per watt when work can run concurrently, including independent jobs. It does not automatically accelerate one serial task; algorithmic and single-core improvements still matter.')
s=s.replace('If a fraction p of the work can be spread over n cores and the rest is serial:', 'For a fixed-size job, let p be the fraction of its single-core execution time that scales perfectly over n equally fast cores. Assume unchanged serial time and no communication, scheduling, contention or other parallel overhead:')
s=s.replace('def amdahl(p, n):\n    return', 'def amdahl(p, n):\n    if not 0 <= p <= 1 or type(n) is not int or n < 1:\n        raise ValueError("require 0 <= p <= 1 and integer n >= 1")\n    return')
s=s.replace('This is why single-thread performance still matters, and why chips keep a few powerful cores rather than hundreds of weak ones.', 'This shows why serial performance still matters for this workload. Other workloads can justify many smaller cores; the model does not prescribe one chip organisation.')
s=s.replace('Since about 2005, CPU design has been about performance per watt.', 'Performance per watt is one important CPU design objective, alongside latency, throughput, cost and other constraints.')
a=s.index("The core's voltage and frequency");b=s.index('### Turbo boost',a)
s=s[:a]+'''DVFS changes operating frequency and voltage at runtime within supported operating points. Lowering voltage can substantially reduce switching power; frequency changes alone are not governed by a universal cubic law. The best setting depends on workload demands and total energy, including how long execution lasts.

'''+s[b:]
a=s.index('The power and thermal budget');b=s.index('### Race to idle',a)
s=s[:a]+'''Supported processors can raise frequency above a specified base level when power, current, thermal and other limits allow. The available boost depends on the processor and active-core configuration; boost can involve multiple or all active cores, and idle cores need not all be power-gated. Maximum advertised boost is not a guarantee for every workload.

'''+s[b:]
s=s.replace('because idle power-gated cores leak almost nothing.', 'because completing work can allow lower-power idle states.')
s=s.replace('Clock gating stops the clock to idle units (removing their switching power). Power gating cuts the supply entirely, removing leakage too, at the cost of a wake-up delay.', 'Clock gating suppresses clock transitions and associated switching activity; it does not remove leakage or necessarily prevent every data-driven transition. Power gating disconnects selected supply domains to reduce leakage, with transition costs and possible state-retention requirements. Neither implies that the whole system consumes zero power.')
a=s.index("If one core design can't");b=s.index('## Dark silicon',a)
s=s[:a]+'''Heterogeneous processors combine cores with different performance and energy characteristics. An energy-aware scheduler can use workload demand and an energy model to choose placement, subject to affinity, ISA compatibility, policy and available capacity. A background task is not guaranteed to consume less energy on any core simply labelled “efficient”; evaluate the actual workload and system.

'''+s[b:]
a=s.index('Transistor counts still grow');b=s.index('## The bigger picture',a)
s=s[:a]+'''**Dark silicon** describes a power-constrained inability to use all available circuitry simultaneously at full performance. The 2011 study by Esmaeilzadeh and colleagues modelled such limits; its projections are not measurements of every current chip or proof that a fixed fraction must be physically powered off at every instant.

Specialised units can perform supported workloads with less instruction-processing overhead or more suitable data paths than general-purpose cores. Benefits depend on utilisation, data movement, programmability and implementation. Idle units may be gated; no universal efficiency multiplier or idle-power figure is established here.

'''+s[b:]
a=s.index('| Era |');b=s.index('> [!warning]',a)
s=s[:a]+'''Clock frequency, IPC, parallel execution and specialised hardware all contribute to performance. Their importance varies by workload. More cores or an accelerator help only when software and data movement can use them effectively.

'''+s[b:]
a=s.index('## Key takeaways');b=s.index('## Further reading',a)
s=s[:a]+'''## Key takeaways
- Capacitive switching power is approximately a × C × V² × f; cubic frequency scaling requires an extra voltage-frequency assumption.
- Ideal Dennard scaling keeps power density constant; its breakdown increases the importance of power and thermal budgets.
- Multicore can improve throughput for concurrent work, without automatically speeding up a serial job.
- Fixed-work Amdahl speedup approaches 1 / (1 − p) for p < 1; p = 1 has no finite ceiling in that ideal model.
- DVFS, boost, gating, heterogeneous placement and specialisation have workload-dependent power and energy tradeoffs.

'''+s[b:]
s+='\n- [CMOS Power Consumption (Texas Instruments)](https://www.ti.com/lit/an/scaa035b/scaa035b.pdf)\n- [Dark Silicon and the End of Multicore Scaling (original 2011 paper)](https://www.cs.cmu.edu/~18742/papers/Esmaeilzadeh2011.pdf)\n- [Intel processor technology definitions](https://www.intel.com/content/www/us/en/support/articles/000006513/processors.html)\n- [Linux Energy Aware Scheduling](https://kernel.org/doc/html/latest/scheduler/sched-energy.html)\n'
p.write_text(s);p=p.with_suffix('.questions.json');q=json.loads(p.read_text())
q[0]['workedExample']='Holding activity, capacitance and voltage fixed, doubling frequency doubles the modelled switching power. A real operating point may require a voltage change, but its size and feasibility require device data.'
q[0]['options'][2]['explanation']='Eightfold follows if both voltage and frequency double while activity and capacitance remain fixed. Only frequency doubles here.'
q[1]['prompt']='Why did power constraints make continuing rapid CPU clock scaling harder around the mid-2000s?'
q[1]['options'][1]['text']='Voltage and device properties no longer followed ideal constant-field scaling, making power density and heat removal stronger constraints'
q[1]['options'][1]['explanation']='Correct. Reduced voltage scaling and leakage constraints undermined the ideal constant-power-density model. This is not a universal voltage floor, cooling limit or 4 GHz ceiling.'
q[1]['options'][2]['explanation']='CPU-bound code can benefit from faster clocks, though memory and I/O waits may limit gains. The issue here is feasible power and thermal operation.'
q[1]['workedExample']='Ideal scaling reduces dimensions and voltage together. Real-device voltage, threshold and leakage constraints prevent indefinite continuation of those relationships. Raising frequency then consumes more of the available power and thermal budget. This encouraged multicore and efficiency work, while clocks and per-core performance continued improving.'
q[2]['prompt']+=' Use fixed-work Amdahl assumptions: equal core speeds and no added parallel overhead.'
q[3]['prompt']+=' Assume unchanged activity and capacitance.'
q[3]['options'][0]['explanation']='Correct: 0.9² × 0.9 = 0.729, so switching power falls 27.1%. This does not establish the change in workload performance or total energy.'
q[3]['workedExample']=q[3]['workedExample'].replace('This is why DVFS is so effective: modest slowdowns buy large power savings.', 'This is a switching-power estimate; leakage, execution duration and the rest of the system determine total energy.')
q[4]['options'][2]['explanation']='A voltage that fails to scale invalidates the constant-density derivation, but does not imply an exact doubling without assumptions about capacitance, activity and frequency.'
q[4]['workedExample']=q[4]['workedExample'].replace('Each generation gave more and faster transistors for free, until voltage stopped scaling.', 'This is the ideal constant-field result at unchanged activity, not a guarantee for every real process generation.')
q[5]['prompt']+=' Assume per-core activity, capacitance and IPC are unchanged, CPU-bound throughput follows frequency, and exclude leakage and shared-system overhead.'
q[5]['workedExample']='Each core has relative throughput 0.8 and switching power 0.8² × 0.8 = 0.512. Two cores give throughput 1.6 and power 1.024: 60% more throughput for 2.4% more modelled switching power. A hypothetical single-core 1.6× frequency and voltage increase would cost 1.6³ = 4.096× switching power; feasibility is not established.'
q[6]['options'][0]['text']='Supported turbo boost can let busy cores exceed base frequency when operating limits allow'
q[6]['options'][0]['explanation']='True. Power, current, temperature and product limits govern boost; it can apply to multiple active cores too.'
q[6]['options'][1]['explanation']='False. Clock gating reduces clock-driven switching but does not remove leakage. Power gating can reduce leakage in selected domains.'
q[6]['options'][2]['explanation']='True. DVFS adjusts supported voltage/frequency operating points at runtime; exact policy and update rate vary.'
q[6]['options'][3]['explanation']='True as a heterogeneous-design strategy. Actual scheduling depends on demand, energy models, compatibility, affinity and policy.'
q[6]['workedExample']=q[6]['workedExample'].replace('stops the clock, so no switching; leakage continues.', 'suppresses clock-driven switching; leakage and some other activity can remain.')
q[7]['prompt']+=' Assume equal per-core speed, fixed work and no parallel overhead; p is the fraction of original single-core execution time.'
q[7]['workedExample']=q[7]['workedExample'].replace('Halving the serial part to 2.5% would raise the ceiling to 40×, often a better investment than more cores.', 'If the same workload could instead have parallelisable fraction 97.5%, the ideal ceiling would be 40×. Whether that change is feasible or cost-effective needs separate evidence.')
q[8]['prompt']+=' Hold instruction count fixed and assume CPU-bound performance in both options; keep activity and capacitance fixed for A.'
q[8]['options'][3]['explanation']='The values are swapped under the explicit assumptions. Other designs can have different voltage, activity and capacitance tradeoffs.'
q[9]['prompt']='For a compatible background job without a tight deadline, measurements show lower total energy on an efficiency core. Why might the OS choose it while a performance core is idle?'
q[9]['options'][0]['explanation']='The given evidence concerns energy, not a guarantee that an efficiency core is faster.'
q[9]['options'][1]['explanation']='The compatible task is not inherently prohibited on a performance core; placement also depends on affinity and scheduling policy.'
q[9]['options'][2]['explanation']='No I/O-specific instruction set follows from the core label. The question states that the task is compatible.'
q[9]['options'][3]['text']='It meets the job’s requirements using less measured total energy and may allow the idle performance core to stay in a low-power state'
q[9]['options'][3]['explanation']='Correct under the supplied measurements. This is a workload-specific tradeoff, not a guarantee based only on the core’s name.'
q[9]['workedExample']='The scheduler balances demand, energy and policy. Here the task tolerates its measured completion time and consumes less total energy on the efficiency core. An idle performance core may remain in a low-power state. Exact gating, leakage and migration behaviour depend on the platform.'
q[10]['options'][0]['text']='Dark silicon refers to a power budget that prevents all circuitry from running at full performance simultaneously'
q[10]['options'][0]['explanation']='True. This does not specify that a fixed fraction is physically powered off at every instant.'
q[10]['options'][2]['text']='Specialised units can improve performance per watt for workloads that suit their implementation'
q[10]['options'][2]['explanation']='True. Tailored data paths and reduced instruction-processing overhead can help; data movement and utilisation still matter.'
q[10]['options'][3]['text']='Selective use of specialised accelerators can be one way to use area under a constrained power budget'
q[10]['options'][3]['explanation']='True as a design option. Area, idle leakage, transition costs and workload benefit must still be evaluated.'
q[10]['workedExample']='Dark silicon concerns power-constrained utilisation, not defective circuitry. Specialised accelerators can offer useful tradeoffs for suitable workloads; they are not universally faster or cheaper in energy. The end of ideal Dennard scaling is distinct from the historical trend in transistor counts.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print('Power lesson and 11 questions corrected')
