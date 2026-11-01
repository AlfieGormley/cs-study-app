---
id: sys-aslr-guess-models
title: ASLR and the assumptions behind guessing
level: intermediate
minutes: 4
sourceLesson: sys-mitigations
summary: ASLR changes selected mapping locations according to platform support and policy.
---

## ASLR: hide the addresses

**Address space layout randomisation** varies placement of selected mappings, such as libraries and stacks, when a process image is loaded. Support and configuration determine which mappings vary. A forked child process normally inherits the existing address space. Wrong target guesses can fail or crash; neither outcome is guaranteed for every corruption.

How much it helps depends on **entropy**, the number of random bits. Each independent, uniformly random bit doubles the number of places a mapping can start: 8 bits give 256 possible bases, and 28 bits give over 268 million. These are teaching examples, not asserted Linux defaults. Architecture, kernel settings and distribution policy affect actual entropy. On supported Linux systems, `vm.mmap_rnd_bits` controls randomisation for relevant mappings.

## Two guessing models

ASLR's job is to make the attacker *guess* a useful address. An attacker who learns an address from an information leak does not need to guess at all (the next lesson shows how). Without a leak, how many guesses are needed depends on whether the base changes between attempts:

- **Fixed base.** Forked workers inherit their parent's layout, so every worker shares the same unknown base. Each wrong guess crashes a worker but rules that base out. The right base is equally likely to be first, second and so on, so on average the attacker succeeds about halfway through the list, and never needs more than all of it: about 128 attempts for 256 bases, about 134 million for 28 bits.
- **Fresh base every attempt.** If each attempt meets a newly randomised base (for example, each attempt runs a newly executed process), a wrong guess rules nothing out. Every try is a new 1-in-N chance, so the average is N attempts, 256 for 8 bits, with no upper limit.

```formula reference
N = 2^b
E_fixed = (N + 1) / 2
E_new = N
where
N: the number of equally likely positions (base addresses) the mapping can have
b: the bits of entropy: how many independent, uniformly random bits choose the position
2^b: b copies of 2 multiplied together
E_fixed: the expected (average) number of attempts when the base stays fixed and no base is tried twice
E_new: the expected number of attempts when the base is re-randomised every time; the mean of a geometric distribution, which counts tries up to the first success
In words: b random bits give 2^b possible bases. If the base stays fixed and wrong guesses are crossed off, the right one turns up about halfway through on average; if every attempt meets a fresh random base, it takes as many attempts on average as there are bases.
```

> [!analogy] Real-world analogy: two kinds of combination lock
> One three-digit bike lock keeps its code until its owner changes it. Another, imaginary, lock picks a new random code after every wrong try.
>
> **How it maps:** The fixed lock is the forked-worker case: crossing off each wrong code eventually exhausts the list, and on average you are done halfway through. The self-resetting lock is re-randomisation on every attempt: no wrong try teaches you anything, so the average is the full number of codes and there is no guaranteed finish. Learning the code from a note left nearby is an information leak: no guessing at all.
>
> **Where it stops:** Trying a bike lock is silent. A wrong ASLR guess usually crashes a process, which costs the attacker time and gives defenders something to notice. Neither model says how long an attack takes: request rate, restart cost and monitoring decide that.

## Key takeaways
- ASLR changes selected mapping locations according to platform support and policy.
- Without a leak the attacker must guess; fixed placement with distinct guesses differs from rerandomisation on every attempt.
- Entropy counts possible placements under a model; it does not directly measure elapsed attack duration.

## Further reading
- [Linux virtual-memory sysctls](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [fork — POSIX](https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html)
