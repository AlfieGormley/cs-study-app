---
id: git-release-automation-metrics
title: Release automation and delivery measurements
level: advanced
minutes: 4
sourceLesson: git-cd-release
summary: Conventional Commits can drive configured versioning and release notes.
---

Version numbers communicate a contract; release automation derives that version from declared changes. Delivery measurements then help a team inspect how reliably changes reach production.

## Automating versions and release notes

**Conventional Commits** gives commit messages a machine-readable prefix:

```
fix(parser): handle empty input
feat(api): add pagination to /orders
feat!: remove deprecated v1 endpoints

BREAKING CHANGE: v1 endpoints removed.
```

`fix` maps to PATCH, `feat` to MINOR, and `!` or a `BREAKING CHANGE:` footer to MAJOR. Configured release tooling derives versions and release notes from commits. semantic-release can publish through plugins; release-please opens release PRs and creates tags and GitHub releases, but package-manager publication requires separate automation.

Useful Git commands for releases. This template assumes an existing release history, `origin` remote and tag-push permission. The `describe` output is illustrative for a commit ten commits after `v2.1.0`; hashes vary and an exact tag prints without the suffix.

```
# Mark the exact commit as a release.
git tag -a v2.1.0 -m "Release 2.1.0"
# Publish only this tag to the remote.
git push origin v2.1.0

# what changed since the last release
git log --oneline v2.0.0..HEAD

# Describe the current commit using a tag.
git describe
# Illustrative: tag, distance, commit ID.
# v2.1.0-10-gefb7ccd
```

`git describe` gives the nearest annotated tag, the number of commits since it and the abbreviated object ID (prefixed `g` for Git). It ignores lightweight tags unless you pass `--tags`, which is one reason to use annotated tags for releases.

> [!tip] Sorting version tags
> `git tag --sort=-v:refname` sorts numerically (1.10.0 above 1.9.0), but by default places `v2.0.0-rc.1` *above* `v2.0.0`. Set `versionsort.suffix=-` to place pre-release suffixes before their corresponding release. This setting does not make every Git tag comparison follow all SemVer version precedence requirements.

## Measuring delivery: the DORA metrics

DORA's research groups delivery performance into DORA throughput metrics and DORA instability metrics:

| Metric | Measures |
|---|---|
| Change lead time | Commit to production |
| Deployment frequency | How often you deploy |
| Failed deployment recovery time | Time to recover |
| Change fail rate | Deploys needing fixes |
| Deployment rework rate | Share of deploys caused by production incidents |

Two of the five are simple ratios, counted over a period such as a month:

```formula
CFR = D_fail / D_total
DRR = D_rework / D_total
CFR = 3 / 40 = 0.075 = 7.5 %
where
CFR: change fail rate, as a fraction or a percentage
DRR: deployment rework rate, as a fraction or a percentage
D_total: the number of deployments to production in the period
D_fail: deployments that needed immediate intervention afterwards, such as a rollback or a hotfix
D_rework: deployments that were not planned and happened only because of an incident in production
%: per cent: parts per hundred
In words: each DORA instability metric is the share of all deployments that went wrong (CFR) or were emergency repairs (DRR).
```

For example, a team that deployed 40 times last month, with 3 deployments needing a rollback, has a change fail rate of 7.5 %. If 2 of the 40 deployments were unplanned hotfixes for production incidents, its deployment rework rate is 2 / 40 = 5 %. The other three metrics are durations or counts: lead time and recovery time are measured in hours or days, deployment frequency in deployments per day or week.

DORA's consistent finding is that speed and stability are not a trade-off: teams that deploy small changes often also tend to have lower failure rates and faster recovery. Small batches are one practice associated with good performance; these observations do not establish a single universal cause.

Use the metrics to improve a team, not to rank teams. Once deployment frequency becomes a target, people split deploys meaninglessly.

## Pitfalls

- **Big-bang releases**: weeks of changes deployed at once make every failure hard to diagnose. Ship small.
- **Rollbacks that have never been tested.** Rehearse them; automate the trigger where you can.
- **Irreversible migrations bundled with code.** Separate them with expand and contract.
- **Breaking changes in a minor version.** Your users' `^` ranges will pull it in automatically.
- **Mutable tags.** Never move a release tag after publishing; issue a new version instead.

## Key takeaways

- Conventional Commits can drive configured versioning and release notes.
- Annotated tags support plain git describe; its suffix records distance and the commit's object ID.
- DORA metrics describe delivery for an application or service; use their context to improve it, not rank individuals.

## Further reading

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [DORA's software delivery metrics](https://dora.dev/guides/dora-metrics/)
