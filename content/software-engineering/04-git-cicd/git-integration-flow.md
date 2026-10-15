---
id: git-integration-flow
title: Integration risk and GitHub flow
level: intermediate
minutes: 3
sourceLesson: git-workflows
summary: Integration frequency controls how soon incompatible changes are discovered.
---

Git lets you branch any way you like. A **workflow** (or branching strategy) is the team's agreement about which branches exist, how long they live, and how work flows into the code you ship.

There are many named workflows, but they mostly differ on one variable: **how often each developer's work is integrated with everyone else's**. Get that right and the rest is detail.

## Why integration frequency matters

When two people work apart, their changes drift. Longer separation can increase integration work and delay discovery of incompatibilities; there is no universal mathematical growth law:

> [!note] Evidence gap
> No numerical integration-cost growth curve is included: this project has no reproducible evidence establishing a universal relationship between branch age and effort. The risks below are qualitative.


- More lines changed on each side means more textual conflicts.
- Worse, **semantic conflicts** appear: changes that merge cleanly but break each other. One person renames a function's meaning while the other adds a new caller relying on the old meaning. Git cannot detect this; review, static analysis and tests of the combined code may detect it.
- Feedback arrives late. You learn your design clashes with a colleague's after a week of work rather than after an hour.

Martin Fowler calls the dreaded end-of-project phase **integration hell**. The fix is counter-intuitive: if integrating hurts, do it *more often*, so each integration is small.

```
 integrate every 2 weeks:

 dev A  ======================\
                               >> big merge
 dev B  ======================/

 integrate daily:

 dev A  ==\==\==\==\==\==\==\==
 trunk  ---+--+--+--+--+--+--+--
 dev B  ==/==/==/==/==/==/==/==
```

## Key terms

- **Mainline / trunk**: the single branch that represents the current state of the product, usually `main`.
- **Healthy branch**: a branch where every commit builds and passes tests, providing a baseline for further work. Passing tests alone does not establish release readiness.
- **Feature branch**: a branch for one piece of work, merged back when finished.
- **Release branch**: a branch cut to stabilise and maintain a particular release.

## GitHub flow

The simplest common workflow, popularised by GitHub:

1. `main` is always deployable.
2. Create a descriptively named branch from `main` for each change.
3. Push it and open a pull request; CI runs and colleagues review.
4. Merge to `main` once approved and green.
5. Deploy `main` (often automatically, right after merge).

There are no `develop` or long-lived release branches. It suits web services that deploy continuously and only ever run one version in production. Its main risk is feature branches that live too long: GitHub flow does not *force* branches to be short, so teams must keep them short by habit.

## Key takeaways

- Integration frequency controls how soon incompatible changes are discovered.
- A semantic conflict can survive a clean textual merge.
- GitHub flow uses one deployable main branch with reviewed change branches.

## Further reading

- [Patterns for Managing Source Code Branches — Martin Fowler](https://martinfowler.com/articles/branching-patterns.html)
- [GitHub flow — GitHub Docs](https://docs.github.com/en/get-started/using-github/github-flow)
