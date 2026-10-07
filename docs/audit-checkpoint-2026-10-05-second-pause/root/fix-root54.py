from pathlib import Path
import json
p=Path('content/architecture/04-pipelining/pipe-out-of-order.md');s=p.read_text()
s=s.replace('But fetching four instructions a cycle is pointless if the second depends on the first, or the first is waiting 200 cycles for DRAM. To keep many execution units busy, the core must look further ahead in the instruction stream, find independent work and run it **out of order**, while making the program appear to have run exactly in order.', 'In-order superscalar execution can improve throughput, but a blocked instruction can prevent younger independent work from issuing. **Out-of-order** execution finds ready work further ahead while preserving the architectural rules. The 200-cycle load used below is hypothetical, not a universal DRAM latency. In-order retirement does not imply sequentially consistent interthread memory ordering.')
a=s.index('The simplest superscalar core');b=s.index('The weakness of in-order issue',a)
s=s[:a]+'A simple in-order superscalar design can issue two instructions per cycle when pairing rules, operands and execution resources allow. Multiple issue does not itself require out-of-order scheduling.\n\n'+s[b:]
s=s.replace('# cache miss: 100+ cycles', '# assume a long cache miss')
s=s.replace('A modern out-of-order (OoO) core has three parts:', 'A common out-of-order (OoO) teaching design has three parts. Real designs differ in µop grouping, scheduler organisation and retirement bookkeeping:')
s=s.replace('and allocate each µop an entry', 'and allocate tracking space')
s=s.replace('**Renaming** gives every result a fresh physical register. The core has many more physical registers (often a couple of hundred integer ones) than architectural ones (16 on x86-64, 31 on Arm64, 32 on RISC-V).', '**Renaming** assigns distinct storage to simultaneously live register versions. A physical-register implementation maintains more result storage than the architectural register set. Exact counts depend on the core and ISA extensions; they are omitted without a specified implementation.')
s=s.replace('```python\ndef rename', 'This teaching renamer handles a finite straight-line sequence of ordinary register-producing operations. It has no retirement, branches, zero-register semantics or free-list reclamation; names x0… are generic, not a complete RISC-V implementation.\n\n```python\ndef rename')
s=s.replace('    rat = {f"x{i}"', '    if not 0 < n_arch <= n_phys:\n        raise ValueError("require 0 < n_arch <= n_phys")\n    rat = {f"x{i}"')
s=s.replace('        rat[dst] = free.pop(0)', '        if dst not in rat:\n            raise ValueError("unknown destination register")\n        if not free:\n            raise ValueError("teaching model: no free registers")\n        rat[dst] = free.pop(0)')
s=s.replace('In real hardware the free list is refilled at retirement:', 'In a simple design without shared physical mappings or other retained references, the free list is refilled at retirement:')
s=s.replace('Its ideas underpin every modern OoO core.', 'Its tag-based scheduling and renaming ideas are foundational; modern implementations need not use the original structure.')
s=s.replace('Tags *are* renaming: the reservation station names act as physical registers.', 'Tags distinguish producer versions, providing renaming without requiring the separate physical register file used in the preceding example. A reservation station is not literally a physical register.')
s=s.replace('State after all four have issued and before any has finished:', 'Assume enough reservation stations, ready initial registers and sufficiently long operation latencies for all four to issue before any result broadcasts. This is a schematic floating-point instruction trace, not literal IBM instruction syntax:')
s=s.replace('- **Mult1** finishes last, even though it was issued second.', '- **Mult1** can finish last despite issuing second; exact completion order depends on latencies and resource availability.')
s=s.replace('Its interrupts were **imprecise**. It also couldn\'t execute past an unresolved branch and undo the work.', 'It could produce **imprecise** floating-point exceptions. The original tag-and-broadcast algorithm described here lacks the modern speculative branch-recovery machinery.')
s=s.replace('The **reorder buffer** (proposed by Smith and Pleszkun in 1985) fixes both. It is a circular queue with one entry per in-flight instruction, in program order.', 'A **reorder buffer**, discussed by Smith and Pleszkun in their work on precise interrupts, is one solution. In this teaching model it is a circular queue with one entry per in-flight instruction, in program order. Real entry granularity can differ. Checkpointing and other bookkeeping are also needed for speculative recovery.')
s=s.replace('Retirement is in order, several per cycle.', 'Retirement is in order, up to the supported retirement width per cycle.')
s=s.replace('caches and predictor tables are not rolled back,', 'some microarchitectural effects, such as cache state, may persist; recovery of predictor history is implementation-dependent,')
a=s.index('- Stores go into a **store buffer**');b=s.index('## How big is the window?',a)
s=s[:a]+'''- Ordinary cacheable stores retain speculative data in a store queue or buffer until it is safe to commit. Squashing a store must not make its data architecturally visible; related address translation or ownership requests can still affect microarchitectural state.
- A load may forward bytes from the youngest matching older store when address, data and coverage requirements permit. Partial overlaps or unavailable data can require stalling or replay.
- A core may let a load pass older stores with unknown addresses (**memory disambiguation**). If required ordering was violated, recovery re-executes affected work; a full squash from the load is one implementation, not a universal mechanism.

## How big is the window?

> [!note] Product data omitted
> Exact commercial decode widths and ROB sizes are omitted because sufficiently reliable, consistently defined primary-source figures were not established here. Instruction counts, µop counts and ROB entries are not interchangeable.

'''+s[b+len('## How big is the window?\n\n'):]
a=s.index('Approximate figures');b=s.index('## Why not let the compiler do it?',a)
s=s[:a]+'''For a hypothetical 80 ns miss at 4 GHz, latency is 320 cycles. Maintaining allocation at four entries per cycle while retirement is blocked would require space for roughly 1,280 entries. This is an occupancy estimate, assuming sufficient independent work and no earlier resource limit. It does not prove all real misses stall for a fixed duration. A larger window may discover independent memory accesses whose latencies overlap (**memory-level parallelism**); bandwidth and other queues still limit progress.

'''+s[b:]
a=s.index('**VLIW**');b=s.index('## The costs',a)
s=s[:a]+'''**VLIW** (very long instruction word) designs expose operation grouping to the compiler, shifting much scheduling work from hardware to software. Variable memory latency makes static scheduling harder. Intel Itanium used **EPIC**, an explicitly parallel design with bundles, instruction groups, predication and speculation; it should not be reduced to a simple VLIW machine with no means to tolerate uncertain execution. A single-cause explanation of its commercial outcome is omitted because this lesson has not established evidence for one.

'''+s[b:]
s=s.replace('Real code rarely sustains more than a few IPC, however wide the machine.', 'Dependence chains, branch recovery, fetch limits and memory behaviour can leave issue capacity unused; achievable IPC is workload- and core-dependent.')
s=s.replace('A deeper, wider window means more wrong-path work to throw away.', 'More speculative capacity can allow more wrong-path work, but does not by itself fix the recovery latency or amount discarded.')
s=s.replace('pick any ready instruction from a window', 'pick ready instructions whose execution resources and ordering constraints permit issue')
s=s.replace('giving precise exceptions and allowing speculation past branches to be undone.', 'supporting precise exceptions and architectural recovery with additional bookkeeping; it does not erase every speculative side effect.')
s+='\n- [Smith and Pleszkun: Implementing Precise Interrupts in Pipelined Processors](https://american.cs.ucdavis.edu/academic/readings/papers/smithpleszkun.pdf)\n- [University of Edinburgh HASE Tomasulo model](https://www.icsa.inf.ed.ac.uk/research/groups/hase/models/tomasulo/tomasulo.html)\n- [Intel: hardware behaviour related to speculative execution](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/hardware-behavior-related-to-speculative-execution.html)\n'
p.write_text(s);p=p.with_suffix('.questions.json');q=json.loads(p.read_text())
q[0]['prompt']='Which register dependences does register renaming eliminate?'
q[1]['workedExample']=q[1]['workedExample'].replace("Without a ROB, instruction 10's result would already be in the registers", "Without a ROB or another precise-state mechanism, immediate out-of-order register updates could expose instruction 10's result")
q[2]['prompt']+=' Assume all four fit in the scheduling window, other operands are ready and suitable units are available; exclude value prediction.'
q[2]['workedExample']=q[2]['workedExample'].replace("so the program can't tell the difference", 'preserving specified architectural results; timing and other microarchitectural effects can differ')
q[4]['workedExample']=q[4]['workedExample'].replace('Mult1 may now start.', 'Mult1 may start if its other operand and the functional unit are ready.')
q[5]['prompt']='A 4-wide core executes only one long chain of dependent integer adds, each with one-cycle result latency and forwarding. Ignoring loop-control, fetch and retirement overhead, what is the maximum steady-state add IPC?'
q[5]['workedExample']='Each add needs the previous result, so at most one add starts per cycle: add IPC = 1. Independent accumulators can expose more parallelism if arithmetic reassociation preserves required semantics and enough ALUs and issue capacity exist. Four-wide decode alone does not imply four add-capable execution units.'
q[6]['options'][3]['text']='WAR hazards are avoided by capturing the current value or its producer tag when an instruction issues'
q[6]['options'][3]['explanation']='True. A later register write cannot replace the saved value or change the producer version named by the tag.'
q[6]['workedExample']=q[6]['workedExample'].replace('360/91 interrupts were imprecise: **false**.', 'The claim that 360/91 always guaranteed precise interrupts is **false**; some floating-point exceptions were imprecise.')
q[7]['prompt']='In a simplified 3 GHz core, a load at the ROB head has 100 ns remaining. Assume about 512 free entries, allocation at four entries per cycle, no retirement until it returns, and no earlier resource bottleneck. Roughly when does allocation stop?'
q[7]['options'][1]['explanation']='Retirement is already blocked, but allocation and independent execution can continue while resources remain.'
q[7]['options'][2]['text']='The free entries fill in about 128 cycles; allocation then waits roughly another 172 cycles'
q[7]['options'][2]['explanation']='Correct in this occupancy model: 100 ns × 3 GHz = 300 cycles, 512 / 4 = 128, and 300 − 128 = 172. Already allocated instructions may still execute.'
q[7]['workedExample']='At 3 GHz, 100 ns is 300 cycles. About 512 free entries fill in 128 cycles at four entries per cycle. Allocation then waits about 172 cycles. Retirement is blocked throughout, but execution need not cease when allocation stops. Real free capacity, dependencies, other queues and memory bandwidth may change this estimate.'
q[8]['options'][3]['explanation']='Ordinary branch misprediction recovery is handled by hardware; it does not itself require an OS exception.'
q[8]['workedExample']=q[8]['workedExample'].replace('Microarchitectural state (caches, predictor tables) is not rolled back,', 'Some microarchitectural effects, such as cache changes, may persist; predictor-history recovery varies,')
q[9]['prompt']+=' Assume aligned ordinary memory, equal access sizes, no intervening store or external writer, and a design that recovers by squashing from the load.'
q[9]['options'][2]['text']='The core detects the violation and re-executes the load and younger work; the load must obtain the older store’s value'
q[9]['options'][2]['explanation']='Correct under the stated recovery design. The value may be forwarded when store data is ready, or read after the store becomes visible; immediate forwarding is not guaranteed.'
q[9]['workedExample']='The younger load must observe the older same-address store under these assumptions. If it speculatively read stale data, the core detects the ordering violation and recovers by the stipulated squash. On re-execution it waits, forwards or reads the now-updated memory as appropriate. Other designs may use more selective replay.'
q[10]['options'][0]['text']='A scheduler may need many result-tag/operand comparisons and selection paths, making width and window expansion costly'
q[10]['options'][0]['explanation']='True. Comparison count grows with the number of broadcast results and waiting operands in this design. Actual area, timing and power scaling depend on scheduler organisation.'
q[10]['options'][2]['explanation']='True. Dependences and control flow can prevent a workload from supplying enough independent ready operations.'
q[10]['options'][3]['text']='A wider speculative machine can do more wrong-path work before a branch resolves'
q[10]['options'][3]['explanation']='True as a possible cost, not a universal width-times-depth penalty. Resolution timing, dependencies and occupancy matter.'
q[10]['workedExample']=q[10]['workedExample'].replace('Misprediction cost scales with window: real.', 'Additional speculative capacity can increase wasted work: a real possible cost, not a fixed scaling law.')
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print('OoO lesson and 11 questions corrected')
