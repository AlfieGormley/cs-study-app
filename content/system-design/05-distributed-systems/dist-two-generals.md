---
id: dist-two-generals
title: Why acknowledgements cannot guarantee agreement
level: basic
minutes: 3
summary: Use the Two Generals argument to understand what retries and acknowledgements can promise.
sourceLesson: dist-why-hard
---

A reply gives useful evidence, but asking the other party to acknowledge that reply starts the same uncertainty again. The Two Generals thought experiment isolates that limit.

## The Two Generals problem

This thought experiment proves that **no protocol over an unreliable channel can guarantee that two parties agree** to act together.

Two armies, A and B, camp on hills either side of a city. They win only if they attack at the same time. Their only means of communication is a message carrier who must run through the valley, where they might be captured.

```
General A                General B
  |-- "attack at 9" ------>|
  |                        | got it, but
  |                        | does A know?
  |<----- "ack" -----------|
  | got ack, but does B    |
  | know I got it?         |
  |-- "ack of ack" ------->|
  |          ... forever   |
```

Suppose some protocol worked, and consider the *shortest* sequence of messages that results in both attacking. The last message in that sequence might be captured. Whoever sent it can't know whether it arrived, so the decision must not depend on it, meaning a shorter protocol also works. Repeat the argument and you reach zero messages, which obviously can't coordinate anything. Contradiction.

### What it means in practice

You can't get *certain* agreement over a lossy network, so real systems settle for something weaker:

- **Probabilistic confidence**: send many message carriers; the chance all are lost shrinks quickly.
- **Idempotent retries**: keep retrying until acknowledged, and make repeats harmless.
- **Agreement among a majority**: consensus algorithms (covered later in this module) don't need every node to know; a majority is enough, and they tolerate lost messages by retrying.

TCP's connection close runs into the same limitation: the final ACK can be lost, and the side that sent it can't know. That's one reason the `TIME_WAIT` state exists: it lingers so it can re-send the ACK if the peer re-sends its FIN.

> [!note] Two Generals vs Byzantine Generals
> Two Generals is about **unreliable messages** between honest parties. The Byzantine Generals problem is about **dishonest or arbitrarily faulty nodes**. Practical Byzantine fault tolerance (PBFT and its descendants) needs more than three nodes per traitor tolerated; most data-centre systems assume nodes are honest and only tolerate crashes, which needs a little over two nodes per fault. The next unit gives the exact counts for these quorum models.

## Key takeaways
- A final acknowledgement can always be lost, so another acknowledgement cannot create certain common knowledge.
- Retries, idempotency and majority agreement offer useful weaker guarantees under their own assumptions.
- Two Generals concerns unreliable communication; Byzantine Generals concerns arbitrarily faulty participants.

## Further reading
- [Two Generals' Problem (Wikipedia)](https://en.wikipedia.org/wiki/Two_Generals%27_Problem)
- [Byzantine fault (Wikipedia)](https://en.wikipedia.org/wiki/Byzantine_fault)
