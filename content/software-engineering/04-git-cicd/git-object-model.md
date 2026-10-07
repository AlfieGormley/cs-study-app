---
id: git-object-model
title: Git's object model
level: basic
minutes: 12
summary: Blobs, trees, commits and tags, content addressing, refs and HEAD, the index, packfiles, and how reflogs can recover commits while their objects are retained.
---

Most people learn Git as a list of commands. That works until something goes wrong: a rebase eats a commit, a branch "disappears", or a merge produces something nobody expected. At that point the commands stop making sense, because they are thin wrappers around a very simple data model.

Learn the model and nearly every command becomes obvious. Git is two things:

1. A **content-addressed object store**: a key-value database where the key is a hash of the value.
2. A small set of **refs**: human-readable names that point at objects in that store.

Everything else (branches, merges, rebases, tags, `git log`) is built from those two pieces.

## Snapshots, not diffs

Git models committed project state as **snapshots**. This logical model is separate from delta compression used to store or transfer objects. Every commit records the complete state of the project tree at that moment.

That sounds wasteful, but it is not. If a file has not changed, the new snapshot simply points at the same stored copy as the previous one. Diffs are computed on demand when you ask for them (`git diff`, `git log -p`); they are not the logical representation of commits. Packfiles can nevertheless store object deltas, as described below.

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

A **tree** is a directory listing. Each entry has a mode, a type, a hash and a name. You can inspect one with `git cat-file -p`:

```
$ git cat-file -p 'HEAD^{tree}'
100644 blob ce0136...  hello.txt
040000 tree 5f6ed9...  src
```

Common modes are `100644` (normal file), `100755` (executable), `120000` (symlink), `040000` (subdirectory) and `160000` (a submodule commit). Git tracks the executable bit and nothing else about permissions.

### Commits

A **commit** points at exactly one tree (the root of the snapshot), zero or more parents, and records who and when (hashes shortened to fit):

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

### Annotated tags

An **annotated tag** (`git tag -a v1.0 -m "..."`) is a real object with a tagger, date, message and optionally a GPG or SSH signature. A **lightweight tag** (`git tag v0.1`) is not an object at all: it is a ref pointing directly at an object, usually a commit. The commands here default to HEAD. You can check with `git cat-file -t v1.0` (prints `tag`) versus `git cat-file -t v0.1` (prints `commit`).

## Content addressing: the hash is the name

In a SHA-1-format repository, an object's name is the SHA-1 hash of a short header followed by its content. For a blob the header is `blob <size>` and a NUL byte. You can reproduce Git's hashes yourself:

```python
import hashlib

def git_hash(kind, body):
    head = f"{kind} {len(body)}\0".encode()
    sha = hashlib.sha1(head + body)
    return sha.hexdigest()

blob = git_hash("blob", b"hello\n")
print(blob)
# ce013625030ba8dba906f756967f9e9ca394464a

# tree entry: mode, name, NUL, raw hash
entry = (b"100644 hello.txt\0"
         + bytes.fromhex(blob))
print(git_hash("tree", entry))
# aaa96ced2d9a1c8e72c56b253a0e2fe78393feb7
```

Those match `git hash-object hello.txt` and `git write-tree` in a SHA-1 repository whose index contains just that file, with the shown mode and no content-conversion filters.

Content addressing has three big consequences.

**1. Deduplication is free.** Copy `hello.txt` to `copy.txt` and commit: Git writes only two new objects, a new tree and a new commit. The tree has two entries pointing at the same blob hash.

**2. History is tamper-evident.** A commit's hash covers its tree hash and its parent hashes. The tree hash covers every blob and subtree hash. Change one byte in one file ten commits ago and every hash from there to the tip changes. This structure is a **Merkle DAG**, the same idea behind blockchains and certificate transparency logs.

**3. Objects are immutable.** You cannot edit a commit. Commands that seem to edit history actually create new objects and move a ref.

```
 a commit and what it points at

 commit a08133 --> tree 920677
   |               |- blob ce0136 hello.txt
   | parent        |- blob ce0136 copy.txt
   v               '- tree 5f6ed9 src/
 commit 587031          '- blob b917a7
                           app.py
```

> [!example] `--amend` makes a new commit
> Run `git commit --amend -m "copy file"` on a commit whose hash is `375494`. The result has a new hash, `a08133`, because the message is part of the hashed content. The old commit `375494` still exists in the object store; the branch simply points somewhere else now.

## Refs, branches and HEAD

Hashes are unfriendly, so Git keeps **refs**: names that map to a hash.

- A **branch** is a ref under `refs/heads/`. With the files backend and a loose SHA-1 ref, .git/refs/heads/main is a 40-hex-digit object ID plus a newline. Packed refs, SHA-256 and the reftable backend use different representations; an unborn branch has no commit ref yet.
- A **tag** is a ref under `refs/tags/`.
- A **remote-tracking branch** such as `origin/main` lives under `refs/remotes/` and records the last known remote position, normally updated by fetch and also by successful pushes with a matching tracking mapping.
- **HEAD** is a *symbolic* ref saying which branch you are on: `.git/HEAD` contains `ref: refs/heads/main`.

Creating a branch records a ref rather than copying the project or its history, so it is normally inexpensive. That is why Git encourages branching where older systems discouraged it.

When you commit, Git writes the new objects, then updates the branch that HEAD points to. HEAD itself does not change.

### Detached HEAD

