---
id: comp-three-address-lowering
title: "Lower Calc trees to three-address instructions"
level: advanced
minutes: 3
sourceLesson: comp-ir-ssa
summary: "Lower subexpressions to explicit operands and fresh destination names."
---

The AST mirrors what the programmer wrote: nested, full of sugar, shaped by the grammar. The machine wants flat sequences of simple operations. In between sits the **intermediate representation** (IR), the form in which a compiler does most of its thinking.

A good IR is simple enough that each optimisation needs only a few rules, explicit enough that nothing is hidden (every temporary value has a name), and reusable across source languages and targets, while preserving language semantics and relevant target layout constraints. The pipeline units showed why that last property matters: it lets LLVM serve dozens of languages and targets with one optimiser.

Real compilers often use several IRs at different levels. GCC lowers to GIMPLE, then RTL. rustc goes from AST to HIR, then MIR (where the borrow checker runs), then LLVM IR. Swift has SIL. MLIR is a framework for defining such levels.

## Three-address code

The classic IR is **three-address code**: each instruction has at most one operator and at most three names, two operands and a destination. Nested expressions are flattened by giving every intermediate result a **compiler temporary**.

```python
@dataclass
class Ins:
    dest: str
    op: str      # + - * / ^ neg
    args: tuple
```

Lowering Calc's AST is one more tree walk. It returns the *operand* that holds each subexpression's value: an `int` for a constant, or a temp name such as `"t3"`.

```python
class Lowerer:
    def __init__(self, params=()):
        self.code = []
        self.n = 0
        # Generated names must not hide
        # parameters.
        self.used = set(params)

    def emit(self, op, *args):
        self.n += 1
        dest = f"t{self.n}"
        while dest in self.used:
            self.n += 1
            dest = f"t{self.n}"
        self.used.add(dest)
        ins = Ins(dest, op, args)
        # Dependencies are emitted before
        # uses.
        self.code.append(ins)
        return dest

    def lower(self, node, env):
        match node:
            case Num(value):
                return value
            case Var(name):
                return env[name]
            case Neg(operand):
                a = self.lower(operand, env)
                return self.emit("neg", a)
            case BinOp(op, left, right):
                a = self.lower(left, env)
                b = self.lower(right, env)
                return self.emit(op, a, b)
            case Let(name, value, body):
                v = self.lower(value, env)
                # Bind an operand, not a new
                # IR copy.
                e2 = {**env, name: v}
                return self.lower(body, e2)
```

The wrapper reserves input names before generating temporaries. In this toy IR, strings denote named operands and integers denote constants:

```python
def is_temp(value):
    # Strings are operands; integers are
    # literals.
    return isinstance(value, str)

def to_ir(tree, params=()):
    lowerer = Lowerer(params)
    env = {p: p for p in params}
    result = lowerer.lower(tree, env)
    return lowerer.code, result
```

A let initializer may emit instructions; the binding itself only updates the environment. Source binding names disappear, while parameter names remain as inputs.

```
let a = 3 in let b = a * a in b - a

t1 = 3 * 3
t2 = t1 - 3
ret t2
```

## Key takeaways
- Lower subexpressions to explicit operands and fresh destination names.
- Reserve parameter names so generated temporaries cannot collide with inputs.

## Further reading
- [LLVM language reference](https://llvm.org/docs/LangRef.html#phi-instruction)
- [LLVM analysis and transform passes](https://llvm.org/docs/Passes.html)
- [SSA construction — Cytron and colleagues](https://www.cs.utexas.edu/~pingali/CS380C/2010/papers/ssaCytron.pdf)
- [blog.llvm.org — what-every-c-programmer-should-know.html](https://blog.llvm.org/2011/05/what-every-c-programmer-should-know.html)
- [Finding compiler bugs with Csmith](https://users.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf)
