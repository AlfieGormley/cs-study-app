---
id: api-idempotency
title: Idempotency and safe retries
level: intermediate
minutes: 12
summary: How idempotency keys make POST safe to retry, how Stripe implements them, and how to combine retries with backoff and jitter.
---

In a distributed system, every network call has three possible outcomes: success, failure, and **unknown**. The unknown case, a timeout, is the hard one. Did the server do the work or not?

An unknown outcome can be resolved by querying/reconciling operation status, or by retrying under an **idempotency contract**: repeating the logical operation has the same intended effect as doing it once. Do not blindly repeat an operation whose outcome remains ambiguous.

## Why "exactly once" is really "at least once + idempotent"

You can't guarantee a message is *delivered* exactly once over an unreliable network. You can only choose:

- **At most once**: never retry. Some requests are lost.
- **At least once**: retry until acknowledged. Some requests are duplicated.

One way to obtain an effectively-once business effect is at-least-once delivery plus atomic deduplication with the effect. Delivery, processing and external side effects are different guarantees. Systems such as Kafka idempotent producers and SQS FIFO have specific scopes and retention windows; no claim applies to every payment API or arbitrary external effect. (The messaging module goes deeper on delivery guarantees.)

## Naturally idempotent operations

Some operations are idempotent by design:

| Operation | Idempotent? |
|---|---|
| `SET balance = 110` | Yes |
| `balance = balance + 10` | No |
| `PUT /users/7 {...}` | Yes |
| `DELETE /users/7` | Yes |
| `POST /payments` | No |
| `INSERT ... ON CONFLICT DO NOTHING` | Yes |

Where you can, design operations to be naturally idempotent. Use absolute values instead of deltas. Let the client choose the resource id and use `PUT /orders/{client-uuid}` instead of `POST /orders`.

But many operations are inherently "do something": charge a card, send an email, ship a parcel. For those you need an **idempotency key**.

## Idempotency keys

The client generates a unique key (typically a UUIDv4) for each *logical* operation and sends it with the request. If it has to retry, it sends the **same key**.

```
POST /v1/payments HTTP/1.1
Idempotency-Key: 3f9a1c2e-7b4d-4e0a-9c11...
Content-Type: application/json

{"amount": 5000, "currency": "gbp",
 "customer": "cus_123"}
```

Under the endpoint’s documented key scope and retention contract, the server stores the key with the result and replays completed results. The diagram below shows only a serial happy path, not a safe concurrent implementation; the atomic claim and crash recovery described later are required.

```
Client         API           Store
  |--key K-->  |              |
  |            |--K exists?-->|
  |            |<--- no ------|
  |            | charge card  |
  |            |--save K,201->|
  |  X<--201---|  (lost)      |
  |--key K-->  |              |
  |            |--K exists?-->|
  |            |<--yes, 201---|
  |<---201-----|  (replayed)  |
```

For this completed serial operation, the card is charged once. The first `201` is lost; the retry receives the stored `201`.

> [!warning] The key must be generated before the first attempt
> If the client generates a fresh UUID inside its retry loop, every retry looks like a new operation. The key identifies the *intent* ("pay invoice 881"), so create it once, persist it if the app may restart, and reuse it for every attempt.

## How Stripe does it

Stripe's implementation is the reference design most teams copy:

- Keys are sent in the `Idempotency-Key` header on any `POST`. (`GET` and `DELETE` are already idempotent.)
- Stripe saves the **status code and body** of the first request with that key, *whether it succeeded or failed*, including a declined card or even a `500`. Replays return exactly that result.
- Keys may be pruned once they're at least **24 hours** old. A key reused after it's been pruned is treated as a new request.
- If a retry arrives with the same key but **different parameters**, Stripe returns an error rather than silently returning the old result. That protects against client bugs that reuse keys.
- A request that's rejected before execution starts (failed validation, or a concurrent request with the same key in progress) isn't saved, so it can safely be retried.

An expired IETF Internet-Draft for the **`Idempotency-Key` HTTP header** proposes `409 Conflict` for an operation still in progress and `422` for key reuse with a different payload. As checked in October 2026, it is not an RFC; treat these as a proposed convention, not a universal provider contract.

## Implementing it correctly

