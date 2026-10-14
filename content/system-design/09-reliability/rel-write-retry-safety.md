---
id: rel-write-retry-safety
title: Safe retries and idempotency keys
level: intermediate
minutes: 2
summary: Distinguish retryable failures from unsafe repeated effects.
sourceLesson: rel-timeouts-retries
---

A timeout controls waiting; it does not prove that the server did nothing. Consider a payment whose response is lost after the charge commits. The question is whether another attempt changes the business result, rather than simply whether the network error looks temporary.

## Retries: when they help and when they hurt

Retries are worth it for **transient failures**: a dropped packet, a connection reset, one overloaded host behind a load balancer, a leader election. A later attempt may reach a healthy instance; correlated failures can persist across retries.

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

## Key takeaways

- A timed-out write may already have committed. Retry only when repeated effects are controlled.
- Coordinate concurrent uses of an idempotency key and reject changed parameters.
- Respect deadlines, retry budgets and provider key-retention limits; external effects require provider support or reconciliation.

## Further reading

- [Timeouts, retries and backoff with jitter (AWS Builders' Library)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Limit retries (AWS Well-Architected)](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_mitigate_interaction_failure_limit_retries.html)
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests)
