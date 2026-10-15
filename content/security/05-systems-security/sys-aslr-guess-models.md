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

How much it helps depends on **entropy**, the number of random bits. Each independent, uniformly random bit doubles the number of places a mapping can start:

```formula
N = 2^b
N = 2^8 = 256
N = 2^28 = 268,435,456
where
N: the number of equally likely positions (base addresses) the mapping can have
b: the bits of entropy: how many independent, uniformly random bits choose the position; 8 and 28 here
2^b: b copies of 2 multiplied together
In words: with 8 random bits a mapping has 256 possible positions; with 28 bits it has over 268 million.
```

These are teaching examples, not asserted Linux defaults. Architecture, kernel settings and distribution policy affect actual entropy. On supported Linux systems, `vm.mmap_rnd_bits` controls randomisation for relevant mappings.

An attacker without a leak must guess, and the average number of attempts depends on whether the base changes between attempts. If it stays fixed (forked workers inherit it, as above) and each wrong guess is ruled out, the right base is equally likely to be first, second and so on up to last:

```formula
E_fixed = (N + 1) / 2
E_fixed = (256 + 1) / 2 = 128.5
where
E_fixed: the expected (average) number of attempts until the right base is found, when the base stays fixed
N: the number of equally likely bases; 256 for 8 bits
1: added because the right base's position runs from 1 to N, and the average of 1, 2, …, N is (1 + N) / 2
In words: trying each of N possible fixed bases once finds the answer, on average, about halfway through the list.
```

If instead every attempt meets a freshly randomised base (for example, each attempt runs a newly executed process), no attempt rules anything out. Each try is a new 1-in-N chance, and the average number of tries is N:

```formula
p = 1 / N
E_new = 1 / p = N
E_new = 256
where
p: the chance that one attempt succeeds
N: the number of equally likely bases; 256 for 8 bits
E_new: the expected number of attempts when the base is re-randomised every time; this is the mean of a geometric distribution, which counts tries up to the first success
In words: with a fresh 1-in-256 chance each time, success takes 256 attempts on average.
```

With 28 bits the fixed-base model gives about 134 million attempts on average (268,435,457 / 2). Neither model says how long an attack takes: request rate, restart cost and monitoring decide that.

## Key takeaways
- ASLR changes selected mapping locations according to platform support and policy.
- Fixed unknown placement with distinct guesses differs from independent rerandomisation on every attempt.
- Entropy counts possible placements under a model; it does not directly measure elapsed attack duration.

## Further reading
- [Linux virtual-memory sysctls](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [fork — POSIX](https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html)
