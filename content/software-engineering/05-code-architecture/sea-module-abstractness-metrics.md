---
id: sea-module-abstractness-metrics
sourceLesson: sea-modularity
title: Abstractness and the main sequence
level: advanced
minutes: 5
summary: Read a package's position against Martin's main sequence and interpret what the metric can and can't tell you.
---

The preceding unit measured stability from incoming and outgoing dependencies. The Stable Abstractions Principle adds another question: can a stable package be extended through abstract types rather than changed directly?

### Abstractness and the main sequence

Martin also measures how abstract a package is: the share of its classes that are abstract (interfaces, abstract base classes, and in Python, `Protocol` classes). A package of nothing but interfaces scores 1; a package of only concrete classes scores 0.

```formula reference
A = Na / Nc
where
A: the abstractness of one package, from 0 (no abstract types) to 1 (only abstract types); a ratio of counts, so no unit
Na: the number of abstract classes and interfaces in the package (in Python, abstract base classes and Protocols)
Nc: the total number of classes in the package, abstract and concrete together; the ratio needs at least one class
In words: abstractness is the fraction of a package's classes that are abstract.
```

Martin's ideal is a balance between the two measures. A package that many others depend on (stable) should be mostly abstract, so it can be extended without being edited. A package that nothing depends on (unstable) can be concrete, because changing it hurts nobody. Plot every package on a square with abstractness up one side and instability along the other, and the good packages lie near the diagonal running from "stable and abstract" to "unstable and concrete". Martin calls that line the **main sequence**, and measures how far a package sits from it.

```formula reference
D = |A + I − 1|
where
D: the normalized distance from the main sequence, from 0 (on the ideal line) to 1 (as far from it as possible); no unit
A: the package's abstractness, from 0 (all concrete) to 1 (all abstract)
I: the package's instability, from 0 (maximally stable) to 1 (maximally unstable), as defined in the preceding unit
| |: absolute value: drop any minus sign, so |−0.4| = 0.4
In words: the main sequence is where abstractness plus instability equals 1; the further a package's total is from 1, in either direction, the further it is from Martin's balance.
```

(Martin's 1994 paper gives this as a normalized form; his original distance divides by the square root of 2 to give the true perpendicular distance, at most about 0.707.)

Two examples show the extremes:

- A `core.ports` package holding only two Protocols, imported by the core and the adapters and importing nothing, is fully abstract and fully stable. It sits exactly on the main sequence: the textbook place for ports.
- A concrete `pricing` package with no abstract types, which many packages import and which imports nothing, is fully stable *and* fully concrete. It is as far from the main sequence as a package can be.

Martin's later writing, including his 2017 book *Clean Architecture*, calls that second corner the **zone of pain**: everything depends on the package, and it offers no abstraction to extend instead of editing it. Whether that actually hurts depends on how often the code needs to change. A mature, stable utility that almost never changes does little harm there; a pricing package whose rules change monthly does. The opposite corner, fully abstract with nothing depending on it, is the **zone of uselessness**: abstractions that nobody uses.

These numbers are prompts for a conversation, not targets to optimise. A tool can report them for every package, but adding interfaces just to move a number is the wrong lesson; the useful question is whether the packages that everyone depends on are the ones that keep changing.

## Key takeaways
- Abstractness is the share of classes that are abstract.
- The main sequence balances abstractness with instability.
- Normalized distance measures deviation from that line rather than software quality directly.
- Stable concrete code that rarely changes may be harmless despite a high distance.

## Further reading
- [OO Design Quality Metrics — Robert C. Martin](https://condor.depaul.edu/dmumaugh/OOT/Design-Principles/oodmetrc.pdf)
