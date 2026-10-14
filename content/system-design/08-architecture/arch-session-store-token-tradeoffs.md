---
id: arch-session-store-token-tradeoffs
title: Choosing where sessions live
level: basic
minutes: 4
summary: Compare sticky sessions, a shared store and signed tokens under replacement and token revocation.
sourceLesson: arch-stateless-web-tier
---

Instances are replaceable only when later requests can recover their client state. Choose a session design by both lookup cost and the access cut-off your product needs.

## Where session state goes

Users still log in and have shopping baskets. There are three common places for that state.

### 1. Sticky sessions (avoid as the main strategy)

The load balancer pins each user to one server (via a cookie or IP hash), and the session lives in that server's memory.

- Load spreads unevenly: a few heavy users can overload one box.
- When the server dies or is redeployed, its users lose their sessions.
- Scaling in is painful because you have to drain long-lived sessions.

Sticky sessions are sometimes used as a *performance optimisation* (to keep a warm local cache) on top of a design that still works without them.

### 2. A shared session store

The server stores a random session ID in a cookie, and the session data in Redis or Memcached keyed by that ID.

- Any server can serve any request with a lookup whose latency depends on topology, load and the store.
- The session store must itself be highly available (Redis with replicas, or a managed service).
- Deleting the session prevents future authorizations only once all relevant checks observe the deletion; caches, replicas, failover and already-authorized requests affect cut-off.

### 3. Client-side tokens

The state goes into a signed token the client sends with every request, such as a JWT or a signed cookie.

- Verification can be local if the server already has trusted keys and policy. Signature checking must be accompanied by issuer, audience, expiry and application-specific authorization checks.
- Tokens can't easily be revoked before they expire, so keep them short-lived (say 15 minutes) with a refresh token.
- Every request carries the token, so keep it small (a few hundred bytes, not your whole basket).

| Approach | Lookup cost | Token revocation | Failure risk |
|---|---|---|---|
| Sticky | none | easy | lose sessions |
| Redis store | Store lookup | Depends on observation/consistency | Store outage or lost state |
| JWT | verify sig | hard | key leak |

> [!tip] Files are state too
> Uploaded files written to `/tmp` on one server are invisible to the others. Send uploads straight to object storage (S3, GCS) instead, ideally via presigned URLs so they don't pass through the app tier at all.

> [!note] Evidence gap
> Fixed session-lookup and VM/container startup timings are omitted: this project has no measured deployment establishing them. Use application readiness measurements and load tests for capacity planning.

### Token lifecycle checks

With asymmetrically signed access tokens, application servers verify using trusted public keys; protect the private signing key and plan rotation. Revoke refresh tokens in a server-side store when disabling future renewal. Already-issued access tokens remain usable until their expiry unless each authorisation performs an enforced token revocation check. Rotate refresh tokens on use and detect reuse atomically. Reuse may indicate theft or legitimate concurrent requests; invalidating a refresh-token family stops further renewal once enforced, but does not itself invalidate already-issued access tokens. A short access-token lifetime is a design example, not a universal security optimum; validation, key distribution and clock tolerance are part of the policy.

## Key takeaways
- Sticky sessions lose instance-local sessions when their instance disappears; use them only where the design still works without affinity.
- A shared session store permits replacement but makes authorisation depend on observing the current session policy.
- JWT signature checks require issuer, audience, expiry and authorisation checks; expiry limits exposure rather than providing immediate token revocation.

## Further reading
- [The Twelve-Factor App: Processes](https://12factor.net/processes)
- [OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700.html)
