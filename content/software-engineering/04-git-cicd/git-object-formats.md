---
id: git-object-formats
title: Object formats and hash guarantees
level: basic
minutes: 3
sourceLesson: git-object-model
summary: SHA-1 and SHA-256 encode 160 and 256 bits as 40 and 64 hexadecimal characters.
---

A commit binds its tree and parent IDs into its own hash. That tamper-evidence depends on the hash function; this unit examines the object format and its limits.

## SHA-1, collisions and SHA-256

SHA-1 is broken for collision resistance: the 2017 **SHAttered** attack produced two different PDFs with the same SHA-1. Git responded in two ways:

- Since Git 2.13 it uses **SHA-1DC**, a hardened SHA-1 that detects the known collision-attack patterns and refuses them, while producing the same hashes for normal data.
- Git 2.29 added an experimental **SHA-256** object format (`git init --object-format=sha256`). SHA-256 repositories cannot yet freely exchange objects with SHA-1 ones, and check the intended Git clients and hosting service for SHA-256 interoperability before choosing it.

Why is a SHA-1 object ID 40 characters long, and a SHA-256 one 64? Git prints IDs in hexadecimal (base 16, digits 0–9 then a–f), and each hexadecimal digit carries exactly 4 bits:

```formula
L = b / 4
L = 160 / 4 = 40   for SHA-1
L = 256 / 4 = 64   for SHA-256
where
L: the length of an object ID written in hexadecimal, in characters
b: the hash's output size, in bits: 160 for SHA-1, 256 for SHA-256
4: the bits held by one hexadecimal digit, which has 16 possible values (16 = 2 × 2 × 2 × 2)
SHA-1: the original hash function Git uses for object IDs, with a 160-bit (20-byte) output
SHA-256: a member of the SHA-2 family of hash functions, with a 256-bit (32-byte) output
In words: a longer hash means a longer printed ID; every 4 bits of hash adds one hex character.
```

So a SHA-1 ID is 20 raw bytes inside tree objects and 40 characters when printed, and a SHA-256 ID is 32 bytes or 64 characters. Commands accept a shorter unique prefix (`git show 5870310`), which is why abbreviated hashes of 7 or more characters appear throughout this module.

As checked on 2026-10-15, Git's published plan for 3.0 is to make SHA-256 the default for new repositories, along with `main` as the default branch name (Git 2.x still defaults to `master` unless `init.defaultBranch` is set).

## Key takeaways

- SHA-1 and SHA-256 encode 160 and 256 bits as 40 and 64 hexadecimal characters.
- SHA-1DC detects known attack patterns; it does not restore SHA-1 collision resistance.
- Check client and hosting support before selecting SHA-256; the Git 3.0 defaults remain a published plan.

## Further reading

- [Git Internals: Git Objects — Pro Git](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- [Hash function transition — Git docs](https://git-scm.com/docs/hash-function-transition)
- [Upcoming breaking changes in Git 3.0 — Git docs](https://git-scm.com/docs/BreakingChanges)
