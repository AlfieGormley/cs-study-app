---
id: conc-channel-handshakes
title: Channels, rendezvous and blocked sends
level: intermediate
minutes: 3
sourceLesson: conc-csp-channels
summary: Go channels coordinate communication but do not enforce ownership of referenced data.
---

The shared-memory units established a problem: shared memory plus locks is fast but hard to get right, because nothing tells you which lock protects which data. In 1978 Tony Hoare proposed a different discipline in his paper *Communicating Sequential Processes* (CSP): build a program from **sequential processes** with private state, interacting through synchronous communication. Go’s later channel design is inspired by that family of ideas, rather than a literal implementation of every historical CSP formalism.

Go popularized a CSP-inspired channel style. Its slogan, from *Effective Go*, is:

> Do not communicate by sharing memory; instead, share memory by communicating.

## The intuition: a relay race

In a relay, runners do not grab the baton off a shared table whenever they like. Each one runs their own leg independently, and the only interaction is the **hand-off**, where both runners must be in the zone at the same moment. Whoever holds the baton owns it.

- Each runner is a **process** (in Go, a goroutine).
- The hand-off zone is a **CSP channel**.
- The baton is the data. Passing it passes **ownership**: after sending a pointer, the sender should stop touching what it points to.

## Channels in Go

A goroutine, introduced in the runtime units, is lightweight, so you can afford one per job. A channel is a typed conduit between goroutines:

```go
// A hand-off coordinates sender/reader.
ch := make(chan string) // unbuffered

go func() {
    ch <- "ping"   // send
}()

msg := <-ch        // receive
fmt.Println(msg)   // ping
```

An **unbuffered** channel is a **rendezvous**: a send blocks until a receiver takes the value, and a receive blocks until a sender offers one. The transfer is also a synchronisation point. The Go memory model says the send happens-before the receive completes, so the sender's prior writes are ordered before the corresponding receive completes. Additional conflicting accesses still require coordination.

A **buffered** channel has a queue of fixed capacity:

```go
// The third send has no free capacity.
ch := make(chan int, 2)
ch <- 1   // ok, buffer [1]
ch <- 2   // ok, buffer [1 2]
ch <- 3   // blocks: buffer full
```

For an open buffered channel, send waits for capacity (or a receiver), and receive waits for a value; closed and nil channels follow separate rules. The buffer smooths bursts and gives you **backpressure**: a fast producer is slowed to the consumer's pace once the buffer fills.

## Deadlock, Go style

In this complete standalone program, no goroutine or external event can make the blocked send proceed:

```go
// This send needs a receiving peer.
func main() {
    ch := make(chan int)
    ch <- 1        // no receiver yet
    fmt.Println(<-ch)
}
```

The send waits for a receiver that would only run after the send. Go's runtime notices that *all* goroutines are asleep and crashes with:

```
fatal error: all goroutines are
asleep - deadlock!
```

With `make(chan int, 1)` it prints `1`, because the send fits in the buffer. Note the word *all*: if other runnable work or possible timer/I/O wakeups remain, this global deadlock detector may not diagnose the stuck goroutines, and the stuck goroutines just hang silently.

## Key takeaways
- Go channels coordinate communication but do not enforce ownership of referenced data.
- An unbuffered hand-off needs both parties; a finite buffer only postpones backpressure.

## Further reading
- [Primary source: go.dev](https://go.dev/ref/spec#Channel_types)
- [Primary source: go.dev](https://go.dev/ref/spec#Select_statements)
- [Primary source: go.dev](https://go.dev/blog/pipelines)
- [Primary source: go.dev](https://go.dev/ref/mem)
