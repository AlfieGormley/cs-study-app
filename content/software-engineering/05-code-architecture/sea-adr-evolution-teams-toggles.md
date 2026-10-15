---
id: sea-adr-evolution-teams-toggles
sourceLesson: sea-adr-evolution
title: Evolving boundaries, teams and toggles
level: advanced
minutes: 4
summary: Relate architecture to domain learning and team structure, and control the configuration cost of old toggles.
---

Incremental replacement depends on the surrounding code and organisation. This unit connects evolutionary design to domain learning, team ownership and the cleanup of migration toggles.

### Other evolutionary ideas

- **Monolith first.** In his 2015 essay, Fowler reported that almost all successful microservice stories he had heard began with monoliths, while many from-scratch stories involved trouble. This is practitioner experience, not a representative success-rate study; because boundaries are hard to get right before you understand the domain. A well-modularised monolith keeps the option open.
- **Sacrificial architecture.** Sometimes the right design for today is one you expect to throw away when you reach 10× scale. Fowler's example is eBay, which moved from Perl to C++ to Java as it grew, as recounted in his essay. Knowing it's temporary changes how much you invest.
- **Conway's law.** "Organizations which design systems are constrained to produce designs which are copies of the communication structures of these organizations." Ownership shared between teams can affect boundaries, but Conway's observation does not deterministically predict that any shared module will blur. The *inverse Conway manoeuvre* shapes teams to match the architecture you want.

## Pitfalls

1. **ADRs written after the fact for show.** If they don't influence decisions, they become stale paperwork. Write them at decision time.
2. **ADR as a design document.** ADRs record a *decision*. Long technical designs belong elsewhere and can be linked.
3. **Fitness functions nobody runs.** A check outside CI is a suggestion.
4. **Evolution as an excuse for no design.** "We'll refactor later" works only if the code is testable and modular enough to refactor, and if later actually comes.
5. **Toggles that never die.** Every independent on/off flag doubles the number of configurations the code could run in (see the formula below); dependencies, and flags that can't both be on, can reduce the reachable combinations. Put a removal date on them.

Each toggle has two states, and independent toggles can be combined freely, so the possible configurations multiply:

```formula
C_max = 2^n
C_max = 2^10 = 1024
where
C_max: the largest possible number of distinct on/off combinations of the toggles, each a separate configuration that could need testing
n: the number of independent feature toggles, each simply on or off; here 10
2^n: n copies of 2 multiplied together
In words: each extra independent toggle doubles the number of possible configurations, so 10 long-lived toggles allow up to 1024.
```

This is an upper bound: toggles that depend on each other, or can't both be on, rule some combinations out. It still shows why old toggles should be deleted rather than left to accumulate.

## Key takeaways
- A modular monolith keeps boundaries movable while the domain is being learned.
- A sacrificial architecture is a conscious temporary investment.
- Conway’s observation motivates aligning team communication with intended ownership.
- Independent on/off flags create exponentially many configurations; remove obsolete toggles.
- Evolution needs testable boundaries and checks that actually run.

## Further reading
- [Monolith First — Martin Fowler](https://martinfowler.com/bliki/MonolithFirst.html)
- [Sacrificial Architecture — Martin Fowler](https://martinfowler.com/bliki/SacrificialArchitecture.html)
- [Conway’s original paper](https://www.melconway.com/Home/Conways_Law.html)
- [Inverse Conway manoeuvre — Thoughtworks](https://www.thoughtworks.com/radar/techniques/inverse-conway-maneuver)
