exec(open('/tmp/cs-study-audit-2026-10-04/fix-root.py').read().split("go=['https:")[0])
report=json.loads(Path('docs/audit-root.json').read_text());findings=report['findings']
src=['https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf','https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/listsort.txt','https://docs.rs/regex/latest/regex/','https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/']
p='content/dsa/01-complexity/cx-growth-rates'
patch(p+'.md',[
('To count as an algorithm, a procedure should be:', 'For this introductory discussion, a deterministic algorithm that correctly solves a total problem should be:'),
('a function call.', 'the overhead of a function call (its body must be counted separately). Arithmetic and comparisons are constant-cost only for bounded-size values in this model.'),
('(a reasonable ballpark for compiled code)', '(an illustrative assumed rate, not a general hardware benchmark)'),
('At n = 10^6, n log n takes a fraction of a second while n^2 takes hours.', 'At n = 10^6, the illustrative 10^8-operations/s model gives a fraction of a second for n log n and hours for n^2; actual timings require measurement.')], 'Scope correctness definition and unit-cost model; label hardware throughput as a hypothetical assumption.',src)
def fg(q):
 q[1]['prompt']='Which properties are required of a deterministic algorithm that correctly solves a total problem for every valid input? Select all that apply.'
 q[7]['prompt']=q[7]['prompt'].replace('What is the best description of its cost?', 'As the permitted bit width grows, what is the best description of its worst-case iteration count?')
 q[7]['options'][2]['explanation']='A literally fixed finite input domain admits a constant upper bound, but that hides the huge practical cost. The question asks how work grows when bit width varies.'
 q[7]['workedExample']=q[7]['workedExample'].replace('`b = log2 N`','`b = floor(log2 N) + 1`').replace('feasible in seconds to minutes, but still exponential in b.', 'about 30 seconds only under the hypothetical 10^8-divisions/s model; still exponential in b.')
 q[8]['prompt']+=' Assume integer n ≥ 2.'
 q[9]['workedExample']=q[9]['workedExample'].replace('would take under half a second; a hash set would be faster still.', 'would give under half a second only if its steps also sustain the assumed rate. A hash set reduces the expected operation count to O(n); benchmark actual costs.')
 q[10]['options'][0]['explanation']=q[10]['options'][0]['explanation'].replace('N = s^2.', 'N is proportional to s² at a fixed aspect ratio.')
