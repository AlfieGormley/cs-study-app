---
id: type-local-inference
title: Local and contextual inference
level: intermediate
minutes: 3
sourceLesson: type-inference
summary: Java infers a local binding from its initialiser; TypeScript also uses expected context.
---

Some statically typed APIs require repetitive annotations: `ArrayList<String> names = new ArrayList<String>();`. The compiler already knew the right-hand side was an `ArrayList<String>`, so the annotation was pure ceremony.

**Type inference** lets the compiler work types out from how values are used. You get the safety of static checking without most of the typing. How much a language can infer varies enormously, from "the type of this one variable" to "every type in the whole program".

## Local inference: from the right-hand side

The simplest form looks at an initialiser and copies its type to the variable:

```java
// Java 10+
// The initialiser fixes the element type.
var names = new ArrayList<String>();
var n = names.size(); // int
```

C++ `auto`, C# `var`, Go's `x := 1` short declaration, Kotlin `val` and Swift `let` can similarly infer a local from its initialiser. This example does not describe each language’s full inference rules: contextual and bidirectional inference can also contribute.

It has limits. In Java, `var list = new ArrayList<>();` infers `ArrayList<Object>`, because the diamond operator `<>` has nothing to go on. Method parameters and fields must still be annotated.

### TypeScript: local plus contextual

TypeScript infers variable and return types, and also flows types *inwards* from context (**contextual typing**):

```ts
let l = "hi";      // string (widened)
const c = "hi";    // "hi" (literal type)
let xs = [1, "a"]; // (string | number)[]

// x inferred from the array's type:
// Each result is twice its input.
[1, 2].map(x => x * 2);

function f(x) { return x * 2; }
// error under strict: Parameter 'x'
// implicitly has an 'any' type
```

TypeScript does **not** infer parameter types from how a function body uses them. That last line is the key difference from Hindley–Milner.

### Rust: inference within a function

Rust requires full signatures on functions but infers many local types inside the body, including from **later** uses:

```rust
let mut v = Vec::new(); // Vec<?>
// A later use fixes the unknown element.
v.push(1u8);            // now Vec<u8>
```

Sometimes nothing pins a type down, and you must help:

```rust
let nums: Vec<i32> = "1 2 3"
    .split(' ')
    // Parse each word as the chosen i32.
    .map(|s| s.parse().unwrap())
    .collect();
```

Without the `Vec<i32>` annotation, neither `parse` nor `collect` knows what to produce, and the compiler reports that type annotations are needed (the diagnostic code depends on the unresolved constraint).

Rust also accepts explicit type arguments at the call site: `.collect::<Vec<i32>>()` fixes both the collection and its element type. This `::<...>` notation is often called the turbofish. Writing only `.parse::<i32>()` fixes the parsed element but leaves `collect` ambiguous. Alternatively, `Vec<_>` on the binding fixes the collection while `parse::<i32>()` fixes its element; the underscore asks Rust to infer the remaining part.

Python's mypy does something similar. `x = []` followed by `x.append(1)` in the same scope infers `list[int]`; a bare `x = []` with no later clue is an error: `Need type annotation for "x"`.

## Key takeaways
- Java infers a local binding from its initialiser; TypeScript also uses expected context.
- Rust can use later local constraints; ambiguous parse and collect operations still need information.

## Further reading
- [OpenJDK: Local variable inference](https://openjdk.org/projects/amber/guides/lvti-style-guide)
- [TypeScript Handbook: Type inference](https://www.typescriptlang.org/docs/handbook/type-inference.html)
- [Rust by Example: Inference](https://doc.rust-lang.org/rust-by-example/types/inference.html)
- [mypy: Inference and annotations](https://mypy.readthedocs.io/en/stable/type_inference_and_annotations.html)
