---
id: git-ranges-undo
title: Reading ranges and undoing shared changes
level: intermediate
minutes: 3
sourceLesson: git-merge-rebase
summary: Log ranges select reachable commits; diff ranges compare snapshots.
---

After choosing how to integrate history, you need to inspect which commits and file changes differ, and undo mistakes without confusing ancestry with file contents.

## Pull is fetch plus integrate

`git pull` is `git fetch` followed by a merge or a rebase. If your branch and the remote have both moved, recent Git versions refuse with "Need to specify how to reconcile divergent branches" until you choose: `pull.rebase true`, `pull.rebase false` (merge) or `pull.ff only`. Many teams set `pull.rebase true` so routine pulls do not create "Merge branch 'main' of ..." noise.

## Reading ranges: two dots and three dots

| Command | Means |
|---|---|
| `git log A..B` | On B, not on A |
| `git log A...B` | On either, not both |
| `git diff A..B` | Tip A vs tip B |
| `git diff A...B` | Base vs tip B |

`git diff main...feat` compares a merge base with `feat`, as GitHub's PR comparison does. The merge base can advance after integrations; it need not be the original branch point.

## Undoing things

| Mistake | Fix |
|---|---|
| Bad local merge/rebase | Inspect ORIG_HEAD/reflog, preserve current work, then choose a recovery commit |
| Lost local committed history | Inspect git reflog and create a rescue branch at a retained commit |
| Pushed bad commit | `git revert <sha>` |
| Pushed bad merge | `git revert -m 1 <merge>` |

A hard reset discards tracked working-tree and staged changes, so it is not a general undo operation. Reflogs record ref changes, not every edit.

Reverting a merge commit needs `-m <parent-number>` to select the mainline parent; it is parent 1 for the merge shown here. There is a catch: once a merge is reverted, merging the same branch again brings in only *newer* commits, because the old ones are already ancestors. To bring the reverted work back, revert the revert.

## Merge or rebase?

| | Merge | Rebase |
|---|---|---|
| History | Original ancestry retained | Replayed ancestry; normally linear |
| Hashes | Preserved | Rewritten |
| Conflicts | Once | Per commit |
| Safe if shared | Yes | No |

A widely used compromise: **rebase your private branch** onto `main` to keep it current and tidy, then integrate it via a merge commit or squash merge on the platform. You get readable history without rewriting anything other people depend on.

## Key takeaways

- Log ranges select reachable commits; diff ranges compare snapshots.
- Revert records a new inverse change, while reset moves refs and can discard local edits.
- Reverting a merge leaves its ancestry in place, so a later merge brings only newer work.

## Further reading

- [git-rebase documentation](https://git-scm.com/docs/git-rebase)
- [git-merge documentation](https://git-scm.com/docs/git-merge)
- [gitrevisions: specifying ranges](https://git-scm.com/docs/gitrevisions)
