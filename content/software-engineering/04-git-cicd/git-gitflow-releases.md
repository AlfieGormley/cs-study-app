---
id: git-gitflow-releases
title: GitFlow and maintaining numbered releases
level: intermediate
minutes: 3
sourceLesson: git-workflows
summary: GitFlow keeps released code on main and ongoing integration on develop.
---

GitHub flow keeps a deployable main branch. GitFlow instead separates released history from ongoing integration, with explicit branches for stabilisation and urgent fixes.

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

A hotfix, in commands. This template assumes existing `main`, `develop` and `v1.0` references; the comment marks where the actual fix and commit must be made.

```
git switch -c hotfix/1.0.1 v1.0
# Commit a tested fix on released code.
git switch main
git merge --no-ff hotfix/1.0.1
git tag -a v1.0.1 -m "Hotfix 1.0.1"

# Carry the fix into future releases too.
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

## Key takeaways

- GitFlow keeps released code on main and ongoing integration on develop.
- Hotfixes must reach both release history and future development.
- The model adds coordination cost; its author recommends simpler flows for continuously delivered web applications.

## Further reading

- [A successful Git branching model — Vincent Driessen](https://nvie.com/posts/a-successful-git-branching-model/)
