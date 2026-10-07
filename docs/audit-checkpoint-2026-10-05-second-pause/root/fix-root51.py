from pathlib import Path
import json
base=Path('content/architecture/04-pipelining');p=base/'pipe-iron-law.md';s=p.read_text()
a=s.index('Two laptops');b=s.index('To reason',a);s=s[:a]+'Two processors can run at the same clock frequency and complete the same task in different times. Clock speed alone does not specify how much useful work a processor completes.\n\n'+s[b:]
s=s.replace('The time a program takes is:', 'For one thread’s measured CPU execution interval at a fixed clock frequency, using matching instruction and cycle counts:')
s=s.replace('how many instructions the program actually executes,', 'the dynamic count of architecturally completed instructions in the measured scope,')
s=s.replace('the *average* number of clock cycles each instruction takes.', 'total counted cycles divided by completed instructions. It is not the average latency of individual overlapping instructions.')
s=s.replace('The units cancel neatly:', 'With variable frequency, use compatible cycle/time accounting or sum over fixed-frequency intervals. Waiting off-CPU and concurrent threads need separate accounting; CPU time is not automatically wall-clock response time.\n\nThe units cancel neatly:')
s=s.replace('Both describe the same machine;', 'Both describe the same measured instruction/cycle totals;')
s=s.replace('5 nm transistors', 'logic depth, voltage and process')
s=s.replace('**The algorithm** matters most. A better algorithm can cut IC by orders of magnitude; no hardware trick does that.', '**The algorithm** can substantially change the work required. Hardware instructions, accelerators and compiler transformations can also reduce architectural IC. The best improvement depends on the measured bottleneck.')
s=s.replace('RISC ISAs use more, simpler instructions.', 'Instruction count is not a fair standalone comparison across ISAs; counts also depend on vectorization and other instructions.')
s=s.replace('Different instructions take different numbers of cycles. An add may take 1, a load that hits in cache a few, and a load that misses to DRAM hundreds. The overall CPI is a weighted average, using the fraction of executed instructions of each class:', 'For a simple non-overlapping cost model, assign each instruction class a cycle cost. The overall CPI is then its instruction-frequency-weighted average. On an overlapping superscalar processor, adding individual instruction latencies would double-count shared cycles; a measured CPI breakdown needs a consistent attribution method. The following numbers are hypothetical additive costs:')
a=s.index('In the early 2000s');b=s.index('### MIPS',a);s=s[:a]+'A shorter clock period can be offset by a larger CPI, for example if a deeper design incurs more recovery cycles on mispredicted branches. Exact historical processor stage counts and cross-product performance comparisons are omitted here: they need a specific primary hardware description and benchmark, rather than a general clock-speed anecdote.\n\n'+s[b:]
s=s.replace('It ignores the instruction count,', 'As a throughput score it does not account for how many instructions the task requires,')
s=s.replace('MIPS is only meaningful between machines running the same binary on the same ISA.', 'MIPS can describe instruction throughput, but it predicts task completion time only when the relevant dynamic instruction counts are fixed. The same binary can still execute different counts on different inputs or execution paths.')
s=s.replace('A modern core that can retire 6 or 8 instructions per cycle may average well under 2 on a database or web server, which is dominated by cache misses.', 'Realized IPC depends on instruction mix, dependency chains, front-end delivery, memory behaviour and prediction. No universal IPC value or dominant bottleneck is asserted for databases or web servers.')
s=s.replace('A low IPC (well under 1) on a big server process usually means the CPU is stalled on memory, and the fix is data layout or caching, not a faster clock.', 'Low IPC alone does not identify the cause: serial arithmetic dependencies, execution-unit pressure, front-end limits, branch recovery and memory stalls can all contribute. Use architecture-specific counters and profiles before choosing a fix.')
s=s.replace('**The power wall** stopped clock rates rising around 2005, which is why the industry turned to multiple cores: improving throughput across many programs rather than the time of one.', '**Power and thermal limits** constrained frequency scaling and encouraged multicore designs. Frequency did not stop increasing altogether. Multiple cores can improve throughput and can reduce the time of a parallelizable single job.')
s=s.replace('Run time = instruction count', 'CPU execution time in the stated fixed-frequency scope = instruction count')
s=s.replace('CPI is a weighted average over the instruction mix,', 'In the additive class-cost model, CPI is a weighted average over the instruction mix,')
s+='\n- [Intel top-down performance analysis](https://www.intel.com/content/www/us/en/docs/vtune-profiler/cookbook/2024-0/top-down-microarchitecture-analysis-method.html)\n- [Linux perf project tutorial](https://perfwiki.github.io/main/tutorial/)\n'
p.write_text(s);p=p.with_suffix('.questions.json');q=json.loads(p.read_text())
q[0]['prompt']+=' Assume a fixed frequency and no off-CPU waiting during the interval.'
q[1]['options'][1]['explanation']='1 divided by 2.5 is 0.4. A value of 0.25 would correspond to IPC 4.'
q[1]['workedExample']='For matching counters, IPC=instructions/cycles and CPI=cycles/instructions. Therefore CPI=1/2.5=0.4. This describes more than one completed instruction per counted cycle on average, without implying each instruction has latency below one cycle.'
q[2]['prompt']='For sufficiently large inputs, suppose a replacement sorting algorithm performs substantially fewer operations and hence fewer executed instructions. Which iron-law term is directly reduced?'
q[2]['options'][0]['explanation']='Clock period is not the term directly reduced by this change. Actual frequency can still respond to software-selected policies, load, temperature and hardware control.'
q[2]['options'][1]['explanation']='Changing the algorithm may also change CPI substantially through locality, branches and dependencies, but fewer executed instructions directly reduces IC.'
q[2]['options'][2]['explanation']='Correct by the premise. Big-O operation counts alone do not specify the exact machine-instruction count or the input-size crossover.'
q[2]['options'][3]['explanation']='Algorithms affect both work and memory behaviour. Abstract operation counts and dynamic machine instructions are related, but not identical.'
q[2]['workedExample']='IC counts dynamically executed instructions. Reducing that count directly changes IC, while CPI and actual clock may also change. At n=10^6, n² is 10^12 and n log2 n is about 2×10^7, but their ratio is not a measured speedup: constants, cases and operation costs matter.'
q[4]['prompt']=q[4]['prompt'].replace('A benchmark\'s instruction mix is measured as follows.', 'In an additive class-cost model with non-overlapping cycle costs, the instruction mix is as follows.')
q[5]['prompt']+=' Keep instruction count and clock fixed, and assume additive independent cost reductions.'
q[6]['options'][2]['text']='For matching CPU-time measurements with fixed dynamic instruction count, higher MIPS means shorter CPU execution time'
q[6]['options'][2]['explanation']='True because MIPS=IC/(time×10^6). The same executable alone does not guarantee the same dynamic count.'
q[6]['options'][4]['explanation']='True: instruction mix is one influence. Dependencies, cache behaviour and speculation also matter; raw latencies cannot simply be added on overlapping cores.'
q[6]['workedExample']='Lower IC or higher clock alone does not guarantee less time if other terms change. IPC and CPI are reciprocal for matching counts. With fixed dynamic IC, higher MIPS implies less measured CPU time. CPI depends on the workload, including mix and interaction between instructions.'
q[8]['options'][3]['text']='Marginally: about 2.56% higher performance, or 2.5% less execution time'
q[8]['workedExample']='At fixed IC, new/old time = (1.3/4)/(1/3)=0.975: 2.5% less time. Speedup = 1/0.975≈1.02564: 2.56% higher performance. Power, area and workload measurements are needed to decide whether this hypothetical design trade is worthwhile.'
q[9]['prompt']=q[9]['prompt'].replace('runs on one 3 GHz core', 'runs at a fixed 3 GHz on one core, with matching non-multiplexed instruction/cycle counters for its CPU execution interval')
q[9]['options'][1]['explanation']='Time uses counted cycles divided by the fixed frequency. IPC alone cannot determine whether the workload is compute-bound or memory-bound.'
q[9]['options'][2]['text']='IPC 0.4 and 4 s of counted CPU execution; more evidence is needed to identify the bottleneck'
q[9]['options'][2]['explanation']='Correct: 4.8/12=0.4 and 12×10^9/(3×10^9)=4 seconds. Dependencies, execution resources, memory and front-end issues are possible causes; off-CPU waiting would add wall time.'
q[9]['workedExample']='IPC=4.8/12=0.4 and CPI=2.5. At the stated fixed frequency, the counted interval corresponds to 4 seconds of CPU execution. This does not prove that most cycles do no useful work or that memory is the bottleneck. Use suitable profiles and architecture-specific top-down metrics to distinguish causes.'
q[10]['options'][0]['explanation']='In the hypothetical fixed-CPI model, 3×10^10 / (6×10^9)=5 seconds. Whether a particular processor can sustain that frequency for this workload is a separate question; 6 GHz is not universally impossible.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
p=base/'pipe-five-stage.md';s=p.read_text()
s=s.replace('the single most important idea in CPU design.', 'a fundamental technique in CPU design.')
s=s.replace('A processor runs each instruction through the same sequence of steps.', 'A simplified processor can organize instructions into a common sequence of stages.')
s=s.replace('Using the textbook timings:', 'Using these hypothetical combinational stage delays, with single-cycle boundary overhead ignored:')
s=s.replace('maybe 20 ps or so, so a more honest cycle is about 220 ps.', 'which must be budgeted. Assuming 20 ps of combined per-cycle boundary overhead gives a 220 ps period; this is a teaching assumption, not a measured device value.')
s=s.replace('For n instructions on a k-stage pipeline,', 'For n ≥ 1 instructions on an initially empty, single-issue k-stage pipeline with no stalls,')
s=s.replace('Programs get faster because there are billions of instructions, not because any one of them does.', 'Enough independent work allows the improved throughput to outweigh fill/drain overhead; billions of instructions are not required.')
s=s.replace('**Fixed-length instructions** (32 bits)', '**Fixed-length base instructions** (32 bits in the model; compressed forms such as RISC-V C differ)')
s=s.replace('**Aligned memory accesses** mean a data access never straddles two cache lines in one stage.', '**Naturally aligned scalar accesses** avoid line splits when their power-of-two size does not exceed the line size and divides it. Real ISAs can also allow unaligned accesses, with additional handling.')
s=s.replace('Since the Pentium Pro (1995), Intel and AMD front ends translate', 'Many Intel and AMD implementations translate')
a=s.index('The 5-stage design is a teaching model');b=s.index('## Where it goes wrong',a)
s=s[:a]+'''The five-stage design is a teaching model. Real implementations divide work differently, and “pipeline depth” may refer to different instruction paths or recovery events. A cross-product stage-count table is omitted because comparable primary documentation was not established for every entry.

Splitting a critical stage can shorten the clock period, while adding register overhead and potentially delaying particular result or branch-resolution paths. Not every hazard penalty necessarily increases: that depends on where stages are added and which bypass paths exist.

'''+s[b:]
s=s.replace('Pipelining overlaps instructions so every stage is busy; once full, one instruction completes per cycle.', 'The ideal single-issue model overlaps instructions and completes one per cycle in steady state, with no hazards or resource conflicts.')
s=s.replace('n instructions on a k-stage pipeline take k + n − 1 cycles; the ideal speedup is k.', 'For n ≥ 1 in the ideal model, total cycles are k + n − 1. Long-run speedup approaches k only with balanced stages and negligible overhead.')
s=s.replace('RISC features (fixed-length instructions, load/store design) exist largely to make pipelining easy; x86 cores translate to µops first.', 'Regular encodings and load/store organization simplify this pipeline model; many x86 implementations pipeline decoded micro-ops.')
s=s.replace('    k = len(STAGES)\n    total = k + n - 1', '    if type(n) is not int or n < 0:\n        raise ValueError("bad count")\n    k = len(STAGES)\n    total = k + n - 1 if n else 0')
p.write_text(s);p=p.with_suffix('.questions.json');q=json.loads(p.read_text())
q[3]['options'][1]['explanation']='4.2 divides 1,050 by 250, overlooking the slower 300 ps EX stage. The average-stage calculation would give 5, not 4.2.'
q[3]['workedExample']=q[3]['workedExample'].replace('ID and WB sit idle for over half of each cycle.', 'The shorter stages still receive the full 300 ps slot; ID uses half of it and WB one-third in this model.')
q[6]['options'][4]['explanation']='Variable length adds boundary-detection work. Extra stages or predecoding are possible implementation choices, not a mandatory fixed structure.'
q[7]['workedExample']=q[7]['workedExample'].replace('larger hazard penalties.', 'potentially changed hazard penalties, depending on the affected paths.')
q[9]['prompt']+=' The rest of the five-stage control and timing is left unchanged.'
q[9]['options'][2]['text']='EX no longer holds the prior instruction’s isolated operand/control state; it instead follows ID, breaking the assumed five-stage sequencing'
q[9]['options'][2]['explanation']='Correct with unchanged control. Removing the register merges the combinational path; a deliberate four-stage redesign could still work with adjusted timing and control.'
q[10]['options'][4]['text']='Doubling total stage count guarantees fewer misprediction-recovery cycles'
q[10]['options'][4]['explanation']='False. Total depth alone does not determine branch recovery; where the branch resolves and how fetch restarts matter.'
q[10]['workedExample']=q[10]['workedExample'].replace('hazards and mispredictions cost more cycles in deeper pipelines, which eventually outweighs the faster clock.', 'hazard and recovery penalties depend on the paths being split and can offset clock gains; total stage count alone does not quantify them.')
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print('Applied iron-law and five-stage reviews, 22 questions')
