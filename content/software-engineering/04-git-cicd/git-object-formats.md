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
- Git 2.29 added a **SHA-256** object format (`git init --object-format=sha256`), at first marked experimental. According to the Git 2.56 documentation (October 2026), new repositories still default to SHA-1 (hardened), SHA-256 repositories are supported, and there is still no interoperability between SHA-256 and SHA-1 repositories. Check the intended Git clients and hosting service for SHA-256 support before choosing it.

Why is a SHA-1 object ID 40 characters long, and a SHA-256 one 64? Git prints IDs in **hexadecimal** (base 16, digits 0–9 then a–f), and each hexadecimal digit carries exactly 4 bits. SHA-1's 160 bits therefore print as 40 characters and SHA-256's 256 bits as 64. Inside tree objects the IDs are stored as raw bytes instead: 20 bytes for SHA-1 and 32 for SHA-256.

Commands accept a shorter unique prefix (`git show 5870310`), which is why abbreviated hashes of 7 or more characters appear throughout this module.

Git's published plan for its next breaking release, Git 3.0, is to make SHA-256 the default for new repositories, along with `main` as the default branch name. As of the Git 2.56 documentation (October 2026), Git 3.0 has no release date, and Git 2.x still names the first branch `master` unless `init.defaultBranch` (or `git init -b`) sets another name.

## Key takeaways

- SHA-1 and SHA-256 encode 160 and 256 bits as 40 and 64 hexadecimal characters.
- SHA-1DC detects known attack patterns; it does not restore SHA-1 collision resistance.
- SHA-1 remains the default; check client and hosting support before selecting SHA-256, since the Git 3.0 defaults are still a plan without a release date.

## Further reading

- [Git Internals: Git Objects — Pro Git](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- [Hash function transition — Git docs](https://git-scm.com/docs/hash-function-transition)
- [Upcoming breaking changes in Git 3.0 — Git docs](https://git-scm.com/docs/BreakingChanges)
