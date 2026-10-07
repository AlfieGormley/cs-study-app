---
id: conc-csp-channels
title: CSP, goroutines and channels
level: intermediate
minutes: 13
summary: Tony Hoare's idea of independent processes that only talk over channels, as realised in Go, with unbuffered and buffered channels, select, closing, pipelines, worker pools, and the deadlocks and leaks to watch for.
---

The first lesson ended with a problem: shared memory plus locks is fast but hard to get right, because nothing tells you which lock protects which data. In 1978 Tony Hoare proposed a different discipline in his paper *Communicating Sequential Processes* (CSP): build a program from **sequential processes** that share nothing, and let them interact **only by sending messages over channels**.

Go popularized a CSP-inspired channel style. Its slogan, from *Effective Go*, is:

> Do not communicate by sharing memory; instead, share memory by communicating.

## The intuition: a relay race

In a relay, runners do not grab the baton off a shared table whenever they like. Each one runs their own leg independently, and the only interaction is the **hand-off**, where both runners must be in the zone at the same moment. Whoever holds the baton owns it.

- Each runner is a **process** (in Go, a goroutine).
- The hand-off zone is a **channel**.
- The baton is the data. Passing it passes **ownership**: after sending a pointer, the sender should stop touching what it points to.

## Channels in Go

A goroutine (lesson 3) is cheap, so you can afford one per job. A channel is a typed conduit between goroutines:

```go
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
ch := make(chan int, 2)
ch <- 1   // ok, buffer [1]
ch <- 2   // ok, buffer [1 2]
ch <- 3   // blocks: buffer full
```

For an open buffered channel, send waits for capacity (or a receiver), and receive waits for a value; closed and nil channels follow separate rules. The buffer smooths bursts and gives you **backpressure**: a fast producer is slowed to the consumer's pace once the buffer fills.

## Deadlock, Go style

In this complete standalone program, no goroutine or external event can make the blocked send proceed:

```go
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

## Closing and ranging

A sender signals "no more values" with `close(ch)`. Receivers then drain what is left and get the zero value with `ok == false`:

```go
v, ok := <-ch  // ok false once closed
                // and empty

for v := range ch {  // stops at close
    use(v)
}
```

The rules are worth memorising:

| Operation | Open | Closed | nil |
|---|---|---|---|
| Send | Blocks or sends | Panics | Blocks forever |
| Receive | Blocks or gets | Buffered values, then zero/false | Blocks forever |
| Close | Closes | Panics | Panics |

Assign one owner to close, only after all sends have ended. Often that is the sender; with multiple senders a coordinator can close after waiting for them. Closing is also a **broadcast**: blocked receives become eligible to complete; scheduling is not simultaneous. That is how `context.Context` works: `ctx.Done()` returns a channel that is closed on cancellation, waking every goroutine that selects on it.

## select: waiting on several channels

`select` blocks until one of its cases can proceed. If several are ready, it makes a uniform pseudo-random choice among ready communication cases. This does not guarantee a bounded wait or deterministic starvation freedom:

```go
select {
case r := <-results:
    fmt.Println(r)
case <-time.After(time.Second):
    fmt.Println("timeout")
case <-ctx.Done():
    return ctx.Err()
}
```

A `default` case makes the select non-blocking: it runs if nothing else is ready. And because operations on a `nil` channel block forever, setting a channel variable to `nil` **disables** its case. That is the idiom for merging two channels until both are closed:

```go
for a != nil || b != nil {
    select {
    case v, ok := <-a:
        if !ok { a = nil; continue }
        fmt.Println(v)
    case v, ok := <-b:
        if !ok { b = nil; continue }
        fmt.Println(v)
    }
}
```

## Pipelines

CSP's natural shape is a **pipeline**: stages connected by channels, each stage a goroutine that receives, transforms and sends.

```go
func gen(ns ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range ns {
            out <- n
        }
        close(out)
    }()
    return out
}

func sq(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

// prints 4, 9, 16
for v := range sq(gen(2, 3, 4)) {
    fmt.Println(v)
}
```

```
gen --2,3,4--> sq --4,9,16--> main
```

The `<-chan int` return type is a **receive-only** channel: the compiler stops callers from sending or closing. Each stage closes its output when its input runs dry, so the close ripples down the pipeline and every `range` loop ends.

## Fan-out, fan-in: a worker pool

Several goroutines reading the same channel share the work (**fan-out**); their results merge into one channel (**fan-in**):

```go
jobs := make(chan int)
results := make(chan int)
var wg sync.WaitGroup

for w := 0; w < 3; w++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        for j := range jobs {
            results <- j * 2
        }
    }()
}
go func() {
    for i := 1; i <= 5; i++ {
        jobs <- i
    }
    close(jobs)
}()
go func() {
    wg.Wait()       // all workers done
    close(results)
}()