`git switch --detach <commit>` (or `git checkout <hash>`) makes HEAD contain a raw hash instead of a branch name. `git status` reports `HEAD detached at 5870310`. New commits made now are not on any branch. Switch away without creating a branch and they become unreachable, which leads us to the safety net.

### Packed refs

Thousands of tiny ref files are slow, so `git gc` moves them into a single `.git/packed-refs` file. Do not rely on reading `.git/refs/` directly in scripts; use `git rev-parse` or `git for-each-ref`. Git also supports the **reftable** ref storage backend; use Git commands rather than depending on its on-disk representation.

## The index (staging area)

Between your working directory and the object store sits the **index**, the file `.git/index`. It is a flat list of paths, modes and blob hashes describing the *next* commit.

- `git add f` applies configured content conversions (such as line-ending or clean filters), stores the resulting blob and records its hash in the index.
- `git commit` turns the index into tree objects, writes a commit pointing at the root tree, then moves the branch.

So blobs are created at `git add` time, not at commit time. If you `git add` a file and later discard it, the blob lingers until garbage collection.

## How objects are stored

Ordinary local object creation usually writes a **loose** object: zlib-compressed, at `.git/objects/ce/013625...` (the first two hex characters become a directory name). That is fine for a few objects but wasteful for millions.

`git gc` (which also runs automatically from time to time) combines objects into a **packfile**. Inside a pack, Git stores some objects as **deltas** against similar objects, often an older version of the same file. So Git's *model* is snapshots, while its *storage* uses delta compression. The two ideas are independent.

Network transfers (`fetch`, `push`, `clone`) normally transfer packs based on negotiated wants and common history. Negotiation, filtering and transport choices determine the set; it need not equal every and only missing object.

## Reachability, reflog and garbage collection

An object is **reachable** if you can get to it by following pointers from some ref. Garbage collection only deletes unreachable objects, and even then not immediately.

When enabled and retained, a **reflog** records local updates to a ref:

```
$ git reflog
a08133f HEAD@{0}: commit (amend): copy file
375494d HEAD@{1}: commit: copy
```

Reflog entries keep old commits alive. By default, entries for commits that are still reachable expire after 90 days and entries for unreachable ones after 30 days (`gc.reflogExpire`, `gc.reflogExpireUnreachable`). The usual prune grace period is two weeks (gc.pruneExpire), including expiry when using modern cruft packs. These are configurable age thresholds, not an extra guaranteed two weeks after a reflog entry expires.

> [!tip] Recovering "lost" work
> Bad rebase or hard reset? Run `git reflog`, find the hash from before the mistake, and `git branch rescue <hash>`. The reflog is local only: it is not pushed, and a fresh clone has none of your history of moves.

## SHA-1, collisions and SHA-256

SHA-1 is broken for collision resistance: the 2017 **SHAttered** attack produced two different PDFs with the same SHA-1. Git responded in two ways:

- Since Git 2.13 it uses **SHA-1DC**, a hardened SHA-1 that detects the known collision-attack patterns and refuses them, while producing the same hashes for normal data.
- Git 2.29 added an experimental **SHA-256** object format (`git init --object-format=sha256`). SHA-256 repositories cannot yet freely exchange objects with SHA-1 ones, and check the intended Git clients and hosting service for SHA-256 interoperability before choosing it.

As checked on 2026-10-04, Git's published plan for 3.0 is to make SHA-256 the default for new repositories, along with `main` as the default branch name (Git 2.x still defaults to `master` unless `init.defaultBranch` is set).

## Common pitfalls

- **Thinking a branch is a series of commits.** A branch is one pointer to one commit. "The commits on a branch" means everything reachable from that pointer.
- **Committing secrets.** Deleting the file in a later commit does not remove the blob from history. Anyone with a clone has it. Rotate the secret first, then rewrite history if you must (for example with `git filter-repo`).
- **Huge binaries.** Each distinct version is a blob, and a full clone normally retains reachable versions. Compression, partial/shallow clones and deliberate history removal affect actual disk use and retention. Use Git LFS or keep artefacts out of the repository.
- **Panicking after a reset.** A retained reflog may recover committed work. It is not a backup and does not recover arbitrary uncommitted changes discarded by a hard reset.

## Key takeaways
- Git is a content-addressed store of four object types (blob, tree, commit, annotated tag) plus refs that name them.
- An object's ID is the hash of its type, size and content, so identical content is stored once and any change ripples up to a new commit hash.
- Objects are immutable. Amend and replaying rebase create commits; commit-level reset moves a ref and may update the index and working tree without creating a replacement commit.
- A branch is a ref naming a commit, with backend-dependent storage; HEAD usually names the current branch.
- Git models snapshots but stores packs with delta compression; reflogs and configurable prune grace periods can retain otherwise unreachable work, but provide no universal recovery guarantee.

## Further reading
- [Git Internals: Git Objects — Pro Git](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- [Git Internals: Git References — Pro Git](https://git-scm.com/book/en/v2/Git-Internals-Git-References)
- [Git Internals: Packfiles — Pro Git](https://git-scm.com/book/en/v2/Git-Internals-Packfiles)
- [git-gc documentation](https://git-scm.com/docs/git-gc)
- [Hash function transition — Git docs](https://git-scm.com/docs/hash-function-transition)
- [Upcoming breaking changes in Git 3.0 — Git docs](https://git-scm.com/docs/BreakingChanges)
