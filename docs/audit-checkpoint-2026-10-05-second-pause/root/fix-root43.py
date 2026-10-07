from pathlib import Path
import json
B=Path('content/architecture/01-data-representation');p=B/'rep-floating-point.md';s=p.read_text()
def r(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
r('Integers are exact but have a narrow range.', 'Fixed-width integers are exact within a bounded range and do not directly encode fractions.')
r('Before it, every manufacturer rounded differently, and the same program gave different answers on different machines.', 'Earlier floating-point designs differed in formats and arithmetic rules. IEEE 754 improved portability, though evaluation order, formats, compiler options and language APIs can still change results.')
r('Since that leading 1 is always there, IEEE 754 does **not store it**.', 'For normal values in the binary interchange formats discussed here, that leading 1 is implicit and is **not stored**. Subnormals and other formats require separate rules.')
r('You can compare two non-negative floats by comparing their bits as integers, which made early hardware simpler and still powers tricks like radix-sorting floats.', 'Unsigned ordering of the canonical binary32/binary64 encodings agrees with numeric ordering for values with sign bit zero, excluding NaNs. Negative zero, negative numbers and NaNs require additional handling.')
r('negating a float just flips bit 31.', 'changing the sign of a binary32 value flips bit 31 (bit 63 for binary64).')
r('JavaScript (where every number is a double)', 'JavaScript Number values (binary64, distinct from BigInt)')
r(", and why 64-bit IDs from Twitter's API are also sent as strings", '; decimal strings or BigInt are alternatives for larger exact integer IDs')
r('The gap near any value *x* is roughly *x* × epsilon.', 'For normal values away from zero, spacing scales roughly with |x| times epsilon; it is constant within each binade and doubles at powers of two. Subnormals have fixed absolute spacing.')
r('Overflow produces ±infinity rather than wrapping:', 'Under the usual non-trapping round-to-nearest mode, overflow produces ±infinity rather than integer-style wrapping; directed rounding modes may instead return a largest finite value. For example,')
r('`x != x` is true only for NaN,', 'for ordinary floating-point values, `x != x` is true only for NaN,')
r('Sorting a list containing NaNs can produce garbage, because sorting assumes a consistent ordering.', 'NaNs do not supply an ordinary total numeric ordering, so a sort using plain numeric comparisons may not give the ordering you intended. Choose an explicit NaN placement policy.')
r('This **gradual underflow** guarantees that `x - y == 0` only when `x == y`. The cost: on many CPUs, subnormal arithmetic falls back to microcode and can be tens of times slower, sometimes worse. Audio and ML code often enables "flush to zero" (FTZ/DAZ) modes to avoid this.', 'With gradual underflow and correctly rounded subtraction of finite inputs in the same format, distinct representable numbers do not collapse to zero merely because their difference is tiny. Some processors and operations incur costly assists for subnormal operands or results; others handle them efficiently. FTZ and DAZ modes change arithmetic semantics by flushing small results or treating small inputs as zero, so enable them only when the application tolerates that change.')
a='> A Patriot battery';start=s.index(a);end=s.index('\n\nPractical rules:',start)
s=s[:start]+'''> The GAO investigation found that limited precision in a time conversion caused an increasingly inaccurate tracking calculation. After over 100 hours of continuous operation, the system looked in the wrong place for the incoming Scud, which hit barracks and killed 28 Americans. This was an accumulated numerical conversion error, not physical clock drift or a failure of IEEE binary32 specifically. The GAO reports a roughly 0.34-second time error at 100 hours.
'''+s[end:]
r('**Never compare floats for exact equality** after arithmetic. Use a tolerance that fits the problem: `math.isclose(a, b, rel_tol=1e-9)`.', '**Choose equality semantics for the problem.** Exact equality is appropriate for some exact/discrete computations. For approximate results use justified relative and absolute tolerances; near zero, a positive abs_tol may be needed. `math.isclose` does not choose a scientifically valid error budget for you.')
r("**Summing many values** accumulates error. Kahan (compensated) summation or `math.fsum` fixes it.", '**Summing many values** can accumulate rounding error. Compensated summation and math.fsum reduce it; they do not make every result exact or eliminate all overflow and platform effects.')
r('This **catastrophic cancellation** wipes out most significant digits.', 'Cancellation can expose error already present in approximate operands and produce a large relative error. Subtraction of nearby floating-point values can itself be exact; rearrangement is useful when it improves the conditioning or avoids prior errors.')
r('Neural networks tolerate low precision, and halving the bits halves memory and bandwidth. Two 16-bit formats dominate:', 'Many neural-network workloads can use reduced precision with suitable training and accumulation strategies. Halving element size halves storage for the same tensor, not necessarily total model memory or traffic: auxiliary states and wider accumulators remain. Two common 16-bit formats are:')
r('| bfloat16 | 1 / 8 / 7 | ≈ 3.4e38 |','| bfloat16 | 1 / 8 / 7 | ≈ 3.39e38 |')
r('- A float is sign × 1.fraction × 2^(exponent − bias); the leading 1 is implicit.', '- A normal binary interchange value is (−1)^sign × 1.fraction × 2^(exponent − bias); subnormals, zeros, infinities and NaNs use special encodings.')
r('integers are exact only up to 2^24 (float) and 2^53 (double).', 'all integers in the consecutive ranges through 2^24 (binary32) and 2^53 (binary64) are exact, but larger values are representable only at wider spacing.')
s+='\n- [GAO investigation of the Dhahran Patriot failure](https://www.gao.gov/assets/imtec-92-26.pdf)\n- [Python math accuracy and isclose](https://docs.python.org/3/library/math.html)\n- [Google TPU bfloat16 semantics](https://cloud.google.com/tpu/docs/bfloat16)\n'
p.write_text(s)
p=B/'rep-floating-point.questions.json';qs=json.loads(p.read_text());q={str(i+1):v for i,v in enumerate(qs)}
q['2']['options'][0]['explanation']='The usual binary64, nearest-even evaluation gives this result across languages. C implementations, expression precision and compiler modes can differ; decimal arithmetic follows different representation rules.'
q['2']['options'][1]['explanation']='Python float is normally IEEE binary64, with 53 significant bits. No finite binary format represents 0.1 exactly, though the outcome of this particular equality is not determined by that fact alone.'
q['4']['options'][2]['explanation']='0xC1C80000 decodes to −25.0: its fraction encodes 0.5625 rather than the required 0.28125. A hidden-bit mistake would change the fraction differently.'
q['5']['options'][2]['explanation']='Ignoring the fraction with exponent −1 would give 0.5, not 0.25. A result of 0.25 additionally uses an incorrect scale.'
q['6']['prompt']=q['6']['prompt'].replace('in a C `float`', 'in IEEE binary32 using nearest-even rounding after each addition')
q['6']['options'][1]['explanation']='At 2²⁴ the value is far below the binary32 overflow threshold. This failure is loss of increment precision, not overflow.'
q['8']['workedExample']=q['8']['workedExample'].replace('the result of, for example, `-1e38f * 10.0f`.', 'the result of, for example, binary32 `-1e38f * 10.0f` rounded to nearest with non-trapping overflow.')
q['10']['options'][2]['explanation']='Correct for amounts in specified minor units, or decimal arithmetic with a specified precision and rounding policy. Tax, currency conversion and fractions of a minor unit still require explicit rounding rules.'
q['11']['options'][2]['text']='Subnormal arithmetic can incur substantial extra cost on some processors and operations'
q['11']['options'][2]['explanation']='Correct. Expensive assists are implementation-dependent; FTZ/DAZ may avoid them by changing results, not by preserving full gradual-underflow semantics.'
q['12']['prompt']=q['12']['prompt'].replace('most directly fixes this', 'most directly expands the representable range for these activations')
q['12']['options'][3]['explanation']='Toward-zero rounding can avoid an infinity by returning a largest finite value, but it still cannot represent 70,000 faithfully. It does not solve the inadequate range.'
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n')
print('floating-point corrections applied')
