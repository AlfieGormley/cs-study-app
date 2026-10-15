---
id: sea-module-abstractness-metrics
sourceLesson: sea-modularity
title: Abstractness and the main sequence
level: advanced
minutes: 5
summary: Compare a package’s abstractness with instability and interpret the metric’s limits.
---

The preceding unit defined instability from incoming and outgoing dependencies. Stable Abstractions adds another question: can a stable package be extended through abstract types rather than changed directly?

### Abstractness and the main sequence

Martin also measures how abstract a package is, so the two principles can be checked together:

```formula
A = Na / Nc
where
A: the abstractness of one package, from 0 (no abstract types) to 1 (only abstract types); a ratio of counts, so no unit
Na: the number of abstract classes and interfaces in the package (in Python, abstract base classes and Protocols)
Nc: the total number of classes in the package, abstract and concrete together
In words: abstractness is the fraction of a package's classes that are abstract.
```

This ratio requires at least one class. With no classes, abstractness is undefined unless a tool supplies a convention. The normalized distance below also requires defined abstractness and instability, so an empty or completely isolated package needs explicit tool conventions.

Martin's ideal is that a package's abstractness and instability add up to 1: stable packages fully abstract, unstable packages fully concrete, or a balance in between. He calls the line where they add up to 1 the **main sequence**, and measures how far a package sits from it. (His original distance divided this by the square root of 2 to give the true perpendicular distance, at most about 0.707; the simpler form below, which he also gives, runs from 0 to 1.)

```formula
D = |A + I − 1|
where
D: the distance from the main sequence, from 0 (on the ideal line) to 1 (as far from it as possible); no unit
A: the package's abstractness, from 0 to 1, the number of abstract classes and interfaces divided by all classes in this package
I: the package's instability, from 0 to 1, as defined in the preceding unit; outgoing dependencies divided by all incoming and outgoing dependencies
| |: absolute value: drop any minus sign, so |−0.4| = 0.4
In words: add abstractness and instability; the further the total is from 1, in either direction, the more the package breaks the stable-abstractions guideline.
```

First example: a `core.ports` package holds two Protocols and nothing else. The core and the adapters import it. Count only dependencies between these application packages; standard-library imports such as typing are excluded from this worked example.

```formula
A = Na / Nc = 2 / 2 = 1
I = Ce / (Ca + Ce) = 0 / (2 + 0) = 0
D = |A + I − 1| = |1 + 0 − 1| = 0
where
A: abstractness: both of its 2 classes are abstract
Na: abstract classes and interfaces: 2
Nc: all classes in the package: 2
I: instability, from 0 to 1
Ce: packages it imports: none, so 0
Ca: packages importing it: the core and the adapters, counted here as 2
D: distance from the main sequence, from 0 to 1
| |: absolute value: drop any minus sign
In words: the ports package is fully abstract and fully stable, so it sits exactly on the main sequence.
```

Second example: a concrete `pricing` package with no abstract types, which many packages import and which imports nothing.

```formula
A = 0
I = 0
D = |0 + 0 − 1| = 1
where
A: abstractness: no abstract types, so 0
I: instability: nothing imported, so 0
D: distance from the main sequence, from 0 to 1
| |: absolute value: drop any minus sign
In words: a stable but fully concrete package is as far from the main sequence as possible.
```

Martin calls this corner the **zone of pain**: everything depends on the package, and it offers no abstraction to extend instead of edit. Stable concrete code that almost never needs to change, such as a standard string library, is harmless there. The opposite corner, fully abstract and fully unstable, is the **zone of uselessness**: abstract types with no incoming dependents; the metric alone does not establish whether implementations exist. These numbers are prompts for a conversation, not targets to optimise.

## Key takeaways
- Abstractness is the share of classes that are abstract.
- The main sequence balances abstractness with instability.
- Normalized distance measures deviation from that line rather than software quality directly.
- Stable concrete code that rarely changes may be harmless despite a high distance.

## Further reading
- [OO Design Quality Metrics — Robert C. Martin](https://condor.depaul.edu/dmumaugh/OOT/Design-Principles/oodmetrc.pdf)