The naïve version has a race. Two retries arrive at the same time on different servers. Both check "does K exist?", both see "no", and both charge the card.

The fix is to **claim the key atomically before doing the work**:

```
1. INSERT INTO idem_keys
     (key, account, req_hash,
      status='started')
   -- unique on (account, key)
   -- if conflict: go to step 5
2. Do the work (charge card)
3. UPDATE idem_keys SET
     status='done', code=201,
     body='{...}'
4. Return 201
5. Existing row?
   - req_hash differs -> 422
   - status 'started' -> 409
   - status 'done'    -> replay
```

Key details:

- **Scope keys per account** (or per API key). Otherwise two customers who happen to pick the same key collide.
- **Fingerprint the operation** (method/route and semantically relevant parameters as well as the body) to reject key reuse for a different intent; canonicalization and key scope must be defined.
- **Handle crashes in step 2.** If the server dies after charging but before step 3, the row is stuck in `started`. Recovery needs either a timeout plus a check with the downstream system ("did charge X happen?"), or making step 2 itself idempotent by passing the same key downstream.

### Atomic phases

Brandur Leach, formerly of Stripe, describes going further for multi-step operations, implemented in Postgres. The work is split into **atomic phases**, each a single database transaction, with a **recovery point** recorded after each one. A retry resumes from the last recovery point rather than starting over.

```
started
  | tx1: create charge row
  v
charge_created
  | call card network
  |  (pass idem key downstream)
  v
card_charged
  | tx2: mark paid, enqueue email
  v
finished
```

Foreign calls (to the card network) happen *between* transactions, and are themselves idempotent because the same key is forwarded. Side effects like emails are enqueued atomically with the state change (the **transactional outbox** pattern). The relay can deliver twice; exactly-once external effects additionally require recipient-side deduplication or an idempotent sending API.

## Retries need backoff and jitter

Idempotency makes retries *safe*. It doesn't make them *wise*. If a service is struggling and every client retries immediately, you've multiplied the load on something that's already failing.

**Exponential backoff** spaces retries out:

```
attempt 1: wait 0.1 s
attempt 2: wait 0.2 s
attempt 3: wait 0.4 s
attempt 4: wait 0.8 s
cap at, say, 20 s
```

**Jitter** randomises the wait so clients don't retry in synchronised waves. AWS's "full jitter" is:

```
sleep = random(0, min(cap,
          base * 2^(attempt - 1)))
```

Without jitter, 10,000 clients that all failed at the same moment retry at the same moment, every time. That's a **thundering herd**.

Also:

- **Cap the number of attempts** according to the deadline and overload budget (for example, three total attempts).
- **Use a retry budget**: allow retries to add at most, say, 10% extra load, so a full outage doesn't triple your traffic.
- **Retry only retryable errors**: timeouts, connection resets, `429`, `502`, `503`, `504`, and an idempotency layer's `409` meaning "the original is still in progress". Never retry `400` or `422` unchanged.
- **Honour `Retry-After`** when the server sends one. It knows better than your backoff formula.
- **Retry at one layer only.** If the app, the SDK and a sidecar each allow 3 total attempts, one failure can become 3 × 3 × 3 = 27 attempts on the struggling backend.

## Key takeaways
- A timeout can leave the outcome **unknown**; reconcile status or retry within a documented idempotency contract.
- At-least-once delivery plus atomic deduplication can give an effectively-once effect within a defined failure model and retention window.
- Prefer naturally idempotent designs: absolute values, client-chosen ids, `PUT`.
- For `POST`, use an **idempotency key** generated once per logical operation and reused on every retry.
- Claim the key **atomically** before doing work, scope it per account, hash the request, and plan for crashes mid-operation.
- Pair retries with **exponential backoff, jitter, attempt caps and retry budgets**, and retry at only one layer.

## Further reading
- [Stripe API: Idempotent requests](https://docs.stripe.com/api/idempotent_requests)
- [Stripe blog: Designing robust and predictable APIs with idempotency](https://stripe.com/blog/idempotency)
- [IETF draft: The Idempotency-Key HTTP header field](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)
- [Brandur Leach: Implementing Stripe-like idempotency keys in Postgres](https://brandur.org/idempotency-keys)
- [AWS Builders' Library: Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
- [AWS Builders' Library: Timeouts, retries and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
