---
id: app-kademlia-distance-and-buckets
title: "Kademlia XOR distance and bounded routing buckets"
level: advanced
minutes: 4
sourceLesson: app-p2p-webrtc
summary: "Kademlia ranks node and key IDs by XOR distance in one shared identifier space."
---

## Kademlia: the XOR metric

A **distributed hash table** (DHT) maps keys to values with no central server. BitTorrent's **Mainline DHT** (BEP 5) is based on **Kademlia** (Maymounkov and Mazières, 2002) and stores "which peers have info-hash X".

Nodes and keys share a 160-bit ID space (info-hashes are 160 bits, so they fit). The distance between two IDs is their **XOR** (exclusive or: compare the IDs bit by bit, writing 1 where they differ and 0 where they match), read as an integer. With 4-bit IDs:

```formula essential
d(a, b) = a ⊕ b
d(0110, 0011) = 0101 = 5
where
d(a, b): the Kademlia distance between IDs a and b, a whole number
a, b: two node or key IDs, written here in binary (base 2); 160 bits long in Mainline DHT
⊕: XOR, exclusive or: each result bit is 1 if the two input bits differ and 0 if they are the same
In words: two IDs are as far apart as the binary number marking where their bits differ; 0110 and 0011 differ in the second and fourth bits, giving 0101, which is 5.
```

In Python the XOR operator is `^`, so `0b0110 ^ 0b0011` gives 5. A difference in a high bit outweighs all the lower bits together, so IDs that share a longer leading prefix are always closer. That gives a quick rule: to find the closest ID, look for the longest shared prefix.

XOR distance behaves like ordinary distance (it is a true metric): every ID is at distance zero from itself, the distance from a to b equals the distance from b to a, and going via a third ID is never shorter than going direct.

Crucially, **for any point and any distance there is exactly one ID at that distance**, so all nodes can consistently rank IDs for a target. Completing a lookup also requires adequate live routing information. Original Kademlia replicates each value on a small, fixed number of the closest nodes (the contact/replication parameter k); Mainline DHT stores peer contact information associated with the hash.

### k-buckets

Each node keeps a DHT routing table made of **k-buckets**. In the basic distance-bucket model, each bucket covers a band of distances twice as wide as the one before. Put another way, bucket i holds contacts whose IDs first differ from ours at the same bit position: the nearest bucket holds contacts that share all but the last bit with us, and the farthest holds contacts that differ in the very first bit, which is half of the whole ID space.

Each bucket holds a fixed maximum number of contacts, the contact-capacity parameter k: 20 as the original paper's example, and **8 in Mainline DHT**.

The capacity per bucket is bounded by k; contact **density** falls across exponentially larger distance regions. Mainline DHT uses a splitting routing-table implementation rather than a literal permanently allocated array of 160 buckets.

> [!analogy] Real-world analogy: An address book that thins out with distance
> Your address book holds almost every neighbour on your street, a handful of people elsewhere in your town, a few in other cities and one or two in each distant country. Each region gets only a few slots, however many people live there.
>
> **How it maps:** Regions further away are the higher buckets, which cover exponentially larger stretches of the ID space but still hold at most k contacts. Close to your own ID you know almost everyone; far away you know a few people, which is enough to ask for directions.
>
> **Where it stops:** Real distance is geographic. Kademlia "nearness" is only XOR closeness of random IDs, which says nothing about where the computers are or how fast they respond.

When a bucket is full and a new contact appears, Kademlia **pings the least recently seen** contact and drops the newcomer if the old one answers. The paper's analysis of Gnutella traces motivated favouring older responsive contacts; current networks need not have the same uptime distribution. This impedes an attacker simply displacing old contacts with a flood of new IDs, but does not eliminate Sybil or eclipse attacks.

## Key takeaways
- Kademlia ranks node and key IDs by XOR distance in one shared identifier space.
- Bounded k-buckets retain contacts across distance scales; Mainline DHT uses a splitting table.

## Further reading
- [BEP 5](https://www.bittorrent.org/beps/bep_0005.html)
- [Original Kademlia paper](https://pdos.csail.mit.edu/~petar/papers/maymounkov-kademlia-lncs.pdf)
