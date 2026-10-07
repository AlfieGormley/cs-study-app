---
id: git-ci-pipelines
title: CI pipelines
level: intermediate
minutes: 14
summary: Continuous integration as a practice, how to structure a fast pipeline, testing the merged result with merge queues, flaky tests, build-once artefacts and securing the pipeline itself.
---

**Continuous integration** (CI) is often confused with "having a CI server". The tool is the easy part. CI is a **practice**: everyone integrates their work into the mainline frequently, at least daily, and every integration is verified by an automated build and test run. When the build breaks, fixing it is the team's top priority.

The tooling (GitHub Actions, GitLab CI, Jenkins, Buildkite, CircleCI) exists to make that practice cheap. A team running a sophisticated pipeline on week-old feature branches is not doing CI in this sense.

## Why CI works

- **Small integrations are cheap.** Problems surface within minutes of the change that caused them, while the author still remembers it.
- **The mainline stays healthy.** If `main` always builds and passes tests, developers have a tested baseline for branching and diagnosis. Release readiness also depends on deployment, compatibility and operational checks.
- **It replaces fear with evidence.** The pipeline supplies repeatable evidence about the behaviors and properties its checks cover; a green run is not proof that nothing breaks.

The cost is discipline: tests must be good enough to trust, and a red build must be fixed (or the change reverted) quickly. A common rule is that if a fix is not obvious within about ten minutes, revert first and investigate afterwards.

## Anatomy of a pipeline

A typical pipeline runs on every push to a pull request and every merge to `main`:

```
 push / PR
    |
    v
 [checkout] -> [restore cache]
    |
    v
 [lint + type check]      ~1 min
    |
    v
 [unit tests]  (parallel) ~3 min
    |
    v
 [build artefact]         ~2 min
    |
    v
 [integration tests]      ~4 min
 [security scans]
    |
    v
 [publish artefact: app:sha-abc123]
```

Two principles shape the order:

1. **Fail fast.** Run the cheapest, most likely-to-fail checks first. A lint error should not wait behind a 20-minute integration suite.
2. **Fan out.** Independent jobs (unit tests, scans, docs build) run in parallel; only true dependencies are sequential.

### A GitHub Actions example

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]
  merge_group:

concurrency:
  group: >-
    ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      matrix:
        py: ["3.12", "3.13"]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.py }}
          cache: pip
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: pytest -q
```

This teaching example uses readable version tags and a moving runner label; production policy should pin reviewed action commits and control tool/dependency versions. requirements.txt must include the test and lint dependencies.

What each part does:

- `on`: run for pull requests, pushes to `main`, and `merge_group` (the event a GitHub merge queue sends, covered below).
- `concurrency` with `cancel-in-progress`: a new push to the same branch cancels the run for the previous push, saving minutes. (Many teams exclude `main` so that every commit on `main` gets a full result.)
- `permissions: contents: read`: the job's `GITHUB_TOKEN` gets read-only access, following least privilege.
- `timeout-minutes`: a hung test fails after 15 minutes instead of the default 360.
- `strategy.matrix`: the job runs once per Python version, in parallel.
- `cache: pip`: restores downloaded packages keyed on dependency files and environment details; pip installation still runs, and speed depends on the cache hit and remaining work.

## Speed is a feature

Extreme Programming's **ten-minute build** is still a good target: fast enough that developers wait for the result rather than context-switching. As pipelines slow down, people stop running them locally, batch changes and ignore results.

Techniques, roughly in order of effort:

1. **Cache dependencies** and build outputs. Key caches on lockfile hashes so they invalidate correctly.
2. **Parallelise and shard.** Split a test suite across machines.
3. **Run only what changed.** Monorepo build tools (Bazel, Nx, Pants, Turborepo) compute which targets are affected by a change and skip the rest.
4. **Push slow tests later.** Run end-to-end suites after merge or on a schedule, not on every push, as long as failures are acted on.

> [!example] Sharding arithmetic
> A suite of 2,400 tests averages 0.5 s each: 1,200 s, or 20 minutes, on one runner. Split across 8 shards it is about 150 s of test time per shard. Add around 60 s of setup per runner and the wall-clock time is roughly 3.5 minutes, at the price of 8 × 210 s = 28 runner-minutes instead of 21. You trade compute for feedback time, usually a good deal.

## The test pyramid

Not all tests cost the same:

```
          /\        end-to-end
         /  \       few, slow, brittle
        /----\
       /      \     integration
      /        \    some
     /----------\
    /            \  unit
   /              \ many, fast, precise
  ------------------
