---
id: cplx-quantum-classes
title: "Qubits, interference and BQP"
level: advanced
minutes: 4
summary: "A pure qubit register is described by amplitudes, while measurement yields one outcome."
sourceLesson: cplx-randomised-quantum
---

## Quantum: BQP

A quantum computer on a register of qubits has a pure state described by complex **amplitudes**, one per possible bit string. Quantum gates apply structured linear transformations to that state, and measurement returns a single outcome:

```formula
N_amp = 2^n
N_amp = 2^50 ≈ 1.1 × 10^15   for n = 50
Pr[x] = |α_x|^2
where
N_amp: the number of complex amplitudes needed to describe the state
n: the number of qubits; 50 in the second line
2^n: n copies of 2 multiplied together: one amplitude per n-bit string
x: one possible measurement outcome, an n-bit string
α_x: alpha sub x, the amplitude (a complex number) attached to outcome x
|α_x|: the magnitude (size) of that complex number
Pr[x]: the probability that measuring the register gives outcome x; these probabilities add up to 1
≈: approximately equal to
In words: 50 qubits need about a million billion amplitudes to describe classically, but measuring them gives just one 50-bit outcome, chosen with probability equal to the squared size of its amplitude.
```

The power isn't "trying everything in parallel"; measurement gives you one outcome. It is **quantum interference**: arranging for amplitudes of wrong answers to cancel and right answers to reinforce.

**BQP** is the set of decision problems solvable by a polynomial-time-uniform family of polynomial-size quantum circuits with error at most 1/3 (amplifiable, as for BPP).

What's proven:

```formula
P ⊆ BPP ⊆ BQP ⊆ PP ⊆ PSPACE
where
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps on an n-bit input, for some fixed k)
BPP: bounded-error probabilistic polynomial time: decision problems a randomised polynomial-time algorithm answers correctly with probability at least 2/3 on every input
BQP: bounded-error quantum polynomial time: decision problems a quantum computer solves in polynomial time with error at most 1/3 on every input
PP: probabilistic polynomial time: yes-instances are accepted with probability greater than one half, while no-instances are accepted with probability at most one half. There is no fixed success gap as in BPP, so the usual polynomial-repetition amplification guarantee does not follow
PSPACE: decision problems solvable with a polynomial amount of memory, however long it takes
⊆: "is contained in": every problem in the left class is also in the right class (the two may turn out to be equal)
In words: everything a classical randomised computer can do efficiently, a quantum computer can too, and everything a quantum computer can do efficiently fits inside PP and inside polynomial space.
```

- BQP inside PSPACE (Bernstein and Vazirani, 1993): sum the amplitudes path by path, reusing space.
- BQP inside PP (Adleman, DeMarrais and Huang, 1997).

That last containment is why a classical-versus-quantum separation is so hard to prove:

```formula
BPP ≠ BQP  gives  BPP ≠ PSPACE
BPP ≠ PSPACE  gives  P ≠ PSPACE
where
BPP: bounded-error probabilistic polynomial time: decision problems a randomised polynomial-time algorithm answers correctly with probability at least 2/3 on every input
BQP: bounded-error quantum polynomial time: decision problems a quantum computer solves in polynomial time with error at most 1/3
PSPACE: decision problems solvable with a polynomial amount of memory
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps on an n-bit input, for some fixed k)
≠: "is not equal to": the two classes contain different problems
In words: BPP sits inside BQP, which sits inside PSPACE. If BQP were strictly bigger than BPP, PSPACE would be too; and since P sits inside BPP, P would then differ from PSPACE, an open problem nobody can currently touch.
```

So proving BQP and BPP different would prove P and PSPACE different, which is far beyond current techniques. This rules out claiming a proven separation of BQP from BPP. It does not rule out proven query-complexity advantages or smaller speed-ups within polynomial time.

## Key takeaways

- A pure qubit register is described by amplitudes, while measurement yields one outcome.
- BPP is contained in BQP, PP and PSPACE.
- Separating BPP from BQP would also separate P from PSPACE.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Randomised complexity — Arora lecture notes](https://users.cs.duke.edu/~reif/courses/complectures/Arora/lec6.pdf)
