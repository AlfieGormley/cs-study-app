---
id: conc-channel-lifecycle
title: Closing channels and selecting ready cases
level: intermediate
minutes: 3
sourceLesson: conc-csp-channels
summary: Closed channels drain buffered values before returning zero and false.
---

A channel coordinates senders and receivers, but its lifecycle must also be explicit. The following rules concern Go channels, including nil and closed values.

## Closing and ranging

A sender signals "no more values" with `close(ch)`. Receivers then drain what is left and get the zero value with `ok == false`:

```go
// range ends after close and drain.
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
// Only a ready communication can win.
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
// A closed receive stays ready.
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

## Key takeaways
- Closed channels drain buffered values before returning zero and false.
- Nil disables a communication case; ready select cases have no bounded-wait guarantee.

## Further reading
- [Primary source: go.dev](https://go.dev/ref/spec#Channel_types)
- [Primary source: go.dev](https://go.dev/ref/spec#Select_statements)
- [Primary source: go.dev](https://go.dev/blog/pipelines)
- [Primary source: go.dev](https://go.dev/ref/mem)
