---
id: comp-stack-codegen
title: "Generate stack bytecode and bound stack depth"
level: advanced
minutes: 4
sourceLesson: comp-codegen-regalloc
summary: "Emit child code before its operator and use checker-resolved slots for bindings."
---

After optimisation, the program is a list of simple instructions over an unlimited supply of temporaries. Real hardware has neither unlimited temporaries nor our instruction set. The **back end** closes the gap with three jobs:

1. **Instruction selection.** Which machine instructions implement each IR operation?
2. **Register allocation.** Which of the CPU's few registers holds each value, and what goes to memory when they run out?
3. **Instruction scheduling.** In what order should instructions run so the pipeline stays busy?

This lesson covers the first two, and a simple teaching back end: a stack machine.

## Target 1: a stack machine

The abstract operand-stack instruction set does not name hardware registers. Its interpreter or JIT implementation may still allocate registers. Every instruction takes its operands from the top of an operand stack and pushes its result. The JVM, CPython, WebAssembly and .NET's CIL all use this model for their bytecode.

Code generation is a **post-order** tree walk: emit code for the children, then the operator.

```python
def compile_bc(tree):
    chk = check(tree)
    if chk.errors:
        raise SyntaxError(chk.errors[0])
    code = []
    def gen(node):
        match node:
            case Num(value):
                code.append(("PUSH", value))
            case Var():
                s = chk.slot[id(node)]
                code.append(("LOAD", s))
            case Neg(operand):
                gen(operand)
                code.append(("NEG", None))
            case BinOp(op, left, right):
                gen(left)
                # Children leave operands on
                # stack.
                gen(right)
                code.append(
                    (OPCODE[op], None))
            case Let(_, value, body):
                gen(value)
                s = chk.slot[id(node)]
                # Save the initializer in
                # its slot.
                code.append(("STORE", s))
                gen(body)
    gen(tree)
    code.append(("RET", None))
    return code, chk.scopes.nslots
```

The slot numbers come from the checker in the earlier semantic-analysis units. `let x = 5 in x * x - 1` becomes:

```
PUSH 5
STORE 0      x lives in slot 0
LOAD 0
LOAD 0
MUL
PUSH 1
SUB
RET          -> 24
```

The VM must reserve enough stack, so compilers compute the **maximum stack depth** statically. The JVM stores it in each method’s Code attribute as `max_stack`, and CPython records `co_stacksize`. JVM depth counts a long or double as two units; Calc counts each integer as one value. Calc's `max_stack` just tracks each instruction's effect: `PUSH` and `LOAD` add one, binary operators remove one, `STORE` removes one.

```formula
d_0 = 0
d_i = d_{i−1} + e_i
D_max = max(d_i for all i)
where
d_0: the stack depth before the first instruction: the stack starts empty
d_i: the stack depth after instruction number i, counted in values
i: the instruction number, counting from 1 for the first instruction
d_{i−1}: the depth just before instruction i
e_i: instruction i's effect on the depth: +1 for PUSH and LOAD, −1 for a binary operator, STORE or RET, and 0 for NEG (it pops one value and pushes one)
D_max: the maximum stack depth: how many stack slots the VM must reserve
max: the largest of the listed values
In words: start from an empty stack, add each instruction's effect in turn, and remember the deepest point reached.
```

For the program above, the depths after each instruction are 1, 0, 1, 2, 1, 2, 1 and finally 0 after `RET`, so D_max is 2: the VM needs room for only two values.

Tree shape matters. `((1+2)+3)+4` needs a depth of 2, while `1+(2+(3+4))` needs 4, because every left operand waits on the stack while the right side is computed. The same idea, for registers, is Sethi–Ullman numbering below.

Stack code is compact and trivial to generate, which is why it is popular for portable bytecode. The bytecode records an evaluation order, but implementations can cache stack values in hardware registers or optimize the instruction sequence.

## Key takeaways
- Emit child code before its operator and use checker-resolved slots for bindings.
- Instruction stack effects determine the maximum operand-stack depth.

## Further reading
- [LLVM code generator design](https://llvm.org/docs/CodeGenerator.html)
- [Linear scan register allocation — Poletto and Sarkar](https://web.cs.ucla.edu/~palsberg/course/cs132/linearscan.pdf)
- [Register allocation and coalescing research](https://www.cs.princeton.edu/~appel/modern/text/color1.html)
- [C11 committee draft: expressions and integer arithmetic](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [AArch64 procedure-call standard](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
