exec(open('/tmp/cs-study-audit-2026-10-04/fix-root.py').read().split("go=['https:")[0])
report=json.loads(Path('docs/audit-root.json').read_text());findings=report['findings']
p='content/software-engineering/04-git-cicd/git-cd-release.md'
sources=['https://martinfowler.com/bliki/ParallelChange.html','https://sre.google/workbook/canarying-releases/','https://dora.dev/guides/dora-metrics/']
patch(p,[
('That difference is detectable.', 'That is a possible signal, not a guaranteed detection: power depends on the baseline sample, traffic dependence and the chosen test.'),
('it cannot tell you anything about error rates.', 'it gives little power to detect a modest increase in a rare error rate, though it can reveal a severe regression.'),
('3. **Backfill**: copy `name` into `full_name` for existing rows, in batches.', '3. **Backfill**: after all old-only writers have been replaced, copy `name` into `full_name` in batches using concurrency-safe updates. Verify consistency before switching reads.'),
('6. **Contract**: once no deployed version uses `name`, drop it.', '6. **Contract**: after all readers and writers have migrated and the rollback window for old code has closed, drop `name`.'),
('Every step can be deployed and rolled back on its own.', 'Expansion can preserve rollback compatibility, but stopping old-column writes and dropping the column restrict which versions are safe to restore. Check that contract explicitly at each stage.'),
('Small batches are the common cause.', 'Small batches are one practice associated with good performance; these observations do not establish a single universal cause.')], 'Remove unsupported statistical certainty and unsafe migration/rollback assurances.',sources)
def release(q):
 q[5]['workedExample']='1. Add the nullable new column.\n2. Deploy dual writers that still read the old column, and wait until all old-only writers are gone.\n3. Backfill with concurrency-safe updates and verify consistency.\n4. Switch all readers while preserving dual writes during the rollback window.\n5. Stop old-column writes only when old readers cannot return.\n6. Drop the old column after all dependencies and the rollback window have gone.\n\nContracting the schema is not automatically reversible; define the oldest safe rollback version at each stage.'
 q[6]['workedExample']=q[6]['workedExample'].replace('A release that doubles errors to 12 is detectable, but a 20% increase (about 7) is not.', 'Neither 12 nor about 7 expected errors guarantees a decision: statistical power depends on baseline uncertainty, independence and the test threshold. Larger changes are easier to detect with the same sample.')
 q[7]['prompt']='You maintain a Python library at 2.6.0 whose declared public compatibility contract includes support for Python 3.9. Which changes require a MAJOR version bump under that contract? Select all that apply.'
 q[7]['options'][3]['explanation']='Under the stated contract, removing supported Python 3.9 compatibility breaks existing supported users. Runtime support policies must be specified; SemVer does not independently define them.'
 q[8]['prompt']=q[8]['prompt'].replace('A team uses blue-green deployment.', 'A team uses blue-green application deployment with a shared database.')
 q[10]['workedExample']=q[10]['workedExample'].split('\n\nReproduced in a scratch repo')[0]+'\n\nThe abbreviated commit hash depends on the actual repository; efb7ccd is illustrative, not a universal reproduced result.'
questions('content/software-engineering/04-git-cicd/git-cd-release.questions.json',release,'Align migration, canary and SemVer question assumptions; remove unsupported specific Git reproduction claim.',sources+['https://semver.org/','https://git-scm.com/docs/git-describe'])
p='content/theory/06-complexity/cplx-randomised-quantum.md'
sources=['https://www.scottaaronson.com/democritus/lec10.html','https://cs.uwaterloo.ca/~eblais/cs365/w25/P-and-BPP','https://arxiv.org/abs/2210.10173']
patch(p,[
('Miller–Rabin finds the primes inside every RSA key, randomised quicksort is the standard in-memory sort,', 'Miller–Rabin is widely used in probable-prime generation, randomised quicksort illustrates efficient expected-time sorting,'),
('**Monte Carlo**: fixed running time, small chance of a wrong answer.', '**Monte Carlo**: a bounded running-time guarantee, but some chance of a wrong answer. Actual running time can still vary.'),
('At that point, a hardware fault is likelier than an algorithmic error.', 'The mathematical error bound assumes independent random choices and correct execution; it is not a hardware-reliability estimate.'),
('Multiplying n × n matrices takes about O(n^2.37) at best (and O(n³) in practice).', 'The naive matrix product uses O(n³) arithmetic operations; subcubic algorithms also exist. The comparison below is with naive multiplication, not a claim about the current best exponent.'),
('so a trial catches it exactly when r[1] = 1; in 100,000 single trials I measured a detection rate of 0.499.', 'so a trial catches it exactly when r[1] = 1, with probability exactly 1/2.\n\n> [!note] Content gap: empirical measurement\n> The previous measured detection-rate claim has been omitted because no reproducible run record was available to verify it. The probability calculation above follows directly from the two equally likely values of r[1].'),
('for each input length there is one fixed "good" coin sequence that works for every input.', 'after amplifying error below 2^−n for inputs of length n, a union bound shows there exists one polynomial-length coin string that works for all inputs of that length. The string is non-uniform advice, not a known efficient way to find it.'),
('solvable by polynomial-size quantum circuits with error at most 1/3', 'solvable by a polynomial-time-uniform family of polynomial-size quantum circuits with error at most 1/3'),
('So **no unconditional quantum speed-up for a decision problem is proven**.', 'This rules out claiming a proven separation of BQP from BPP. It does not rule out proven query-complexity advantages or smaller speed-ups within polynomial time.'),
('so no quantum separation can be proven without proving P ≠ PSPACE.', 'separating BQP from BPP would imply P ≠ PSPACE. Query-model advantages such as Grover\'s do not require that class separation.')], 'Correct universal algorithm claims, distinguish uniform BQP and class separation from query speed-ups, and remove unverified empirical evidence.',sources)
def quantum(q):
 q[0]['options'][0]['explanation']='Monte Carlo algorithms have a running-time bound but may err; they need not take exactly the same time on every run.'
 q[2]['prompt']=q[2]['prompt'].replace('for two 1,000 × 1,000 matrices.', 'for two 1,000 × 1,000 integer matrices, using exact arithmetic.')
 q[8]['options'][1]['explanation']='Separating polynomial-time quantum decision computation from all polynomial-time classical randomised computation would separate P from PSPACE. This does not exclude query-model or within-polynomial speed-ups.'
 q[8]['workedExample']=q[8]['workedExample'].replace('So quantum supremacy for decision problems can only be supported by evidence:', 'So a BQP-versus-BPP separation remains unproved; relevant evidence includes')
