---
id: msg-burst-backlog-draining
title: Absorb a burst and calculate the drain time
level: basic
minutes: 4
summary: Work out backlog growth, spare drain capacity and the longest FIFO wait.
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

Without a queue, you need 20 workers (2,000 ÷ 100) sitting mostly idle to survive the peak. With a queue and 2 workers (200 per second capacity), the backlog grows while arrivals exceed capacity:

```formula
B = (λ_burst − μ) × T_burst
B = (2000/s − 200/s) × 30 s
B = 1800/s × 30 s = 54000 msg
where
B: the backlog: messages waiting in the queue when the burst ends
λ_burst: lambda, the arrival rate during the burst, here 2,000 messages per second
μ: mu, the processing capacity of all workers together, here 2 workers × 100 = 200 messages per second
T_burst: how long the burst lasts, here 30 seconds
s: seconds; "/s" means per second
msg: messages
In words: during a burst the queue grows by the excess of arrivals over capacity, for every second the burst lasts.
```

After the burst, arrivals drop to 50 per second, so the workers eat into the backlog with whatever capacity is left over:

```formula
T_drain = B / (μ − λ_after)
T_drain = 54000 msg / (200/s − 50/s)
T_drain = 54000 msg / (150/s) = 360 s
where
T_drain: the time after the burst until the queue is empty again, in seconds (s); 360 s is 6 minutes
B: the backlog at the end of the burst, here 54,000 messages
μ: mu, the total processing capacity, here 200 messages per second
λ_after: lambda, the arrival rate after the burst, here 50 messages per second
msg: messages
s: seconds; "/s" means per second
In words: the backlog shrinks only by the spare capacity left after serving new arrivals, so it takes 6 minutes to clear, not 54,000 ÷ 200 = 4.5 minutes.
```

The message at the back of the burst waits roughly as long as it takes the workers to get through everything in front of it:

```formula
W_max ≈ B / μ
W_max ≈ 54000 msg / (200/s) = 270 s
where
W_max: the longest wait in first-in, first-out (FIFO) order: the wait of the last message of the burst, in seconds (s)
B: the backlog at the end of the burst, 54,000 messages
μ: mu, the total processing capacity, 200 messages per second
≈: approximately equal to
msg: messages
s: seconds; "/s" means per second
In words: the last message of the burst waits about 4.5 minutes, because 54,000 messages are ahead of it and the workers do 200 a second.
```

So you trade **latency** (the longest wait is about 270 seconds, while the queue returns to empty after 6 minutes) for **cost and stability** (10× fewer workers in this idealised fixed-rate model; consumer admission and downstream capacity still need protection). That trade is acceptable when the product permits the resulting delay, including an explicit pending-job experience.

> [!warning] A queue is not infinite capacity
> Load levelling only works if the **average** arrival rate is below the processing rate. If arrivals average 250 per second and you can do 200, the backlog grows forever. A queue hides overload; it does not fix it. Always alarm on queue depth and on the age of the oldest message.

## Key takeaways

- During overload, the backlog grows by the difference between arrivals and processing capacity.
- After a burst, new arrivals consume capacity too; only spare capacity drains the backlog.
- Average arrivals must remain below processing capacity: a queue cannot cure sustained overload.

## Further reading

- [Queue-Based Load Leveling pattern (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling)
- [Avoiding insurmountable queue backlogs (Amazon Builders' Library)](https://aws.amazon.com/builders-library/avoiding-insurmountable-queue-backlogs/)
