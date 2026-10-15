---
id: conc-channel-pipeline
title: Pipelines, worker pools and channel owners
level: intermediate
minutes: 3
sourceLesson: conc-csp-channels
summary: A stage owns and closes its output after it finishes producing.
---

Earlier units established channel blocking, receive loops and closing. A pipeline combines those rules: each stage receives from one channel and owns the channel it produces into.

## Pipelines

CSP's natural shape is a **channel pipeline**: stages connected by channels, each stage a goroutine that receives, transforms and sends.

```go
// Each stage owns its output channel.
func gen(ns ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range ns {
            // Forward each input in order.
            out <- n
        }
        // This stage owns its output close.
        close(out)
    }()
    return out
}

func sq(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            // Transform before handing off.
            out <- n * n
        }
        // This stage owns its output close.
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
// Close only after all senders finish.
jobs := make(chan int)
results := make(chan int)
var wg sync.WaitGroup

for w := 0; w < 3; w++ {
    // Register before the worker can
    // finish.
    wg.Add(1)
    go func() {
        // Mark completion on every exit.
        defer wg.Done()
        for j := range jobs {
            // Send may wait for a receiver.
            results <- j * 2
        }
    }()
}
go func() {
    for i := 1; i <= 5; i++ {
        jobs <- i
    }
    // No more jobs; worker ranges can end.
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

The order in which results arrive varies from run to run, but the sum does not, because addition gives the same total in any order:

```formula
S = 2 × 1 + 2 × 2 + 2 × 3 + 2 × 4 + 2 × 5
S = 2 + 4 + 6 + 8 + 10 = 30
where
S: the value of `sum` printed once `results` is closed and drained
2: the factor each worker applies to its job number (`j * 2`)
In words: jobs 1 to 5 are each doubled by whichever worker takes them, and the five results add up to 30 whatever order they arrive in.
```

Notice who closes what: the feeder closes `jobs`; a separate goroutine closes `results` only after *every* worker has finished, because three workers share one output and none of them may close it alone.

## Key takeaways
- A stage owns and closes its output after it finishes producing.
- Receive-only channel types prevent sending and closing through that reference.
- Several readers distribute work; a coordinator waits before closing their shared results.
- Arrival order varies, but doubling each fixed input gives the same total.

## Further reading
- [Primary source: go.dev](https://go.dev/ref/spec#Channel_types)
- [Primary source: go.dev](https://go.dev/ref/spec#Select_statements)
- [Primary source: go.dev](https://go.dev/blog/pipelines)
- [Primary source: go.dev](https://go.dev/ref/mem)