questions('content/theory/06-complexity/cplx-randomised-quantum.questions.json',quantum,'Qualify exact arithmetic and avoid conflating all quantum advantage with BQP/BPP separation.',sources)
sources=['https://docs.rs/ropey/latest/ropey/struct.Rope.html','https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation']
patch('content/dsa/10-advanced/adv-sparse-tables.md',[
('Persistent structures keep every past version of themselves for about O(log n) extra memory per update.', 'Balanced persistent trees using path copying can retain each version with O(log n) extra nodes per point update; persistence alone does not guarantee that bound.'),
('a version never changes, so readers need no locks. Writers create a new version and publish its root atomically.', 'immutable, safely published nodes need no mutation locks for readers. Publishing roots and keeping nodes alive still require the language\'s synchronisation and memory-reclamation rules.'),
('| Insert / delete in middle | O(n) | O(log n) |','| Insert m new characters | O(n + m) | O(log n + m) |\n| Delete a range | O(n) | Implementation-dependent |'),
('Concatenation just creates a new root over two ropes, then rebalances.', 'These bounds assume balanced trees and bounded leaf sizes. Inserting new text must read/copy its m characters; deletion can also incur work to reclaim removed nodes. Concatenation creates a new root over two ropes, then rebalances.'),
('any update can invalidate O(n log n) entries.', 'a point update can affect O(n) blocks across all levels, because the number at level k is at most 2^k.'),
('giving O(log n) index, insert, delete and concatenation for very long text.', 'giving logarithmic tree navigation when balanced; insertion also costs O(m) for m new characters, and deletion costs depend on reclamation.')], 'State persistence synchronisation and rope complexity assumptions; correct point-update block count.',sources)
def sparse(q):
 q[3]['workedExample']=q[3]['workedExample'].replace('and f is associative and commutative enough that order does not matter.', 'and f is associative. Commutativity is not required: the two adjacent copies of the overlapping aggregate collapse by idempotence.')
 q[5]['options'][0]['explanation']='A point change can affect O(n) stored blocks across levels, whereas a segment tree updates O(log n) nodes.'
 q[5]['workedExample']='1. A sparse table point update may change O(n) entries, making frequent updates expensive at this scale.\n2. A segment tree supports both range minima and point updates in O(log n), with O(n) memory.\n3. log2(10^7) is about 23.3, which indicates tree height, not an exact query node count or measured throughput.\n4. Benchmark the actual implementation; asymptotic bounds do not establish that the workload is trivial.'
 q[9]['options'][0]['text']='Readers need no mutation locks for immutable nodes that are safely published and kept alive'
 q[9]['options'][0]['explanation']='Immutability removes concurrent mutations, but root publication and safe memory reclamation still require a correct synchronisation protocol.'
 q[9]['workedExample']=q[9]['workedExample'].replace('A root, once published, points to nodes that never change.', 'A safely published root points to immutable nodes whose lifetimes are protected. This does not eliminate publication or reclamation synchronisation.')
questions('content/dsa/10-advanced/adv-sparse-tables.questions.json',sparse,'Correct overlap algebra, persistent reader synchronisation, and unmeasured performance claims.',sources)
report['findings']=findings
for stem in ['content/software-engineering/04-git-cicd/git-cd-release','content/theory/06-complexity/cplx-randomised-quantum','content/dsa/10-advanced/adv-sparse-tables']:
 report['reviewed_files'] += [stem+'.md',stem+'.questions.json']
report['omissions']=[{'file':'content/theory/06-complexity/cplx-randomised-quantum.md','detail':'Unverifiable historical empirical detection-rate measurement replaced with explicit content-gap note and exact probability.'}]
Path('docs/audit-root.json').write_text(json.dumps(report,indent=2)+'\n')
