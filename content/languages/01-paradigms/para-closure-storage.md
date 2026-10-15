---
id: para-closure-storage
title: Captured environments and lifetimes
level: advanced
minutes: 3
sourceLesson: para-scope-closures
summary: Escaping captures must remain valid beyond the creating call.
---

A captured value must remain valid whenever a closure uses it. Languages differ in how they retain bindings, copy values and reject references that would outlive their data.

## How closures are implemented

A C function's automatic locals have block lifetime and are commonly stored in a call frame; static locals have a different lifetime and compilers can keep automatic values in registers or remove them entirely. A closure breaks that: an inner function may be *returned* and called later, after the outer frame is gone. This is the **upward funarg problem**, and it's why closures need captured variables to live somewhere longer-lived, usually heap storage.

```
counter() frame (gone)
         |
inc --> [code] + [env] --> cell holding 3
                           (in heap storage)
```

In the discussion below, `c` is the counter closure from the preceding unit, after three calls; its captured `n` binding holds the integer 3.

- **CPython** stores captured variables in **cell objects**. You can see them: `c.__closure__[0].cell_contents` is `3`. Both the outer function and every closure share the same cell, which is how `nonlocal` writes are visible.
- **Lua** uses *upvalues*: they point into the stack while the outer function runs and are moved ("closed") to heap storage when it returns.
- C has no closures. Callbacks take a function pointer plus a `void *` context argument, which is a closure built by hand.
- **Rust** and **C++** make capture explicit. A C++ lambda says `[x]` (copy) or `[&x]` (reference); a reference that outlives `x` is undefined behaviour. Safe Rust rejects escaping borrows that outlive their referents. A `move` closure captures by value, moving or copying its captures; moving a borrowed reference does not extend the referent’s lifetime.

Closures also keep their environment alive. In JavaScript, an event listener that closes over a large object keeps that object from being garbage collected while the listener and captured object remain reachable. Removing the listener helps only if no other live reference retains the closure or object.

## Key takeaways
- Escaping captures must remain valid beyond the creating call.
- Capture ownership and storage choices differ between languages.

## Further reading
- [Lua: variable visibility and upvalues](https://www.lua.org/manual/5.4/manual.html#3.5)
- [Rust: closure captures](https://doc.rust-lang.org/book/ch13-01-closures.html)
