---
id: rel-timeouts-retries
title: Timeouts, retries, backoff and jitter
level: intermediate
minutes: 12
summary: Set timeouts from latency data, retry only what's safe, add exponential backoff with jitter, and stop retry storms with budgets.
---

Every remote call can hang, fail or succeed slowly. Timeouts bound how long you wait; retries turn transient failures into successes. Used carelessly, though, retries can contribute to large outages: they multiply load at the exact moment a system is weakest.

This lesson covers how to set each one, and how to keep them from turning a blip into a meltdown.

## Timeouts: every call needs one

A call with no timeout can hold a thread, a connection and memory forever. Many client libraries default to *no timeout* or to absurdly long ones (some HTTP clients default to minutes). Under a gray failure (a dependency that's slow but alive), these calls pile up until the caller runs out of threads and fails too.

There are usually several timeouts on one call:

| Timeout | Bounds | Typical value |
|---|---|---|
| Connect | Connection establishment; TLS/DNS coverage depends on client | Measure for the client and network |
| Request / read | Response wait or inactivity interval, depending on client | Choose from measured latency |
| Overall deadline | Whole operation | user's budget |

### Choosing the value

The AWS Builders' Library recommends picking a timeout from the dependency's **latency distribution**: choose an acceptable false-timeout rate (say 0.1%) and set the timeout at the matching percentile (p99.9), plus some padding.

- Too short: you time out healthy-but-slightly-slow requests, retry them and *add* load.
- Too long: callers wait on doomed requests and exhaust their resources.

### Deadline propagation

A user-facing request with a 2-second budget calls A, which calls B, which calls C. If each hop independently uses a 2 s timeout, C may keep working for seconds after the user has given up.

The fix is to propagate a **deadline**, not a timeout. gRPC supports this when the language/runtime propagates the incoming context to outgoing calls. The remaining budget travels with the request; handlers must observe cancellation and stop their own work, because the deadline does not forcibly roll back or terminate every side effect.

```
User deadline: T+2000ms
  A starts T+0     remaining 2000
  A → B at T+300   remaining 1700
  B → C at T+900   remaining 1100
  C: if remaining < its p50, fail fast
```

## Retries: when they help and when they hurt

Retries are worth it for **transient** failures: a dropped packet, a connection reset, one overloaded host behind a load balancer, a leader election. A later attempt may reach a healthy instance; correlated failures can persist across retries.

They are harmful when:

- The failure is **persistent** (bad request, auth error, bug). Retrying a `400` or `403` just wastes capacity.
- The dependency is **overloaded**. Retrying adds load to the thing that's already drowning.
- The operation is **not idempotent**. Retrying "charge £50" after a timeout might charge twice.

### Idempotency first

A timeout tells you nothing about whether the server did the work. Before retrying writes, make them idempotent:

```
POST /payments
Idempotency-Key: 7f3a-…-c91e
{ "amount": 5000, "currency": "GBP" }
```

The server coordinates concurrent requests and stores the key with the result. Stripe returns the stored result for the same key and parameters once execution has begun, including stored failures. Its keys may be pruned after at least 24 hours; reuse after pruning can execute a new request. External effects need compatible provider idempotency or reconciliation, because a local database transaction cannot atomically commit an external charge.

### What to retry

| Response | Retry? |
|---|---|
| Connection reset / refused | If no effect is possible, or operation is idempotent |
| Timeout (idempotent op) | If retryable and budget/deadline allow |
| `429 Too Many Requests` | If safe to repeat; honour `Retry-After` and budget |
| `503 Service Unavailable` | If safe to repeat, with backoff and budget |
| `500` | Maybe; often a bug |
| `400`, `401`, `403`, `404` | Usually no blind retry; fix the request or follow a specific recovery protocol |

## Exponential backoff

Retrying immediately after a failure hits the dependency again while it's still struggling. **Exponential backoff** waits longer after each failure:

```
sleep = min(cap, base * 2^attempt)

base=100ms, cap=10s:
  attempt 0: 100ms
  attempt 1: 200ms
  attempt 2: 400ms
  attempt 3: 800ms
  attempt 4: 1.6s ...
```

Backoff gives the dependency time to recover and spreads load over time. But on its own it has a nasty property.

## Jitter: breaking the synchronisation

Suppose 1,000 clients all fail at the same instant (a dependency restarted). With pure exponential backoff, they all wait exactly 100 ms, then all retry together, then all wait 200 ms, then all retry together again. The retries arrive in **synchronised waves** that look like a series of load spikes.

```
No jitter:          Full jitter:
 ▲                   ▲
 █   █    █          ▄▄▄▄▄▄▄▄▄▄▄▄
 █   █    █          ████████████
 └────────────▶      └────────────▶
  spikes              spread out
```

**Jitter** adds randomness so retries spread out. Marc Brooker's analysis on the AWS Architecture Blog compared variants:

```
// Full jitter (recommended default)
sleep = random(0, min(cap, base * 2^n))

// Equal jitter
t = min(cap, base * 2^n)
sleep = t/2 + random(0, t/2)

// Decorrelated jitter
sleep = min(cap,
            random(base, prev_sleep * 3))
```

In his simulations, full jitter used the fewest calls; decorrelated jitter finished slightly sooner but did more work; equal jitter was the loser, doing slightly more work than full jitter and taking much longer. Equal jitter's one attraction is that it guarantees a minimum wait. All three are vastly better than no jitter.

The AWS SDKs use full jitter: in standard retry mode the delay is `random(0, 1) × min(cap, base × 2^retry)`, with a 20-second cap.

> [!tip] Jitter everything periodic
> The same synchronisation problem hits cron jobs, cache expiry and health checks. Add jitter to TTLs and scheduled tasks too, or every client refreshes on the hour.

## Retry amplification across layers

This is where retries cause outages. Suppose a request passes through three layers and each layer makes **up to 3 attempts** (1 try + 2 retries):

```
Client  ──3x──▶ API
API     ──3x──▶ Service
Service ──3x──▶ Database
```

If the database is completely down, one user request produces:

- 3 attempts at the API
- 3 × 3 = 9 at the service
- 3 × 3 × 3 = **27** at the database

In general, `attempts^layers`, where *layers* counts the hops that retry. With 5 layers of 3 attempts that's 243×. The database, which was perhaps just overloaded, now receives 27 times its normal traffic and has no chance to recover. This is a **retry storm**.

Partial failure amplifies too, just less dramatically. With a single retrying layer and an independent, unchanged failure probability `p` per attempt, the expected attempts per request with up to 3 tries is `1 + p + p²`:

| Failure rate p | Attempts per request |
|---|---|
| 10% | 1.11× |
| 50% | 1.75× |
| 90% | 2.71× |
| 100% | 3× |

The extra load arrives exactly as the dependency gets worse, which is a positive feedback loop: more failures cause more retries, which cause more failures.

### Fixes for amplification

1. **Retry at one layer only.** AWS's Well-Architected guidance is to implement retries at only one level of the stack. Usually that's the layer immediately above the failing dependency; every other layer fails fast and passes the error up.
2. **Retry budgets.** Cap retries as a fraction of total traffic.
3. **Propagate "don't retry" signals.** If a downstream is overloaded, return an error that tells upstream callers not to retry it. Google uses an explicit "overloaded; don't retry" response, so callers receiving that signal suppress retries.

## Retry budgets and token buckets

A **retry budget** limits retries to a proportion of requests, e.g. "retries may be at most 10% of original calls to this dependency". When things are healthy, the occasional failure gets retried. When everything is failing, retries are capped at +10% load instead of +200%.

The AWS SDKs implement a version with a **token bucket** (the "retry quota"):

```
on first-try success:
  bucket = min(max, bucket + 1)
on retryable failure:
  if bucket >= cost:
    bucket -= cost; retry
  else:
    give up (return the error)
on success after a retry:
  refund that retry's cost
```

When most calls succeed, the bucket stays full and retries are free. During a sustained outage the bucket drains and clients stop retrying, automatically. In the SDKs' current standard mode the bucket holds 500 tokens and a retry costs several tokens (more for transient errors than for throttling), so each retry has to be "paid for" by several successes. The exact costs have changed between SDK versions, so treat them as tunables.

The bucket is typically per client instance; exact scope depends on SDK. A thousand hosts each with their own bucket still add up, which is why server-side signals matter too.

Google's SRE book describes a similar pair of limits: a per-request cap (a request that has failed three times is not retried again) plus a per-client cap where retries must stay below 10% of requests. The book notes that the per-request cap alone can still triple load in the worst case, whereas the 10% cap limits growth to about 1.1×.

> [!warning] Retries hide failures
> Retries make dashboards look green while users wait. Always emit a metric for retry rate. A rising retry rate is often the earliest sign of trouble.

## Putting it together

```
def call(req, deadline):
  for attempt in range(MAX_ATTEMPTS):
    remaining = deadline - now()
    if remaining <= 0: raise Timeout
    try:
      return rpc(req,
        timeout=min(remaining, PER_TRY))
    except Exception as e:
      if not retryable(e): raise
      if attempt + 1 == MAX_ATTEMPTS: break
      if not budget.try_acquire(): raise
      delay = random(0,
        min(CAP, BASE * 2**attempt))
      left = deadline - now()
      if left <= 0: raise Timeout
      sleep(min(delay, left))
  raise Exhausted
```

## Key takeaways

- Every remote call needs a timeout; pick it from the dependency's latency percentiles and propagate deadlines across hops.
- Retry only transient failures on idempotent operations; use idempotency keys for writes.
- Exponential backoff spaces retries out; jitter (full jitter is a good default) stops clients synchronising into waves.
- Retries amplify multiplicatively across layers (`attempts^layers`), so retry at one layer only.
- Retry budgets and token buckets cap retry load during sustained failure, reducing retry amplification; separate capacity controls remain necessary because even bounded extra load can overload a dependency.

## Further reading

- [Timeouts, retries and backoff with jitter (AWS Builders' Library)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Exponential backoff and jitter (AWS Architecture Blog)](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- [Handling overload (Google SRE book)](https://sre.google/sre-book/handling-overload/)
- [Addressing cascading failures (Google SRE book)](https://sre.google/sre-book/addressing-cascading-failures/)
- [Limit retries (AWS Well-Architected)](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_mitigate_interaction_failure_limit_retries.html)
