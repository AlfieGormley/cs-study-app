---
id: git-snapshots-objects
title: Snapshots and Git objects
level: basic
minutes: 4
sourceLesson: git-object-model
summary: A blob stores bytes; its containing tree stores the filename and mode.
---

Most people learn Git as a list of commands. That works until something goes wrong: a rebase eats a commit, a branch "disappears", or a merge produces something nobody expected. At that point the commands stop making sense, because they are thin layers over a very simple data model.

Learn the model and nearly every command becomes obvious. Git is two things:

1. A **content-addressed object store**: a key-value database where the key is a hash of the value.
2. A small set of **refs**: human-readable names that point at objects in that store.

Everything else (branches, merges, rebases, tags, `git log`) is built from those two pieces.

## Snapshots, not diffs

Git models committed project state as **snapshots**. This logical model is separate from delta compression used to store or transfer objects. Every commit stores the complete state of the project tree at that moment.

That sounds wasteful, but it is not. If a file has not changed, the new snapshot simply points at the same stored copy as the previous one. Diffs are computed on demand when you ask for them (`git diff`, or `git log` with `-p`); they are not the logical representation of commits. Packfiles can nevertheless store object deltas, as described below.

## The four object types

Every object has a type, a size and some content. There are exactly four types.

| Type | Holds | Points to |
|---|---|---|
| blob | File bytes | Nothing |
| tree | A directory listing | Blobs, trees, submodule commit IDs |
| commit | Snapshot + metadata | One tree, parents |
| tag | Annotated tag | Usually a commit |

### Blobs

A **blob** is just the bytes of a file. It has no filename, no permissions and no timestamp. Two files with identical contents, anywhere in the history, are the same blob.

### Trees

A **tree** is a directory listing. Each entry has a mode, a type, a hash and a name. You can inspect one with `git cat-file -p`. The following is an illustrative excerpt: hashes are shortened and depend on the repository contents.

```
$ git cat-file -p 'HEAD^{tree}'
100644 blob ce0136...  hello.txt
040000 tree 5f6ed9...  src
```

Common modes are `100644` (normal file), `100755` (executable), `120000` (symlink), `040000` (subdirectory) and `160000` (a submodule commit). For ordinary files, Git tracks the executable bit rather than general permission bits. File type is represented separately by the mode.

### Commits

A **commit** points at exactly one tree (the root of the snapshot), zero or more parents, and records who and when. This is an illustrative excerpt whose object IDs are shortened to fit; identity fields record claims rather than establishing a person's identity:

```
$ git cat-file -p HEAD
tree 9206775a7554ab7faa1adcd66cd5...
parent 587031027f90b8688d233955b7...
author Ada <ada@ex.io> 1767268800 +0000
committer Ada <ada@ex.io> 1767268800 +0000

copy
```

- A root commit has **no parent**; a repository can contain multiple roots.
- A normal commit has **one** parent.
- A merge commit has **two or more**.

The **author** is who wrote the change; the **committer** is who last applied it. Rebase and cherry-pick normally preserve authorship while recording the current committer and time; the two identities can still be the same person.

When one nested file changes, Git needs its new blob, a replacement tree for each containing directory up to the root, and a new commit. Unchanged blobs and subtrees are reused. For `src/lib/util.py`, that means three replacement trees: `lib`, `src` and the root.

### Annotated tags

An **annotated tag** (`git tag -a v1.0 -m "..."`) is a real object with a tagger, date, message and optionally a GPG or SSH signature. A **lightweight tag** (`git tag v0.1`) is not an object at all: it is a ref pointing directly at an object, usually a commit. The commands here default to HEAD. You can check with `git cat-file -t v1.0` (prints `tag`) versus `git cat-file -t v0.1` (prints `commit`).

## Key takeaways

- A blob stores bytes; its containing tree stores the filename and mode.
- A commit names one root tree and its parents, preserving a complete logical snapshot.
- Annotated tags are objects; lightweight tags are refs.

## Further reading

- [Git Internals: Git Objects — Pro Git](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
