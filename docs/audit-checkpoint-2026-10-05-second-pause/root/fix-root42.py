from pathlib import Path
import json
B=Path('content/architecture/01-data-representation');p=B/'rep-bitwise.md';s=p.read_text()
def r(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
r('A single instruction can test, set or clear 64 flags,', 'A 64-bit bitwise operation can manipulate up to 64 flag bits at once,')
r('To work on bit *k*, build the mask `1 << k`:', 'For unsigned int x and 0 ≤ k < its width, build the mask `1u << k`. A wider x needs a correspondingly wide unsigned mask; complementing a 32-bit mask before widening it would clear the upper bits of a 64-bit x.')
r('if (x & (1u << k)) /* test bit k   */', 'if (x & (1u << k)) { /* bit is set */ }')
r('Each `O_` constant is a different power of two, so OR-ing them sets independent bits, and the kernel tests each with AND.', 'Many open options are independent bit flags, but **not every O_ constant is one bit**. Access modes are alternatives selected with O_ACCMODE; O_RDONLY is commonly zero. Test a mode with `(flags & O_ACCMODE) == O_RDONLY`, not a simple AND with O_RDONLY. Creation mode 0644 is also filtered by the process umask when a file is created.')
r('A mask of the low *n* bits is `(1 << n) - 1`.', 'In Python, for non-negative n, a mask of the low *n* bits is `(1 << n) - 1`. In C, the operand type, promotions and shift-count limit matter; use an appropriately wide unsigned mask and handle n equal to the width separately.')
r('So `-17 >> 1` is −9 but `-17 / 2` is −8. Compilers know this, which is why `x / 2` on a signed `int` compiles to a shift plus a small correction, not a bare shift.', 'On C implementations with arithmetic right shift, `-17 >> 1` is −9 while C99-and-later `-17 / 2` is −8. A compiler may implement signed division using a corrected shift, unless it proves a correction unnecessary; a bare arithmetic shift is not generally equivalent.')
r('**at least the width** of the type', '**at least the width** of the promoted left operand')
r('On x86 the hardware masks the count to 5 bits,', 'For ordinary 32-bit x86 shifts the hardware masks the count to 5 bits (6 bits for 64-bit shifts),')
r('Left-shifting a signed value so that a 1 reaches or passes the sign bit is undefined.', 'Under C23 and earlier ISO C rules, left shift of a negative signed value is undefined, even by zero; for a non-negative signed value, the multiplied result must be representable in the promoted type.')
r('The safe habit: do bit manipulation on **unsigned** types (`uint32_t`, `uint64_t`) and write constants with a `u` suffix.', 'Use suitably wide **unsigned** operands and masks, check shift counts, and account for integer promotions. A plain `1u` has unsigned-int width; use a wider constant when needed. These are C rules, not a statement of the differing modern C++ shift rules.')
r('These come up in interviews, in kernels and in high-performance code.', 'The following identities assume non-negative Python integers or unsigned fixed-width C arithmetic as appropriate. Signed C `x - 1` or `-x` can overflow at the minimum value; narrow unsigned operands can also undergo integer promotion.')
r('def popcount(x):\n    n = 0', 'def popcount(x):\n    if x < 0:\n        raise ValueError("negative input")\n    n = 0')
r("In practice use the hardware: x86 `POPCNT`, ARM `CNT`, C's `__builtin_popcount`, C23's `stdc_count_ones`, Python 3.10+'s `int.bit_count()`.", 'Prefer supported library/compiler operations: GCC/Clang `__builtin_popcount` (and width-appropriate variants), C23 `stdc_count_ones`, or Python 3.10+ `int.bit_count()`. They may use hardware such as x86 POPCNT or suitable ARM instructions, but lowering depends on the target. Python bit_count counts ones in the absolute value, unlike this non-negative-only loop; arbitrary-precision cost grows with integer size.')
r('The *position* of that bit is "count trailing zeros" (`__builtin_ctz(0x2C)` is 2).', 'For nonzero unsigned x, the position of that bit is "count trailing zeros" (`__builtin_ctz(0x2C)` is 2). GCC\'s traditional `__builtin_ctz(0)` is undefined; handle zero explicitly.')
r('in O(n) time and O(1) space.', 'in O(n) word operations and O(1) auxiliary words for fixed-width values; arbitrary-precision integer costs depend on bit length.')
r('A one-time pad and the keystream step of stream ciphers such as ChaCha20 are XOR with a key; doing it again decrypts.', 'A one-time pad XORs with a secret uniformly random message-length pad used only once. A stream cipher such as ChaCha20 XORs plaintext with a generated keystream, not directly with its short secret key. Repeating the same XOR recovers the input; that identity alone does not provide secure encryption.')
r('It is slower on modern CPUs than a plain swap via a register, it fails if `a` and `b` are the same memory location (both become 0), and compilers already generate optimal swaps.', 'It introduces dependencies and can lose to a plain swap, but performance depends on compilation and target. It fails for aliased a and b (the shared value becomes 0). Prefer a clear temporary or language swap; no compiler universally guarantees optimal code.')
r('Routers do this lookup billions of times a second.', 'Actual routing lookup uses longest-prefix matching and implementation-specific data structures. No universal throughput rate is implied.')
r('With a power-of-two table size, `hash & (size - 1)` replaces the slower `hash % size`.', 'For non-negative or unsigned hashes and a nonzero power-of-two table size, `hash & (size - 1)` equals `hash % size`. Compilers can already optimise remainder by a known power of two; a speedup is not guaranteed.')
p.write_text(s)
p=B/'rep-bitwise.questions.json';qs=json.loads(p.read_text());q={str(i+1):v for i,v in enumerate(qs)}
q['2']['prompt']=q['2']['prompt'].replace('unsigned `x`', 'unsigned int `x`')
q['5']['prompt']=q['5']['prompt'].replace('A 32-bit hardware register stores','A register value read into a uint32_t on a 32-bit-int C platform stores')
q['5']['workedExample']+=' This is a value-manipulation example; a live device register may have read/modify/write side effects that require its hardware-specific access procedure.'
q['7']['prompt']='In C on a platform where uint32_t is unsigned int and int is 32 bits, which statements are always true? Select all that apply.'
q['7']['options'][3]['text']='`(x ^ x) == 0`'
q['7']['options'][3]['explanation']='Correct. Parentheses matter: the unparenthesised C expression x ^ x == 0 would mean x ^ (x == 0), not the identity intended here.'
q['8']['workedExample']=q['8']['workedExample'].replace('it adds 3 to negative values first.', 'one possible implementation adds 3 to negative values before arithmetic shifting, unless analysis permits a simpler operation.')
q['9']['prompt']=q['9']['prompt'].replace('    n = 0','    if x < 0:\n        raise ValueError("negative input")\n    n = 0')
q['9']['workedExample']=q['9']['workedExample'].replace("For sparse values this beats checking all 64 positions, but the `POPCNT` instruction (`int.bit_count()` in Python 3.10+) is faster still.", 'The loop performs fewer iterations on sparse non-negative inputs, but speed depends on the implementation. Prefer Python int.bit_count(); it is not a promise of one POPCNT instruction for an arbitrary-size Python integer.')
q['10']['workedExample']=q['10']['workedExample'].replace('so collisions roughly quadruple.', 'so the expected colliding-pair count for independent uniform hashes scales by 1000/256 ≈ 3.91 at the same number of keys; other collision measures need their own model.')
q['12']['prompt']='In ISO C23, with 32-bit int and uint32_t defined as unsigned int, which expressions have undefined behaviour? Select all that apply.'
q['12']['workedExample']=q['12']['workedExample'].replace('If E1 is signed, the result must be representable, otherwise UB.', 'If the promoted E1 is signed, E1 must be non-negative and the multiplied result representable, otherwise UB.')
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n')
print('bitwise corrections applied')
