---
id: git-merge-rebase
title: Branching, merging vs rebasing
level: intermediate
minutes: 14
summary: Fast-forwards, three-way merges and conflicts, rebasing and interactive rebase, squash merges, safe force-pushing, and how to undo each of them.
---

Two people start from the same commit and each make changes. Sooner or later the work has to come back together. Git gives you two fundamentally different ways to do that:

- **Merge**: keep both lines of history as they happened and *join* them with a new commit.
- **Rebase**: *replay* one line of work on top of the other, as if it had been written later.

For straightforward independent changes, both often produce the same final files. This is not guaranteed: rebase replays intermediate commits, may skip already-applied patches and can expose different conflicts. What differs is the **shape of the history** and **which commits exist**. With the object model from the last lesson, each is easy to reason about.

## The merge base

In this simple history there is one **merge base**, the best common ancestor of the two branches (`git merge-base main feat`).

```
          C---D        feat
         /
 A---B---E             main

 merge base of main and feat = B
```

Git compares three snapshots: the base (B), "ours" (E, the branch you are on) and "theirs" (D). That is why it is called a **three-way merge**. Complex histories can have multiple best bases; recursive strategies can combine them into a virtual base. A line changed on only one side takes that side's version. A line changed differently on both sides is a **conflict**.

## Fast-forward merges

If `main` has not moved since `feat` branched off, there is nothing to combine. `main` is an ancestor of `feat`, so Git just moves the `main` pointer forward:

```
$ git merge feat
Updating dd0d6ad..cbdec69
Fast-forward
```

No new commit is created. History stays a straight line, and you can no longer see that a branch ever existed.

`git merge --no-ff feat` forces a merge commit even when a fast-forward is possible. Teams use it to keep a visible record of each feature as a unit.

## Three-way merges and merge commits

When both sides have moved, Git creates a **merge commit** with two parents:

```
          C---D        feat
         /     \
 A---B---E------M      main
```

```
$ git cat-file -p HEAD
tree dc7872...
parent dd0d6ad...
parent cbdec69...
```

Parent order matters. The **first parent** is the branch you were on (`main`); the second is the branch you merged in. `git log --first-parent` follows only first parents, giving a view that skips merged side-branch internals while retaining direct mainline commits of `main` even in a merge-heavy history.

Since Git 2.34 the default two-head merge strategy is **ort** (you will see "Merge made by the 'ort' strategy"), a faster rewrite of the older `recursive` strategy.

## Conflicts

Suppose both branches change `timeout = 30`. `main` sets 45 and `feat` sets 60:

```
<<<<<<< HEAD
timeout = 45
=======
timeout = 60
>>>>>>> feat
```

The default markers do not show what the line was *before*. Turn on `git config merge.conflictStyle zdiff3` (or `diff3`) and you also see the base:

```
<<<<<<< HEAD
timeout = 45
||||||| 21e3099
timeout = 30
=======
timeout = 60
>>>>>>> feat
```

Now you can see that both sides raised the timeout, which is often the context you need to resolve it correctly.

To resolve: edit the file, `git add` it, then `git commit` (or `git merge --continue`). To give up: `git merge --abort`.

> [!tip] Remember resolutions with rerere
> `git config rerere.enabled true` makes Git record how you resolved each conflict. If the same conflict appears again, for example when you redo a rebase, Git prints "Resolved 'cfg.py' using previous resolution" and applies it for you.

## Rebasing

`git rebase main` (run on `feat`) does this:

1. Find the commits on `feat` that are not on `main` (C and D).
2. Check out `main`'s tip (E).
3. Re-apply each commit's change, one at a time, creating **new** commits C' and D'.
4. Move `feat` to point at D'.

```
 before:         C---D        feat
                /
        A---B---E             main

 after:             C'--D'    feat
                   /
        A---B---E             main
```

C' has the same change and message as C but a **different hash**, because its parent is different. The originals can be found via retained reflogs. ORIG_HEAD initially records the old branch tip, but other commands during the rebase can overwrite it.

`main` can now fast-forward to `feat`, giving a perfectly linear history.

### Conflicts during rebase

Each replayed commit can conflict. Git stops, you resolve, `git add`, then `git rebase --continue`. Other options are `--skip` (drop this commit) and `--abort` (go back to how things were).

> [!warning] "Ours" and "theirs" swap during a rebase
> A rebase works by checking out the *upstream* and applying your commits onto it. So during a rebase of `feat` onto `main`, `git checkout --ours` gives you the upstream side **including commits already replayed** and `--theirs` gives you the commit being replayed from `feat`. This is the opposite of what people expect.

### Interactive rebase

