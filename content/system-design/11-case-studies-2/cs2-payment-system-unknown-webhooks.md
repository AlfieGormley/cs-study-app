---
id: cs2-payment-system-unknown-webhooks
title: Payment state and asynchronous evidence
level: advanced
minutes: 3
summary: Resolve unknown calls and process authenticated provider events without assuming order.
sourceLesson: cs2-payment-system
---

## Deep dive 2: the payment state machine

```
CREATED -> AUTHORISING -> AUTHORISED
  -> CAPTURING -> CAPTURED -> SETTLED
AUTHORISING -> DECLINED | FAILED
AUTHORISING -> UNKNOWN (timeout)
CAPTURED -> REFUNDING -> (PART)REFUNDED
CAPTURED -> DISPUTED -> WON | LOST
```

- Every transition is a conditional update: a version-checked SQL update of the expected prior state. The transition graph, version check and atomic ledger write together prevent invalid regression; conditional updates alone do not define a correct graph. Track authorisation, capture, refund amounts and disputes separately where they overlap.
- Persist **before** calling out (move to AUTHORISING, *then* call the PSP), so after a crash you know a call may have happened.

### The UNKNOWN state
The PSP call times out. Did the charge happen? You **don't know**, and guessing either way is wrong.

- Don't mark it FAILED and let the customer retry with a new key. That's how double charges happen.
- Do mark it UNKNOWN, then **resolve** it: retry within the PSP's documented idempotency contract with the *same* key, or query the PSP for the payment's status, or wait for the webhook. A background resolver sweeps UNKNOWN payments until resolved, escalating unresolved cases for investigation. An authorisation can be declined, cancelled or expire without settling.

## Deep dive 4: PSP integration and webhooks

PSPs report many outcomes **asynchronously** via webhooks: 3-D Secure completion, captures, refunds, disputes, payouts.

- **Verify using the provider's documented scheme or SDK**. For Stripe this includes the raw body and signed timestamp; check timestamp tolerance and deduplicate event IDs because an authentic event can be replayed within the tolerance.
- **Dedupe by `event_id`**. Insert into `psp_events` with a primary key. If it already exists, return `200` and do nothing. Providers can retry webhook delivery, so duplicates are possible; finite retry windows still permit missed events. Ensure stored but unprocessed events remain discoverable after a crash.
- **Don't trust order.** `charge.refunded` can arrive before `charge.captured`. Either apply events through the state machine, which rejects invalid transitions and retries them later, or treat the webhook as a hint and **fetch the current object** from the PSP API.
- **Acknowledge fast**: write the event durably, return `200`, and process it asynchronously. Slow handlers cause PSP timeouts and redelivery storms.

Multi-PSP setups add **routing**: choose a provider by cost, region, card type and live health, with a circuit breaker for new, unattempted operations. Do not reroute an ambiguous in-flight charge to another PSP: keys are not shared across providers, and the first may already have charged. Resolve its outcome first. Each adapter normalises provider-specific states into your state machine.

## Key takeaways
- Persist intent before sending an external operation.
- A timeout means UNKNOWN rather than failure.
- Durably capture signed events, deduplicate and recover processing; fetch current provider state when needed.

## Further reading
- [Idempotent requests (Stripe API docs)](https://docs.stripe.com/api/idempotent_requests)
- [The Payment Intents API (Stripe docs)](https://docs.stripe.com/payments/payment-intents)
- [Designing robust and predictable APIs with idempotency (Stripe)](https://stripe.com/blog/idempotency)
- [Stripe webhook contract](https://docs.stripe.com/webhooks)
