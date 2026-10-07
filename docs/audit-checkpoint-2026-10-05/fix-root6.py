exec(open('/tmp/cs-study-audit-2026-10-04/fix-root.py').read().split("go=['https:")[0])
report=json.loads(Path('docs/audit-root.json').read_text());findings=report['findings']
src=['https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf','https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/listobject.c','https://doc.rust-lang.org/std/vec/struct.Vec.html']
p='content/dsa/01-complexity/cx-amortised-analysis'
patch(p+'.md',[
('That is badly wrong in practice.', 'O(n²) is a valid but unnecessarily loose upper bound; the tight bound for appends from an empty list is Θ(n).'),
('With growth factor g, total copying is roughly `n / (g - 1)`: about n for g = 2, 2n for g = 1.5.', 'Ignoring integer rounding, if C is the final capacity and the initial capacity is 1, total copying is `(C - 1) / (g - 1)`. Since n ≤ C < gn, a bound in terms of arbitrary n needs the extra factor g. The smaller estimate `n / (g - 1)` applies near a full final capacity.'),
('| Rust `Vec` | 2x |', '| Rust `Vec` | amortised O(1) push; no particular growth factor guaranteed |'),
('For throughput this is irrelevant.', 'Amortisation bounds aggregate work, but allocation and copying still affect measured throughput.'),
('a Python list', 'a Python list')], 'Correct loose-bound terminology and growth-series coefficient; distinguish Rust API guarantees from implementation policy.',src)
def fa(q):
 q[0]['prompt']+=' Assume the array starts empty.'
 q[0]['workedExample']=q[0]['workedExample'].replace('**any** n appends','**any** n appends from empty in the doubling model')
 q[2]['workedExample']=q[2]['workedExample'].replace('The total is about `n / (g - 1)`.', 'Ignoring rounding, the total is `(C - 1)/(g - 1)` for final capacity C; C may be almost gn.')
 q[7]['options'][1]['explanation']='Correct. A fixed factor above 1 keeps total copies O(n); with 1.5x growth an arbitrary stopping point can approach 3n copies, ignoring rounding.'
 q[7]['options'][3]['explanation']='Correct. A fixed factor above 1 plus a constant still gives O(n) total copying; the exact coefficient depends on where the sequence stops.'
 q[7]['workedExample']=q[7]['workedExample'].replace('| x2 | 2 | ~n |','| x2 | 2 | <2n |').replace('| x1.5 | 1.5 | ~2n |','| x1.5 | 1.5 | O(n) |').replace('| x1.125 + c | 1.125 | ~8n |','| x1.125 + c | 1.125 | O(n) |')
 q[9]['options'][3]['explanation']='A larger factor reduces resize frequency but retains occasional full relocation and increases spare capacity. It does not guarantee a latency bound.'
 q[9]['workedExample']=q[9]['workedExample'].replace('a bigger factor makes the largest copies bigger.', 'a bigger factor still permits large copies.')
questions(p+'.questions.json',fa,'Correct arbitrary-prefix copy bounds and initial-state assumptions in amortised analysis questions.',src)
p='content/dsa/01-complexity/cx-asymptotic-notation'
patch(p+'.md',[
('The pattern for disproofs is always the same: show that the ratio `f(n) / g(n)` grows without limit, so no fixed c can contain it.', 'For eventually positive g, showing `f(n) / g(n)` tends to infinity disproves O(g), but is not necessary: the ratio may oscillate. The general requirement is that for every c and n0, some n ≥ n0 has f(n) > c g(n).'),
('but there is no simple g with `f = Θ(g)`, because the ratio to any candidate keeps jumping. This is rare for whole algorithms, but it is a reminder that O and Ω are separate statements and Θ only exists when they meet.', 'but it is neither Θ(n) nor Θ(1). A tight bound still exists: trivially f = Θ(f), or use the same piecewise expression as g. It simply does not match one of the usual monotone growth classes.'),
('To disprove, show f/g grows without limit.', 'To disprove, show that no eventual constant upper bound contains f/g (a limit of infinity is sufficient).')], 'Fix false claim that every disproof needs an infinite ratio limit or an oscillating function has no Theta class.',src)
def fs(q):
 q[0]['prompt']=q[0]['prompt'].replace('tightest simple description', 'fully simplified description with constants and dominated terms removed')
 q[6]['options'][0]['explanation']='Being in the same rough range does not imply Θ. The ratio must eventually stay between two positive constants; it need not converge. Here it tends to zero.'
 q[9]['workedExample']=q[9]['workedExample'].replace('The O and Ω bounds never meet, so no simple Θ exists. Big-O and Big-Omega are independent statements; Θ only exists when they agree.', 'Neither Θ(n) nor Θ(1) describes f. However, f = Θ(f) always holds: a piecewise bound captures the oscillation exactly.')
