---
id: sea-adr-incremental-replacement
sourceLesson: sea-adr-evolution
title: Replacing architecture incrementally
level: advanced
minutes: 4
summary: Use strangler fig routing, branch by abstraction and parallel runs to reduce migration risk.
---

With decisions recorded and fitness checks guarding constraints, architecture can change in smaller steps. These techniques preserve feedback and reduce the size of each risky cutover.

### Changing structure incrementally

A long all-at-once rewrite can delay feedback and lose undocumented behavior. Joel Spolsky's essay Things You Should Never Do argues against this approach using Netscape as a cautionary example.

> [!note] Evidence gap
> A universal rewrite failure rate and a precise single-cause Netscape chronology are omitted; an opinion essay is not sufficient evidence for those claims. The alternative is a set of techniques for changing structure in small, safe steps.

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

**Parallel run.** For risky logic like pricing, run old and new implementations side by side, return the old result, and log differences. GitHub's open-source `Scientist` library (Ruby, with ports in other languages) does exactly this. Switch only when relevant differences are understood. Shadow execution must isolate side effects and cap additional load; Scientist evaluates both behaviors but does not inherently run them concurrently.

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
