---
id: msg-burst-backlog-draining
title: Absorb a burst: backlog and drain time
level: basic
minutes: 4
summary: Predict how a burst builds a backlog, why only spare capacity drains it and how long the last message waits.
sourceLesson: msg-sync-vs-async
---

A durable queue can hold a temporary traffic spike while a smaller worker fleet catches up. The useful question is how long users must wait, and whether the fleet can ever catch up.

## Load levelling

The most common practical reason to add a queue is to protect a slow or fragile component from bursts. This is the **queue-based load levelling** pattern.

Imagine an image-thumbnail service. Uploads arrive in bursts: 2,000 per second for 30 seconds after a marketing email, then 50 per second for the rest of the hour. Each worker can process 100 images per second.

```
 arrivals/s
 2000 ┤ ████
      │ ████
      │ ████
  200 ┤ ████ - - - - - - - - - workers
   50 ┤ ████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
      └──────────────────────▶ time
```

Without a queue, you need 20 workers (2,000 ÷ 100) sitting mostly idle to survive the peak. With a queue and 2 workers (200 per second capacity), the backlog grows while arrivals exceed capacity, and shrinks only by the capacity left over once new arrivals are served:

This fixed-rate estimate assumes an initially empty queue, a burst faster than processing, and post-burst arrivals slower than processing. It ignores startup delays and variation between jobs.

```formula reference
B = (λ_burst − μ) × T_burst
T_drain = B / (μ − λ_after)
where
B: the backlog: messages waiting in the queue when the burst ends
λ_burst: lambda, the arrival rate during the burst, in messages per second
μ: mu, the processing capacity of all workers together, in messages per second
T_burst: how long the burst lasts, in seconds
T_drain: the time after the burst until the queue is empty again, in seconds
λ_after: lambda, the arrival rate after the burst, in messages per second
In words: during a burst the queue grows by the excess of arrivals over capacity for as long as the burst lasts; afterwards it drains only at the spare capacity, so new arrivals slow the recovery.
```

In the thumbnail example the queue gains 1,800 messages a second for 30 seconds, leaving about 54,000 waiting. Afterwards the workers still have to serve 50 new uploads a second, so only 150 a second of their 200 is spare: the queue takes about 6 minutes to empty, not the 4.5 minutes you get by dividing the backlog by full capacity.

Those 4.5 minutes do mean something: in first-in, first-out (FIFO) order, the last message of the burst waits roughly as long as the workers take to clear the 54,000 ahead of it, about 270 seconds. The queue is empty only later, because new arrivals keep joining behind it.

So you trade **latency** (the longest wait is about 4.5 minutes, and the queue returns to empty after about 6) for **cost and stability** (10× fewer workers in this idealised fixed-rate model; consumer admission and downstream capacity still need protection). That trade is acceptable when the product permits the resulting delay, including an explicit pending-job experience.

> [!analogy] Real-world analogy: a bath with the tap on and the plug half out
> Turn the tap on full and the water level rises even though the plughole is draining. Turn the tap down to a trickle and the bath empties, but only as fast as the plughole beats the trickle. Leave the tap running faster than the plughole on average and the bath eventually overflows.
>
> **How it maps:** The tap is the arrival rate, the plughole is the workers' total capacity and the water level is the backlog. The level rises at the difference between them during the burst and falls only at the spare capacity afterwards, which is why recovery is slower than "backlog ÷ capacity".
>
> **Where it stops:** Water has no order, so the bath says nothing about how long the *last* message waits in FIFO order. Real worker capacity also varies with message size and downstream health. And a bath overflows visibly, whereas a queue can grow silently until retention deletes old messages, which is why you alarm on depth and oldest-message age.

> [!warning] A queue is not infinite capacity
> Load levelling only works if the **average** arrival rate is below the processing rate. If arrivals average 250 per second and you can do 200, the backlog grows forever. A queue hides overload; it does not fix it. Always alarm on queue depth and on the age of the oldest message.

## Key takeaways

- During overload, the backlog grows by the difference between arrivals and processing capacity.
- After a burst, new arrivals consume capacity too; only spare capacity drains the backlog.
- Average arrivals must remain below processing capacity: a queue cannot cure sustained overload.

## Further reading

- [Queue-Based Load Leveling pattern (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling)
- [Avoiding insurmountable queue backlogs (Amazon Builders' Library)](https://aws.amazon.com/builders-library/avoiding-insurmountable-queue-backlogs/)