questions(p+'.questions.json',fs,'A positive finite ratio limit is sufficient, not necessary, for Theta; remove ambiguous tightness question.',src)
p='content/dsa/01-complexity/cx-analysing-code'
patch(p+'.md',[
('1. **Simple statements** (assignment, arithmetic, comparison, indexing a list) are O(1).', '1. **Cost model.** Treat fixed-size arithmetic, comparison and indexing as O(1). Python arbitrary-precision integers, long strings, user-defined comparisons and output can cost more; the counts below abstract those costs unless stated otherwise.'),
('n calls, O(1) each: Θ(n).', 'Θ(n) calls and multiplications in the unit-cost model. Actual Python integer multiplications become more expensive as n! grows.'),
('Plain quicksort with a fixed pivot choice is average Θ(n log n) over random inputs but Θ(n^2) on sorted input', 'For distinct keys, quicksort with a first- or last-element pivot is average Θ(n log n) over uniformly random permutations but Θ(n²) on sorted input'),
('`return` inside a loop improves the best case, not the worst. When analysing, ask "what input makes the early exit never fire?"', 'An early return can improve best or average time. Whether it changes the worst case depends on whether any inputs still force the original expensive path. Ask which inputs attain the maximum after adding the check.')], 'State arithmetic and data assumptions; early exits do not have a universal no-worst-case-improvement rule.',src)
def fc(q):
 q[1]['prompt']+=' Count each print call as one operation, ignoring formatting and I/O cost.'
 q[4]['options'][1]['explanation']='Correct. The exact count is the sum of ceil(n/i), which lies between nH(n) and nH(n)+n. Both give Θ(n log n).'
 q[4]['workedExample']=q[4]['workedExample'].replace('about 1,000 x 7.5 = 7,500 calls', '8,053 calls (sum of ceil(1000/i)); nH(n) alone is about 7,485')
 q[5]['prompt']+=' Assume hashable records with constant-cost hashing and equality.'
 q[5]['workedExample']=q[5]['workedExample'].replace('In CPython, at very roughly 10^7 to 10^8 simple operations per second, that is minutes.', 'The elapsed time depends on the machine and equality operation.').replace('so the total is Θ(n): well under a second.', 'so the expected total is Θ(n); measure elapsed time for the actual records.')
 q[7]['options'][1]['explanation']='Removing the last element needs no shifting and is amortised O(1); an occasional shrinking reallocation can cost O(n).'
 q[7]['workedExample']=q[7]['workedExample'].replace('| `lst.pop()` | last slot | O(1) |','| `lst.pop()` | last slot, occasional resize | amortised O(1) |')
 q[10]['prompt']+=' Assume distinct keys and ordinary two-way quicksort partitioning for the quicksort claims.'
 q[10]['options'][2]['text']='Adding an early return always improves worst-case asymptotic complexity'
 q[10]['options'][2]['explanation']='False. Some inputs may still take the old expensive path. Whether worst-case complexity improves depends on the algorithm and condition.'
 q[10]['workedExample']=q[10]['workedExample'].replace('Worst case = the input that avoids the exit. Unchanged. False.', 'An input may still avoid the exit; improvement is not guaranteed. False.')
questions(p+'.questions.json',fc,'Fix harmonic-loop exact count, unmeasured timing promises, occasional pop resize, and early-exit/duplicate assumptions.',src)
for stem in ['cx-amortised-analysis','cx-asymptotic-notation','cx-analysing-code']:
 for ext in ['.md','.questions.json']: report['reviewed_files'].append('content/dsa/01-complexity/'+stem+ext)
report['findings']=findings
Path('docs/audit-root.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
