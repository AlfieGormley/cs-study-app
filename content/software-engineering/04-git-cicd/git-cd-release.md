---
id: git-cd-release
title: CD, release engineering, semantic versioning
level: advanced
minutes: 15
summary: Continuous delivery versus deployment, separating deploy from release, rolling, blue-green and canary rollouts, safe schema changes, rollback strategy, SemVer and its ranges, automated versioning and the DORA metrics.
---

CI tells you a change is probably good. **Continuous delivery** (CD) takes it the rest of the way: every change that passes the pipeline produces something you *could* put in front of users, safely and on demand.

This lesson covers how changes reach production, how to limit the damage when a bad one gets through, and how to communicate change to the people who depend on you: version numbers, tags and release notes.

## Delivery versus deployment

The two terms are easy to mix up:

- **Continuous delivery**: the software is kept in a state where it **can be released to production at any time**. The decision to release may still be a human pressing a button.
- **Continuous deployment**: every change that passes the pipeline **goes to production automatically**, with no human gate.

Continuous deployment requires continuous delivery, but not the reverse. A mobile app team can practise continuous delivery perfectly while app store review stops them deploying continuously.

## Deploy is not release

**Deploying** puts new code on production machines. **Releasing** exposes a behaviour to users. Feature flags let you separate them:

- Deploy on Tuesday with the feature flag off: the gated behavior remains hidden, provided initialization, schema and other deployment changes remain compatible.
- Release on Thursday by turning the flag on for 1% of users, then everyone.
- Turn the flag off to return to the old path without redeploying, if that path is still compatible. Propagation takes time and disabling a flag does not undo data changes or completed side effects.

A **dark launch** goes further: the new code path runs in production on real traffic (for example computing new recommendations) but its result is discarded or only logged, so you can check performance and correctness before anyone sees it.

## The deployment pipeline

```
 commit --> CI: build + unit tests
               |
               v  artefact app:sha-abc123
            acceptance tests
               |
               v
            staging (same artefact)
               |
               v  gate: auto or approval
            production: progressive rollout
               |
               v
            monitor -> continue / roll back
```

Each stage increases confidence and cost. The same artefact moves through every stage; only configuration differs per environment.

## Rollout strategies

| Strategy | How | Rollback |
|---|---|---|
| Recreate | Stop old, start new | Redeploy |
| Rolling | Replace in batches | Roll back batches |
| Blue-green | Switch traffic | Switch back |
| Canary | Small % first | Shift traffic back |

**Recreate** stops old instances before starting new ones and can cause downtime. It can suit any workload whose availability requirements permit that interruption.

**Rolling** replaces instances a few at a time (Kubernetes Deployments do this by default). It needs no spare capacity beyond a small surge, but during the rollout **old and new versions serve traffic simultaneously**, so they must be compatible with each other and with the database.

**Blue-green** runs two full environments. Blue serves traffic; you deploy to green, test it, then switch the router. Rollback is switching back, as long as nothing irreversible (such as a destructive migration) happened. The cost is double capacity during the switch.

**Canary** sends a small share of traffic to the new version and compares it with the old one before expanding:

```
  1%  --10 min-->  check
  5%  --10 min-->  check
 25%  --20 min-->  check
100%
 check: errors, p99 latency, saturation
        canary vs baseline
```

Compare the canary against a **baseline** running the old version at the same scale and time, not against yesterday's numbers; otherwise normal daily variation hides real regressions or triggers false alarms.

> [!example] Is the canary big enough?
> At 2,000 requests per second, a 1% canary sees 20 rps, or 12,000 requests in 10 minutes. If the normal error rate is 0.1%, you expect about 12 errors. A regression that doubles it gives about 24. That is a possible signal, not a guaranteed detection: power depends on the baseline sample, traffic dependence and the chosen test. At 20 rps total, the same canary would see 120 requests and about 0.1 expected errors: it gives little power to detect a modest increase in a rare error rate, though it can reveal a severe regression. Low-traffic services need longer canary stages or synthetic traffic.

