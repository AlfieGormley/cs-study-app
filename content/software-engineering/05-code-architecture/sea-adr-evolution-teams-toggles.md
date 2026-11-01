---
id: sea-adr-evolution-teams-toggles
sourceLesson: sea-adr-evolution
title: Evolving boundaries, teams and toggles
level: advanced
minutes: 5
summary: Relate architecture to domain learning and team structure, and control the configuration cost of old toggles.
---

Incremental replacement depends on the surrounding code and organisation. This unit connects evolutionary design to domain learning, team ownership and the cleanup of migration toggles.

### Other evolutionary ideas

- **Monolith first.** In his 2015 essay, Fowler reported a pattern in the stories he had heard: almost all successful microservice systems started as a monolith that grew too big and was broken up, while almost all built as microservices from scratch ended up in serious trouble. That is practitioner experience, not a representative study, and it is contested: in a companion article on Fowler's site, Stefan Tilkov argued that when the goal is microservices, starting with a monolith can make clean separation harder. Fowler's explanation is that service boundaries are hard to get right before you understand the domain. A well-modularised monolith keeps the option open.
- **Sacrificial architecture.** Sometimes the right design for today is one you expect to throw away when you reach 10× scale. Fowler's example is eBay, which moved from Perl to C++ to Java as it grew, as recounted in his essay. Knowing it's temporary changes how much you invest.
- **Conway's law.** "Organizations which design systems are constrained to produce designs which are copies of the communication structures of these organizations." (Conway, 1968.) It describes a strong tendency rather than a mechanical rule: boundaries tend to form where teams find it hard to talk. The *inverse Conway manoeuvre* uses this deliberately, shaping teams to match the architecture you want.

## Pitfalls

1. **ADRs written after the fact for show.** If they don't influence decisions, they become stale paperwork. Write them at decision time.
2. **ADR as a design document.** ADRs record a *decision*. Long technical designs belong elsewhere and can be linked.
3. **Fitness functions nobody runs.** A check outside CI is a suggestion.
4. **Evolution as an excuse for no design.** "We'll refactor later" works only if the code is testable and modular enough to refactor, and if later actually comes.
5. **Toggles that never die.** Each independent on/off flag doubles the number of configurations the code could run in, so ten long-lived toggles allow up to 1,024 combinations, far more than anyone tests. Toggles that depend on each other, or can't both be on, rule some combinations out, but the growth is still why old toggles should be deleted. Put a removal date on them.

```formula reference
C_max = 2^n
where
C_max: the largest possible number of distinct on/off combinations of the toggles, each a separate configuration that could need testing
n: the number of independent feature toggles, each simply on or off
2^n: n copies of 2 multiplied together
In words: each extra independent on/off toggle doubles the number of possible configurations, so the count grows exponentially with the number of toggles.
```

## Key takeaways
- A modular monolith keeps boundaries movable while the domain is being learned.
- A sacrificial architecture is a conscious temporary investment.
- Conway’s observation motivates aligning team communication with intended ownership.
- Independent on/off flags create exponentially many configurations; remove obsolete toggles.
- Evolution needs testable boundaries and checks that actually run.

## Further reading
- [Monolith First — Martin Fowler](https://martinfowler.com/bliki/MonolithFirst.html)
- [Don't start with a monolith — Stefan Tilkov](https://martinfowler.com/articles/dont-start-monolith.html)
- [Sacrificial Architecture — Martin Fowler](https://martinfowler.com/bliki/SacrificialArchitecture.html)
- [Conway’s original paper](https://www.melconway.com/Home/Conways_Law.html)
- [Inverse Conway manoeuvre — Thoughtworks](https://www.thoughtworks.com/radar/techniques/inverse-conway-maneuver)
