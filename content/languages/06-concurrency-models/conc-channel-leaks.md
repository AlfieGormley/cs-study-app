---
id: conc-channel-leaks
title: Abandoned senders and ownership discipline
level: intermediate
minutes: 4
sourceLesson: conc-csp-channels
summary: Every goroutine needs a finish path, including senders whose receiver returns early.
---

Closing a channel is only part of a goroutine’s lifetime story. A sender can remain blocked forever even while the rest of a service is healthy.

## The classic leak

```go
// Returning abandons the other sends.
func first(urls []string) string {
    ch := make(chan string)
    for _, u := range urls {
        go func(u string) {
            // No reader remains after
            // first.
            ch <- fetch(u)
        }(u)
    }
    return <-ch
}
```

For a nonempty input, this receives the first response successfully handed off; scheduling can affect which fetch wins. Empty input blocks forever, so a production API must define that case. But the other goroutines then try to send on an unbuffered channel that nobody will ever read. They block forever, holding their stacks and whatever `fetch` allocated. Call `first` once per request and memory grows without bound. The runtime does not detect it: the process as a whole is not deadlocked.

The growth is easy to estimate. Every call leaks all but one of its senders, and each leaked goroutine keeps at least its starting stack:

```formula
L = (u − 1) × r
L = (4 − 1) × 1,000,000 = 3,000,000
M ≥ L × S_0
M ≥ 3,000,000 × 2 KiB ≈ 6.1 GB
where
L: the number of leaked goroutines after r calls
u: the number of URLs passed to each call, here 4
r: the number of calls to `first`, here an illustrative 1,000,000; this is not a measured traffic rate
M: the memory held by the leaked goroutines, in gigabytes (GB)
S_0: assumed lower bound for retained stack allocation, 2 KiB in the cited implementation; actual initial allocation may be larger
KiB: kibibyte, 1,024 bytes
≥: at least under the stated retained-stack model; actual stack sizes, live fetched values and goroutine metadata can add overhead
GB: gigabyte, 1,000,000,000 bytes; the unrounded stack-only model gives 6.144 GB
In words: four URLs per call leak three goroutines per call, so a million calls strand three million goroutines and at least 6 GB of stack.
```

The estimate assumes every call gets at least one response and that no sender ever finishes another way; it is a lower bound, since it ignores the heap data each stuck goroutine still references.

Fixes: give the channel room for every sender (`make(chan string, len(urls))`) so sends never block, or arrange cancellation after the first result, make each sender select on ctx.Done(), and pass that context into fetch so outstanding I/O can stop. Uber's `goleak` package checks tests for leftover goroutines.

> [!tip] Leaks are the CSP version of forgotten locks
> Every goroutine should have an obvious answer to "how does this one end?". The later task-scope unit’s structured concurrency makes that answer part of the code's shape.

## Channels are not always the answer

Go has `sync.Mutex` too, and uses it widely. A rough guide from Go's own wiki: use channels to pass ownership of data, distribute work or communicate results; use a mutex for caches and state that many goroutines briefly read and update.

```go
// Use the same lock for every access.
mu.Lock()
hits[path]++
mu.Unlock()
```

Channel and mutex costs depend on contention and workload; channel implementations can use locks and park goroutines, and Go does not stop you sharing memory. Sending a pointer or a map over a channel and then mutating it from both sides is still a data race; Go's race detector can expose races on exercised execution paths; one passing run is not proof of absence.

## CSP beyond Go

- **occam**, an INMOS language from the 1980s, was designed around CSP-style communicating parallel processes and used with transputers. Its later reference manuals define concrete language rules beyond that slogan.
- Newsqueak, Alef and Limbo belong to the language lineage behind Go’s channel-based concurrency; they were developed by different, overlapping teams.
- **Clojure core.async** and **Kotlin** channels bring CSP to the JVM, the latter on coroutines.
- Rust has `std::sync::mpsc` and the `crossbeam` crate. Python's `queue.Queue(maxsize=n)` and `asyncio.Queue` provide bounded queues when the capacity `n` is positive; `maxsize=0` means unbounded, unlike Go's unbuffered channel. Their close/shutdown and acknowledgement APIs differ.

In this Go-style comparison, channels are explicit communication endpoints and unbuffered sends rendezvous. Historical CSP formalisms vary; anonymous processes versus named channels is not a universal definition of CSP.

## Key takeaways
- Every goroutine needs a finish path, including senders whose receiver returns early.
- Buffering results or cooperative cancellation addresses different parts of leaked work.

## Further reading
- [Go concurrency history — Rob Pike](https://go.dev/talks/2012/concurrency.slide)
- [Alef reference manual — original authors](https://doc.cat-v.org/plan_9/2nd_edition/papers/alef/ref)
- [Limbo reference manual — original authors](https://www.vitanuova.com/inferno/papers/limbo.html)
- [occam reference manual — INMOS authors](https://www.wotug.org/occam/documentation/oc3refman.pdf)
- [Newsqueak reference manual — Rob Pike](https://swtch.com/~rsc/thread/newsqueak.pdf)
- [Communicating sequential processes — Wikipedia](https://en.wikipedia.org/wiki/Communicating_sequential_processes)
- [Effective Go: Concurrency](https://go.dev/doc/effective_go#concurrency)
- [Go Concurrency Patterns: Pipelines and cancellation — The Go Blog](https://go.dev/blog/pipelines)
- [Share Memory By Communicating — The Go Blog](https://go.dev/blog/codelab-share)
- [The Go Programming Language Specification: Select statements](https://go.dev/ref/spec#Select_statements)
- [The Go Memory Model](https://go.dev/ref/mem)
- [Use a sync.Mutex or a channel? — Go Wiki](https://go.dev/wiki/MutexOrChannel)
- [Primary source: go.dev](https://go.dev/ref/spec#Channel_types)
