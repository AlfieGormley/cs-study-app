---
id: dist-raft-log-commit-safety
title: Raft log replication and the current-term rule
level: advanced
minutes: 4
summary: Explain log matching, leader completeness and why an old-term majority is insufficient to commit.
sourceLesson: dist-consensus-raft
---

A Raft leader proposes ordered commands, and followers may be behind or have conflicting uncommitted suffixes. Matching logs is only part of the job: the commit rule must also survive the next election.

### Log replication

Each log entry has an **index**, a **term** and a **command**.

1. Client sends a command to the leader.
2. Leader appends it to its log and sends `AppendEntries` to followers, including the index and term of the **preceding** entry.
3. A follower accepts only if its log has an entry at that preceding index with the same term (the **consistency check**). Otherwise it rejects, and the leader retries with an earlier index until they match, then overwrites the follower's conflicting suffix.
4. Once an entry **from the leader's current term** is stored on a **majority** (counting the leader itself), the leader marks it **committed**, along with every entry before it, applies it to its state machine and replies to the client. (Why "current term" matters is the subtle rule below.)
5. Followers learn the commit index from later `AppendEntries` and apply it.

```
idx:    1  2  3  4  5
leader [1][1][2][3][3]
f1     [1][1][2][3][3]  match
f2     [1][1][2]        behind
f3     [1][1][2][2]     conflict
                ^ idx 4 overwritten
```

**Log Matching Property**: if two logs have an entry with the same index and term, they're identical up to that index. The consistency check enforces it by induction.

### Safety

The crucial guarantee is **Leader Completeness**: once an entry is committed, it's present in the logs of all future leaders.

Why: a committed entry is on a majority. To win, a candidate needs votes from a majority. Two majorities always overlap, so at least one voter has the entry, and it refuses to vote for a candidate whose log is less up to date.

> [!warning] The subtle rule
> A leader only counts replicas to commit entries **from its own term**. Entries from earlier terms become committed indirectly when a current-term entry after them commits. Figure 8 in the Raft paper shows an old-term entry replicated to a majority that is still overwritten. That's why new leaders append a no-op entry at the start of their term: committing it also commits everything before it.

Here is the Figure 8 scenario, step by step, with five nodes:

```
term 2: S1 leader, writes X at idx 2
        reaches S1, S2 only; S1 dies
term 3: S5 elected (S3, S4, S5)
        writes Y at idx 2, on S5 only
term 4: S1 back, elected; copies X
        to S3. X now on S1 S2 S3
```

X (term 2) is now on a majority. If S1 treated that as committed and then crashed, S5 could win term 5: its last entry has term 3, which beats the term-2-or-earlier entries on S2, S3 and S4, so they vote for it. S5 would then overwrite X with Y on every node, "un-committing" X. Raft forbids this: S1 may only commit X once an entry from term 4 is also on a majority, and then S5 can no longer win, because a majority holds a term-4 entry that beats its log.

## Key takeaways
- AppendEntries checks the preceding entry’s index and term before replacing a conflicting follower suffix.
- Committed entries survive future leader elections; the election restriction and log-matching rules work together.
- Replica counting directly commits only current-term entries; earlier entries commit with a later current-term entry.

## Further reading
- [The Raft consensus algorithm (visualisations, implementations)](https://raft.github.io/)
- [In Search of an Understandable Consensus Algorithm (Raft paper)](https://raft.github.io/raft.pdf)
