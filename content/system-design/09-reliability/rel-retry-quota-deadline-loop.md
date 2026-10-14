---
id: rel-retry-quota-deadline-loop
title: Retry quotas and a deadline-aware loop
level: intermediate
minutes: 4
summary: Bound extra retry work and combine quota, timeout and backoff in one call path.
sourceLesson: rel-timeouts-retries
---

The earlier retry units established safety, full jitter and one retry layer. Here the budget decides whether an otherwise safe retry is allowed. The displayed loop is a dependency-injected fragment: the RPC, clock, sleeper, retry predicate, quota and exception classes must be supplied by the application.

## Retry budgets and token buckets

A **retry budget** limits retries to a proportion of requests, e.g. "retries may be at most 10% of original calls to this dependency". When things are healthy, the occasional failure gets retried. When everything is failing, the cap decides the load:

```formula
L_max = N(1 + β)
L_max = 1000 calls/s × (1 + 0.1)
L_max = 1100 calls/s
where
L_max: the most calls per second the dependency can receive, including retries
N: the original (first-try) calls per second, here 1,000
β: the retry budget, the most retries allowed as a fraction of original calls, here 10% = 0.1
calls/s: calls per second
In words: with a 10% budget, total load can never exceed 1.1 times normal, compared with 3 times normal (+200%) when every request may make 3 attempts.
```

The AWS SDKs implement a version with a **token bucket** (the "retry quota"):

This executable event model keeps the original refill, charge and refund operations. The caller must invoke the matching method after each outcome. It assumes one fixed retry cost and serial access; it does not implement a production SDK, synchronization or a fractional traffic budget.

```python
class RetryQuota:
  def __init__(self, capacity, cost):
    self.capacity = capacity
    self.cost = cost
    self.tokens = capacity

  def first_success(self):
    # Healthy initial calls replenish quota.
    self.tokens = min(self.capacity,
      self.tokens + 1)

  def try_retry(self):
    # Pay before a retry reaches the
    # service.
    if self.tokens < self.cost:
      return False
    self.tokens -= self.cost
    return True

  def retry_success(self):
    # Refund only the successful retry's
    # cost.
    self.tokens = min(self.capacity,
      self.tokens + self.cost)
```

When enough calls succeed, refunds keep quota available; retries still consume tokens and network resources. During a sustained outage the bucket drains and clients stop retrying. The documented 2026 opt-in standard behaviour starts with 500 tokens, charges 14 for transient-error retries and five for throttling retries, refunds the successful retry’s cost, and restores one token for a first-attempt success. A later success does not refund earlier failed retries. Other SDK versions and modes differ, and a finite initial bucket permits a burst rather than enforcing an exact traffic fraction.

The bucket is typically per client instance; exact scope depends on SDK. A thousand hosts each with their own bucket still add up, which is why server-side signals matter too.

Google's SRE book describes a similar pair of limits: a per-request cap (a request that has failed three times is not retried again) plus a per-client cap where retries must stay below 10% of requests. The book notes that the per-request cap alone can still triple load in the worst case, whereas the 10% cap limits growth to about 1.1×.

> [!warning] Retries hide failures
> Retries make dashboards look green while users wait. Always emit a metric for retry rate. A rising retry rate is often the earliest sign of trouble.

## Putting it together

```python
def call(req, deadline):
  # One quota is shared across requests.
  for attempt in range(MAX_ATTEMPTS):
    # Earlier calls and sleeps spent budget.
    remaining = deadline - now()
    if remaining <= 0: raise Timeout
    try:
      # A successful RPC returns
      # immediately.
      return rpc(req,
        timeout=min(remaining, PER_TRY))
    except Exception as e:
      # Predicate admits expected faults
      # only.
      if not retryable(e): raise
      if attempt + 1 == MAX_ATTEMPTS: break
      # Refuse extra work when quota is
      # empty.
      if not budget.try_acquire(): raise
      # Full jitter spreads retry arrival
      # time.
      delay = random.uniform(0,
        min(CAP, BASE * 2**attempt))
      left = deadline - now()
      if left <= 0: raise Timeout
      # Never intentionally sleep past
      # budget.
      sleep(min(delay, left))
  # Every allowed attempt failed.
  raise Exhausted
```

## Key takeaways

- A fractional retry budget caps aggregate extra traffic; a finite token quota has its own burst and refund behaviour.
- Client-local quotas add up across hosts. Retain server-side overload signals and capacity limits.
- Check the remaining deadline before calls and sleeps, and classify retryable failures narrowly.

## Further reading

- [Timeouts, retries and backoff with jitter (AWS Builders' Library)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Handling overload (Google SRE book)](https://sre.google/sre-book/handling-overload/)
- [Addressing cascading failures (Google SRE book)](https://sre.google/sre-book/addressing-cascading-failures/)
- [AWS SDK retry quota](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html)