questions(p+'.questions.json',fg,'Correct finite-domain asymptotic ambiguity, bit-length formula, and hypothetical timing scope.',src)
p='content/dsa/01-complexity/cx-space-complexity'
patch(p+'.md',[
('A neat fact: **space can never exceed time** (asymptotically). Writing to a memory cell costs at least one step, so an algorithm that runs in O(T) time cannot use more than O(T) space. The reverse doesn\'t hold: an O(1)-space algorithm can run for exponential time.', 'In a model that reads or writes only O(1) cells per step, an O(T)-time computation can touch only O(T) **auxiliary cells**. This excludes the pre-existing input and does not bound untouched virtual memory reserved by an allocator. Low space does not imply low time: an n-bit counter can enumerate 2ⁿ values while reusing O(n) bits.'),
('So `fact` uses Θ(n) auxiliary space. An iterative loop with a running product uses O(1).', 'Counting frames and treating arithmetic values as atomic, `fact` uses Θ(n) auxiliary space; an iterative version keeps a constant number of values. Actual Python integers are not fixed-size: n! alone needs Θ(n log n) bits.'),
('Python\'s built-in sort (Timsort) is not in place;', 'Python\'s `list.sort()` mutates its input, but is not in-place in the strict O(1)-auxiliary-space sense;'),
('Checking for duplicates with a set takes O(n) time', 'Checking for duplicates with a set takes expected O(n) time'),
('Hash set: O(n) time', 'Hash set: expected O(n) time'),
('In 64-bit CPython:', 'For a typical 64-bit CPython build (check `sys.getsizeof` on the actual build):'),
('10 million distinct integers costs roughly', '10 million distinct small integers costs roughly'),
('one fits in a 256 MB container and the other doesn\'t.', 'the packed data fits below a 256 MB budget, while the list does not. Runtime overhead and temporary conversion buffers still need headroom.')], 'Limit space≤time to touched auxiliary cells, distinguish integer bit complexity and mutation from strict in-place space, qualify process memory sizing.',src)
def fsp(q):
 for i in [0,1,2,3]: q[i]['prompt']+=' Use the lesson\'s simplified model counting arithmetic values as atomic; Python big-integer storage is a separate cost.'
 q[5]['prompt']=q[5]['prompt'].replace('Which representation fits?', 'Which representation has a data buffer below that limit? Allow additional headroom for runtime and construction overhead.')
 q[5]['options'][0]['explanation']=q[5]['options'][0]['explanation'].replace('about 28 bytes: roughly 360 MB', 'at least roughly 28 bytes in the assumed build: about 360 MB or more')
 q[9]['prompt']=q[9]['prompt'].replace('runs in Θ(n) time', 'performs Θ(n) additions (ignoring their growing bit cost)')
 q[9]['options'][0]['explanation']='The error is recursion depth. Reducing the cache size does not shorten the first recursive descent; a cache of 128 does not inherently cause drastic recomputation for this recurrence.'
 q[9]['options'][1]['explanation']=q[9]['options'][1]['explanation'].replace('uses O(1) space.', 'keeps two values, whose bit lengths grow as Θ(n).')
 q[9]['workedExample']=q[9]['workedExample'].replace('Θ(n) time, O(1) space, no recursion.', 'Θ(n) additions and a constant number of integer objects, with no recursion. The integers use Θ(n) bits; their arithmetic is not constant-time as n grows.')
 q[10]['options'][0]['text']='If each step touches O(1) memory cells, O(T(n)) time can touch at most O(T(n)) auxiliary cells, excluding input storage'
 q[10]['options'][0]['explanation']='True under the stated model. This does not bound untouched virtual address space reserved in bulk.'
 q[10]['options'][1]['text']='An algorithm using O(n) bits can still take exponential time'
 q[10]['options'][1]['explanation']='True. An n-bit counter enumerates 2ⁿ values while reusing the same n bits.'
 q[10]['workedExample']=q[10]['workedExample'].replace('1. **Space ≤ time.** You can\'t use a memory cell without spending a step on it. True.', '1. **Touched auxiliary cells ≤ steps.** This excludes existing input and untouched bulk reservations. True.').replace('2. **Small space, huge time.** A counter loop to 2^n is O(1) words (counting a counter as one word) and exponential time. True.', '2. **Small space, huge time.** An n-bit counter can enumerate 2ⁿ values using O(n) bits. True.')
questions(p+'.questions.json',fsp,'Correct cache-size distractor, big-integer model and false constant-space exponential counter example.',src)
p='content/dsa/01-complexity/cx-recurrences'
patch(p+'.md',[
('for some `k >= 0`, every level contributes about equally, and you pick up an extra log:', 'for some `k >= 0`, summing the level costs introduces one more log power (levels are equal only when k = 0):'),
('For merge sort, guess `T(n) <= c n log2 n`:', 'For merge sort, prove `T(n) <= c n log2 n` for powers of two n ≥ 2, choosing c large enough to cover T(2). Treat T(1) separately, since log2(1) = 0:'),
('The **Akra–Bazzi** method (1998) handles recurrences with several subproblems of different sizes:', 'The **Akra–Bazzi** method handles recurrences with several subproblem sizes under regularity assumptions: nonnegative g with suitable polynomial growth, bounded positive base cases, and sufficiently small perturbations of the subproblem sizes. The smooth polynomial/logarithmic examples here satisfy these conditions:'),
('`T(n) = Θ(n^1.585)`', '`T(n) = Θ(n^(log2 3))` (exponent approximately 1.585)')], 'State case-2 level-cost distinction, induction base case and regularity preconditions; avoid rounded exponents in exact Theta bounds.',src)
def fr(q):
 q[10]['workedExample']+='\n\nFor that final induction, start at n = 2 and choose c to cover T(2); T(1) is handled separately because log2(1) = 0.'
 q[8]['options'][3]['text']='Θ(n^(log3 5)), with exponent about 1.465'
 q[8]['workedExample']=q[8]['workedExample'].replace('`T(n) = Θ(n^1.465)`','`T(n) = Θ(n^(log3 5))`')
