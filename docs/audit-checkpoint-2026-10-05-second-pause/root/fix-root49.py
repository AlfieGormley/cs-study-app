from pathlib import Path
import json
p=Path('content/architecture/03-isa/isa-loops-arrays-structs.md');s=p.read_text()
s=s.replace('Apart from the first, schematic, example, the listings are real Clang `-O1` output for Linux (Intel syntax for x86-64), lightly trimmed.', 'The listings are illustrative scalar implementations using Linux LP64 type sizes and System V x86-64 or AAPCS64 conventions. They are not promises of exact Clang output; version, flags and target change instruction selection. Assume valid object bounds and no signed C arithmetic overflow. Partial dispatch listings explicitly omit case bodies.')
s=s.replace('An `if` becomes', 'One common lowering of an `if` uses')
s=s.replace('That trades a possible misprediction (around 15–20 cycles on a modern core) for always computing both values.', 'This can trade branch-misprediction costs for evaluating both candidate values; whether it helps depends on the core, dependencies and workload. A universal cycle penalty is omitted because no particular core or measurement is specified.')
s=s.replace('For this exact snippet Clang is cleverer still.', 'For this snippet another valid lowering is possible.')
s=s.replace('Expect this kind of rewrite whenever the two values differ by a constant.', 'This illustrates one possible rewrite; inspect actual compiler output to see whether it is used.')
s=s.replace('Compilers instead **rotate** the loop:', 'Compilers can **rotate** the loop:')
s=s.replace('ARM64 Clang goes further and turns the index', 'An A64 version turns the index')
a=s.index('// n == 0') if '// n == 0' in s else -1
old='    mov   x0, x8\n    ret\n```';assert old in s
s=s.replace(old,'    mov   x0, x8\n    ret\n.Lzero:\n    mov   x0, #0\n    ret\n```',1)
s=s.replace('a multiply per iteration becomes an add.', 'an indexed-address recurrence becomes a pointer increment. The original scaled addressing did not necessarily require a separate multiply instruction.')
s=s.replace('Everything between the label and the branch is the loop body.', 'Then inspect the control-flow graph for a cycle; backward branches alone do not prove source-level loop boundaries in arbitrarily laid-out code.')
s=s.replace('You will see the scalar loop kept as a tail for the last few elements.', 'Remainders may use a scalar tail, masked vectors or other cleanup.')
s=s.replace('anything that doesn\'t change between iterations (a bound, an address) is computed once before the loop.', 'expressions proven invariant may move outside a loop when doing so preserves language semantics and is profitable.')
s=s.replace('The structure is still "guard, main loop, remainder loop".', 'A common structure is a guard, main loop and remainder handling; it is not universal.')
s=s.replace('For an array of elements of size `s`, the address of `a[i]` is `a + i*s`.', 'In byte-address notation, element `a[i]` starts at `base + i*s`, where `s` is the element size. C’s typed expression `a + i` already applies that scaling.')
s=s.replace('element `a[i][j]` lives at `a + (i*C + j)*4`.', 'with 4-byte `int`, element `a[i][j]` has byte address `base + (i*C + j)*4`; this is not a literal typed C pointer expression.')
s=s.replace('Each field is aligned to its own size (on x86-64 and ARM64 Linux),', 'Each field has a type- and ABI-defined alignment, not necessarily equal to its size,')
s=s.replace('that is 8 MB saved and a third fewer cache lines touched.', 'the allocation saves 8,000,000 bytes. A full sequential byte scan has roughly one-third less data; actual cache-line traffic depends on alignment and which fields are accessed.')
s=s.replace('stride 24 and offset 4 tell you the element size and which field is in use.', 'under the assumed direct p[i].field access, stride 24 and offset 4 reveal element size and field offset; they do not uniquely reconstruct the original type or declaration.')
s=s.replace('A `switch` over **dense** case values compiles to', 'A `switch` over **dense** case values can compile to')
s=s.replace('The cost is constant whatever the value of `x`: one load and one indirect branch.', 'For in-range inputs this sequence uses a fixed number of dispatch instructions, including one table load and one indirect branch. Elapsed time is not constant: caches and prediction matter, and out-of-range inputs take a different path.')
s=s.replace('becomes a range check and a single load from an array of the answers.', 'can become a range check and a table lookup; a simple arithmetic progression may instead become arithmetic.')
s=s.replace('Unoptimised code stores every variable to the stack and reloads it, so a loop looks five times bigger than it really is.', 'Unoptimized code often spills and reloads locals, making a listing longer; no fixed size ratio applies.')
s=s.replace('If the compiler cannot prove two pointers don\'t overlap, it must reload values from memory each iteration and may not vectorise. `restrict` in C (or Rust\'s borrow rules) gives it that proof.', 'Possible aliasing can prevent some transformations, but compilers may use runtime overlap checks or other proofs. C `restrict` provides specific access-based promises that must be honored; it does not simply declare that every pointer has a different numerical address. Rust reference rules also have specific validity and aliasing constraints.')
s=s.replace('`if` compiles to a compare and a branch on the *inverted* condition;', 'An `if` may use a compare and a branch on the inverted condition;')
s=s.replace('Loops are rotated into', 'Loops can be rotated into')
s=s.replace('ordering fields largest-first minimises padding.', 'ordering suitable scalar fields by alignment often reduces padding, but is not a universal minimum-size rule for arbitrary types.')
s=s.replace('Dense `switch` statements become', 'Dense `switch` statements may become')
p.write_text(s);p=p.with_suffix('.questions.json');q=json.loads(p.read_text())
q[0]['prompt']+=' Assume a 4-byte int and an in-range index.'
q[0]['workedExample']=q[0]['workedExample'].replace('`a + i * sizeof(int)` = `a + 4i`','byte address `base + i * sizeof(int)` = `base + 4i` (C pointer arithmetic already scales `a + i`)')
q[2]['prompt']='Which is a useful first clue when looking for a loop in a conventional scalar assembly listing, to be confirmed by inspecting control-flow paths?'
q[2]['options'][2]['explanation']='Comparisons also occur in selections and guards, and not every selection uses CMP. A comparison alone does not establish repetition.'
q[2]['options'][3]['explanation']='A backward conditional branch is a common clue. Confirm that control can cycle back to it; layout alone does not uniquely identify a source-level loop.'
q[2]['workedExample']='In the lesson’s SUM, the backward JNE returns to the loop body, whose fall-through path reaches JNE again. That forms a cycle. Arbitrary code can place non-loop blocks at lower addresses, and loops can use indirect or unconditional branches, so use the control-flow graph to confirm the pattern.'
q[3]['options'][1]['explanation']='A signed JG would fail to reject −1, but MOV EAX,EDI then zero-extends it to 4,294,967,295. The subsequent lookup would use a huge positive index, not table[−1].'
q[5]['prompt']+=' Assume rdi is the exact base and these instructions implement a direct p[i].field access with no further index transformation.'
q[5]['options'][2]['explanation']='The address arithmetic alone does not establish member types. EAX receives four bytes; it does not reveal whether those bits came from an integer, float or another representation.'
q[5]['workedExample']='LEA computes 5i, and MOV loads four bytes from base + 40i + 4. Under the stated direct indexing assumption, the element stride is 40 and the field offset is 4. This does not reveal the member’s name, semantic type, declaration position or the other fields.'
q[6]['prompt']+=' Assume 4-byte int.'
q[7]['options'][0]['text']='Dense cases with distinct code bodies can use a jump table and an indirect branch'
q[7]['options'][0]['explanation']='Correct as a possible lowering. Case count, target, optimization settings and profiling influence the choice.'
q[7]['options'][1]['text']='Widely spaced case values can use compare chains or trees instead of a huge sparse table'
q[7]['options'][1]['explanation']='Correct. A compiler may choose comparisons, bit tests, several smaller clusters or another profitable form.'
q[7]['workedExample']='Dense code cases can use jump tables; sparse cases can use comparisons; constant-result cases can use data tables or arithmetic. None is unconditionally fastest. The compiler considers target costs, case structure and options such as -fno-jump-tables.'
q[8]['workedExample']=q[8]['workedExample'].replace('and a third fewer cache lines to stream through.', 'for allocation. A complete streaming scan has roughly one-third fewer bytes; exact cache-line traffic depends on access patterns and alignment.')
q[10]['prompt']='In the shown position-independent jump table, targets and table move together and every offset fits signed 32 bits. Compared with 64-bit absolute entries, which are genuine benefits of 32-bit relative entries? Select all that apply.'
q[10]['options'][0]['explanation']='Each entry uses four rather than eight bytes, before any padding. Fewer cache lines may suffice, depending on table size, alignment and accessed entries.'
q[10]['options'][1]['explanation']='The target-minus-table differences remain fixed when both move by the same amount. These entries therefore need no load-time base fixups and can remain in shareable read-only storage.'
q[10]['options'][3]['explanation']='JMP RAX uses a 64-bit target, subject to canonical-address, mapping, permission and other architectural checks. Relative table entries are an encoding choice.'
q[10]['workedExample']='With targets and table in the same relocated module, target−table is fixed at link time. Four-byte entries halve entry storage and avoid load-time base relocations for those entries. The dispatch adds each offset to the table’s runtime base. This changes storage and address calculation, not a guarantee about exact branch prediction or runtime cost.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print('Applied loops lesson and 11-question corrections; fixed missing A64 .Lzero target')
