---
id: rel-admission-goodput-priority
title: Admission limits, deadlines and priority
level: intermediate
minutes: 4
summary: Preserve goodput by shedding excess work cheaply before expensive processing.
sourceLesson: rel-overload-protection
---

Goodput counts useful completions while throughput counts completed work regardless of usefulness. This unit protects the former. A capacity-limited server cannot make every caller happy, but early admission rejection can keep the accepted requests within their deadlines.

## Load shedding

When a server is beyond capacity, it should **reject excess work quickly** rather than accept everything and serve it all late. An early `503` can cost far less than normal processing; a request that times out after doing 2 s of work costs 2 s of capacity for nothing.

The AWS Builders' Library describes the principle: protect **goodput** (useful completed work) by shedding just enough to keep latency within the clients' timeouts.

### How to decide what to shed

- **Concurrency limits**: cap in-flight requests (e.g. 100). Above that, reject. Use Little’s law as a starting estimate, then load-test the cap against latency and burst requirements. Adaptive versions (like Netflix's concurrency-limits library) adjust the cap from observed latency, TCP-congestion style.
- **Queue time**: if a request waited in the queue longer than the client's timeout, drop it if its useful work is tied to that deadline. Durable accepted jobs may still need completion even after a client disconnects. A system can switch from oldest-first to newest-first as the queue builds up (adaptive LIFO), favouring requests whose callers are more likely still waiting. This is a heuristic, not a guarantee; it can starve older work and still needs deadlines and rejection.
- **Priority / criticality**: shed lower-priority traffic first. Google tags requests as `CRITICAL_PLUS`, `CRITICAL`, `SHEDDABLE_PLUS` and `SHEDDABLE`, and sheds from the bottom.

Choose a concurrency limit from measured workload behaviour:

Use measured healthy throughput and mean latency to estimate typical in-flight work, then test a bounded cap with headroom. For example, a service averaging 80 in-flight requests might start testing a cap of 100; bursts and latency targets determine whether that choice works.

The numbers here are illustrative. The admission check might look like this in code:

This dependency-injected fragment assumes `slots` performs an atomic check-and-acquire and trusted policy has already assigned the request priority. The clock, limits, rejection response and processor are application dependencies.

```python
def admit(req):
  # Expired work cannot help this caller.
  if req.deadline <= now():
    return reject(503)
  # Priority is assigned by trusted policy.
  # Lower classes have smaller limits.
  cap = limits[req.trusted_priority]
  # Check and reserve atomically.
  if not slots.try_acquire_below(cap):
    return reject(503, retry_after=1)
  try:
    return process(req)
  finally:
    # Release on success and exceptions
    # alike.
    slots.release()
```

> [!tip] Make rejection cheap
> Shedding only works if rejecting is much cheaper than serving. Use cheap early admission checks before expensive body parsing or database access. Authenticate or validate any priority/tenant identity used for admission; never trust a caller-supplied criticality flag to bypass limits.

## Key takeaways

- Reject before costly parsing or database work, and release admission slots on every exit path.
- Discard work whose usefulness ended with its deadline; durable accepted jobs can have different obligations.
- Assign priorities with trusted policy and shed lower-priority work first. A concurrency limit must be measured under target latency.

## Further reading

- [Using load shedding to avoid overload (AWS Builders' Library)](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/)
- [Handling overload (Google SRE book)](https://sre.google/sre-book/handling-overload/)
