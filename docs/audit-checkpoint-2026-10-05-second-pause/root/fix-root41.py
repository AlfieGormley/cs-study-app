from pathlib import Path
import json
B=Path('content/architecture/01-data-representation');p=B/'rep-number-systems.md';s=p.read_text()
def r(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
r('Everything a computer stores (numbers, text, pictures, programs) ends up as a long row of switches that are either off or on.', 'Digital computers represent numbers, text, pictures and programs using binary states. These are logical states, implemented by physical storage and signalling technologies rather than necessarily one literal switch per bit.')
r('Two hex digits make one byte', 'Two hex digits represent one eight-bit byte')
r('are all written in hex.', 'are often written in hex.')
r('In C, C++, Java and JavaScript (non-strict), a literal starting with `0` is octal.', 'An integer literal such as `010` is octal in C, C++ and Java, and in JavaScript legacy non-strict syntax. Other prefixes and floating literals have separate rules; JavaScript legacy literals containing 8 or 9 may instead be decimal.')
r('printf("%x %o\\n", 181, 181);','printf("%x %o\\n", 181u, 181u);')
r("only if its denominator's prime factors all divide *b*.", 'if and only if, after reducing it to lowest terms, every prime factor of its denominator divides *b*.')
r('the smallest addressable unit of memory on essentially all machines.', 'the smallest addressable unit on common byte-addressed processors; some DSPs and other architectures differ.')
r('A "64-bit CPU" has 64-bit registers and addresses.', 'A "64-bit CPU" usually has 64-bit general-purpose integer registers. Implemented virtual and physical address widths may be smaller and need not equal each other.')
r('| 8 bits | 0–255 | bytes, ASCII |', '| 8 bits | 0–255 | octets; ASCII fits in seven bits |')
r('The gap grows with each prefix: about 2.4% at kilo, 7.4% at giga, 10% at tera.', 'Measured relative to the decimal unit size, the binary unit is about 2.4% larger at kilo, 7.4% at giga and 10.0% at tera. The displayed numeric shortfall uses a different denominator: 1 TB is about 0.9095 TiB, about 9.05% below the number 1.')
r('- A byte is 8 bits;', '- An octet is 8 bits; a C byte contains CHAR_BIT bits (at least 8);')
p.write_text(s)
p=B/'rep-number-systems.questions.json';qs=json.loads(p.read_text());q={str(i+1):v for i,v in enumerate(qs)}
q['3']['prompt']=q['3']['prompt'].replace('C program','C fragment, inside main with <stdio.h> included,')
q['8']['workedExample']=q['8']['workedExample'].replace('In practice you would probably store it in a 16-bit field, because memory is addressed in whole bytes.', 'A 16-bit field is convenient on common byte-addressed machines, but a packed format can use exactly 10 bits per ID.')
q['9']['workedExample']=q['9']['workedExample'].replace('any base from 2 to 36;', 'bases 2 through 36 (or 0 to infer a supported literal prefix);')
q['10']['options'][3]['explanation']='Correct. Integer register width need not match implemented virtual or physical address width.'
q['11']['options'][2]['explanation']='This changes the last two bits from 01 to 10. The first eight multiply-by-two steps give 00011001; 00011010 would instead be rounding that eight-place approximation upward.'
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n')
p=B/'rep-integers.md';s=p.read_text()
r("Almost every computer built since the 1970s uses one of them: **two's complement**.", 'Mainstream present-day processors use **two\'s complement** for signed integers.')
r('Only division, comparison, widening and right shifts need to know the sign.', 'Division, comparison, widening, high multiplication bits and arithmetic flags can depend on signedness.')
r('although no mainstream compiler had used them for decades.', 'although two\'s complement was already the norm on common general-purpose targets. Representation does not change the rule that signed arithmetic overflow is undefined.')
r('CPUs record two different kinds of overflow after an add:', 'Architectures such as x86, and flag-setting ARM add instructions, distinguish two kinds of overflow. Not all ISAs have these flags:')
r('The program has no meaning once it happens, and the optimiser is allowed to assume it never does.', 'The C standard imposes no requirements on an execution with undefined behaviour; consequences need not be confined to the point of overflow. Optimisers may assume defined executions do not overflow.')
r('Or check before you add: `if (b > 0 && a > INT_MAX - b)`.', 'Or check both directions before adding `int` operands: `if ((b > 0 && a > INT_MAX - b) || (b < 0 && a < INT_MIN - b))` detects overflow without first overflowing.')
r('`-fwrapv` makes signed overflow wrap, `-ftrapv` makes it trap,', 'GCC\'s `-fwrapv` specifies wrapping for signed addition, subtraction and multiplication, and `-ftrapv` requests traps for those operations; neither is a blanket fix for every undefined integer operation,')
r('It is undefined in C, and in practice produces `INT_MIN` again.', 'It is undefined in C; a wrapping hardware instruction may produce `INT_MIN` again, but the compiler need not preserve that result.')
r('When the hash is `Integer.MIN_VALUE`, `Math.abs` returns it unchanged (Java defines wrapping), the result is negative, and indexing the array throws.', 'For positive n, when the hash is `Integer.MIN_VALUE`, `Math.abs` returns it unchanged. Its remainder is negative unless n divides it exactly; a negative index throws.')
r('−1 becomes 4,294,967,295,', 'For 32-bit unsigned int, −1 becomes 4,294,967,295,')
r('/* never ends: i is unsigned */', '/* condition cannot stop unsigned i */')
r('`i >= 0` is always true for an unsigned type, so when `i` reaches 0, `i--` wraps to `SIZE_MAX`. Compile with `-Wall -Wextra` (which enables `-Wsign-compare` and `-Wtype-limits`) to catch both.', '`i >= 0` is always true, so the condition cannot stop the loop. After unsigned wrap (or immediately for n = 0), indexing is out of bounds: this is undefined behaviour, not a guaranteed infinite loop. GCC warnings such as `-Wsign-compare` and `-Wtype-limits` can help; flags and diagnostics differ between compilers. A safe reverse traversal is `for (size_t i = n; i > 0; ) use(a[--i]);`.')
r('It grows as needed, so `2**100` is exact and `int` never overflows.', 'Arithmetic has no fixed-width wraparound, so `2**100` is exact. Storage and implementation limits still apply; a computation can fail for lack of resources.')
r('NumPy warns about overflow for scalars, but array operations wrap silently', 'under the usual NumPy error settings scalar arithmetic warns, while integer array arithmetic generally wraps without that warning')
a='- **Ariane 5, 1996.**';b='- **Boeing 787, 2015.**';start=s.index(a);end=s.index(b,start)
s=s[:start]+'''- **Ariane 5, 1996.** A conversion of the horizontal-bias alignment result (related to horizontal velocity) from 64-bit floating point to a 16-bit signed integer raised an exception. Both inertial reference systems failed through the same software path; the inquiry identified reuse of assumptions from Ariane 4 and inadequate protection/testing, not just a number being too large.
'''+s[end:]
r('shutting down electrical power. 2^31 hundredths of a second is 248.55 days, consistent with a signed 32-bit counter of centiseconds.', 'potentially losing all AC electrical power if the units entered failsafe together. The FAA directive states the counter-overflow interval; it does not specify a 32-bit centisecond representation. That implementation claim is omitted because it could not be verified from the directive.')
a='- **YouTube, 2014.**';start=s.index(a);end=s.index('- **The year 2038 problem.**',start)
s=s[:start]+'''> [!note] Evidence gap
> The YouTube/Gangnam Style migration anecdote is omitted: the original engineering account of counter type and migration timing was not available for reliable primary-source verification. A hypothetical signed 32-bit view counter still has the demonstrable limit 2,147,483,647.

'''+s[end:]
r('then wraps to December 1901.', 'and a wrapping interpretation of the next bit pattern corresponds to December 1901. Actual software may fail differently; signed overflow in C is not guaranteed to wrap.')
r('Modern 64-bit systems use a 64-bit `time_t`,', 'Common current 64-bit Unix ABIs use a 64-bit `time_t`,')
r('- Mixing signed and unsigned in C comparisons converts the signed side, so −1 becomes huge.', '- Mixing int and unsigned int converts the signed side to unsigned. Other signed/unsigned combinations follow ranks and representable ranges, not a universal unsigned-wins rule.')
s+='\n- [FAA 2015 Boeing 787 directive](https://www.govinfo.gov/content/pkg/FR-2015-05-01/pdf/2015-10066.pdf)\n- [GCC code generation options](https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html)\n'
p.write_text(s)
p=B/'rep-integers.questions.json';qs=json.loads(p.read_text());q={str(i+1):v for i,v in enumerate(qs)}
q['3']['workedExample']=q['3']['workedExample'].replace('negating it gives itself.', 'fixed-width modular negation reproduces that pattern; a C expression first follows integer promotions and may produce 32768 in a wider int.')
q['4']['prompt']=q['4']['prompt'].replace('An 8-bit CPU adds', 'An 8-bit addition with unsigned carry and two\'s-complement signed-overflow flags adds')
q['6']['prompt']=q['6']['prompt'].replace('holding `0xF6`', 'with the bit pattern `0xF6` (value −10)')
q['6']['workedExample']=q['6']['workedExample'].replace('the compiler emits `movsx`; for a `uint8_t` it would emit `movzx`', 'a compiler can use `movsx`; for a `uint8_t` it can use `movzx`')
q['9']['options'][2]['explanation']='Both operands already have type int, so the operation stays int. Integer promotions also cover certain bit-fields and enumeration types, not only nominally narrow integer types.'
q['9']['workedExample']=q['9']['workedExample'].replace('On ARM64 Clang emits just', 'For example, an ARM64 Clang build may emit')
q['10']['options'][3]['text']='Integer division by 10 overflows'
q['10']['workedExample']=q['10']['workedExample'].replace('It is rare because only one hash value in 2³² triggers it, which is exactly why it survives testing.', 'Only one possible int hash value triggers this abs issue, but its frequency depends on the keys and hash function; uniform probability cannot be assumed.')
q['11']['options'][3]['explanation']='That is 2³¹ hundredths of a second. It differs from the unsigned millisecond units here; the FAA\'s 248-day incident alone does not establish its counter representation.'
q['11']['workedExample']=q['11']['workedExample'].replace('across one wrap (mod 2³²)', 'across wrap provided the actual elapsed interval is less than 2³² milliseconds').replace(' This bug caused some Windows 95/98 machines to hang after 49.7 days of uptime.', ' Distinguishing intervals of one full counter period or more requires additional state.')
q['12']['workedExample']=q['12']['workedExample'].replace('Conversions *to* unsigned are always defined; conversions of out-of-range values *to* signed are implementation-defined, not undefined.', 'Integer-to-unsigned conversion is defined modulo the range. Under the C23 rules used here, an out-of-range integer-to-signed conversion gives an implementation-defined result or raises an implementation-defined signal. Floating-to-integer conversion has separate rules.')
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n')
print('number/integer corrections applied')
