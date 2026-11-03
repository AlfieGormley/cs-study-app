---
id: dist-quorum-overlap
title: Read and write quorum overlap
level: intermediate
minutes: 3
summary: Use replica-set intersections to predict when reads can miss a completed write.
sourceLesson: dist-quorums
---

Leader-based replication (covered in the databases module) sends every write through one node. Amazon's 2007 Dynamo paper popularised the alternative: **leaderless replication**, where clients (or a coordinator acting for them) send each write to several replicas in parallel and consider it done once enough of them acknowledge.

Cassandra, Riak, ScyllaDB and Voldemort all descend from this design. (DynamoDB the service, confusingly, uses leaders and Paxos internally.)

## N, R and W

Three numbers define a quorum system:

- **N**: how many replicas store each key (the replication factor).
- **W**: how many must acknowledge a write before it's reported successful.
- **R**: how many must respond to a read.

In the simplified Dynamo ring picture, the key's primary copies go on the next N distinct nodes clockwise. Its **preference list** also contains additional candidates for fallback; real placement strategies can respect racks and data centres.

```
        A
     F     B     key k hashes here
               <- replicas: B, C, D
     E     C        (N = 3)
        D
```

### The overlap rule

If **R + W > N**, every read set overlaps every write set in at least one node, so a read contacts at least one participant in each completed write. Returning the intended newest version additionally depends on durable retained versions and the reconciliation protocol; set overlap alone does not establish that.

```formula essential
R + W > N
where
R: the number of replicas that must respond to a read
W: the number of replicas that must acknowledge a write
N: the number of replicas that store the key (the replication factor)
In words: if the replicas a read hears from plus the replicas that took the write add up to more than the total, the two groups can't be completely separate, so at least one replica is in both.
```

Why it works: the write landed on W of the N replicas. If a read needs more replicas than the number left without the write, it cannot fit entirely inside that stale group, so it must reach at least one replica with the write. That is the same inequality rearranged. With 3 replicas, 2 write acknowledgements and 2 read responses, the two pairs cannot be 4 different nodes out of 3.

> [!analogy] Real-world analogy: three flatmates and a parcel
> Three flatmates share a house. When a parcel is left with a neighbour, the person who hears about it tells one other flatmate, so two of the three know. Later, anyone wondering about it asks two of the three. However the pairs are chosen, at least one person asked was one of the two who knew, because two pairs drawn from three people must share somebody.
>
> **How it maps:** The three flatmates are three replicas of a key, the two who know are a write acknowledged by two replicas, asking two is a read from two replicas, and the shared person is the replica that the overlap rule guarantees is in both sets.
>
> **Where it stops:** A flatmate who heard two different stories needs a rule for which is newer; replicas need version numbers, timestamps or vector clocks to decide which copy is newest. And real stores can quietly substitute stand-in replicas during failures (sloppy quorums), which breaks the guarantee.

```
N=3, W=2, R=2:
write -> [B] [C]  .
read  ->  .  [C] [D]
overlap:     C
```

The read reconciles versions: a timestamp rule picks a winner, while a vector clock identifies obsolete versions and concurrent siblings. Concurrent siblings have no unique causally newest value and may need a merge.

There is a second overlap condition people forget: any two *write* sets must overlap too, so two writes can't both complete on disjoint replicas without at least one node seeing both.

```formula essential
W > N / 2
where
W: the number of replicas that must acknowledge a write
N: the number of replicas that store the key
In words: if every write reaches more than half the replicas, any two writes share at least one replica.
```

Read-write overlap alone does not imply write-write overlap. For example, with 5 replicas, writes acknowledged by 2 and reads answered by 4, every read meets every write (4 + 2 is more than 5), but two writes are not forced to meet (2 + 2 is not more than 5).

Two concurrent writes of 2 replicas each can land on {A, B} and {C, D} and never meet. Then only the version-ordering rule (often a timestamp) decides which one survives.

## Key takeaways
- Leaderless replication accepts an operation after enough members of a key’s replica set respond.
- Read-plus-write quorum size greater than the replica count guarantees a set intersection under strict placement.
- Write-write overlap is a separate condition; even overlapping writes still need a version-ordering protocol.

## Further reading
- [DynamoDB architecture (USENIX ATC 2022)](https://www.usenix.org/system/files/atc22-elhemali.pdf)
- [Dynamo: Amazon's Highly Available Key-value Store (SOSP 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Cassandra Dynamo architecture](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Quorum (distributed computing) (Wikipedia)](https://en.wikipedia.org/wiki/Quorum_%28distributed_computing%29)
