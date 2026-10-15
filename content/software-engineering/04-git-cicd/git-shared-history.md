---
id: git-shared-history
title: Shared history, force leases and squash merges
level: intermediate
minutes: 5
sourceLesson: git-merge-rebase
summary: Rewriting commits colleagues use makes their ancestry diverge.
---

Rebase can tidy private commits, but replacing published ancestry affects everyone using it. This unit covers that coordination boundary, force-update checks, and alternatives for integrating or copying changes.

## The golden rule of rebasing

> [!warning] Don't rebase commits other people have built on
> Rebasing replaces commits with new ones. If a colleague has pulled your old commits and built on them, their history and yours now diverge, with duplicated changes under different hashes. Rebase freely on private branches; do not rewrite `main` or a shared branch.

Rewriting your own pushed feature branch (for example, after review) is common and fine, but it needs a force-push, which brings its own hazard.

## Force-pushing safely

After rewriting a pushed branch, a normal `git push` is rejected as a non-fast-forward. If server policy permits it, `git push --force` can replace the remote branch tip and remove a teammate's commits from that branch's ancestry. Those objects may still be retained elsewhere.

`git push --force-with-lease` is safer: it only overwrites the remote if the remote branch is still where your remote-tracking ref (`origin/feat`) says it is. If someone pushed since your last fetch, you get `! [rejected] (stale info)`.

There is a subtle trap. If you (or your editor, in the background) run `git fetch`, your `origin/feat` is updated to include the teammate's commit, and the lease passes, so their work is overwritten anyway. Adding `--force-if-includes` (Git 2.30+) closes that gap: it checks whether the remote-tracking tip is reachable from an entry in the local branch reflog used for the rewrite. This prevents the illustrated unseen-update overwrite; it does not prove the rewritten code preserved every remote change.

This assumes an upstream-configured feature branch and permission to rewrite it. These checks limit particular overwrites; they do not review the replacement code.

```
# Check the lease and local inclusion.
git push --force-with-lease \
         --force-if-includes
```

## Squash merges

Platforms such as GitHub and GitLab offer **squash and merge**: all the branch's changes become a single new commit on `main`, with one parent. Locally it is `git merge --squash feat` followed by `git commit`.

- History on `main` is linear with one commit per pull request, which is easy to read, bisect and revert.
- The branch's individual commits are not ancestors of `main`. git branch -d feat may refuse if checking against main; if feat has an upstream it checks that upstream instead, and continuing to work on the same branch afterwards produces confusing repeated conflicts.

### Why linear history helps bisect

**`git bisect`** finds the commit that introduced a bug by binary search. You mark one commit as good (bug absent) and a later one as bad (bug present). Git checks out a commit halfway between them; you test it and answer `git bisect good` or `git bisect bad`, and the suspect range halves. Because the range halves every time, the number of tests grows only with the logarithm of the number of commits:

```formula
s ≈ ⌈log_2(n)⌉
s ≈ ⌈log_2(1000)⌉ = ⌈9.97⌉ = 10
where
s: roughly how many commits you must test before git bisect names the first bad commit
n: the number of candidate commits between the known-good and known-bad commits
log_2: the base-2 logarithm: how many times you halve a number to get down to 1 (log_2(8) = 3, because 8 → 4 → 2 → 1)
⌈ ⌉: the ceiling: round up to the next whole number, because you cannot run part of a test
≈: approximately equal to; Git's own "roughly N steps" message counts only the tests still left after the one it has just checked out, so for 1,000 commits it first says roughly 9
In words: each test halves the suspects, so doubling the number of commits adds only about one more test.
```

So 1,000 commits take about 10 tests and 1,000,000 take about 20. The estimate assumes every commit can be built and tested: a commit that does not build has to be skipped (`git bisect skip`), which costs extra steps. With squash merges each candidate is one whole, reviewed pull request, so bisect lands on a meaningful unit; merge-heavy history works too, but bisect may test side-branch commits that never ran CI.

## Cherry-pick

`git cherry-pick <sha>` applies one commit's change on top of the current branch as a new commit. It is mostly used to backport a fix to a release branch. Use `-x` to append "(cherry picked from commit ...)" to the message so the link is traceable.

## Key takeaways

- Rewriting commits colleagues use makes their ancestry diverge.
- An implicit force lease can be weakened by a background fetch; --force-if-includes adds a reflog-based check.
- Squash merges record one combined commit without preserving the feature commits as ancestors.
- Bisect needs buildable, testable candidate commits; cherry-pick copies a change for a backport.

## Further reading

- [git-rebase documentation](https://git-scm.com/docs/git-rebase)
- [git-push documentation (force-with-lease)](https://git-scm.com/docs/git-push)