## Rolling back versus rolling forward

**Rolling back** (deploying the previous artefact) is usually the fastest way to stop an incident and should be routine and rehearsed. **Rolling forward** (shipping a fix) is tempting but slower under pressure, and a hurried fix may have insufficient validation. Choose the tested recovery path compatible with the current state.

A rollback is only safe if the previous version can still run against the current state. The usual thing that breaks this is the database.

## Database changes: expand and contract

Code rollback can be faster than reversing state changes, but neither its duration nor safe data recovery is guaranteed. And during a rolling deploy, old and new code run at the same time. So schema changes must be **backward compatible** at every step. The standard technique is **expand and contract** (also called **parallel change**).

Renaming `customers.name` to `full_name`:

1. **Expand**: add nullable `full_name`. Old code ignores it.
2. **Dual write**: deploy code that writes both columns and still reads `name`.
3. **Backfill**: after all old-only writers have been replaced, copy `name` into `full_name` in batches using concurrency-safe updates. Verify consistency before switching reads.
4. **Switch reads**: deploy code that reads `full_name` (still writing both).
5. **Stop writing** `name`.
6. **Contract**: after all readers and writers have migrated and the rollback window for old code has closed, drop `name`.

Expansion can preserve rollback compatibility, but stopping old-column writes and dropping the column restrict which versions are safe to restore. Check that contract explicitly at each stage. The cost is several deploys spread over days, which is cheap if deploys are routine.

> [!warning] The one-step rename
> `ALTER TABLE customers RENAME COLUMN name TO full_name` deployed with new code breaks every old instance still running mid-rollout, and makes rolling back the code impossible without another migration.

## Semantic versioning

For anything others depend on (libraries, APIs, CLIs), the version number is a promise. **Semantic Versioning 2.0.0** defines `MAJOR.MINOR.PATCH`:

- **PATCH** (1.4.2 → 1.4.3): backward-compatible bug fixes.
- **MINOR** (1.4.3 → 1.5.0): backward-compatible new functionality, or deprecating something. Patch resets to 0.
- **MAJOR** (1.5.0 → 2.0.0): any backward-incompatible change to the public API. Minor and patch reset to 0.

Further rules worth knowing:

- **0.y.z is for initial development**: anything may change at any time. 1.0.0 defines the public API.
- **Pre-releases** use a hyphen: `2.0.0-rc.1`. A pre-release has **lower** precedence than the release, and identifiers are compared piece by piece, numerically when they are digits:

```
1.0.0-alpha < 1.0.0-alpha.1
 < 1.0.0-alpha.beta < 1.0.0-beta
 < 1.0.0-beta.2 < 1.0.0-beta.11
 < 1.0.0-rc.1 < 1.0.0
```

- **Build metadata** after a plus sign (`1.0.0+20260101`) is **ignored** for precedence.

### Version ranges

Package managers let consumers accept compatible updates automatically. In npm's notation:

| Range | Allows |
|---|---|
| `^1.2.3` | `>=1.2.3 <2.0.0` |
| `^0.2.3` | `>=0.2.3 <0.3.0` |
| `~1.2.3` | `>=1.2.3 <1.3.0` |
| `1.2.3` | Exactly 1.2.3 |

Note the caret is stricter below 1.0: `^0.2.3` does not accept 0.3.0, because in 0.x a minor bump may break things. Ranges also exclude pre-releases by default: `^1.2.3` does not match `1.3.0-beta.1`.

Ranges say what you are *willing* to accept; the **lockfile** records what you actually got, which helps reproduce dependency resolution. Bit-for-bit builds also require controlled toolchains, environment and other inputs.

### What counts as breaking?

More than you might think. Removing a function is obviously breaking. So can be: tightening input validation, changing an error type, changing default behaviour, or dropping support for a runtime version. **Hyrum's Law** warns that with enough users, every observable behaviour of your system will be depended on by somebody. SemVer is a promise about your *documented* API; be conservative and document what is public.

