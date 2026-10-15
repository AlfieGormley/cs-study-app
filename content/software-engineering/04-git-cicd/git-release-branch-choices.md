---
id: git-release-branch-choices
title: Release branches, forks and workflow choices
level: intermediate
minutes: 3
sourceLesson: git-workflows
summary: When a defect affects trunk, fix and test there first, then backport to the maintained release.
---

Trunk-based development can maintain older numbered releases without using them as development branches. This unit follows fixes across that boundary and compares workflow choices.

## Release branches in trunk-based development

Teams that must support a release for a while (mobile apps, versioned products) **cut a release branch from trunk** shortly before release. Fixes are made **on trunk first** and then cherry-picked to the release branch:

This command template assumes both branches exist and the bug affects trunk. Replace `abc123` with the actual tested fix commit.

```
git switch main
# Commit the tested fix; note its ID.
git switch release/2.4
# Copy the fix and record its source ID.
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

- When a defect affects trunk, fix and test there first, then backport to the maintained release.
- Forking controls contribution access independently of the upstream branching model.
- Promote the same tested artefact through environments rather than treating drifting environment branches as proof of equivalence.

## Further reading

- [Patterns for Managing Source Code Branches — Martin Fowler](https://martinfowler.com/articles/branching-patterns.html)
- [Trunk Based Development](https://trunkbaseddevelopment.com/)
- [A successful Git branching model — Vincent Driessen](https://nvie.com/posts/a-successful-git-branching-model/)
