---
id: type-dynamic-consistency
title: Dynamic types and gradual consistency
level: advanced
minutes: 3
sourceLesson: type-gradual-soundness
summary: The dynamic type admits flows in both directions; a safe top type requires narrowing before type-specific operations.
---

Gradual typing permits statically checked and unchecked portions of one program to interact. The dynamic type records missing static information; it is distinct from a safe top type.

## The dynamic type

The central idea, from Jeremy Siek and Walid Taha (2006), is a special type, written `?` in papers and `any`/`Any` in practice, meaning "not statically known".

`any` is *not* just a top type like `unknown` or `object`. It works in **both** directions:

```ts
let a: any = 3;
let s: string = a;   // allowed
a.foo.bar();         // allowed

let u: unknown = 3;
let t: string = u;   // error
u.foo;               // error
```

- `unknown` is a true top type: anything goes in, while type-specific operations require narrowing; operations such as equality checks remain available.
- `any` goes in and comes out as anything. The checker permits unsafe flows and operations. This is a useful intuition, not literal compatibility with every TypeScript type: for example, `any` is not assignable to `never`.

Siek and Taha replace type equality with a **consistency relation**: the dynamic type is consistent with every type, and concrete base types are consistent only when they match; structured types compare their components recursively, so a structure containing dynamic components can be consistent with a more precise structure. Consistency is deliberately **not transitive**:

```formula
? ~ T  and  T ~ ?   for all T
number ~ ?  and  ? ~ string
number ≁ string
where
?: the dynamic type, "not statically known" (any in TypeScript, Any in Python)
T: any type
~: "is consistent with": a value of one type may flow where the other is expected without a static error
≁: "is not consistent with"
number, string: two concrete types (TypeScript's names for numbers and text)
In words: anything can flow into or out of the dynamic type, but going through it does not make number and string compatible with each other.
```

If consistency were transitive, the second line would give `number ~ string`, and then every type would be compatible with every other. Keeping it non-transitive is what lets untyped and typed code meet without making everything compatible with everything.

## Gradual guarantee

A well-designed gradual system also satisfies the **gradual guarantee** (Siek and others, 2015): making annotations less precise preserves static acceptance and successful computed behaviour under the formal system’s precision relation. More precise annotations may introduce a static rejection or a runtime cast error; the theorem constrains these changes rather than promising that adding types always succeeds. This is what makes migration incremental: a file with no annotations is still a valid program.

## Key takeaways
- The dynamic type admits flows in both directions; a safe top type requires narrowing before type-specific operations.
- Consistency is intentionally non-transitive; gradual guarantees constrain changes in precision.

## Further reading
- [Siek: What is gradual typing?](https://jsiek.github.io/home/WhatIsGradualTyping.html)
- [Siek et al.: Refined criteria for gradual typing](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.SNAPL.2015.274)
- [TypeScript Handbook: Everyday types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html)
