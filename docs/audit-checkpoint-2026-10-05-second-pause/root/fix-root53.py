from pathlib import Path
import json
p=Path('content/architecture/04-pipelining/pipe-branch-prediction.md');s=p.read_text()
a=s.index('A branch appears');b=s.index('## What a misprediction costs')
s=s[:a]+'''A processor can fetch and execute instructions beyond a branch before its direction and target are known. If its prediction is wrong, it must discard younger wrong-path work and redirect execution. How much work is lost depends on the processor and when the branch resolves.

> [!note] Evidence limits
> Universal branch frequencies, prediction accuracies, pipeline depths and product-specific predictor details are omitted: they need a named workload and reliable documentation or measurements. The numerical examples below are explicit teaching models.

'''+s[b:]
s=s.replace('The extra CPI from branches is:', 'In an additive model with a fixed average recovery penalty and no overlap with other counted stalls, estimated extra CPI is:')
s=s.replace('> 20% of instructions', '> Assume unchanged retired instruction count and clock frequency, with additive penalties. 20% of instructions')
s=s.replace("The wider and deeper the core, the more each misprediction costs. This is why branch predictors in high-end CPUs use a substantial share of the core's area.", 'Lower base CPI makes a given additional CPI more significant. Width and pipeline organisation can affect recovery, but neither alone determines a universal penalty or area cost.')
s=s.replace('Cheap, but loops are taken most of the time, so this does badly.', 'Simple; it misses each taken iteration of a loop-back branch.')
s=s.replace('This gets surprisingly far on simple code.', 'This is a heuristic, not a guarantee about source-level control flow.')
s=s.replace('all feed this.', 'can inform these layout and optimisation decisions; they do not guarantee a particular hardware predictor action.')
s=s.replace('A **2-bit counter** fixes this by requiring two wrong guesses in a row before changing its mind:', 'A **2-bit counter** adds hysteresis: a strongly biased state needs two consecutive opposite outcomes to reverse its prediction. From a weak state, one opposite outcome is enough:')
s=s.replace('def two_bit(outcomes, start=1):\n', 'def two_bit(outcomes, start=1):\n    if type(start) is not int or not 0 <= start <= 3:\n        raise ValueError("start must be an integer 0..3")\n')
s=s.replace('Bigger tables reduce it; tagged tables (below) avoid it.', 'More capacity can reduce interference. Tags help distinguish entries, but finite capacity and partial tags do not eliminate every collision or replacement effect.')
s=s.replace('```c\nif (x == 0)', 'The following is source-level pseudocode; assume x and y stay unchanged. Compiler lowering may introduce, remove or invert machine branches.\n\n```text\nif (x == 0)')
s=s.replace("B3's outcome is fully determined by B1 and B2.", 'The third condition is determined by the first two conditions. When corresponding machine branches and relevant history are available, this provides a learnable correlation.')
s=s.replace('def gshare(outcomes, pc=0x40, hbits=4):\n', 'def gshare(outcomes, pc=0x40, hbits=4):\n    if type(hbits) is not int or not 1 <= hbits <= 16:\n        raise ValueError("teaching model: hbits must be 1..16")\n')
s=s.replace('A pattern that defeats a plain 2-bit counter is strict alternation, T N T N:', 'For the following single-branch model, pass Boolean outcomes and an integer PC; it uses the low PC bits directly, without modelling instruction alignment or speculative history recovery. A pattern that defeats a plain 2-bit counter is strict alternation, T N T N:')
s=s.replace('still misses about 11% of the time', 'produces 108 misses in the 1,000-outcome trace above (10.8%)')
a=s.index('- **Tournament predictors**');b=s.index('## Predicting the target',a)
s=s[:a]+'''- **Tournament predictors** combine different predictors, such as local and global history, with a chooser trained to select between them.
- **TAGE** (Seznec and Michaud, 2006) combines a base predictor with tagged tables using geometrically increasing history lengths. Long histories can distinguish contexts that short histories merge. Matching and alternate-prediction policies vary with the TAGE design.
- **Perceptron predictors** (Jiménez and Lin, 2001) predict using a learned weighted sum of signed history bits and a bias. A single perceptron has a linear-separability limitation; it cannot represent every Boolean history pattern.

These are predictor families, not a verified inventory of any current commercial CPU. Product-specific implementation claims are omitted because sufficiently reliable documentation was not established here.

'''+s[b:]
s=s.replace("Knowing a branch is taken is useless if you don't know where it goes. The fetch stage needs a target in the same cycle, before the instruction has even been decoded.", 'Direction alone does not supply the next fetch address. An early target prediction can redirect fetch before decoding and executing the branch; exact stages and latencies depend on the design.')
s=s.replace('Each `call` pushes its return address; each `ret` pops it.', 'Conceptually, recognised calls push return addresses and returns pop them. Real structures have finite capacity and may lose synchronisation; prediction is not guaranteed correct.')
s=s.replace('> The BTB and history tables are shared between programs and between user and kernel code on the same core. An attacker who trains them can steer another program\'s speculation. This is the root of the Spectre variant 2 vulnerability.', '> On affected processors, predictor state can allow one security context to influence indirect-branch speculation in another. Spectre variant 2 exploits such mistraining, together with a disclosure mechanism. Sharing and isolation depend on the processor, firmware, operating system and enabled mitigations; this is not a claim that every CPU exposes all predictor state across domains.')
s=s.replace('The famous demonstration:', 'Illustrative C loop body: assume `data` is a valid array of `uint8_t`, `n` is its length (`size_t`), and `sum` is `uint64_t` initially zero. Include `<stdint.h>` and `<stddef.h>`. Unsigned accumulation is defined modulo 2^64:')
s=s.replace('for (int i = 0; i < n; i++)', 'for (size_t i = 0; i < n; i++)')
s=s.replace('With random bytes in `data`, the branch is a coin flip: about 50% mispredicted. Sort `data` first and the branch becomes N N N ... T T T, nearly perfectly predicted. The sorted version can run several times faster, with identical instruction count. Only CPI changed.', 'If byte values are independently uniform over 0–255 and unpredictable from available history, the condition is a fair coin flip. If a machine branch remains, history prediction has expected accuracy 50%. Sorting the same values produces long runs of false then true conditions, which simple predictors learn. This can reduce misprediction cost, but supplies no guaranteed speedup: inspect the generated code and exclude or amortise sorting cost. The compiler may remove the branch in both versions.')
s=s.replace('When a branch is genuinely unpredictable, remove it.', 'For an unpredictable branch, consider a branchless implementation and measure it.')
s=s.replace('A `cmov` always waits for both inputs, while a well-predicted branch lets the CPU run ahead speculatively. Use branchless code for unpredictable conditions (around 50/50 on random data), and keep branches for predictable ones. Measure with `perf stat -e branches,branch-misses`.', 'Branchless selection can introduce data dependencies or work on both alternatives, whereas a predicted branch permits speculative execution. Either source form may compile to the same machine code. Compare generated code and measure the actual workload; on supported Linux systems, `perf stat -e branches,branch-misses` provides useful counters, subject to hardware availability and permissions.')
s=s.replace('gives the indirect predictor more context than one central `switch`.', 'can give a PC-indexed indirect predictor more context than one central `switch`, if the compiler preserves separate dispatch sites. This does not guarantee a speedup.')
s=s.replace('if you process it many times.', 'if changing order preserves semantics and repeated processing amortises the rearrangement cost.')
a=s.index('## Key takeaways');b=s.index('## Further reading',a)
s=s[:a]+'''## Key takeaways
- Additive branch CPI estimates require explicit penalty and overlap assumptions.
- Two-bit counters tolerate isolated opposite outcomes from strong states; global history can distinguish patterns they miss.
- Direction and target prediction solve different parts of speculative fetching.
- Branchless source does not guarantee branchless machine code or faster execution: inspect and measure.
- Cross-domain predictor influence is a security issue on affected systems; isolation and mitigations are implementation-specific.

'''+s[b:]
s+='\n- [Combining Branch Predictors (McFarling, original DEC technical report; mirror)](https://shiftleft.com/mirrors/www.hpl.hp.com/techreports/Compaq-DEC/WRL-TN-36.pdf)\n- [Spectre attacks: exploiting speculative execution (original paper)](https://spectreattack.com/spectre.pdf)\n'
p.write_text(s)
p=p.with_suffix('.questions.json');q=json.loads(p.read_text())
q[0]['prompt']+=' Use the additive model, with no overlapping penalties.'
q[0]['options'][2]['explanation']='This uses the hit rate rather than miss rate. A correct prediction incurs no misprediction-recovery penalty in this model; prediction itself still uses resources.'
q[0]['workedExample']=q[0]['workedExample'].replace('about 23% of its time wasted on wrong-path work','the added recovery term accounts for 0.3 / 1.3 ≈ 23% of modelled execution time')
q[1]['options'][1]['explanation']='Correct. Its target is backward, so the BTFN rule predicts taken. Repeated loop-back branches motivate this heuristic; not every backward branch is taken or belongs to a long loop.'
q[1]['workedExample']='For the stated backward branch BTFN predicts taken without using execution history. If its outcomes are 99 taken followed by one not-taken exit, it is correct 99 times out of 100.'
q[2]['prompt']='In the teaching pipeline, fetch must choose the next PC before decoding the current instruction. Why is a BTB useful alongside a direction predictor?'
q[4]['prompt']+=' Assume a dedicated counter with no interference from other branches.'
q[4]['options'][2]['explanation']='This ordinary two-bit saturating direction counter still misses the exit. A different design, such as a loop-iteration predictor, can learn more.'
q[4]['workedExample']=q[4]['workedExample'].replace('Short loops are the worst case. To predict the exit you need history (a local or global history predictor).', 'This counter does not learn the loop period. A history-based or loop-iteration predictor can distinguish the exit; short loops are not the only difficult pattern.')
q[5]['prompt']='A compiled loop conditionally adds unsigned bytes ≥ 128. Compare the same machine code on independently uniform bytes versus the same values sorted, excluding sorting time. The conditional branch remains and counters show many fewer misses after sorting. What explains that reduction?'
q[5]['options'][2]['text']='Sorting changes unpredictable outcomes into long runs of false then true conditions that the predictor can learn'
q[5]['options'][2]['explanation']='Correct. The order becomes predictable. This supports a reduction in branch misses, not a guaranteed total speedup or fixed recovery cost.'
q[5]['workedExample']='With independent uniform bytes and no predictive side information, expected accuracy is 50%. Sorted values create long false and true runs. A two-bit counter saturated at not-taken misses the first two taken outcomes at the transition, then predicts taken. Sorting preserves which values contribute to the sum. Include sorting cost when assessing end-to-end performance; either source form may otherwise be compiled without a branch.'
q[6]['options'][0]['explanation']='True as the conceptual purpose of the RAS. Finite capacity, unusual control flow or speculation recovery can cause prediction failures.'
q[6]['options'][4]['explanation']='False. Aliasing means different branches or history contexts map to the same predictor entry and may interfere; it is not the definition of multiple jump targets.'
q[8]['prompt']+=' Assume unchanged retired instruction count and clock frequency, and additive nonoverlapping penalties.'
q[8]['options'][0]['explanation']='The miss rate halves (6% to 3%), but the effect on total time depends on both the base CPI and the recovery term.'
q[8]['workedExample']='Old CPI = 0.3 + 0.2 × 0.06 × 16 = 0.492. New CPI = 0.3 + 0.2 × 0.03 × 16 = 0.396. With unchanged instruction count and clock, speedup = 0.492 / 0.396 ≈ 1.24. Recovery CPI halves; base CPI does not.'
q[9]['prompt']='For unsigned count, a C loop uses `if (err != 0) count++;`, true once in about 10,000 iterations. It is rewritten as `count += (err != 0);`. What can you conclude about performance from this source change alone?'
q[9]['options'][0]['explanation']='Source branches are not always machine branches, and a predictable machine branch is not automatically a bottleneck.'
q[9]['options'][1]['text']='No definite speedup or slowdown: inspect generated code and benchmark the workload'
q[9]['options'][1]['explanation']='Correct. Both forms may compile identically. If machine code differs, prediction, dependencies, extra work and vectorisation determine the result.'
q[9]['options'][3]['explanation']='The source frequency is not a measured misprediction rate, and neither rate follows from syntax alone.'
q[9]['workedExample']='The comparison yields C int 0 or 1, so the unsigned updates are semantically equivalent. The compiler may use a branch, conditional operation or vectorisation for either form. A rare true outcome can make a retained branch predictable, but source outcome frequency alone does not specify its actual prediction accuracy. Check assembly and measure with available performance counters.'
q[10]['options'][2]['explanation']='No. For a trace beginning T,N, state 1 cycles 1→2→1 and misses every outcome. Starting in state 2 or 3 yields 50% steady-state accuracy; state 0 approaches that pattern.'
q[10]['options'][3]['text']='Independent random outcomes, each taken with probability 50%'
q[10]['options'][3]['explanation']='No: when outcomes are independent of predictor information, expected accuracy is 50%; a finite sample can differ.'
q[10]['workedExample']=q[10]['workedExample'].replace('it cannot learn periodic patterns, which need history.', 'it does not track phase within a period. It can score well on a biased periodic pattern without learning its exact sequence.')
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print('Branch prediction lesson and 11 questions corrected')
