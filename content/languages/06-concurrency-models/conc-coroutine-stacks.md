---
id: conc-coroutine-stacks
title: Stackless and stackful suspension
level: intermediate
minutes: 3
sourceLesson: conc-coroutines-green-threads
summary: Stackless suspension is explicit through each participating coroutine frame.
---

The preceding generator scheduler resumed saved frames one step at a time. Here we compare how much call state a runtime preserves, and what callers must do to propagate suspension.

## Stackless coroutines

Python generators, async functions in Python, JavaScript, C#, Rust and Kotlin, and C++20 coroutines are all **stackless**. Only the coroutine's *own* frame can be suspended. Implementations preserve resumable state, often using compiler-generated state machines. Python retains interpreter frames and instruction position rather than necessarily generating the same explicit struct used by Rust.

```
async fn get() {        state 0: start
  let a = read().await;  -> state 1
  let b = read().await;  -> state 2
  a + b                  -> done
}
```

A concrete compiler-generated Rust future has a statically known size; it can live inside another struct with no heap allocation at all.

The catch: a function *called from* the coroutine cannot suspend it.

```python
# Calling a generator does not run it.
def helper():
    yield "deep"

def task():
    helper()   # makes a generator,
               # never runs it!
    yield "top"
```

`task` must write `yield from helper()` to pass the suspension up. That is the root of **function colouring**: every function on the path to a suspension point must itself be a coroutine (`async`), because each frame has to be turned into a state machine separately.

## Stackful coroutines

A **stackful** coroutine has its own separate call stack. Nested calls can suspend the coroutine stack where the runtime permits yielding; native-call boundaries may impose restrictions. Lua, Ruby's Fibers and Python's `greenlet` library work this way.

```lua
-- Nested helper yields the coroutine.
local function helper()
  coroutine.yield("deep")
end

local co = coroutine.create(function()
  helper()          -- ordinary call
  return "done"
end)

print(coroutine.resume(co)) -- true deep
print(coroutine.resume(co)) -- true done
```

`helper` is a plain function, yet it suspends `co` from two frames down. No colouring is needed. Preserving nested call state costs memory; implementations may use separate native stacks, copied stacks, or VM-managed frames.

| | Stackless | Stackful |
|---|---|---|
| Suspend from | Own resumable frame | Nested frames, within runtime limits |
| Storage | Resumable state; representation varies | Preserved call stack |
| Colouring | Yes | No |
| Examples | Python, JS, Rust, C# | Lua, Go, greenlet |

## Key takeaways
- Stackless suspension is explicit through each participating coroutine frame.
- Stackful runtimes preserve a call stack; native boundaries can still restrict suspension.

## Further reading
- [Primary source: peps.python.org](https://peps.python.org/pep-0342/)
- [Primary source: www.lua.org](https://www.lua.org/manual/5.4/manual.html#2.6)
- [Primary source: go.dev](https://go.dev/src/runtime/stack.go)
- [Primary source: openjdk.org](https://openjdk.org/jeps/444)
- [Primary source: openjdk.org](https://openjdk.org/jeps/491)
