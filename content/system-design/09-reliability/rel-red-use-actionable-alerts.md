---
id: rel-red-use-actionable-alerts
title: RED, USE and actionable alerts
level: intermediate
minutes: 2
summary: Separate user symptoms from resource causes when choosing dashboards and pages.
sourceLesson: rel-observability
---

Metrics aggregate, logs explain events and traces connect the request path. These checklists decide which measurements deserve attention. The goal is a page that prompts useful action for users, with enough diagnostic signals to identify the cause.

## What to measure: RED and USE

Two complementary checklists stop you drowning in metrics.

### RED: for every service (request-driven)

Tom Wilkie's **RED method**, for each service or endpoint:

- **Rate**: requests per second.
- **Errors**: failed requests per second (or ratio).
- **Duration**: latency distribution (histogram).

RED describes what users experience, which makes it a good basis for dashboards and SLIs.

### USE: for every resource

Brendan Gregg's **USE method**, for each resource (CPU, memory, disk, network, connection pools, queues):

- **Utilisation**: how busy a resource is, such as busy-time percentage for a device or used capacity for memory and pools.
- **Saturation**: extra work it can't service yet (run-queue length, swap, queue depth).
- **Errors**: error events (disk errors, dropped packets).

USE helps diagnose *why* a service's RED metrics went bad.

| Method | Applies to | Answers |
|---|---|---|
| RED | services | Are users OK? |
| USE | resources | What's the bottleneck? |

Google's SRE book recommends the **four golden signals**: latency, traffic, errors and saturation. That's essentially RED plus the most important USE question: how full is the service?

> [!tip] Alert on symptoms, investigate with causes
> Page a human on symptoms users feel (RED metrics, SLO burn). Use cause metrics (USE: CPU, disk, GC) on dashboards for diagnosis. Paging on "CPU utilisation above 80%" wakes people for things that may not matter to users.

## Key takeaways

- RED measures service rate, errors and duration.
- USE checks each resource’s utilisation, saturation and errors.
- Page on actionable user symptoms and investigate their causes with resource telemetry.

## Further reading

- [The USE method (Brendan Gregg)](https://www.brendangregg.com/usemethod.html)
- [The RED method (Grafana Labs)](https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/)
- [Monitoring distributed systems (Google SRE book)](https://sre.google/sre-book/monitoring-distributed-systems/)
