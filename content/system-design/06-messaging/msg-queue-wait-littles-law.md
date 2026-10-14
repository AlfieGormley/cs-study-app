---
id: msg-queue-wait-littles-law
title: Convert average queue depth into waiting time
level: basic
minutes: 2
summary: Use Little's Law with a stable queue and a consistent system boundary.
sourceLesson: msg-sync-vs-async
---

Queue depth is a count, but users experience a delay. Little's Law connects the two. Decide what you count before using it: messages still waiting correspond to queue wait, while waiting plus in-flight messages correspond to total time in that system.

## Little's Law: a useful sanity check

Little's Law says that, in a stable system (one where, over time, items leave as fast as they arrive), the average number of items in it equals the arrival rate times the average time each item spends in it. Rearranged, it tells you the average wait from two numbers a dashboard already shows:

```formula
L = λ × W
W = L / λ
W = 12000 msg / (400/s) = 30 s
where
L: the average number of items in the system; for a queue, the average queue depth, here 12,000 messages
λ: lambda, the average arrival rate, here 400 messages per second
W: the average time an item spends in the system, in seconds (s)
msg: messages
s: seconds; "/s" means per second
In words: average depth equals arrival rate times average wait, so depth divided by arrival rate gives the average wait.
```

So a queue that receives 400 messages per second and holds a steady 12,000 makes each message wait about 30 seconds on average. This turns "queue depth" (which dashboards show) into "delay" (which users feel). It holds for long-run averages in a stable system; while a queue is growing during a burst, the momentary numbers need not match it.

## Key takeaways

- In a stable system, average depth divided by average arrival rate gives average time spent inside the measured boundary.
- Waiting-only depth measures time before processing; including active work measures the whole residence time.
- Use long-run averages; a snapshot taken during burst growth need not obey the steady-state estimate.

## Further reading

- [Little's law (Wikipedia)](https://en.wikipedia.org/wiki/Little%27s_law)
- [Avoiding insurmountable queue backlogs (Amazon Builders' Library)](https://aws.amazon.com/builders-library/avoiding-insurmountable-queue-backlogs/)