```

Lots of fast unit tests, fewer integration tests, and a thin layer of end-to-end tests. A suite shaped like an ice-cream cone (mostly end-to-end) is slow and flaky, and when it fails it tells you little about *where* the problem is.

## Flaky tests

A **flaky** test passes and fails on the same code. Google reported in 2016 that about **1.5% of all test runs** gave a flaky result, that almost **16% of tests** had some flakiness, and that about **84% of pass-to-fail transitions** they observed involved a flaky test.

That last number is the real damage: many transitions involved tests known to be flaky. This does not establish that most red builds were false positives: intermittent failures can expose real races or other defects. Common causes are timing (`sleep(1)` and hope), test order dependence, shared state, real network calls and unseeded randomness.

What to do:

- **Quarantine**: move a known-flaky test out of the blocking suite, file a ticket and fix it soon.
- **Track flakiness** per test; many CI systems can detect pass-after-retry.
- **Do not blindly retry.** Automatic retries hide real race conditions, which then ship to production.

## Testing what will actually be merged

What PR CI tests depends on the trigger and checkout ref. But the thing that matters is **`main` after the merge**. GitHub's `pull_request` event helps by checking out a temporary merge commit (branch merged into the current base), not just the branch tip.

There is still a race:

```
 main at M
 PR A: green against M
 PR B: green against M
 merge A -> main = M+A
 merge B -> main = M+A+B   never tested!
```

If A renamed a function that B calls, `main` is now broken even though both PRs were green. Two fixes:

- **Require branches to be up to date** before merging. Correct, but it serialises merging: each PR must update by merge or rebase and rerun CI after every other merge. It does not scale to busy repositories.
- **A merge queue** (GitHub merge queue, GitLab merge trains, Zuul, bors). Approved PRs join a queue. The queue builds a temporary branch of `main` plus the PRs ahead of it plus this PR (GitHub names these `gh-readonly-queue/...`) and runs the required checks. If they pass, the PR merges; if not, it is removed and the queue rebuilds without it. Queues can test several candidates in parallel, so throughput stays high.

## Build once, deploy many

The pipeline should produce **one immutable artefact per commit** (a container image, wheel or binary), associated with the source revision and identified by an immutable digest, and every later stage should deploy that exact artifact. A SHA-shaped image tag is still mutable unless registry policy prevents replacement. Rebuilding for staging and again for production means production runs something that was never tested.

Supporting practices:

- **Pin dependencies** with lockfiles, so a build next month gets the same versions.
- **Hermetic builds**: the build depends only on declared inputs, not on whatever happens to be installed on the runner. Bazel is built around this idea.
- **Reproducible builds**: the same specified source, build instructions and environment reproduce bit-for-bit identical designated artifacts. Independent reproduction supports provenance checks; source alone does not specify all build inputs.

## Securing the pipeline

CI runners hold secrets (registry tokens, cloud credentials) and can push code. That makes them a prime target.

- **Least privilege.** Set `permissions` explicitly; give deploy credentials only to jobs that deploy, ideally via short-lived OIDC tokens rather than long-lived secrets.
- **Untrusted pull requests.** Fork pull_request workflows normally receive restricted tokens and no repository secrets, but runner isolation and repository settings still matter. pull_request_target can access privileged base-repository credentials, subject to explicit permissions and event policy. Executing untrusted PR code or injecting untrusted input into its commands can expose those credentials; merely using the trusted workflow file does not make it safe.
- **Pin third-party actions to a full commit SHA.** Tags can be moved. In March 2025 attackers modified the version tags of the popular `tj-actions/changed-files` action to point at a malicious commit that dumped CI secrets into workflow logs; pins to reviewed unaffected commits resisted that tag-repointing attack. A pin to malicious code, or an action that dynamically downloads unpinned code, is still unsafe.
- **Caches are readable by PRs.** Never put secrets in cached paths.
- **Provenance.** Frameworks such as **SLSA** describe levels of build integrity, including signed provenance stating which source and build produced an artefact.

## Pitfalls

- **Normalising red.** If `main` is broken for hours and people keep merging, you have lost CI. Stop and fix, or revert.
- **"Retry until green".** It hides flaky tests and real races.
- **Pipelines only one person understands.** Keep pipeline config in the repository, reviewed like code.
- **CI that differs from local.** Use the same commands (a `Makefile`, `tox`, `nox` or task runner) locally and in CI.

## Key takeaways
- CI is a practice: integrate to mainline at least daily, verify each integration automatically, and fix a broken build immediately.
- Order pipelines to fail fast, run independent jobs in parallel, and aim for about ten minutes using caching, sharding and affected-target builds.
- Flaky tests erode trust in red builds; quarantine and fix them instead of retrying.
- Green PRs can still break `main` together; merge queues test the actual merge result at scale.
- Build one artifact per intended build configuration, identify it by digest, and promote it; secure the pipeline with least privilege, SHA-pinned actions and care around untrusted PRs.

## Further reading
- [Continuous Integration — Martin Fowler](https://martinfowler.com/articles/continuousIntegration.html)
- [The Practical Test Pyramid — Ham Vocke](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Flaky Tests at Google and How We Mitigate Them](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)
- [Managing a merge queue — GitHub Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue)
- [Secure use reference — GitHub Actions](https://docs.github.com/en/actions/reference/security/secure-use)
- [Securely using pull_request_target — GitHub Docs](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)
- [tj-actions/changed-files compromise — GitHub Advisory](https://github.com/advisories/GHSA-mrrh-fwg8-r2c3)
- [SLSA: Supply-chain Levels for Software Artifacts](https://slsa.dev/)
