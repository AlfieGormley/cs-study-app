---
id: git-refs-index
title: Refs, HEAD and staging the next commit
level: basic
minutes: 3
sourceLesson: git-object-model
summary: A branch ref names a tip; HEAD normally names the current branch.
---

Git objects store immutable content and history. Refs give that history useful names, while the index describes what the next snapshot should contain.

## Refs, branches and HEAD

Hashes are unfriendly, so Git keeps **refs**: names that map to a hash.

- A **branch** is a ref under `refs/heads/`. With the files backend and a loose SHA-1 ref, .git/refs/heads/main is a 40-hex-digit object ID plus a newline. Packed refs, SHA-256 and the reftable backend use different representations; an unborn branch has no commit ref yet.
- A **tag** is a ref under `refs/tags/`.
- A **remote-tracking branch** such as `origin/main` lives under `refs/remotes/` and records the last known remote position, normally updated by fetch and also by successful pushes with a matching tracking mapping.
- **HEAD** is a *symbolic* ref saying which branch you are on: `.git/HEAD` contains `ref: refs/heads/main`.

Creating a branch records a ref rather than copying the project or its history, so it is normally inexpensive. That is why Git encourages branching where older systems discouraged it.

When you commit, Git writes the new objects, then updates the branch that HEAD points to. The symbolic target stored in HEAD stays the branch name; resolving HEAD now reaches the new commit.

### Detached HEAD

`git switch --detach <commit>` (or `git checkout <hash>`) makes HEAD contain a raw hash instead of a branch name. `git status` reports `HEAD detached at 5870310`. New commits made now are not on any branch. Switch away without a durable ref and they may no longer be reachable from branches or tags. Retained reflogs can still protect them temporarily; the next unit covers that recovery window.

### Packed refs

With the files backend, maintenance can pack refs into `.git/packed-refs` to reduce loose-file overhead; not every branch ref is necessarily packed. Do not rely on reading `.git/refs/` directly in scripts; use `git rev-parse` or `git for-each-ref`. Git also supports the **reftable** ref storage backend; use Git commands rather than depending on its on-disk representation.

## The index (staging area)

Between your working tree (the files you edit) and Git's object store sits the **Git index**, also called the **staging area**: the file `.git/index`. It is a flat list of paths, modes and blob hashes describing the *next* commit.

- `git add f` applies configured content conversions (such as line-ending or clean filters), stores the resulting blob and records its hash in the index.
- `git commit` turns the index into tree objects, writes a commit pointing at the root tree, then moves the branch.

So blobs are created at `git add` time, not at commit time. If you `git add` a file and later discard it, that blob lingers until git gc removes it.

## Key takeaways

- A branch ref names a tip; HEAD normally names the current branch.
- Detached HEAD commits need a durable ref if you want to retain them.
- git add stores converted content and records it in the index before git commit builds trees.

## Further reading

- [Git Internals: Git References — Pro Git](https://git-scm.com/book/en/v2/Git-Internals-Git-References)
