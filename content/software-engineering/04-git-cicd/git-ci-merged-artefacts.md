---
id: git-ci-merged-artefacts
title: Test the merge and promote the artefact
level: intermediate
minutes: 3
sourceLesson: git-ci-pipelines
summary: Two green PRs can fail together if nobody tests their combined result.
---

Fast, reliable tests still need to examine the right code. This unit covers concurrent merges and the identity of the built output that later reaches production.

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

- **Require branches to be up to date** before merging. With strict checks on independent PRs this can force one-at-a-time integration: each PR must update by merge or rebase and rerun CI after every other merge. It does not scale to busy repositories.
- **A merge queue** (GitHub merge queue, GitLab merge trains, Zuul, bors). Approved PRs join a queue. The queue builds a temporary branch of `main` plus the PRs ahead of it plus this PR (GitHub names these `gh-readonly-queue/...`) and runs the required checks. If they pass, the PR merges; if not, it is removed and the queue rebuilds without it. Queues can test several candidates in parallel, so throughput stays high.

## Build once, deploy many

The pipeline should produce **one immutable artefact per intended build configuration of a commit** (a container image, Python wheel or binary), associated with the source revision and identified by an immutable digest, and every later stage should deploy that exact artifact. A SHA-shaped image tag is still mutable unless registry policy prevents replacement. Rebuilding for staging and again for production means production runs something that was never tested.

Supporting practices:

- **Pin dependencies** with lockfiles, so a build next month gets the same versions.
- **Hermetic builds**: the build depends only on declared inputs, not on whatever happens to be installed on the runner. Bazel is built around this idea.
- **Reproducible builds**: the same specified source, build instructions and environment reproduce bit-for-bit identical designated artifacts. Independent reproduction supports provenance checks; source alone does not specify all build inputs.

## Key takeaways

- Two green PRs can fail together if nobody tests their combined result.
- A merge queue tests integration candidates and can speculate ahead when resources permit.
- Promote the same digest-identified build through environments; lockfiles alone do not establish reproducibility.

## Further reading

- [Managing a merge queue — GitHub Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue)
