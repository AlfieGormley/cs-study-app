---
id: app-kademlia-distance-and-buckets
title: "Kademlia XOR distance and bounded routing buckets"
level: advanced
minutes: 4
sourceLesson: app-p2p-webrtc
summary: "Kademlia ranks node and key IDs by XOR distance in one shared identifier space."
---

## Kademlia: the XOR metric

A **distributed hash table** (DHT) maps keys to values with no central server. BitTorrent's **Mainline DHT** (BEP 5) is based on **Kademlia** (Maymounkov and Mazières, 2002) and stores "which peers have info-hash X". A current population estimate is absent because this review did not establish a reliable measurement.

Nodes and keys share a 160-bit ID space (info-hashes are 160 bits, so they fit). The distance between two IDs is their **XOR** (exclusive or: compare the IDs bit by bit, writing 1 where they differ and 0 where they match), read as an integer. With 4-bit IDs:

```formula
d(a, b) = a ⊕ b
d(0110, 0011) = 0101 = 5
where
d(a, b): the Kademlia distance between IDs a and b, a whole number
a, b: two node or key IDs, written here in binary (base 2); 160 bits long in Mainline DHT
⊕: XOR, exclusive or: each result bit is 1 if the two input bits differ and 0 if they are the same
In words: two IDs are as far apart as the binary number marking where their bits differ; 0110 and 0011 differ in the second and fourth bits, giving 0101, which is 5.
```

In Python the XOR operator is `^`, so `0b0110 ^ 0b0011` gives 5. A difference in a high bit outweighs all the lower bits together, so IDs that share a longer prefix are always closer.

XOR distance is a true metric, meaning it behaves like ordinary distance:

```formula
d(a, a) = 0
d(a, b) = d(b, a)
d(a, c) ≤ d(a, b) + d(b, c)
where
d(a, b): the XOR distance between IDs a and b
a, b, c: any three IDs
≤: is less than or equal to
In words: every ID is at distance zero from itself, distance is the same in both directions, and going via a third ID is never shorter than going direct (the triangle inequality).
```

Crucially, **for any point and any distance there is exactly one ID at that distance**, so all nodes can consistently rank IDs for a target. Completing a lookup also requires adequate live routing information. Original Kademlia replicates each value on a small, fixed number of the closest nodes (the contact/replication parameter k); Mainline DHT stores peer contact information associated with the hash.

### k-buckets

Each node keeps a DHT routing table made of **k-buckets**. In the basic distance-bucket model, each bucket covers a band of distances twice as wide as the one before:

```formula
2^i ≤ d < 2^{i+1}
s = 159 − i
where
i: the bucket number, from 0 (nearest) to 159 (farthest) for 160-bit IDs
d: the XOR distance from our own ID to a contact
s: the number of leading bits the contact's ID shares with ours
^: "to the power of"; 2^i is i copies of 2 multiplied together
≤: is less than or equal to
<: is less than
In words: bucket i holds contacts whose first differing bit is bit i counted from the right, so they share the 159 − i bits above it with us.
```

Each bucket holds a fixed maximum number of contacts, the contact-capacity parameter k: 20 as the original paper's example, and **8 in Mainline DHT**.

The capacity per bucket is bounded by k; contact **density** falls across exponentially larger distance regions. Mainline DHT uses a splitting routing-table implementation rather than a literal permanently allocated array of 160 buckets. It's like knowing every house on your street, a few people in your town and one person in each country.

When a bucket is full and a new contact appears, Kademlia **pings the least recently seen** contact and drops the newcomer if the old one answers. The paper's analysis of Gnutella traces motivated favouring older responsive contacts; current networks need not have the same uptime distribution. This impedes an attacker simply displacing old contacts with a flood of new IDs, but does not eliminate Sybil or eclipse attacks.

## Key takeaways
- Kademlia ranks node and key IDs by XOR distance in one shared identifier space.
- Bounded k-buckets retain contacts across distance scales; Mainline DHT uses a splitting table.

## Further reading
- [BEP 5](https://www.bittorrent.org/beps/bep_0005.html)
- [Original Kademlia paper](https://pdos.csail.mit.edu/~petar/papers/maymounkov-kademlia-lncs.pdf)
