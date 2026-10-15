---
id: sys-control-transfer-checks
title: Different checks for calls and returns
level: advanced
minutes: 3
sourceLesson: sys-mitigations
summary: Forward-edge schemes restrict covered indirect calls or jumps with policies permitting different target sets.
---

## Control-flow integrity

**Control-flow integrity** constrains allowed control transfers. Different schemes cover different indirect calls, jumps or returns; they do not all check every transfer or enforce the same policy.

### Forward edges: indirect calls

An indirect call such as `fp()` obtains its target at run time. C++ virtual dispatch commonly also uses indirect calls, though a compiler knowing the target can replace dynamic dispatch with a direct call. A forward-edge check restricts the covered transfer to its permitted target set.

- **Clang CFI** includes type-based indirect-call and virtual-call checks. Its `-fsanitize=cfi` family requires the documented LTO and visibility setup; that flag alone is not a complete build recipe.
- **Microsoft CFG** validates instrumented indirect calls against allowed targets; it is not a complete type-based policy.
- **Intel IBT** and **Arm BTI** constrain relevant indirect branches to suitable landing pads when enforcement is enabled. Landing-pad validation is coarser than checking the intended function type.

### Backward edges: returns

A **shadow stack** keeps protected return-address copies. With x86 CET shadow-stack enforcement, calls update the two stacks and returns check agreement. Linux user-space use requires supporting CPU, kernel, runtime and enablement; kernel availability alone does not protect every application.

**Pointer authentication** can protect selected Arm pointers with a keyed authentication code, incorporating contextual information. It authenticates rather than encrypts the pointer, and is not a general memory-safety check. Code generation, authentication policy and hardware support determine which pointers are protected.

The permitted-target set depends on the CFI policy. Type-based schemes may still permit an unintended same-type target; landing-pad schemes can permit a broader set. Shadow stacks protect returns by a different check, so a same-type target is not itself a shadow-stack bypass.

## Key takeaways
- Forward-edge schemes restrict covered indirect calls or jumps with policies permitting different target sets.
- A shadow stack checks returns against protected copies when enabled for that code.
- Pointer authentication authenticates selected pointers; it does not encrypt them or establish general memory safety.

## Further reading
- [Control-flow integrity — Clang](https://clang.llvm.org/docs/ControlFlowIntegrity.html)
- [CET shadow stacks — Linux](https://docs.kernel.org/arch/x86/shstk.html)
- [Arm pointer authentication — Linux](https://docs.kernel.org/arch/arm64/pointer-authentication.html)
- [Control Flow Guard — Microsoft](https://learn.microsoft.com/en-us/windows/win32/secbp/control-flow-guard)
