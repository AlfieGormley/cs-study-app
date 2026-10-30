---
id: app-kademlia-lookup-and-threats
title: "Kademlia lookup progress and hostile identities"
level: advanced
minutes: 3
sourceLesson: app-p2p-webrtc
summary: "A lookup queries progressively closer candidates and completes its closest responsive candidate set."
---

Kademlia gives each node and key an identifier, using XOR as distance. A node retains bounded contact lists called k-buckets across distance scales. Mainline BitTorrent DHT uses 160-bit IDs and a contact-capacity parameter of eight.

### Lookup

To find the nodes closest to a target identifier (called T in the API examples):

1. Pick the few closest contacts you know (the paper calls this concurrency parameter α, alpha, with 3 as its example) and send each `find_node(T)` (or `get_peers(T)` in BitTorrent) in parallel.
2. Each reply contains the k closest contacts *it* knows.
3. Query the closest ones you haven't asked yet.
4. If a round finds no closer contact, query the remaining unqueried contacts among the k closest seen. Complete when the closest responsive candidates have been checked; handle failed contacts/timeouts rather than stopping after the first non-improving round.

With populated, maintained routing buckets and the model's ID-distribution assumptions, prefix progress supports **O(log n)** lookup scaling, where n is the number of nodes in the network. Big O notation describes how a cost grows as n grows, ignoring constant factors; log n is the logarithm of n, which grows very slowly. Roughly, each round fixes at least one more bit of shared prefix, and the number of bits needed to single out the closest nodes among n is about the base-2 logarithm of n: how many times you can halve n before reaching 1, about 20 for a million nodes. It is not a guarantee that every response halves numeric XOR distance or that an unavailable key will be found. Churn, timeouts, sparse tables and adversaries matter, so real lookups can take more rounds than the model suggests.

XOR distance is symmetric: a query sender can also be a useful routing contact for its receiver. Subject to routing-table admission and maintenance rules, learning from incoming messages improves coverage without contacting every node. This is an opportunity to learn a contact, not evidence that the sender is honest.

Mainline DHT messages are bencoded dictionaries over UDP (KRPC): `ping`, `find_node`, `get_peers` (returns peers, or closer nodes) and `announce_peer`. To stop arbitrary IPs being announced, `get_peers` replies include an IP-bound **announce token** that the requester must return to the issuing node when announcing. It limits announcement of other IP addresses; it does not prove the announcing peer actually has the content.

> [!warning] Sybil attacks
> Anyone can choose a node ID. An attacker who creates many IDs close to a target info-hash can hide or censor it ("eclipse"). Mitigations include tying IDs to IP addresses (BEP 42) and querying several disjoint paths.

## Key takeaways
- A lookup queries progressively closer candidates and completes its closest responsive candidate set.
- Logarithmic scaling needs routing/distribution assumptions; Sybil and eclipse attacks remain risks.

## Further reading
- [BEP 5](https://www.bittorrent.org/beps/bep_0005.html)
- [BEP 42](https://www.bittorrent.org/beps/bep_0042.html)
- [Original Kademlia paper](https://pdos.csail.mit.edu/~petar/papers/maymounkov-kademlia-lncs.pdf)
