---
id: git-content-hashes
title: Content hashes and immutable history
level: basic
minutes: 4
sourceLesson: git-object-model
summary: Git hashes the object header as well as the content.
---

The previous unit introduced blobs, trees, commits and tags. Here the objective is to connect their identities: how Git names an object and why rewriting history creates new commits.

## Content addressing: the hash is the name

In a SHA-1-format repository, an object's name is the SHA-1 hash of a small header followed by its content. A hash function turns any sequence of bytes into a fixed-size fingerprint; the same bytes always give the same fingerprint, and a change normally gives a different fingerprint. Different inputs can collide; tamper-evidence assumes an attacker cannot feasibly find a suitable collision. Written as a formula:

```formula
id = SHA-1(h ‖ c)
h = t ‖ " " ‖ n ‖ NUL
where
id: the object's name (its object ID), written as 40 hexadecimal characters in a SHA-1 repository
SHA-1: the SHA-1 hash function, which turns any sequence of bytes into a fixed 160-bit (20-byte) fingerprint
h: the header Git puts in front of the content
c: the object's content: the file's bytes for a blob, the encoded entry list for a tree, the text of a commit
t: the object's type, written as text: blob, tree, commit or tag
n: the size of the content in bytes, written out as decimal digits (6 for "hello" plus a newline)
NUL: the zero byte (value 0), which marks where the header ends
‖: concatenation: join two byte sequences end to end, in that order
In words: Git glues a short "type size" label onto the content and hashes the lot, so the name depends on every byte of the content and on its type.
```

For a file containing `hello` and a newline, *t* is `blob` and *n* is 6, so Git hashes `blob 6`, a NUL byte, then the six content bytes. You can reproduce Git's hashes yourself:

```python
import hashlib

def git_hash(kind, body):
    # Hash the typed header with the bytes.
    head = f"{kind} {len(body)}\0".encode()
    sha = hashlib.sha1(head + body)
    return sha.hexdigest()

blob = git_hash("blob", b"hello\n")
print(blob)
# Same ID as git hash-object hello.txt.
# ce013625030ba8dba906f756967f9e9ca394464a

# tree entry: mode, name, NUL, raw hash
entry = (b"100644 hello.txt\0"
         + bytes.fromhex(blob))

# A tree hashes a named entry, not a file.
print(git_hash("tree", entry))
# aaa96ced2d9a1c8e72c56b253a0e2fe78393feb7
```

Those match `git hash-object hello.txt` and `git write-tree` in a SHA-1 repository whose index contains just that file, with the shown mode and no content-conversion filters.

Content addressing has three big consequences.

**1. Deduplication is free.** Copy `hello.txt` to `copy.txt` and commit: Git writes only two new objects, a new tree and a new commit. The tree has two entries pointing at the same blob hash.

**2. History is tamper-evident.** A commit's hash covers its tree hash and its parent hashes. The tree hash covers every blob and subtree hash. To record different bytes in an old snapshot, Git needs replacement hashes along that tree and each rewritten descendant, assuming collision resistance. Existing objects are not modified, and the hash chain proves neither authorship nor code safety. This structure is a **Merkle DAG**, the same idea behind blockchains and certificate transparency logs.

**3. Objects are immutable.** You cannot edit a commit. Amend and a replaying rebase create replacement commits and move a ref. A commit-level reset instead moves a ref and may update the index and working tree without creating a replacement commit.

```
 illustrative object graph

 commit a08133 --> tree 920677
   |               |- blob ce0136 hello.txt
   | parent        |- blob ce0136 copy.txt
   v               '- tree 5f6ed9 src/
 commit 587031          '- blob b917a7
                           app.py
```

> [!example] `--amend` makes a new commit
> Illustratively, run `git commit --amend -m "copy file"` on a commit whose shortened hash is `375494`. The result has a different hash, shown here as `a08133`, because the message is part of the hashed content. The old commit `375494` still exists in Git's object store; the branch simply points somewhere else now.

## Key takeaways

- Git hashes a Git object header together with its content.
- Tree and parent hashes bind a commit to its snapshot and history, assuming collision resistance.
- Amend creates a replacement commit and moves a ref rather than editing the old object.

## Further reading

- [Git Internals: Git Objects — Pro Git](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- [Hash function transition — Git docs](https://git-scm.com/docs/hash-function-transition)
- [Upcoming breaking changes in Git 3.0 — Git docs](https://git-scm.com/docs/BreakingChanges)
