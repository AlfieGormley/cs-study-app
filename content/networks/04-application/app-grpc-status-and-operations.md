---
id: app-grpc-status-and-operations
title: "gRPC trailers, deadlines and connection balancing"
level: advanced
minutes: 3
sourceLesson: app-ntp-ssh-grpc
summary: "HTTP success and RPC success are separate; grpc-status in trailers gives the RPC outcome."
---

A native gRPC call is one HTTP/2 stream. Requests carry a method path, a content type and optionally grpc-timeout; 250m means a 250-millisecond remaining budget. Messages have a one-byte compression flag and four-byte length before each encoded body; these examples use protobuf. The final call result is separate from those bytes.

### The response and trailers

```
HEADERS  :status 200
         content-type application/grpc
DATA     <length-prefixed messages>
HEADERS  (END_STREAM)  trailers:
         grpc-status 0
         grpc-message ""
```

The **status is in the trailers**, because a streaming server only knows whether the call succeeded at the end. A conforming gRPC response uses HTTP status 200 even for a gRPC error; HTTP intermediaries and protocol errors can produce other HTTP statuses. A call that fails immediately can send a single "Trailers-Only" HEADERS frame.

Common codes:

| Code | Name | Retry? |
|---|---|---|
| 0 | OK | n/a |
| 3 | INVALID_ARGUMENT | No |
| 4 | DEADLINE_EXCEEDED | Maybe |
| 5 | NOT_FOUND | No |
| 8 | RESOURCE_EXHAUSTED | Depends on quota/resource cause |
| 13 | INTERNAL | Rarely |
| 14 | UNAVAILABLE | Consider retry if safe and budget permits |

Retry decisions need method semantics, duplicate-effect protection, retry policy and remaining deadline. A timeout can occur after a server has committed a change.

### Deadlines and cancellation

Pass the remaining deadline budget to downstream calls, reserving any time needed to finish the current response. Starting with 300 ms and spending 50 ms leaves about 250 ms; giving every downstream hop a fresh 300 ms timeout can keep work running after the caller has stopped waiting. Deadline propagation support differs between language libraries and configuration.

> [!analogy] Real-world analogy: A delivery promise passed to subcontractors
> A restaurant promises a customer dinner within 30 minutes. The kitchen takes 10, so it tells the driver "you have 20 minutes", not "you have 30". If the customer cancels, a sensible restaurant tells the driver to turn back instead of delivering to an empty house.
>
> **How it maps:** The customer's promise is the caller's deadline, the kitchen is service A, and the driver is downstream service B. Passing on "20 minutes" is propagating the remaining budget in `grpc-timeout`. Telling the driver to turn back is cancellation.
>
> **Where it stops:** A driver hears "turn back" at once; a cancelled RPC reaches downstream servers after network delay, and only stops work if the handler checks for it. Nothing un-cooks a meal: a change the server has already committed stays committed.

When a client deadline expires, it can report DEADLINE_EXCEEDED and signal cancellation. Server handlers must cooperate by checking cancellation and stopping unnecessary work; cancellation is not an instantaneous distributed stop and cannot roll back an already committed side effect.

### Operational consequences

- **Browsers** can't read HTTP/2 trailers or control framing through `fetch`, so browsers use **gRPC-Web**, which moves trailers into the body and needs a proxy (or server support) to translate.
- **Load balancing.** A client using one long-lived HTTP/2 connection sends its streams to the backend chosen for that connection by a connection-oriented layer-4 balancer. A channel can also use multiple connections; the backend assignment lasts for that connection. Use a layer-7 (HTTP/2-aware) proxy such as Envoy, or client-side balancing across several connections.
- **gRPC keepalives** are HTTP/2 PING frames. Pinging more often than the server allows gets a GOAWAY with `ENHANCE_YOUR_CALM` and the debug data `too_many_pings`.
- **Message size.** Receive limits are configurable and implementation-specific; exceeding an enforced limit can produce RESOURCE_EXHAUSTED. Defaults differ between language implementations, so check your library's documentation.

## Key takeaways
- HTTP success and RPC success are separate; grpc-status in trailers gives the RPC outcome.
- Retry safety and deadline propagation depend on effects and remaining budget, not just a status name.

## Further reading
- [gRPC HTTP/2 protocol](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md)
- [gRPC deadlines](https://grpc.io/docs/guides/deadlines/)
- [gRPC load balancing](https://grpc.io/blog/grpc-load-balancing/)
- [gRPC keepalive](https://grpc.io/docs/guides/keepalive/)
