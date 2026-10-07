from pathlib import Path
import json
p=Path('content/architecture/04-pipelining/pipe-hazards.md');s=p.read_text()
s=s.replace('The last lesson\'s pipeline diagram assumed', 'This lesson uses a single-issue, in-order five-stage teaching pipeline with one-cycle stages, cache hits, register writes before reads in the same cycle, and the stated bypass paths. Numerical stalls below belong to this model, not every real CPU.\n\nThe last lesson\'s pipeline diagram assumed')
s=s.replace('The fix is to duplicate the resource. That is why every modern CPU has **separate L1 instruction and data caches**', 'Possible fixes include stalling, adding ports or separating resources. Many CPUs use **separate L1 instruction and data caches**')
s=s.replace('If both match, the more recent one (EX/MEM) wins.', 'If both match, the most recent producer takes priority, but its value must actually be available: a load in EX/MEM does not yet provide its loaded data. Stalling must prevent accidentally forwarding that load’s address or an older superseded value.')
s=s.replace('Take `a = b + c; d = e + f`:', 'For ordinary valid, nonvolatile memory accesses with independent values and no aliasing or observable-order constraints, take `a = b + c; d = e + f`. The listings below are schematic (symbolic addresses rather than literal RISC-V load/store syntax):')
s=s.replace('It records the earliest cycle each register can be read in ID:', 'It records the earliest logical issue slot compatible with each dependency. With forwarding this is not the cycle when the register file itself contains the new value. Program entries are `(op, dst, srcs)` with integer register IDs 0–31, `dst=None` for no register result, and register 0 hard-wired to zero. All forwarded sources, including store data, are required by EX in this simplified model; it does not model a separate late store-data bypass, branches, cache misses or multicycle units:')
s=s.replace('rdy = {}     # reg -> earliest ID cycle', 'rdy = {}     # reg -> earliest issue slot')
s=s.replace('cycle = 0    # ID cycle of this instr', 'cycle = 0    # logical issue slot')
s=s.replace('need = [rdy.get(r, 0) for r in srcs]', 'need = [rdy.get(r, 0)\n                for r in srcs if r != 0]')
s=s.replace('In the scheduled order every load is at least two instructions ahead of its first use,', 'In the scheduled order every load has an independent instruction between it and its first dependent operation,')
s=s.replace('The original MIPS defined the instruction after a branch to *always* execute.', 'Classic MIPS branches with a normal delay slot execute that slot on both taken and not-taken paths; some later branch-likely forms have annulment rules.')
s=s.replace('It hid exactly one cycle on a 5-stage pipeline,', 'It provides one architecturally executed slot; that does not necessarily hide the entire branch penalty of a particular implementation,')
s=s.replace('Hazards add stall cycles to the ideal CPI of 1:', 'For a long run in this scalar model, ignoring fill/drain and avoiding double-counting overlapping penalties, hazards add stall cycles to ideal CPI 1:')
s=s.replace('Load stalls: 0.25', 'Assume these penalties are additive, and the stated dependencies need operands in EX. Load stalls: 0.25')
s=s.replace('where the penalty is 15 or more cycles rather than 2.', 'where recovery penalties may be larger. Exact real-core cycle counts require a specified core and measurement.')
s=s.replace('Structural hazards are fixed by duplicating hardware,', 'Structural hazards can be handled by stalling or providing more resources,')
s=s.replace('A load followed immediately by its use still costs one stall;', 'An immediate EX-stage load consumer costs one stall in this model;')
p.write_text(s);p=p.with_suffix('.questions.json');q=json.loads(p.read_text())
q[0]['prompt']=q[0]['prompt'].replace('single memory','single-ported memory with at most one access per CPU cycle')
q[0]['options'][2]['explanation']='Correct. Separate instruction/data caches are one way to remove this conflict; adding ports or stalling are alternatives. Not every modern CPU has the same cache structure.'
q[0]['workedExample']='Both instructions need the same limited port, giving a structural hazard. Separate access resources can remove it; alternatively stall one instruction or provide a suitable additional port.'
q[4]['prompt']+=' Assume every stated load-use dependency needs its operand in EX, no additional branch operand stalls, additive penalties and negligible fill/drain.'
q[5]['options'][0]['explanation']='The consumer needs the newest value from SUB. Even if the older ADD has updated the register file during this cycle, it is not the value required by program order.'
q[7]['prompt']+=' Assume valid ordinary memory, no faults or observable volatile/I/O ordering, and the specified one-cycle stages.'
q[8]['options'][0]['explanation']='B’s period is 3% longer (its frequency is divided by 1.03), but the CPI reduction more than compensates in the stated model.'
q[8]['workedExample']=q[8]['workedExample'].replace("B's clock is 3% slower.","B's clock period is 3% longer.")
q[9]['options'][3]['explanation']='The stated missing zero-register check selects a wrong forwarded value; it does not introduce a condition that stalls the pipeline forever.'
q[10]['options'][1]['explanation']='True for an EX-stage consumer in this model, excluding writes to zero and operands not actually read. A store-data operand with a later bypass can need different handling.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print('Applied hazard model and 11-question corrections')