questions(p+'.questions.json',fr,'Close induction base-case gap and express Toom-3 exponent exactly.',src)
p='content/dsa/01-complexity/cx-in-practice'
s=Path(p+'.md').read_text(); start=s.index('The RAM model says'); end=s.index('So **access patterns**')
patch(p+'.md',[
('A common rule of thumb is that compiled code (C, C++, Rust, Java after warm-up) does somewhere around **10^8 simple operations per second** on one core. Treat it as an order of magnitude, not a specification.', 'For the arithmetic exercise below, **assume 10^8 counted operations per second** and unit leading constants. This is a hypothetical model, not measured throughput or a guarantee for any language.'),
('| any | O(log n), O(1) |', '| large n, subject to constants and storage | O(log n), O(1) |'),
('> [!warning] Python is slower\n> Pure Python loops run very roughly 10 to 100 times slower than compiled code, often a few times 10^7 simple operations per second at best. Divide the n limits accordingly, or move the inner loop into C: built-ins like `sum`, `sorted` and set operations, or vectorised NumPy, run at close to native speed.', '> [!note] Content gap: cross-language timings\n> A reproducible benchmark for the claimed universal Python-to-compiled speed ratio is absent, so that ratio is omitted. Interpreter version, operation type, data and hardware matter. Native built-ins or vectorisation can reduce interpreter overhead; measure the actual workload.'),
('**Timsort** (Python\'s `sorted`, Java\'s object sort) uses binary insertion sort to build sorted runs of a minimum length, chosen between 32 and 64, then merges them.', '**Timsort-style natural merge sorts** extend short runs with binary insertion sort, then merge them. Thresholds differ by implementation; modern CPython uses a Powersort merge policy, so a single threshold/policy should not be attributed to both Python and Java.'),
(s[start:end], 'The RAM model treats memory accesses uniformly, but real machines have caches, main memory and storage with different access costs.\n\n> [!note] Content gap: hardware latency measurements\n> The repository contains no reproducible measurement setup for the original latency table. Exact nanosecond and microsecond figures are omitted; consult the target hardware documentation and benchmark its access patterns. Cache-line size is hardware-specific (64 bytes is common on x86; ARM implementations vary).\n\n'),
('Engines like RE2 (and Rust\'s `regex`) guarantee linear time by not backtracking.', 'RE2 and Rust\'s `regex` provide bounded search complexity for supported patterns. Rust documents O(mn) for individual searches (pattern size m, haystack size n), while repeated-match iterators can reach O(mn²). A fixed-pattern single search is linear in n.'),
('A fixed pivot rule turns already-sorted (or attacker-chosen) data into Θ(n^2). Randomised pivots or introsort\'s heapsort fallback fix it.', 'A first- or last-element pivot can turn sorted distinct input into Θ(n²). Randomisation gives an expected bound; introsort\'s heapsort fallback provides the worst-case bound.'),
('Time it at n, 2n, 4n and look at the ratios:', 'Time it at n, 2n, 4n and look at the ratios. These numbers are illustrative, not recorded measurements:'),
('so it wins on every axis that matters here', 'making it a suitable starting point to benchmark'),
('Roughly 10^8 simple operations per second for compiled code: n of about 10^6 allows O(n log n), about 10^4 allows O(n^2), about 20 allows O(2^n). Python is 10 to 100 times slower in pure loops.', 'A hypothetical 10^8-operation budget illustrates growth-rate differences; real time budgets require workload-specific measurements.'),
('a cache miss to main memory costs around 100 ns.', 'cache misses and dependent loads can be expensive relative to sequential access.')], 'Remove unsupported portable speed/latency claims with explicit gaps; correct sort implementation and regex complexity scope.',src)
def fp(q):
 q[0]['prompt']='At n = 200,000, assume exactly 10^8 counted operations per second and unit leading constants. Which listed operation-count growth fits a one-second budget?'
 q[0]['workedExample']=q[0]['workedExample'].replace('Use the rule of thumb of about', 'Use the hypothetical assumption of')
 q[1]['prompt']+=' Assume each subset can be checked in at most 20 cheap operations.'
 q[1]['options'][2]['explanation']='Correct. There are 1,048,576 subsets, so the stated check costs at most about 21 million operations. Benchmark whether that fits the daily job budget.'
 q[1]['workedExample']=q[1]['workedExample'].replace('even in Python it\'s seconds, fine for a daily job.', 'actual runtime must be measured for the implementation.')
 q[4]['prompt']=q[4]['prompt'].replace('Which loop is faster, and why?', 'Assume 8-byte doubles, 64-byte cache lines, a matrix larger than cache, and no compiler loop interchange. Which loop has better sequential locality?')
 q[4]['options'][2]['text']='A walks sequentially; B advances by 80,000 bytes in its inner loop'
 q[4]['workedExample']=q[4]['workedExample'].replace('far bigger than any cache', 'larger than the cache by assumption').replace('Result: A is typically several times faster, sometimes by an order of magnitude.', 'Result: A has better spatial locality; measure the actual speed difference.')
 q[5]['prompt']='Consider a natural merge sort that uses binary insertion sort to extend short runs to a bounded target of at most 64 elements. Why can this quadratic subroutine fit an O(n log n) overall sort?'
 q[6]['prompt']='A loop performs 4 × 10^8 iterations. A representative benchmark on the target machine measured between 10^6 and 10^7 iterations per second. What runtime does that measured range predict?'
 q[6]['options'][1]['explanation']='Correct. Divide 4 × 10^8 by the stated rates: 40 to 400 seconds, or tens of seconds to several minutes.'
 q[6]['options'][2]['explanation']='Four seconds would require 10^8 iterations/s, above the stated measured range.'
 q[6]['options'][3]['explanation']='The stated range predicts 40–400 seconds, not hours.'
 q[6]['workedExample']='1. Fast end: 4 × 10^8 / 10^7 = 40 seconds.\n2. Slow end: 4 × 10^8 / 10^6 = 400 seconds.\n3. This estimate applies only if the benchmark remains representative at the larger input. The numbers are scenario assumptions, not a universal Python speed claim.'
 q[7]['options'][1]['explanation']='Yes. Backtracking can be superlinear or exponential depending on the pattern. Cloudflare\'s July 2019 incident involved a quadratic regex, not an exponential one.'
 q[8]['options'][0]['text']='Keep the existing baseline until representative benchmarks show that the proposed implementation is faster and meets memory and accuracy needs'
 q[8]['options'][0]['explanation']='Correct. A smaller asymptotic exponent alone does not establish performance at n = 10,000. Constants, implementation, memory and numerical behaviour matter.'
 q[8]['workedExample']='1. An exponent-only ratio ignores leading constants and lower-order work.\n2. Require a concrete implementation and benchmark representative shapes, sizes and numeric types.\n3. Check accuracy and peak memory as well as time.\n4. Keep the measured baseline until the alternative demonstrates an improvement.'
 q[11]['prompt']='Which factors can explain why a Θ(n²) algorithm beats a Θ(n log n) algorithm over a particular finite input range? Select all that apply.'
 q[11]['options'][3]['text']='Larger n alone guarantees that the quadratic algorithm wins'
 q[11]['options'][3]['explanation']='False. Growth favours n log n eventually, but no specific finite crossover follows without constants.'
 q[11]['workedExample']=q[11]['workedExample'].replace('around n = 6,300', 'around n = 6,310').replace('**Huge n:** the growth rate always wins eventually, so A wins.', '**Larger n alone:** does not favour B; eventual asymptotic superiority does not specify a finite crossover.')
questions(p+'.questions.json',fp,'Replace hardware guesses with explicit assumptions, correct Cloudflare quadratic incident and avoid benchmark-free algorithm recommendations.',src)
for stem in ['cx-growth-rates','cx-space-complexity','cx-recurrences','cx-in-practice']:
 for ext in ['.md','.questions.json']: report['reviewed_files'].append('content/dsa/01-complexity/'+stem+ext)
report['findings']=findings
Path('docs/audit-root.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
