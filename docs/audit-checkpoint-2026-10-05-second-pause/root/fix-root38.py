from pathlib import Path
import json
B=Path('content/theory/05-computability');p=B/'compu-turing-machines.md';s=p.read_text()
def r(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
r('- **δ: Q × Γ → Q × Γ × {L, R}**:', '- **δ: (Q − {q_accept, q_reject}) × Γ → Q × Γ × {L, R}**:')
r('A finite automaton or PDA always finishes reading its input.', 'A DFA completes one transition per input symbol. A PDA can have infinite epsilon-move branches; a decision algorithm for CFL membership still exists.')
r('1C000     0 → 1, halt','1C100     0 → 1, halt')
# Above state must be before original 0 at position1 after trailing carries: tape1000, state at index1 => 1C000. Original actually correct! undo and retain verified trace.
r('1C100     0 → 1, halt','1C000     0 → 1, halt')
r('    tape = dict(enumerate(w))', '    if max_steps < 0:\n        raise ValueError("negative step cap")\n    tape = dict(enumerate(w))')
r('        head += 1 if move == "R" else -1', '        if move not in {"L", "R"}:\n            raise ValueError("invalid move")\n        head += 1 if move == "R" else -1')
r('you have learned nothing about whether the machine would halt later.', 'you know only that it did not halt within that budget; the timeout alone does not settle eventual halting.')
r('| k tapes | O(t²) steps for t |', '| A fixed number k of tapes | Standard O(t²) simulation when t ≥ input length |')
r('| Nondeterministic | BFS of the choice tree, exponential time |', '| Nondeterministic | Fair search; exponential upper bound in a branch-time bound |')
r('| RAM machine | polynomial slowdown |', '| RAM with suitable bit-cost or bounded-word operations | polynomial slowdown |')
r('The exponential slowdown is fine for computability but is exactly the P vs NP question in complexity theory.', 'This simulation establishes an upper bound, not a proof that exponential slowdown is necessary. Whether every language accepted in nondeterministic polynomial time has a deterministic polynomial-time decider is P versus NP.')
r('Among all n-state, 2-symbol TMs that halt when started on a blank tape,', 'For the standard two-way tape, two-symbol busy-beaver model, count n working states separately from a halt state. Among machines that halt from a blank tape,')
r('Several machines needed bespoke non-halting proofs, and some 6-state machines are known to encode open problems similar to the Collatz conjecture.', 'The proof combines exhaustive reduction of machine cases with certified reasoning about non-halting.\n\n> [!note] Evidence gap\n> The previous unspecific claim about six-state machines encoding open Collatz-like problems is omitted: no particular machine, encoding convention and unresolved mathematical statement were identified for verification.')
r('Nobody programs a real computer as a Turing machine.', 'Turing-machine notation is mainly a mathematical and educational model rather than an ordinary application language.')
r('**powerful enough to cover everything**', '**expressive enough to model effective computation**')
r('Treat the memory as unbounded and you have, up to polynomial overhead, a TM.', 'With an effective instruction set and suitably costed operations, unbounded memory gives a model equivalent in computability to a TM; polynomial simulation claims also require an appropriate cost model.')
r('"no program in any language, on any computer, can decide X".', '"no effective procedure can decide X for all inputs in the unbounded model", using the Church–Turing thesis.')
r('After t steps at most t + |input| cells have been visited.', 'In t single-cell moves the head visits at most t + 1 cells; counting initially stored input as well gives at most |input| + t + 1 cells involved.')
r('- A TM is a finite control plus an infinite read-write tape, with δ: Q × Γ → Q × Γ × {L, R}.', '- A TM is a finite control plus an unbounded read-write tape; transitions read/write a symbol and move one cell, with no outgoing transitions from halting states.')
s+='\n- [Determination of the fifth Busy Beaver value — proof authors](https://arxiv.org/abs/2509.12337)\n'
p.write_text(s)
p=B/'compu-turing-machines.questions.json';qs=json.loads(p.read_text());q={x['id'].split('-q')[-1]:x for x in qs}
q['2']['workedExample']=q['2']['workedExample'].replace('gives you no information about the answer', 'alone does not settle eventual acceptance')
q['3']['workedExample']=q['3']['workedExample'].replace('4 moves right, 3 carries and one final write', '3 rightward scanning moves, one left move from the end blank, 3 carries and one final write')
q['5']['prompt']=q['5']['prompt'].replace('asymptotic running time','tight asymptotic running-time bound')
q['5']['options'][1]['text']='Θ(n²): n passes, each walking Θ(n) cells'
q['5']['options'][2]['explanation']='O(n³) is a valid but loose upper bound; the question asks for a tight bound. The three letter blocks are visited within the same pass.'
q['5']['options'][3]['explanation']='O(2ⁿ) is a loose upper bound here, not the tight bound. The stated machine performs quadratically many moves, not exponentially many.'
q['6']['prompt']='A 3-tape TM runs in t(n) = n² time. Which bound follows by substituting into the standard general O(t(n)²) single-tape simulation theorem?'
q['6']['options'][0]['explanation']='Some particular machines may admit this tighter simulation, but substituting t(n) = n² into the stated general bound yields O(n⁴).'
q['6']['options'][1]['explanation']='A constant-factor simulation is not supplied by the stated general sweep construction; a particular machine may admit optimisations.'
q['6']['options'][3]['explanation']='The stated multi-tape simulation theorem gives a polynomial upper bound. Exponential search is a general upper-bound method for nondeterministic branches, not a proven necessary overhead.'
q['8']['prompt']=q['8']['prompt'].replace('Why must the simulation explore the tree of choices breadth-first rather than depth-first?', 'Why does ordinary breadth-first search work where unbounded depth-first traversal may fail?')
q['8']['workedExample']=q['8']['workedExample'].replace('after at most bᵈ nodes (b = maximum branching factor)', 'after at most 1 + b + ... + bᵈ nodes (b is the maximum branching factor)').replace('with exponential time.', 'with an exponential upper bound in accepting depth for bounded branching greater than one; iterative deepening or another fair traversal also works.')
q['10']['prompt']=q['10']['prompt'].replace('an arbitrary n-state TM M', 'an arbitrary n-working-state, two-symbol TM M in the same model')
q['10']['workedExample']=q['10']['workedExample'].replace('This is also why S(n) eventually outgrows every computable function f: otherwise f could replace S in this procedure.', 'This argument rules out a computable global upper bound on S. The stronger theorem that S eventually dominates every computable function needs a separate machine-construction argument; lack of a global bound alone does not establish eventual domination.')
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n')
p=B/'compu-halting.md';s=p.read_text()
r('it is logically impossible, in any language, on any hardware.', 'no effective algorithm decides halting for every program/input pair in a Turing-complete model with unbounded resources. A closed deterministic machine with a fixed finite state space is different: cycle detection decides halting in principle, though it may be infeasible.')
r('so some languages (in fact, almost all of them)', 'so all but countably many languages')
r('a new TM D that takes a machine description and does the opposite of what that machine does on its own description:', 'a TM D that takes a machine description and flips H’s answer to whether that machine accepts its own description:')
r('    ...   # claimed perfect oracle', '    # Proof placeholder, not an algorithm.\n    raise NotImplementedError')
r('paradox(paradox)   # what happens?', '# Hypothetically call paradox(paradox).')
r('Every real language allows this: Python functions are objects, and any program can read its own source file. Kleene\'s recursion theorem shows that a TM can always obtain its own description, so the self-reference is not a trick of Python.', 'Python functions can be passed as objects, but a real program need not have access to its source file. The formal proof uses an encoding that can be passed as data; Kleene’s recursion theorem supplies a general formal account of effective self-reference, not a runtime source-file permission guarantee.')
r('In Python, model each recogniser as a generator', 'For nonnegative integers in the example, model each recogniser as a generator')
r('Neither recogniser alone decides anything:', 'Neither displayed recogniser decides the square-number language by itself:')
r('warn about obvious cases (`while True` with no `break`)', 'can establish nontermination in simple cases such as `while True: pass` in the idealised model')
r('require recursion on structurally smaller arguments.', 'support termination-checked definitions, including structural and well-founded approaches. Their exact accepted forms and escape hatches differ; it is not simply a requirement that every recursive call visibly use a smaller source argument.')
r('- **A halting oracle would solve mathematics.**', '- **A halting oracle would settle some mathematical statements.**')
r('def is_prime(k):\n', 'from math import isqrt\n\ndef is_prime(k):\n')
r('range(2, int(k ** 0.5) + 1))', 'range(2, isqrt(k) + 1))')
r('Many other open problems, and the consistency of mathematics itself, can be phrased the same way. That is a good sanity check that `halts` can\'t exist.', 'This reasoning assumes idealised unbounded integers, time and memory; real execution may fail from resource limits. The same oracle could decide whether an effectively axiomatized formal system has a finite proof of contradiction, by deciding whether a proof search halts. That does not resolve every mathematical statement or define a single "consistency of mathematics" question. The diagonal proof, not the fact that a conjecture is open, establishes impossibility.')
p.write_text(s)
p=B/'compu-halting.questions.json';qs=json.loads(p.read_text());q={x['id'].split('-q')[-1]:x for x in qs}
q['3']['prompt']+=' Interpret Python as an idealised effective language with unbounded resources, without external oracles.'
q['4']['options'][3]['explanation']='The contradiction concerns the stipulated total oracle and idealised execution, not a hardware timing detail.'
q['8']['prompt']+=' Assume exact unbounded integer arithmetic and no resource failures.'
q['8']['workedExample']=q['8']['workedExample'].replace("which is good evidence (beyond the proof) that `halts` can't be built.", 'but the fact that a problem remains open is not a proof that a proposed oracle cannot be built; undecidability follows from diagonalisation.')
q['11']['options'][2]['text']='Given a Python program P and input x, does P halt in the idealised unbounded-resource model?'
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n')
