---
id: git-workflows
title: Workflows (trunk-based, GitFlow)
level: intermediate
minutes: 13
summary: Why integration frequency is the variable that matters, how GitHub flow, GitFlow and trunk-based development work, release branches and backports, and how to choose.
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

## GitFlow

Vincent Driessen's 2010 model, often called **git-flow**, uses two permanent branches plus three kinds of temporary ones:

| Branch | Purpose | Merges into |
|---|---|---|
| `main` | Released code only | — |
| `develop` | Integration | — |
| `feature/*` | New work | `develop` |
| `release/*` | Stabilise | `main`, `develop` |
| `hotfix/*` | Urgent prod fix | `main`, `develop` |

```
 from          branch        into
 ----          ------        ----
 develop    -> feature/*  -> develop
 develop    -> release/*  -> main (tag)
                          +  develop
 main       -> hotfix/*   -> main (tag)
                          +  develop
```

A hotfix, in commands:

```
git switch -c hotfix/1.0.1 v1.0
# fix, commit
git switch main
git merge --no-ff hotfix/1.0.1
git tag -a v1.0.1 -m "Hotfix 1.0.1"
git switch develop
git merge --no-ff hotfix/1.0.1
git branch -d hotfix/1.0.1
```

### Where GitFlow fits and where it hurts

GitFlow was designed for software released in discrete, numbered versions, where several versions may be supported at once: desktop apps, libraries, firmware, on-premises products.

Its costs:

- **Two integration points** (`develop` and `main`), with frequent merges in both directions and a real chance of forgetting to merge a hotfix back into `develop`, so the bug reappears in the next release.
- Feature branches tend to be long, which brings back late integration.
- `main` is usually a release *behind* the code being worked on, so "what is in production?" and "what is being tested?" are separate questions.

In 2020 Driessen added a "note of reflection" to the original post: for teams doing continuous delivery of web apps he recommends a much simpler workflow such as GitHub flow, while GitFlow may still suit explicitly versioned software or multiple supported versions.

## Trunk-based development

In **trunk-based development** (TBD), everyone integrates into one trunk at least daily. There are two styles:

- **Commit straight to trunk**: common in small teams with strong tests and pairing.
- **Short-lived feature branches**: a branch lives hours to a day or two, is reviewed in a small pull request, and merged. This is the usual style in companies that require review.

The rule is not "no branches"; it is "no long-lived development branches apart from trunk; maintained release branches are a separate case".

DORA's research (from its 2016 and 2017 data) found that teams with higher delivery performance tended to have **three or fewer active branches**, **merge into trunk at least daily**, and have **no code freezes or integration phases**.

### Shipping unfinished work safely

If you merge daily, half-built features reach trunk. Two techniques keep that safe:

**Feature flags.** New code paths ship switched off and are enabled when ready, possibly for a percentage of users first.

```python
def checkout(cart, user):
    if flags.enabled("new_pricing", user):
        total = new_pricing(cart)
    else:
        total = legacy_pricing(cart)
    return charge(user, total)
```

**Branch by abstraction.** To replace a large component (say, an ORM), introduce an interface in front of it, move callers onto the interface, build the new implementation behind it step by step, switch over, then delete the old one. Every step is a small, releasable commit on trunk.

> [!warning] Flags are debt
> n independent Boolean flags permit up to 2^n configurations; constraints and mutually exclusive paths can reduce the reachable behavior combinations. Give each flag an owner and an expiry date, and delete it once the feature is fully launched. Stale flags cause real incidents: The SEC's account of Knight Capital's 2012 incident reports losses exceeding $460 million and describes a repurposed old flag that reactivated dead code on one server.

### Release branches in trunk-based development

Teams that must support a release for a while (mobile apps, versioned products) **cut a release branch from trunk** shortly before release. Fixes are made **on trunk first** and then cherry-picked to the release branch:

```
git switch main
# fix, commit -> abc123
git switch release/2.4
git cherry-pick -x abc123
```

Fixing trunk first avoids forgetting to forward-port that fix. Later edits can still regress the behavior, so retain a regression test. Release branches only receive fixes, never features, and are deleted when that release is no longer supported.

## The forking workflow

Open-source projects cannot give push access to every contributor. Instead each contributor **forks** the repository, pushes branches to their fork, and opens a pull request against the upstream. Maintainers review and merge. The branching inside the upstream can be GitHub flow, trunk-based or anything else; forking is about *access*, not branch structure.

## Comparing the options

| | GitHub flow | GitFlow | Trunk-based |
|---|---|---|---|
| Long-lived | `main` | `main`, `develop` | trunk |
| Branch life | Days | Days–weeks | Hours–1 day |
| Releases | Continuous | Versioned | Either |
| Needs | CI, review | Discipline | CI, flags |

## Choosing a workflow

1. **One version in production, deployed often** (most web services): GitHub flow or trunk-based development with short-lived branches.
2. **Several supported versions** (libraries, mobile apps, on-premises products): trunk-based development with release branches, or GitFlow if you really need a separate integration branch.
3. **Large monorepo, many engineers**: trunk-based development, typically with a merge queue so that `main` stays green while dozens of changes land per hour (covered in the CI lesson).

Whatever you pick, measure branch age. If pull requests regularly stay open for a week, you are living with the costs of late integration whatever the workflow is called.

## Common pitfalls

- **Long-lived "feature" branches** for big projects. Use flags or branch by abstraction instead, and merge small slices.
- **Environment branches** (`dev`, `staging`, `prod`) where code is promoted by merging between branches. Each environment's branch drifts, and you end up deploying a merge result that was never tested. Promote the *same build artefact* through environments instead.
- **Code freezes.** A freeze can reflect weak integration confidence or an explicit operational/business constraint. Improve feedback and release controls rather than treating a longer freeze as a substitute for them.
- **Fixing the release branch only**, then forgetting trunk. Fix trunk first, then backport.

## Key takeaways
- The real variable is integration frequency; small, frequent integrations shorten feedback and can reduce conflict size; they do not eliminate conflicts.
- GitHub flow: one deployable `main`, short branches, PR review, deploy after merge.
- GitFlow suits explicitly versioned software but adds a second integration branch and two-way merges; its author now recommends simpler flows for continuously delivered apps.
- Trunk-based development merges into trunk at least daily, using feature flags and branch by abstraction to hide unfinished work.
- Cut release branches from trunk when you must support versions, and prefer trunk-first fixes when the bug exists there; release-only defects still need appropriate maintenance fixes.

## Further reading
- [Patterns for Managing Source Code Branches — Martin Fowler](https://martinfowler.com/articles/branching-patterns.html)
- [Trunk Based Development](https://trunkbaseddevelopment.com/)
- [Trunk-based development — DORA capabilities](https://dora.dev/capabilities/trunk-based-development/)
- [A successful Git branching model — Vincent Driessen](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub flow — GitHub Docs](https://docs.github.com/en/get-started/using-github/github-flow)
- [Branch by abstraction — Martin Fowler](https://martinfowler.com/bliki/BranchByAbstraction.html)
- [Feature Toggles — Pete Hodgson on martinfowler.com](https://martinfowler.com/articles/feature-toggles.html)
