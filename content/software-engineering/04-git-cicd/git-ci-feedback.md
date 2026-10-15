---
id: git-ci-feedback
title: Continuous integration and pipeline structure
level: intermediate
minutes: 4
sourceLesson: git-ci-pipelines
summary: CI is frequent integration verified by automated checks, together with prompt repair of failures.
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
2. **Run independent jobs in parallel.** Independent jobs (unit tests, scans, docs build) run in parallel; only true dependencies are sequential.

### A GitHub Actions example

This workflow is a configuration template for a Python repository with `requirements.txt`, tests and Ruff configuration. It requires GitHub-hosted execution; it does not show a measured run or guarantee these durations.

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
  # Cancel superseded checks in this group.
  cancel-in-progress: true

# Limit the built-in token's permissions.
permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      # One job per Python version.
      matrix:
        py: ["3.12", "3.13"]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.py }}
          cache: pip
      # Install even after cache restore.
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
- `cache: pip`: restores downloaded packages keyed on dependency files and environment details; pip installation still runs, and speed depends on whether a useful dependency cache entry was restored and on the remaining work.

## Key takeaways

- CI is frequent integration verified by automated checks, together with prompt repair of failures.
- Order cheap likely failures early and parallelise independent jobs.
- The workflow example supplies trigger, permission, cancellation, timeout and Python-version controls; tags remain mutable.

## Further reading

- [Continuous Integration — Martin Fowler](https://martinfowler.com/articles/continuousIntegration.html)
- [Secure use reference — GitHub Actions](https://docs.github.com/en/actions/reference/security/secure-use)
