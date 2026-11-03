---
id: dist-fault-models
title: Fault models and cluster size
level: basic
minutes: 3
summary: Choose crash or Byzantine assumptions and understand the quorum counts and durable-state boundary.
sourceLesson: dist-why-hard
---

A fault-tolerance claim is meaningful only with a fault model. A machine stopping is different from a restarted machine forgetting its votes or a node sending contradictory messages.

## Fault models

When you read about an algorithm, check which faults it tolerates:

| Model | Node behaviour |
|---|---|
| Crash-stop | Fails by halting, never returns |
| Crash-recovery | Halts, may restart with its disk |
| Omission | Drops some messages |
| Byzantine | Anything, including lying |

Raft and Paxos assume crash-recovery with durable storage. Many blockchain protocols instead tolerate Byzantine faults. Choosing the model is a design decision: Byzantine tolerance is expensive and rarely needed inside one company's data centre.

### How many nodes you need

The quorum model sets how many nodes a cluster needs to survive a given number of faulty ones. The counts below apply to majority crash quorums and the standard unsigned Byzantine quorum model, rather than every possible timing or signature model:

```formula essential
n_crash = 2f + 1
n_byz = 3f + 1
where
n_crash: the minimum number of nodes for a majority quorum to remain available after f nodes crash (stop)
n_byz: the minimum number of nodes in the standard unsigned Byzantine quorum model when f nodes can lie or behave arbitrarily
f: the number of nodes that may be faulty at the same time
In words: to survive f crashes you need a majority still alive, so twice the faults plus one; to survive f liars you need three times the faults plus one, so that any two decision quorums share at least one honest node.
```

Where the numbers come from:

- **Crashes**: decisions need a majority. If f nodes crash, the remaining f + 1 must still be a majority of the cluster, which first happens at 2f + 1 nodes. Any two majorities share at least one node, so no two decisions can contradict each other.
- **Byzantine faults**: a liar can tell different nodes different things, so a quorum must contain enough honest nodes to outvote it. With 3f + 1 nodes and quorums of 2f + 1, any two quorums share at least f + 1 nodes, and since at most f of those are liars, at least one honest node is in both.

So tolerating 2 faults takes 5 nodes for crashes but 7 for Byzantine faults. That extra cost is why most data-centre systems assume crash faults only.

> [!analogy] Real-world analogy: an absent committee member versus a two-faced one
> A committee splits into two overlapping working groups, and anyone in both groups reports what each group decided to the other. If a member is simply off sick, the overlap still works as long as someone who turned up is in both groups. If a member deliberately tells each group something different, one shared member is not enough: that shared member might be the one spreading the contradiction.
>
> **How it maps:** The working groups are quorums. An absent member is a crash fault; a member who tells each group a different story is a Byzantine fault. Majority quorums guarantee an overlap, which is enough for crashes. Byzantine quorums must overlap in more members than there are liars, so at least one honest member is always in both.
>
> **Where it stops:** Real quorums do not rely on one person relaying news; protocols check which nodes acknowledged each decision. And a dishonest committee member can be questioned later, whereas a Byzantine node's lies may only show up as inconsistent state.

The fine print matters. "Crash-recovery with durable storage" means a node that restarts still has everything it `fsync`ed. A node that comes back with an empty or rolled-back disk (a replaced VM, a disk cache that lied about flushing) has **amnesia**, and that falls outside the model: it can vote twice in the same term and break safety. Likewise, silent data corruption is closer to a Byzantine fault than a crash, which is why storage systems add checksums.

## Key takeaways
- Crash-stop, crash-recovery, omission and Byzantine faults permit different node behaviours.
- Majority crash-tolerant groups and the standard Byzantine quorum model need different replica counts.
- Crash-recovery assumes durable state survives restart; amnesia and silent corruption can violate that assumption.

## Further reading
- [The Byzantine Generals Problem (Lamport, Shostak and Pease)](https://lamport.azurewebsites.net/pubs/byz.pdf)
- [Byzantine fault (Wikipedia)](https://en.wikipedia.org/wiki/Byzantine_fault)
