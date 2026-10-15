---
id: git-merge-mechanics
title: Merge bases, fast-forwards and conflicts
level: intermediate
minutes: 4
sourceLesson: git-merge-rebase
summary: A fast-forward moves a ref; a divergent merge normally records two parents.
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

Git compares three snapshots: the base (B), "ours" (E, the branch you are on) and "theirs" (D). That is why it is called a **three-way merge**. Complex histories can have multiple best bases; the ort strategy (and its earlier Git recursive strategy) can combine them into a virtual base. A line changed on only one side takes that side's version. A line changed differently on both sides is a **merge conflict**.

## Fast-forward merges

If `main` has not moved since `feat` branched off, there is nothing to combine. `main` is an ancestor of `feat`, so Git just moves the `main` pointer forward:

The command output is illustrative; object abbreviations depend on your repository.

```
# Move the branch; no commit is needed.
$ git merge feat
Updating dd0d6ad..cbdec69
Fast-forward
```

No new commit is created. This integration leaves no merge commit recording the feature boundary. The branch ref and local reflogs can still exist.

`git merge --no-ff feat` forces a merge commit even when a fast-forward is possible. Teams use it to keep a visible record of each feature as a unit.

## Three-way merges and merge commits

When both sides have moved, a successful ordinary two-head merge creates a **merge commit** with two parents:

```
          C---D        feat
         /     \
 A---B---E------M      main
```

This illustrative excerpt omits the remaining commit metadata and message. The two parent lines establish the merge ancestry.

```
$ git cat-file -p HEAD
tree dc7872...
parent dd0d6ad...
parent cbdec69...
```

Parent order matters. The **first parent** is the branch you were on (`main`); the second is the branch you merged in. `git log --first-parent` follows only first parents, giving a view that skips merged side-branch internals while retaining direct mainline commits of `main` even in a merge-heavy history.

Since Git 2.34 the default two-head merge strategy is **ort** (you will see "Merge made by the 'ort' strategy"), a faster replacement for the older Git recursive strategy. Since Git 2.50, selecting the option `-s recursive` uses ort; earlier releases had a separate implementation.

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

## Key takeaways

- A fast-forward moves a ref; a divergent merge normally records two parents.
- Three-way merging compares the base with both tips; textual success does not prove semantic correctness.
- diff3-style markers expose the base; resolve deliberately, stage, then continue.

## Further reading

- [Basic Branching and Merging — Pro Git](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)
- [git-merge documentation](https://git-scm.com/docs/git-merge)
- [git-rerere documentation](https://git-scm.com/docs/git-rerere)
