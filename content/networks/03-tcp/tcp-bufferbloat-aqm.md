---
id: tcp-bufferbloat-aqm
sourceLesson: tcp-performance
title: Queueing delay, bufferbloat and AQM
level: advanced
minutes: 4
summary: How oversized queues add latency without adding throughput, and how CoDel and fq_codel fight back.
---

## Bufferbloat

Routers need buffers to absorb bursts. The traditional rule of thumb was one BDP of buffering per link. But memory became cheap, and many home routers, cable modems and mobile base stations were built with **far** more.

A saturated loss-based flow with a large tail-drop queue can sustain substantial queue occupancy: Reno and CUBIC keep growing their windows until the buffer is full and packets are dropped. ECN, AQM, competing traffic and sender limits change this behaviour. For a packet joining a FIFO, the wait is the backlog ahead of it divided by the rate at which the link drains it.

```formula reference
T_q = Q / R
where
T_q: queueing delay, how long a newly arrived packet waits before its own transmission starts, in seconds (s)
Q: the backlog queued ahead of it, in bits (multiply bytes by 8)
R: the rate at which the link drains the queue, in bits per second (bit/s)
s: seconds
bit/s: bits per second
In words: the wait is the amount queued ahead divided by how fast the link sends it, so a bigger full buffer or a slower link means a longer wait.
```

For example, 256 KiB queued at a 2 Mbit/s uplink is about 2.1 million bits, so a packet joining the back waits about a second, ignoring overhead and changes in link rate. Other queues or priority classes can see different delays. Sustained excessive queueing is **bufferbloat**: high throughput can coexist with poor latency under load. Every packet that waits behind that backlog, including a video call's or a game's, has about a second added to its round trip: a 20 ms idle path becomes a path of over a second while the upload runs.

Note what the bigger buffer did *not* do: the upload's throughput is set by the uplink rate, which is already fully used. Extra buffering beyond what bursts need only adds waiting.

> [!analogy] Real-world analogy: A longer queue at the same single till
> A shop with one till installs a much longer waiting lane. The cashier serves customers no faster, so the shop takes the same money per hour, but each customer now waits far longer, including someone who only wants to buy a stamp.
>
> **How it maps:** The cashier's speed is the link rate; the waiting lane is the router buffer; the customers are packets. A bigger buffer, kept full by a loss-based sender, adds waiting time without adding throughput, and the person with a stamp is the latency-sensitive flow stuck behind the bulk upload.
>
> **Where it stops:** People in a queue leave when it gets too long, whereas a TCP sender keeps the queue topped up until packets are dropped or marked. And AQM has no shop equivalent: it deliberately drops or marks packets early to tell senders to slow down.

## Active queue management

Active queue management signals congestion before excessive persistent queues develop. Delay is the signal used by CoDel; other AQM designs use other measurements:

- **CoDel** (Controlled Delay, [RFC 8289](https://www.rfc-editor.org/rfc/rfc8289)) tracks how long packets wait. Its usual target and interval are 5 ms and 100 ms. Persistent excess sojourn time can trigger drops or ECN marks; a remaining-backlog check avoids needlessly starving the link. The target is not a guaranteed maximum for every packet’s delay, and finite buffers can still drop bursts.
- **fq_codel** ([RFC 8290](https://www.rfc-editor.org/rfc/rfc8290)) adds **flow queueing**: packets are hashed into queues, with modified deficit round-robin scheduling and CoDel. This reduces interference between bulk and sparse traffic; hash collisions and shared bottlenecks mean isolation is not absolute.
- **L4S** ([RFC 9330](https://www.rfc-editor.org/rfc/rfc9330)) describes an architecture using scalable congestion control and compatible ECN/AQM behaviour to target low queueing delay. It is not merely a replacement name for CoDel or a guarantee of one-millisecond end-to-end latency.

**Pacing** spreads transmissions and can reduce bursts; **BBR** uses a path model but can still build queues. Locate the actual bottleneck. When it is an inaccessible modem/ISP queue, suitable shaping on a controlled router can move the bottleneck to a queue where AQM is effective; measure the throughput trade-off.

## Key takeaways

- FIFO backlog divided by service rate estimates waiting time before transmission under fixed-rate assumptions.
- Persistent excess queueing can coexist with high throughput and harm latency.
- CoDel, flow queueing, pacing and shaping address related but distinct causes of delay.

## Further reading

- [Introduction to bufferbloat — bufferbloat.net](https://www.bufferbloat.net/projects/bloat/wiki/Introduction/)
- [RFC 8289: Controlled Delay Active Queue Management](https://www.rfc-editor.org/rfc/rfc8289)