`git rebase -i main` opens a to-do list where you can `pick`, `reword`, `edit`, `squash`, `fixup` or `drop` each commit, and reorder them. It is how you turn a messy branch ("wip", "fix typo", "actually fix it") into a tidy series before review.

A neat workflow uses fixup commits:

```
git commit --fixup=<sha-of-target>
git rebase -i --autosquash main
```

`--fixup` creates a commit titled `fixup! <original title>`, and `--autosquash` moves it next to its target and marks it `fixup`, so it melts into that commit.

### Rebase --onto

`git rebase --onto <newbase> <upstream>` takes the commits after `<upstream>` and replays them onto `<newbase>`. The classic use: you branched `feat2` off `feat`, then `feat` was rewritten. `git rebase --onto feat <old-feat-tip>` moves just your `feat2` commits onto the new `feat`.

## The golden rule of rebasing

> [!warning] Don't rebase commits other people have built on
> Rebasing replaces commits with new ones. If a colleague has pulled your old commits and built on them, their history and yours now diverge, with duplicated changes under different hashes. Rebase freely on private branches; do not rewrite `main` or a shared branch.

Rewriting your own pushed feature branch (for example, after review) is common and fine, but it needs a force-push, which brings its own hazard.

## Force-pushing safely

After rewriting a pushed branch, a normal `git push` is rejected as a non-fast-forward. If server policy permits it, `git push --force` can replace the remote branch tip and remove a teammate's commits from that branch's ancestry. Those objects may still be retained elsewhere.

`git push --force-with-lease` is safer: it only overwrites the remote if the remote branch is still where your remote-tracking ref (`origin/feat`) says it is. If someone pushed since your last fetch, you get `! [rejected] (stale info)`.

There is a subtle trap. If you (or your editor, in the background) run `git fetch`, your `origin/feat` is updated to include the teammate's commit, and the lease passes, so their work is overwritten anyway. Adding `--force-if-includes` (Git 2.30+) closes that gap: it checks whether the remote-tracking tip is reachable from an entry in the local branch reflog used for the rewrite. This prevents the illustrated unseen-update overwrite; it does not prove the rewritten code preserved every remote change.

```
git push --force-with-lease \
         --force-if-includes
```

## Squash merges

Platforms such as GitHub and GitLab offer **squash and merge**: all the branch's changes become a single new commit on `main`, with one parent. Locally it is `git merge --squash feat` followed by `git commit`.

- History on `main` is linear with one commit per pull request, which is easy to read, bisect and revert.
- The branch's individual commits are not ancestors of `main`. git branch -d feat may refuse if checking against main; if feat has an upstream it checks that upstream instead, and continuing to work on the same branch afterwards produces confusing repeated conflicts.

## Cherry-pick

`git cherry-pick <sha>` applies one commit's change on top of the current branch as a new commit. It is mostly used to backport a fix to a release branch. Use `-x` to append "(cherry picked from commit ...)" to the message so the link is traceable.

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

Reverting a merge commit needs `-m 1` to say which parent is the mainline. There is a catch: once a merge is reverted, merging the same branch again brings in only *newer* commits, because the old ones are already ancestors. To bring the reverted work back, revert the revert.

## Merge or rebase?

| | Merge | Rebase |
|---|---|---|
| History | Original ancestry retained | Replayed ancestry; normally linear |
| Hashes | Preserved | Rewritten |
| Conflicts | Once | Per commit |
| Safe if shared | Yes | No |

A widely used compromise: **rebase your private branch** onto `main` to keep it current and tidy, then integrate it via a merge commit or squash merge on the platform. You get readable history without rewriting anything other people depend on.

## Key takeaways
- A merge joins histories with a commit that has two parents; a fast-forward just moves the pointer when no join is needed.
- Rebase replays commits as new ones on a new base, so hashes change; never rebase commits others have built on.
- Use `zdiff3` conflict style and `rerere` to make conflicts easier; remember ours and theirs swap during a rebase.
- Prefer `--force-with-lease --force-if-includes` to `--force` when updating a rewritten branch.
- Undo local mistakes with the reflog or `ORIG_HEAD`; undo shared mistakes with `git revert`.

## Further reading
- [Git Branching: Rebasing — Pro Git](https://git-scm.com/book/en/v2/Git-Branching-Rebasing)
- [Basic Branching and Merging — Pro Git](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)
- [git-rebase documentation](https://git-scm.com/docs/git-rebase)
- [git-merge documentation](https://git-scm.com/docs/git-merge)
- [git-push documentation (force-with-lease)](https://git-scm.com/docs/git-push)
- [git-rerere documentation](https://git-scm.com/docs/git-rerere)
- [gitrevisions: specifying ranges](https://git-scm.com/docs/gitrevisions)