sum := 0
for r := range results {
    sum += r
}
fmt.Println(sum)    // 30
```

The order in which results arrive varies from run to run, but the sum is always 2 + 4 + 6 + 8 + 10 = 30. Notice who closes what: the feeder closes `jobs`; a separate goroutine closes `results` only after *every* worker has finished, because three workers share one output and none of them may close it alone.

## The classic leak

```go
func first(urls []string) string {
    ch := make(chan string)
    for _, u := range urls {
        go func(u string) {
            ch <- fetch(u)
        }(u)
    }
    return <-ch
}
```

For a nonempty input, this receives the first response successfully handed off; scheduling can affect which fetch wins. Empty input blocks forever, so a production API must define that case. But the other goroutines then try to send on an unbuffered channel that nobody will ever read. They block forever, holding their stacks and whatever `fetch` allocated. Call `first` once per request and memory grows without bound. The runtime does not detect it: the process as a whole is not deadlocked.

Fixes: give the channel room for every sender (`make(chan string, len(urls))`) so sends never block, or arrange cancellation after the first result, make each sender select on ctx.Done(), and pass that context into fetch so outstanding I/O can stop. Uber's `goleak` package checks tests for leftover goroutines.

> [!tip] Leaks are the CSP version of forgotten locks
> Every goroutine should have an obvious answer to "how does this one end?". Lesson 6's structured concurrency makes that answer part of the code's shape.

## Channels are not always the answer

Go has `sync.Mutex` too, and uses it widely. A rough guide from Go's own wiki: use channels to pass ownership of data, distribute work or communicate results; use a mutex for caches and state that many goroutines briefly read and update.

```go
// A counter is clearer with a mutex
mu.Lock()
hits[path]++
mu.Unlock()
```

Channel and mutex costs depend on contention and workload; channel implementations can use locks and park goroutines, and Go does not stop you sharing memory. Sending a pointer or a map over a channel and then mutating it from both sides is still a data race; Go's race detector can expose races on exercised execution paths; one passing run is not proof of absence.

## CSP beyond Go

- **occam** (1983), designed for the Inmos transputer, was CSP almost verbatim.
- Rob Pike's Newsqueak, Alef and Limbo led directly to Go's channels.
- **Clojure core.async** and **Kotlin** channels bring CSP to the JVM, the latter on coroutines.
- Rust has `std::sync::mpsc` and the `crossbeam` crate. Python queue.Queue(maxsize=n) and asyncio.Queue provide bounded queues for positive n; maxsize=0 means unbounded, unlike Go's unbuffered channel. Their close/shutdown and acknowledgement APIs differ.

In this Go-style comparison, channels are explicit communication endpoints and unbuffered sends rendezvous. Historical CSP formalisms vary; anonymous processes versus named channels is not a universal definition of CSP.

## Key takeaways
- CSP: sequential processes that share nothing and interact only through channels. Go's version is goroutines plus `chan`.
- Unbuffered channels are a rendezvous and a happens-before edge; buffered channels block only when full or empty, giving backpressure.
- A designated owner closes after all sends finish. Closed channels drain buffered values before returning zero with ok == false; nil channels block forever, which disables a `select` case.
- `select` waits on several channels, picks randomly among ready cases, and is how you add timeouts and cancellation.
- Pipelines and worker pools are the main patterns. Plan who closes each channel.
- Go detects only total deadlock. A goroutine blocked forever on an abandoned channel is a silent leak.

## Further reading
- [Communicating sequential processes — Wikipedia](https://en.wikipedia.org/wiki/Communicating_sequential_processes)
- [Effective Go: Concurrency](https://go.dev/doc/effective_go#concurrency)
- [Go Concurrency Patterns: Pipelines and cancellation — The Go Blog](https://go.dev/blog/pipelines)
- [Share Memory By Communicating — The Go Blog](https://go.dev/blog/codelab-share)
- [The Go Programming Language Specification: Select statements](https://go.dev/ref/spec#Select_statements)
- [The Go Memory Model](https://go.dev/ref/mem)
- [Use a sync.Mutex or a channel? — Go Wiki](https://go.dev/wiki/MutexOrChannel)
