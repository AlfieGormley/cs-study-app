---
id: git-storage-recovery
title: Packfiles, reachability and recovery
level: basic
minutes: 3
sourceLesson: git-object-model
summary: Packfile deltas compress stored snapshots without changing their logical model.
---

A branch ref identifies a commit; trees and parent links lead to other objects. This unit connects that graph to disk use, retention and recovering committed work.

## How objects are stored

Ordinary local object creation usually writes a **loose** object: zlib-compressed, at `.git/objects/ce/013625...` (the first two hex characters become a directory name). That is fine for a few objects but wasteful for millions.

`git gc` (which also runs automatically from time to time) combines objects into a **packfile**. Inside a pack, Git stores some objects as **deltas** against similar objects, often another version of the same file. So Git's *model* is snapshots, while its *storage* uses delta compression. The two ideas are independent.

Network transfers (`fetch`, `push`, `clone`) normally transfer packs based on negotiated wants and common history. Negotiation, filtering and transport choices determine the set; it need not equal every and only missing object.

## Reachability, reflog and git gc

An object is **reachable** if you can get to it by following pointers from some ref. Git's garbage collection prunes only objects outside its retention roots. Reflogs and configurable age thresholds can retain objects that no branch or tag reaches; explicit immediate pruning can remove that protection after reflog expiry.

When enabled and retained, a **reflog** records local updates to a ref. This illustrative excerpt shows the amended tip followed by the previous commit; your hashes and entries will differ:

```
$ git reflog
a08133f HEAD@{0}: commit (amend): copy file
375494d HEAD@{1}: commit: copy
```

Reflog entries keep old commits alive. By default, entries for commits that are still reachable expire after 90 days and entries for unreachable ones after 30 days (`gc.reflogExpire`, `gc.reflogExpireUnreachable`). The usual prune grace period is two weeks (gc.pruneExpire), including expiry when using modern cruft packs. These are configurable age thresholds, not an extra guaranteed two weeks after a reflog entry expires.

> [!tip] Recovering "lost" work
> Bad rebase or hard reset? Run `git reflog`, find the hash from before the mistake, and `git branch rescue <hash>`. The reflog is local only: it is not pushed, and a fresh clone has none of your history of moves.

## Common pitfalls

- **Thinking a branch is a series of commits.** A branch is one pointer to one commit. "The commits on a branch" means everything reachable from that pointer.
- **Committing secrets.** Deleting the file in a later commit does not remove its blob from history. Anyone with a clone has it. Rotate the secret first, then rewrite history if you must (for example with `git filter-repo`).
- **Huge binaries.** Each distinct version is a blob, and a full clone normally retains reachable versions. Compression, partial/shallow clones and deliberate history removal affect actual disk use and retention. Use Git LFS or keep artefacts out of the repository.
- **Panicking after a reset.** A retained reflog may recover committed work. It is not a backup and does not recover arbitrary uncommitted changes discarded by a hard reset.

## Key takeaways

- Packfile deltas compress stored snapshots without changing their logical model.
- Reflogs can retain old committed work, but expiry and pruning are configurable.
- Deleting a secret from the current tree leaves its old blob in history; rotate it immediately.

## Further reading

- [Git Internals: Packfiles — Pro Git](https://git-scm.com/book/en/v2/Git-Internals-Packfiles)
- [git-gc documentation](https://git-scm.com/docs/git-gc)
