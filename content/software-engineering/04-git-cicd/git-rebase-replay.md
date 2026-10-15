---
id: git-rebase-replay
title: Replaying and editing private commits
level: intermediate
minutes: 3
sourceLesson: git-merge-rebase
summary: Rebase normally creates new commits on the chosen base, changing their parents and hashes.
---

A merge retains existing ancestry. Rebase instead replays a selected sequence of commits onto another base; this unit follows that replay and its conflict handling.

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

A neat workflow uses fixup commits. This is a command template: replace `<sha-of-target>` with the commit to correct, after adding the correction to the Git index.

```

# Record a correction for an earlier commit.
git commit --fixup=<sha-of-target>

# Reorder and fold it into that target.
git rebase -i --autosquash main
```

`--fixup` creates a commit titled `fixup! <original title>`, and `--autosquash` moves it next to its target and marks it `fixup`, so it melts into that commit.

### Rebase --onto

`git rebase --onto <newbase> <upstream>` takes the commits after `<upstream>` and replays them onto `<newbase>`. The classic use: you branched `feat2` off `feat`, then `feat` was rewritten. `git rebase --onto feat <old-feat-tip>` moves just your `feat2` commits onto the new `feat`.

## Key takeaways

- Rebase normally creates new commits on the chosen base, changing their parents and hashes.
- During rebase, ours is the upstream plus replayed work and theirs is the feature commit being replayed.
- Interactive rebase cleans a private sequence; --onto can move only the commits after a known old base.

## Further reading

- [Git Branching: Rebasing — Pro Git](https://git-scm.com/book/en/v2/Git-Branching-Rebasing)
- [git-rebase documentation](https://git-scm.com/docs/git-rebase)
