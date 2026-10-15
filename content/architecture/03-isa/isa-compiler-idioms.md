---
id: isa-compiler-idioms
title: Zeroing, population count, division and branch-free max
level: intermediate
minutes: 5
sourceLesson: isa-reading-assembly
summary: Recognise compiler idioms while preserving signed rounding and bounds assumptions.
---

## Idioms that look strange at first

| You see | It means |
|---|---|
| `xor eax, eax` | EAX becomes zero (2 bytes, and many cores recognize a dependency-breaking zero idiom) |
| `test rdi, rdi` then `je` | `if (rdi == 0)` |
| `lea eax, [rdi + rdi*2]` | `eax` gets three times `rdi` (low 32 bits kept), no memory access |
| `movsxd rax, edi` / `sxtw x0, w0` | sign-extend 32 to 64 bits (an `int` to 64-bit `long` here) |
| `mov eax, edi` / `mov w0, w0` | zero-extend `unsigned` to 64 bits |
| `cmovg`, `csel` | branch-free `a > b ? a : b` |
| `nop`, `nop dword ptr [rax]` | padding to align a loop or function |
| `endbr64` / `bti c` | landing pad for control-flow protection (later hardening units) |

### Count set bits by clearing one at a time

For an unsigned fixed-width input, subtracting one flips the lowest set bit and the zero bits below it. AND with the original therefore clears exactly that lowest set bit. Repeat until zero; each successful iteration counts one set bit. An initially zero input skips the loop.

```c
// Unsigned arithmetic wraps by definition.
unsigned bits(unsigned long x) {
    unsigned count = 0;
    while (x != 0) {
        // Clear the lowest remaining bit.
        x &= x - 1;
        count++;
    }
    return count;
}
```

For input 44, the set bits are at positions two, three and five, counting from zero; three iterations return 3. This pattern explains the population-count assembly exercise without assuming a dedicated POPCNT instruction.

### Division by a constant

Division can be more expensive than a suitable multiply/shift sequence; costs depend on the instruction and core. Signed `x / 2` must round towards zero, but an arithmetic right shift rounds towards minus infinity (the machine’s arithmetic shift of −7 by one yields −4; negative signed right shift in C17 is implementation-defined). So the compiler adds 1 to negative numbers first:

```
# int half(int x) { return x / 2; }
half:
    mov   eax, edi
    shr   eax, 31        # 1 if x<0 else 0
    add   eax, edi       # bias negatives
    sar   eax, 1         # arithmetic shift
    ret
```

The arithmetic shift (`sar`) rounds down, so the bias is what turns rounding down into rounding towards zero:

```formula
q = ⌊(x + c) / 2⌋
c = 1 if x < 0, otherwise 0
q = ⌊(−7 + 1) / 2⌋ = ⌊−3⌋ = −3
⌊−7 / 2⌋ = ⌊−3.5⌋ = −4
where
q: the result the code returns, which matches C's x / 2
x: the signed integer being halved, here −7
c: the bias: 1 for a negative x, 0 otherwise; `shr eax, 31` produces it by moving the sign bit down to bit 0
⌊ ⌋: floor: round down towards minus infinity, which is what an arithmetic shift right by 1 does to a halving
<: less than
In words: without the bias −7 shifts to −4 (rounded down from −3.5); adding 1 first gives −6, which halves exactly to −3, the round-towards-zero answer C requires.
```

For a non-negative `x` the bias is 0, and rounding down already equals rounding towards zero. For non-power-of-two divisors such as 10, compilers multiply by a "magic" reciprocal constant and shift. If you see a large odd constant and an `imul` where you expected a division, division by a constant is one possibility; confirm the complete sequence before drawing that conclusion.

### Branch-free max

```
# int max(int a, int b)
max:
    mov   eax, esi       # eax = b
    cmp   edi, esi       # compare a with b
    cmovg eax, edi       # if a > b: eax = a
    ret
```

```
// int max(int a, int b)
max:
    cmp   w0, w1
    csel  w0, w0, w1, gt   // a > b ? a : b
    ret
```

## Narrow arguments need explicit widening

Under System V AMD64, a 32-bit unsigned parameter defines only its argument register’s low 32 bits; the remaining bits are unspecified. Before using that value as a 64-bit array index, use a 32-bit register write such as `mov esi, esi` to clear the upper half. A valid index and pointer do not make an uninitialised upper half safe. The ABI lesson later covers the complete argument-register sequence.

## Key takeaways
- Common short sequences implement zeroing, extension and conditional selection.
- Signed division by two needs a bias for negative odd inputs.
- Recognise candidate idioms, then confirm the full data and control flow.

## Further reading
- [Compiler Explorer](https://godbolt.org/)
- [x86 and amd64 instruction reference — Félix Cloutier](https://www.felixcloutier.com/x86/)
- [x86-64 machine-level programming — CMU handout (PDF)](https://www.cs.cmu.edu/~fp/courses/15213-s07/misc/asm64-handout.pdf)
- [X86-64 — Wikipedia](https://en.wikipedia.org/wiki/X86-64)
- [AArch64 — Wikipedia](https://en.wikipedia.org/wiki/AArch64)
- [FLAGS register — Wikipedia](https://en.wikipedia.org/wiki/FLAGS_register)
