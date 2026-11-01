---
id: sea-adr-incremental-replacement
sourceLesson: sea-adr-evolution
title: Replacing architecture incrementally
level: advanced
minutes: 5
summary: Use strangler fig routing, branch by abstraction and parallel runs to reduce migration risk.
---

With decisions recorded and fitness checks guarding constraints, architecture can change in smaller steps. These techniques preserve feedback and reduce the size of each risky cutover.

### Changing structure incrementally

A long all-at-once rewrite delays feedback and risks losing behaviour that only the old code remembers. Joel Spolsky's 2000 essay *Things You Should Never Do* famously called rewriting from scratch "the single worst strategic mistake" a software company can make, using Netscape as his example. It is an influential practitioner's argument rather than a measured study, and some rewrites do succeed, but it explains why teams prefer techniques that change structure in small, safe steps.

> [!analogy] Real-world analogy: renovating while you live in the house
> A family renovates one room at a time. While the kitchen is being redone, they cook on a camping stove in the dining room; when the new kitchen works, the stove goes. The house stays lived-in throughout, and if the budget runs out halfway, they still have a working home.
>
> **How it maps:** Each room is one capability of the system. The camping stove is a temporary seam, like a routing facade or an abstraction, that keeps things working during the change. Removing it at the end is deleting the old implementation and its toggle.
>
> **Where it stops:** Rooms are physically separate. In software, two capabilities often share data, so moving one may need a data migration that is much harder to undo than taking a stove away.

**Strangler fig.** Named by Martin Fowler after vines that grow around a host tree until they replace it. Put a routing layer in front of the old code; move one capability at a time to the new implementation; route to it; delete the old part. The aim is to keep the system serving throughout, but each cutover still needs compatible data, operational checks and a recovery plan.

```
 step 1           step 2          step 3
 +-------+        +-------+       +-------+
 | facade|        | facade|       | facade|
 +---+---+        +-+---+-+       +---+---+
     |              |   |             |
   [old]         [old] [new]        [new]
```

**Branch by abstraction.** For replacing a component used throughout the code (an ORM, a payment provider) without a long-lived feature branch:

1. Introduce an abstraction (a port) over the existing component.
2. Move all callers onto the abstraction.
3. Build the new implementation behind the same abstraction.
4. Switch over, often with a feature toggle, a slice of traffic at a time.
5. Delete the old implementation, and the toggle.

Every step is a small commit on the main branch, so you avoid a months-long merge.

**Parallel run.** For risky logic like pricing, run old and new implementations on the same input, return the old result, and log differences. GitHub's open-source `Scientist` library (Ruby, with ports in other languages) does exactly this; it runs the two one after the other, in random order. Switch only when the differences are understood. The new code must not cause side effects of its own (no second charge or email), and running both costs extra load.

## Key takeaways
- Strangler fig replaces capabilities gradually behind a routing facade.
- Branch by abstraction moves callers onto a seam while implementations change in small main-branch commits.
- Parallel runs compare results before serving the replacement.
- Shadow execution needs isolated side effects and controlled load.
- Incremental cutovers still require compatible data, monitoring and recovery.

## Further reading
- [Strangler Fig Application — Martin Fowler](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Branch By Abstraction — Martin Fowler](https://martinfowler.com/bliki/BranchByAbstraction.html)
- [Scientist — GitHub](https://github.com/github/scientist)
- [Things You Should Never Do — Joel Spolsky](https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/)
