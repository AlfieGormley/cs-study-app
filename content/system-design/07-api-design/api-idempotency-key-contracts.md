---
id: api-idempotency-key-contracts
title: Idempotency keys and replay contracts
level: intermediate
minutes: 3
summary: Reuse one key for one logical operation and understand retention, mismatches and in-progress requests.
sourceLesson: api-idempotency
---

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

## Stripe API v1

Stripe's documented API v1 behaviour is a concrete replay contract:

- Keys are sent in the `Idempotency-Key` header on any `POST`. (`GET` and `DELETE` are already idempotent.)
- Stripe saves the **status code and body** of the first request with that key, *whether it succeeded or failed*, including a declined card or even a `500`. Replays return exactly that result.
- Keys may be pruned once they're at least **24 hours** old. A key reused after it's been pruned is treated as a new request.
- If a retry arrives with the same key but **different parameters**, Stripe returns an error rather than silently returning the old result. That protects against client bugs that reuse keys.
- A request that's rejected before execution starts (failed validation, or a concurrent request with the same key in progress) isn't saved, so it can safely be retried.

API v2 has a different contract: Stripe retries failed or partially failed work to completion where possible and can return an updated response. Do not carry API v1's saved-failure or retention assumptions into API v2 without checking its current documentation.

An expired IETF Internet-Draft for the **`Idempotency-Key` HTTP header** proposes `409 Conflict` for an operation still in progress and `422` for key reuse with a different payload. As checked in October 2026, it is not an RFC; treat these as a proposed convention, not a universal provider contract.

## Key takeaways
- Generate and persist a key before the first attempt; reuse it on retries.
- Replay behaviour depends on the endpoint’s key scope, retention and execution-start contract.
- Stripe API v1 can replay saved failures and prunes eligible keys after at least 24 hours.
- The expired Idempotency-Key draft’s 409/422 choices are a proposed convention, not an RFC.

## Further reading
- [Stripe API: Idempotent requests](https://docs.stripe.com/api/idempotent_requests)
- [Stripe blog: Designing robust and predictable APIs with idempotency](https://stripe.com/blog/idempotency)
- [IETF draft: The Idempotency-Key HTTP header field](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)