## Calendar versioning

Not everything has an API contract. **CalVer** uses dates: Ubuntu's `24.04` is the April 2024 release. It suits applications and distributions where "how old is this?" matters more than compatibility signalling.

## Automating versions and release notes

**Conventional Commits** gives commit messages a machine-readable prefix:

```
fix(parser): handle empty input
feat(api): add pagination to /orders
feat!: remove deprecated v1 endpoints

BREAKING CHANGE: v1 endpoints removed.
```

`fix` maps to PATCH, `feat` to MINOR, and `!` or a `BREAKING CHANGE:` footer to MAJOR. Configured release tooling derives versions and release notes from commits. semantic-release can publish through plugins; release-please opens release PRs and creates tags and GitHub releases, but package-manager publication requires separate automation.

Useful Git commands for releases:

```
# annotated tag for the release
git tag -a v2.1.0 -m "Release 2.1.0"
git push origin v2.1.0

# what changed since the last release
git log --oneline v2.0.0..HEAD

# a version string for any build
git describe
# v2.1.0-10-gefb7ccd
```

`git describe` gives the nearest annotated tag, the number of commits since it and the abbreviated hash (prefixed `g` for Git). It ignores lightweight tags unless you pass `--tags`, which is one reason to use annotated tags for releases.

> [!tip] Sorting version tags
> `git tag --sort=-v:refname` sorts numerically (1.10.0 above 1.9.0), but by default places `v2.0.0-rc.1` *above* `v2.0.0`. Set `versionsort.suffix=-` to sort pre-release suffixes before the release, matching SemVer.

## Measuring delivery: the DORA metrics

DORA's research groups delivery performance into throughput and instability:

| Metric | Measures |
|---|---|
| Change lead time | Commit to production |
| Deployment frequency | How often you deploy |
| Failed deployment recovery time | Time to recover |
| Change fail rate | Deploys needing fixes |
| Deployment rework rate | Share of deploys caused by production incidents |

DORA's consistent finding is that speed and stability are not a trade-off: teams that deploy small changes often also tend to have lower failure rates and faster recovery. Small batches are one practice associated with good performance; these observations do not establish a single universal cause.

Use the metrics to improve a team, not to rank teams. Once deployment frequency becomes a target, people split deploys meaninglessly.

## Pitfalls

- **Big-bang releases**: weeks of changes deployed at once make every failure hard to diagnose. Ship small.
- **Rollbacks that have never been tested.** Rehearse them; automate the trigger where you can.
- **Irreversible migrations bundled with code.** Separate them with expand and contract.
- **Breaking changes in a minor version.** Your users' `^` ranges will pull it in automatically.
- **Mutable tags.** Never move a release tag after publishing; issue a new version instead.

## Key takeaways
- Continuous delivery means always releasable; continuous deployment means every green change ships automatically.
- Separate deploy from release with flags; roll out progressively with canaries compared against a baseline, and size canaries for statistical signal.
- Old and new versions coexist during rollouts, so schema changes must use expand and contract to stay backward compatible and rollback-safe.
- SemVer encodes compatibility: patch for fixes, minor for compatible features, major for breaking changes; caret and tilde ranges plus lockfiles rely on that promise.
- Automate versions and changelogs from Conventional Commits and annotated tags, and track the DORA metrics to see whether delivery is improving.

## Further reading
- [Continuous Delivery — Martin Fowler](https://martinfowler.com/bliki/ContinuousDelivery.html)
- [Blue-green deployment — Martin Fowler](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Canary release — Danilo Sato on martinfowler.com](https://martinfowler.com/bliki/CanaryRelease.html)
- [Canarying releases — Google SRE Workbook](https://sre.google/workbook/canarying-releases/)
- [Parallel change (expand and contract) — martinfowler.com](https://martinfowler.com/bliki/ParallelChange.html)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [node-semver (range syntax)](https://github.com/npm/node-semver)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [DORA's software delivery metrics](https://dora.dev/guides/dora-metrics/)
