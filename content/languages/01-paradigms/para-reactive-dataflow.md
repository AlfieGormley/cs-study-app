---
id: para-reactive-dataflow
title: Dataflow systems and reactive glitches
level: intermediate
minutes: 3
sourceLesson: para-logic-dataflow
summary: Dataflow appears in pipes, builds, distributed processing and reactive UI.
---

The same dependency idea appears in build tools, stream processing and user interfaces. Reactive systems must avoid mixing a newly updated source with an old derived value.

## Other dataflow systems

- **Unix pipes**: `cat log | grep ERROR | sort | uniq -c` is a linear dataflow graph; processes can run concurrently, but sort generally needs the complete input before producing globally sorted output.
- **Build systems**: Make and Bazel track dependencies to decide which targets need rebuilding. Missing outputs, changed commands or configuration, and explicitly always-run targets can also trigger work.
- **Visual languages**: LabVIEW (lab instruments) and Simulink (control systems) are programmed by wiring boxes together.
- **Synchronous languages**: Lustre and tools such as SCADE use clocked stream semantics for safety-critical embedded software. This is distinct from the fixed token-production/consumption model also called synchronous dataflow; both support static reasoning under their respective restrictions, but neither label alone proves every timing property.
- Data processing: Apache Beam, Apache Flink and Apache Spark build dataflow graphs of transformations and distribute them across a cluster. TensorFlow 1.x had you build a graph first, then run it.

## Reactive programming

**Reactive** UI frameworks apply dataflow to user interfaces. In libraries based on **reactive signals** (SolidJS, Preact Signals, Angular signals, Vue's refs), a value declares what it is computed from, and the runtime tracks dependencies and updates only what's affected.

```javascript
// Read computed values to observe updates.
// Preact Signals-style API
const price = signal(10);
const qty = signal(3);
const total = computed(
  () => price.value * qty.value);
// total.value is 30
price.value = 12;
// total.value is now 36
```

A naive push-based implementation can suffer **glitches**. In the graph above, if `a` changes and `c` is recomputed before `b`, `c` briefly sees the new `a` with the old `b`: an inconsistent state that never "should" exist. Glitch-free systems either update in topological order or mark nodes dirty and recompute lazily on read.

## Trade-offs

| Paradigm | Strength | Weakness |
|---|---|---|
| Prolog | Search, rules | Hidden cost, loops |
| Basic finite-domain Datalog | Fixed-point termination | Extensions may lose guarantee |
| Dataflow | Parallel, incremental | Cycles, glitches |

Both paradigms shine when the problem *is* naturally a set of rules (permissions, type systems, code analysis) or a graph of dependent values (spreadsheets, builds, UIs), and are awkward for long sequential processes.

## Key takeaways
- Dataflow appears in pipes, builds, distributed processing and reactive UI.
- A glitch combines newly updated inputs with stale dependencies.

## Further reading
- [Preact: how signals compute updates](https://preactjs.com/blog/signal-boosting/)
- [Verimag: Lustre and synchronous languages](https://verimag.univ-grenoble-alpes.fr/The-Lustre-Programming-Language-and.html?lang=en)
