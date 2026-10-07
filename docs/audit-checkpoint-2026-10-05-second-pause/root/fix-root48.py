from pathlib import Path
import json
base=Path('content/architecture/03-isa')
p=base/'isa-reading-assembly.md';s=p.read_text()
s=s.replace('Sixteen 64-bit general-purpose registers.', 'Baseline x86-64 provides sixteen 64-bit general-purpose registers; APX adds more on supporting implementations.')
s=s.replace('Here is `long f(long x) { return x * 5 + 7; }` in each:', 'Here is a representative implementation of `long f(long x) { return x * 5 + 7; }`, assuming 64-bit `long`, the System V x86-64 or AAPCS64 integer convention, and inputs without signed overflow:')
s=s.replace('GDB and `objdump` default to AT&T;', 'GNU GDB and GNU `objdump` normally default to AT&T on x86;')
s=s.replace('ARM64 is always destination first.', 'A64 instructions with an explicit result normally put the destination first; stores such as `str w0, [x1]` put the source register before the destination address.')
s=s.replace('Conditional branches do not compare anything themselves. A previous instruction sets the flags; the branch reads them.', 'Flag-based branches such as x86 `jcc` and A64 `b.cond` read flags set by an earlier instruction. Other branches test a register directly, such as A64 `cbz`/`cbnz` and `tbz`/`tbnz`.')
s=s.replace('only the `s` forms do:', 'ordinary ADD/SUB/AND leave flags unchanged unless using the flag-setting forms:')
s=s.replace('For comparisons, the signedness of a C variable shows up **only** in which condition code the compiler picks.', 'For these same-width integer comparisons, signedness determines which condition code interprets the flags. It can also affect earlier conversions and instruction selection.')
s=s.replace('Clang `-O1` produces essentially this (labels renamed, comments added).', 'The following is an illustrative scalar implementation, not a promise of exact output from any compiler version. Assume 64-bit `long` and a valid array of at least `n` elements when `n > 0`.')
s=s.replace('A backward branch (`jne .Lloop`) jumping to an earlier label is a loop.', 'Here, the backward branch (`jne .Lloop`) forms a loop. In arbitrary code, inspect the control-flow paths rather than assuming every backward branch means a source-level loop.')
s=s.replace('The ARM64 version from the same source:', 'An equivalent A64 implementation:')
s=s.replace('The same ideas, with RISC flavour: the compiler rewrote', 'The same ideas, with different instruction choices: this version rewrites')
s=s.replace('and CPUs recognise it as dependency-free', 'and many cores recognize a dependency-breaking zero idiom')
s=s.replace('`eax = rdi * 3`, no memory access', '`eax = low32(rdi * 3)`, no memory access')
s=s.replace('sign-extend `int` to `long`', 'sign-extend 32 to 64 bits (an `int` to 64-bit `long` here)')
s=s.replace('Division is slow (tens of cycles), so compilers avoid it.', 'Division can be more expensive than a suitable multiply/shift sequence; costs depend on the instruction and core.')
s=s.replace('(`-7 >> 1` is `-4`)', '(the machine’s arithmetic shift of −7 by one yields −4; negative signed right shift in C17 is implementation-defined)')
s=s.replace('that is what it is.', 'division by a constant is one possibility; confirm the complete sequence before drawing that conclusion.')
s=s.replace('`-O0` output stores every variable to the stack and reloads it,', '`-O0` output often stores locals to the stack and reloads them,')
s=s.replace('Find where `rax`/`x0` is set before `ret`; that is the return value.', 'For a simple integer result, look for `rax`/`x0` before `ret`; other return types follow different ABI rules.')
s=s.replace('On Linux and macOS:', 'For ordinary fixed-parameter integer/pointer arguments under the conventions shown:')
s=s.replace('On both ISAs, `cmp a, b`', 'In Intel x86 syntax and A64 syntax, `cmp a, b`')
s=s.replace('x86-64 has 16 GPRs', 'Baseline x86-64 has 16 GPRs')
s=s.replace('ARM64 is destination first.', 'A64 arithmetic normally places the result first; stores instead place their source register first.')
s=s.replace('Branches read flags set by an earlier', 'Flag-based branches read flags set by an earlier')
p.write_text(s);p=p.with_suffix('.questions.json');q=json.loads(p.read_text())
q[0]['options'][1]['explanation']='Correct. In 64-bit mode an ordinary write to EAX clears RAX’s upper half, leaving the specified zero-extended value.'
q[3]['workedExample']=q[3]['workedExample'].replace('when that\'s at least as fast', 'when their cost model favors it')
q[5]['options'][2]['text']='Absolute value for inputs other than INT_MIN; for INT_MIN the 32-bit result remains 0x80000000'
q[5]['options'][2]['explanation']='Correct. The instruction conditionally negates a 32-bit bit pattern. For ordinary inputs this gives the absolute value; INT_MIN has no positive counterpart representable as a signed 32-bit int.'
q[5]['workedExample']='CMP sets flags for x relative to zero; CNEG conditionally negates the 32-bit value. For −5, 5 and 0 the results are 5, 5 and 0. For INT_MIN the hardware result is 0x80000000, which still represents INT_MIN as signed 32-bit. This does not mean C abs(INT_MIN) is defined to wrap: that C expression has undefined behaviour when the result is unrepresentable.'
q[6]['options'][0]['explanation']='Correct. XOR clears EAX and its 32-bit write clears the upper half of RAX. The two-byte zero idiom is also recognized as independent of the old register value on many cores.'
q[8]['prompt']=q[8]['prompt'].replace('to a single instruction', 'to a plain arithmetic shift after copying the argument')
q[8]['workedExample']+=' The shifts here describe x86 instructions; do not infer portable C17 semantics for right-shifting a negative signed integer.'
q[9]['prompt']=q[9]['prompt'].replace('x86-64 function', 'System V x86-64 function')+' Assume idx is within the array bounds and the table pointer is valid.'
q[10]['prompt']=q[10]['prompt'].replace('compiled `count_pos`', 'illustrative `count_pos`')
q[10]['options'][1]['text']='The upper bits of rdx must be made zero before adding it; the shown xor does that before setg writes dl'
q[10]['options'][1]['explanation']='Correct. SETG writes only DL. Without establishing the other bits as zero, ADD RAX,RDX can include stale data. An alternative implementation could zero-extend DL after SETG.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
p=base/'isa-calling-conventions.md';s=p.read_text()
s=s.replace('no memory traffic at all.', 'no automatic return-address stack access from BL/RET themselves; the function can still access memory.')
s=s.replace('a function that calls another must save `x30` first', 'a function making a nested call and later returning to its own caller must preserve its original return address')
s=s.replace('ARM64 uses **AAPCS64** (Apple\'s platforms follow it with small changes).', 'Linux AArch64 uses **AAPCS64**; Apple’s ARM64 ABI has material differences, particularly for variadic and stack arguments. The table covers common fixed scalar parameters, not every ABI type.')
s=s.replace('as Clang compiles it for x86-64:', 'in a representative System V x86-64 sequence. Assume `rsp` is already 16-byte aligned at the start of this fragment:')
a=s.index('- A struct of up to');b=s.index('## Who saves',a)
s=s[:a]+'''Aggregate returns depend on ABI classification, not size alone:

- Under System V AMD64, many ordinary aggregates up to 16 bytes return in integer and/or vector registers. Unaligned fields and other classification rules can force memory return even for small aggregates; supported vector-shaped aggregates have additional exceptions.
- Under base AAPCS64, ordinary non-homogeneous composites up to 16 bytes can use `x0`/`x1`. Homogeneous floating-point aggregates of up to four members can use vector registers even when larger than 16 bytes.
- For an indirect return, the caller supplies storage. System V passes its address in `rdi`, consuming an integer argument slot, and returns that address in `rax`. AAPCS64 uses `x8`, leaving the normal argument registers available. Consult the full ABI for complex/vector types and C++ objects.

'''+s[b:]
s=s.replace('`rbx rbp r12`–`r15` |', '`rbx rbp r12`–`r15`, restored `rsp` |')
s=s.replace('Each active call has a **stack frame**:', 'When a function needs stack storage, its **stack frame** is')
s=s.replace('At `-O2` compilers turn this into a loop, so here it is written out by hand in the style of `-O1` output.', 'Compilers may replace this recursion with a loop. The examples below deliberately retain recursion. With 64-bit signed `long`, use inputs at most 20 for a representable factorial; the original C multiplication has undefined behaviour on signed overflow.')
s=s.replace('until it runs past the stack limit (8 MB by default for the main thread on most Linux systems) and hits a guard page: a **stack overflow** and a `SIGSEGV`.', 'until stack resources are exhausted. Stack limits and guard arrangements depend on the OS and thread configuration; Linux can signal `SIGSEGV` on stack exhaustion. No universal 8 MB default is assumed.')
s=s.replace('Unoptimised code (and code built with `-fno-omit-frame-pointer`) keeps `rbp` as a fixed reference point:', 'A classic frame-pointer prologue uses `rbp` as a fixed reference point. Compiler options and target rules determine which functions actually retain frame pointers:')
s=s.replace('Each saved `rbp` points to the caller\'s saved `rbp`, forming a linked list through the stack.', 'When callers and callees maintain compatible frame records, saved `rbp` values form a linked list through their frames.')
s=s.replace('Both ABIs require 16-byte stack alignment at calls.', 'For the ordinary calls shown, both ABIs require 16-byte stack alignment at the call boundary. System V can require stronger alignment for some stack-passed over-aligned or vector arguments.')
s=s.replace('sets `al` to the number of vector registers used', 'sets `al` to an upper bound (0–8) on the number of vector argument registers used')
s=s.replace('On Apple ARM64, variadic arguments always go on the stack', 'On Apple ARM64, anonymous variadic arguments go on the stack (named fixed parameters follow their normal rules)')
s=s.replace('and no stack is used.', 'without adding another outstanding return frame; the callee may still use stack space. ABI and language constraints determine whether this transformation is possible.')
a=s.index('- **Frame pointers are back.**');b=s.index('\n\n## Pitfalls',a)
s=s[:a]+'''- **Profiling and unwinding.** Frame pointers simplify walking a compatible chain, while unwind metadata can describe optimized frames without one. A universal performance percentage and blanket claims about distribution package rebuilds are omitted because they require version- and workload-specific evidence.'''+s[b:]
s=s.replace('in a non-leaf ARM64 function,', 'across a nested ARM64 call that must return normally,')
s=s.replace('everything else may be destroyed by a call.', 'consult the ABI tables for other preserved registers and machine state; “everything else” is too broad.')
s=s.replace('large structs are returned via a hidden pointer', 'aggregates classified for indirect return use a hidden pointer')
s+='\n- [Apple ARM64 ABI differences](https://developer.apple.com/documentation/xcode/writing-arm64-code-for-apple-platforms)\n'
p.write_text(s);p=p.with_suffix('.questions.json');q=json.loads(p.read_text())
q[0]['options'][3]['explanation']='These three scalar long arguments fit in integer registers. Aggregate and other special argument classes can follow different rules.'
q[1]['options'][0]['explanation']='BL writes the return address to X30 rather than pushing it to the stack. This does not promise that calling and executing an arbitrary function causes no memory traffic.'
q[1]['workedExample']=q[1]['workedExample'].replace('any function that itself calls another must save `x30` first', 'a function that makes a nested call and later returns normally must preserve its original return address')
q[3]['options'][3]['explanation']='These mixed scalar types use the respective register classes. Other types can require memory for reasons besides register exhaustion.'
q[4]['prompt']+=' Assume no other stack adjustments and an ordinary call requiring 16-byte alignment.'
q[5]['options'][0]['explanation']='For this 24-byte struct of three longs, RDI is used for the return-storage pointer. Other return types require their own ABI classification.'
q[5]['options'][1]['explanation']='Correct. This struct is classified for memory return. RDI carries the hidden buffer address, RSI carries x, and RAX returns the buffer address. Floating-point arguments would retain their separate vector-register allocation.'
q[5]['workedExample']='The struct of three 64-bit longs is 24 bytes and is classified MEMORY by System V AMD64. The hidden storage pointer occupies RDI, so x uses RSI. RAX returns that pointer. Under AAPCS64 this ordinary composite also uses an indirect result, but its pointer uses X8 and x remains in X0. Size alone is not a universal aggregate-return rule: AAPCS64 HFAs and other ABI-specific exceptions exist.'
q[6]['prompt']+=' Assume g returns normally with x30 still containing the address immediately after bl g, and ignore external interruption.'
q[7]['options'][2]['text']='f necessarily retains a physical stack frame that any debugger can walk while g is running'
q[7]['options'][2]['explanation']='False: a tail-call optimization removes that frame. Some debuggers can reconstruct a logical tail-call frame using suitable debug information, so absence from every backtrace is not guaranteed.'
q[7]['options'][3]['explanation']='Correct if the recursive calls are actually optimized and per-step stack requirements stay bounded. This avoids stack growth from the recursive call chain, not every possible source of stack exhaustion.'
q[7]['options'][4]['explanation']='If g needs f’s local object to remain alive, simply discarding its storage would be wrong. The optimizer must preserve the required lifetime; the mere presence of a pointer does not prove it will be used.'
q[7]['workedExample']='A valid tail call restores the outgoing function’s saved state and transfers control without adding a new return frame. The callee returns directly to the original caller. Applying this repeatedly to tail recursion avoids growth from that chain. A physical frame disappears, although debug metadata may let a debugger display a logical call. Required object lifetimes and ABI constraints can prevent the transformation.'
q[11]['workedExample']='In the stated simplified model, 8 MiB / 16 B = 524,288 levels. Actual available depth depends on other stack use, limits, guards and generated code. This hand-written instruction sequence would wrap products at machine width; C factorial overflows a signed 64-bit long above 20 and therefore has undefined behaviour. The depth exercise is not a valid large-input C factorial computation.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print('Applied reading assembly and calling conventions corrections (23 questions)')
