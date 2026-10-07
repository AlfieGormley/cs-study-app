exec(open('docs/audit-checkpoint-2026-10-05/fix-root.py').read().split("go=['https:")[0])
b='content/theory/01-logic-proofs/';src=json.loads(Path('docs/audit-checkpoint-2026-10-05/root-logic-pending.json').read_text())['sources_fetched']
patch(b+'logp-propositional.md',[
('A **proposition** is a statement that is either true or false, never both.', 'In the classical two-valued logic used here, a proposition is a statement that is either true or false, never both.'),
('Their meaning is fixed by a **truth table**', 'The Python column assumes Boolean operands. Python and/or return operands and short-circuit; arbitrary objects can have custom truth tests and equality. The logical connectives have their meaning fixed by a **truth table**'),
('Every formula falls into one of three classes.', 'Tautology, contradiction and contingency form three disjoint classes. Satisfiability is a related property that overlaps them:'),
('- A formula is **satisfiable** if at least one row makes it true. Every tautology is satisfiable; a contradiction is not.', '- A contingent formula is true in some rows and false in others.\n- A formula is satisfiable if at least one row makes it true: both tautologies and contingent formulas qualify.'),
('The contrapositive ¬q → ¬p is equivalent to p → q; the converse and inverse are not.', 'The contrapositive ¬q → ¬p is always equivalent to p → q; converse and inverse are not equivalent to it in general.')], 'Clarify classical logic, Python semantics and overlapping satisfiability categories.',src)
def prop(q):
 q[10]['prompt']+=' Assume each non-None x has an ordinary integer size, with no side effects when reading it.'
questions(b+'logp-propositional.questions.json',prop,'Exclude NaN and effectful properties from ordered guard equivalence.',src)
patch(b+'logp-predicate.md',[
('The rule: **∀ goes with →, ∃ goes with ∧.**', 'For these restricted-domain translations, use implication under ∀ and conjunction under ∃. This is not a restriction on which connectives may appear in quantified formulas.'),
('That explains the empty-domain behaviour.', 'Standard first-order structures usually require a nonempty universe. Restricted quantification over an empty subset is still meaningful; the same conventions apply if empty universes are explicitly allowed. That explains the empty-set behaviour.'),
('On a finite domain {a, b, c},', 'The Python analogy assumes finite iterables, terminating predicates and no side effects. On a finite domain {a, b, c},'),
('"Not every test passed" means "some test failed".', '"Not every test passed" means "some test did not pass"; skipped or pending tests are not automatically failed tests.'),
('> SLO: "every request to /checkout completes within 300 ms".', '> Hypothetical universal requirement: "every completed request to /checkout takes at most 300 ms".'),
('> Its negation, which is what an alert should detect,', '> Its logical negation'),
('one slow checkout request is enough. Note that ≤ flips to >, not to <.', 'one slow completed request refutes this universal requirement. Real SLOs commonly allow an error budget; this is not a recommendation to page on every slow request. Note that ≤ flips to >, not to <.'),
('The definition of f(n) = O(g(n)) is:', 'For eventually nonnegative functions on natural-number inputs, the definition of f(n) = O(g(n)) is:'),
('Renaming it changes nothing:', 'Renaming it consistently to a fresh name, without capturing a free variable, changes nothing:'),
('SQL has ∃ built in as `EXISTS`. It has no `FOR ALL`,', 'SQL has existence tests through EXISTS and quantified comparisons through ALL. It has no standalone FOR ALL quantifier for arbitrary predicates,')], 'Clarify quantifier domains, computational analogies, SLO example, Big-O premises and SQL syntax.',src)
def predicate(q):
 q[0]['options'][2]['explanation']='This requires at least one verified admin. The universal rule requires every admin to be verified and is vacuously true if no admins exist; the two statements differ.'
 q[1]['prompt']+=' Assume all tests have completed and each result is pass or fail.'
 q[8]['prompt']+=' Assume eventually nonnegative functions on natural-number inputs.'
 q[8]['options'][0]['explanation']='This is a different statement, not the negation. For f(n)=g(n)=n, choosing c=1/2 and n₀=1 makes it true even though f is O(g).'
 q[9]['options'][2]['explanation']='Logically every customer qualifies regardless of orders. The database optimizer determines the physical execution plan; SQL semantics do not prescribe whether a table is scanned.'
questions(b+'logp-predicate.questions.json',predicate,'Fix existential/universal relationship, binary test premise and incorrect stronger-negation claim.',src)
patch(b+'logp-proof-techniques.md',[
('p > 1, only divisors 1 and p', 'integer p > 1, only positive divisors 1 and p'),
('as are most lower-bound arguments.', 'and contradiction is also useful in many lower-bound arguments.'),
('No amount of examples ever proves a ∀ claim; one example always disproves it.', 'Checking finitely many examples does not prove a universal claim over an infinite domain. Exhaustively checking every case in a known finite domain can prove it; a counterexample disproves either kind of universal claim.'),
('| Proof by example | Checks cases, proves nothing |', '| Incomplete proof by examples | Leaves unchecked cases unjustified |'),
('Let a = b.\na²', 'Let a = b = 1.\na²'),
('- A proof covers every case; examples only ever give evidence, while one counterexample disproves a ∀ claim.', '- A proof covers every case under its assumptions. Partial sampling gives evidence; exhaustive finite checking can prove a finite-domain claim. One counterexample refutes a universal claim.')], 'Correct finite exhaustive proof distinction and prime/division premises.',src)
def proofs(q):
 q[7]['prompt']=q[7]['prompt'].replace('Let a = b.', 'Let a = b = 1.')
 q[7]['options'][3]['explanation']='Here b=1, so division by b is permitted. The earlier cancellation of a−b=0 is the invalid step.'
 q[9]['workedExample']=q[9]['workedExample'].replace('Every x is rational or irrational', 'Every real x is rational or irrational')
questions(b+'logp-proof-techniques.questions.json',proofs,'Remove second possible division-by-zero error from single-answer proof question.',src)
patch(b+'logp-induction.md',[
('Claim: `total(xs)` returns the sum of `xs`, for every list. Induct on the length n.', 'In an ideal execution model, total(xs) returns the exact sum of any finite integer list. Induct on length n. Actual Python has a recursion limit and finite resources; this slicing implementation also copies Θ(n²) list elements overall. Floating-point addition does not obey all exact-arithmetic rearrangements.'),
('A tournament bracket with 64 teams has 63 matches;', 'A single-elimination tournament with 64 teams, one elimination per match and no extra placement or replay matches, has 63 matches;'),
('A correct recursive function is an induction proof in disguise: base case plus trust in the smaller call.', 'A recursive correctness proof uses base cases and correctness of smaller calls, with termination and implementation limits handled explicitly.')], 'Scope recursive correctness to its arithmetic/runtime model and tournament counting assumptions.',src)
def induction(q):
 q[0]['options'][2]['explanation']='Proving this stronger statement independently is sufficient for the step, but is not required. The inductive step may use P(n).'
 q[3]['options'][1]['text']='Odd n: half(1) calls half(−1), never reaches its base and eventually raises RecursionError in Python; n=1 needs a base case'
 q[5]['prompt']+=' Count only matches that eliminate one team; omit byes and additional placement games.'
 q[6]['options'][2]['explanation']='Correct for the stated recurrence proof: it uses both P(n) and P(n−1). Strong induction with two base cases is natural; ordinary induction on a strengthened pair of statements works too.'
questions(b+'logp-induction.questions.json',induction,'Distinguish sufficient versus required induction steps and real recursion behavior.',src)
patch(b+'logp-invariants.md',[
('Most real code, though, is loops that update variables.', 'Many algorithms use loops that update variables.'),
('A non-negative integer can\'t decrease forever, so the loop terminates.', 'A non-negative integer cannot decrease forever. Assuming each loop test and body execution finishes normally, this proves loop termination. More general well-founded orders can also supply ranking functions.'),
('## A first example\n', '## A first example\n\nAssume a finite list of integers that is not modified concurrently, exact arithmetic and normal execution without resource failures. Include 0 ≤ i ≤ len(a) in the invariant.\n'),
('This version returns the first index whose element is ≥ x (Python\'s `bisect_left`):', 'This version returns the first index whose element is ≥ x (the bisect_left insertion position), assuming a stable ascending list and a total order shared with x. NaNs and inconsistent custom comparisons are excluded. The invariant also includes 0 ≤ lo ≤ hi ≤ len(a):'),
("Python's integers don't overflow; in Java or C, write `low + (high - low) / 2`.", "Python integers have arbitrary precision, subject to memory limits. For nonnegative in-range indices low ≤ high in Java or C, use low + (high - low) / 2. C signed overflow is undefined behavior, whereas Java int arithmetic wraps."),
('Repeated squaring uses O(log n):', 'For integer n ≥ 0, repeated squaring uses O(log(n + 1)) multiplications. This is not a bit-operation bound: large-integer multiplication costs depend on operand size. The proof assumes exact arithmetic:'),
('def power(x, n):\n    result', 'def power(x, n):\n    if not isinstance(n, int) or n < 0:\n        raise ValueError("n must be >= 0")\n    result'),
('The same algorithm, with every multiplication done modulo m, is how RSA computes powers of 2048-bit numbers in milliseconds rather than never.', 'Modular variants of repeated squaring are used in modular exponentiation. Real cryptographic implementations also need side-channel protections; this branching teaching code is not a production RSA implementation.\n\n> [!note] Evidence gap\n> A previous fixed RSA runtime claim is omitted because no reproducible implementation, exponent, hardware or benchmark was supplied.'),
('At outer exit i = len(a), so the whole array is sorted.', 'After the last iteration, the processed prefix has length len(a), so the whole array is sorted. Python’s for-loop variable does not advance to len(a); it remains at its last assigned value, or is never assigned if there are no iterations.'),
('**Database constraints**: `CHECK`, `UNIQUE` and foreign keys are invariants that the database enforces on every transaction.', '**Database constraints** enforce their defined conditions at specified checking points. Deferrable constraints may be checked at commit; PostgreSQL CHECK accepts TRUE or NULL, and default UNIQUE handling permits multiple NULLs. Add NOT NULL when required.'),
('When the assertion fails, it fails at the iteration where the bug happened, not three functions later.', 'An assertion detects a violation when execution reaches that check; the underlying bug may have occurred earlier. Python can disable assert statements under optimization, so do not use them as mandatory input validation.')], 'Add proof preconditions, correct Python loop semantics and arithmetic costs; omit unsupported RSA timing; qualify constraints/assertions.',src)
def invariants(q):
 q[1]['prompt']+=' Assume an unchanged finite list of totally ordered integers and include 1 ≤ i ≤ len(a) in the invariant.'
 q[5]['workedExample']=q[5]['workedExample'].replace('Four iterations, about log₂ 10, instead of ten multiplications.', 'Four iterations perform four squarings and two result multiplications. Iteration count and multiplication count are different quantities.')
 q[8]['workedExample']=q[8]['workedExample'].replace('Total correctness needs a variant: a non-negative integer that strictly decreases every iteration.', 'A decreasing nonnegative integer ranking is one way to prove total correctness, assuming each body execution terminates normally.')
 q[10]['options'][2]['text']='{B} while B: body {I ∧ ¬B}'
 q[10]['options'][2]['explanation']='B alone does not establish I initially. For example, I may be false everywhere and body immediately set B false; the preservation premise holds vacuously but this proposed postcondition fails.'
 q[11]['options'][4]['explanation']='Global sortedness is the desired final property, not an invariant guaranteed at every outer-loop entry.'
 q[11]['workedExample']=q[11]['workedExample'].replace('At exit i = len(a):', 'After the last iteration, the processed prefix has length len(a) (the Python variable i remains at its last assigned value):')
questions(b+'logp-invariants.questions.json',invariants,'Fix valid distractor in single-answer Hoare question, Python for-loop exit and proof premises.',src)
Path('docs/audit-theory-logic.json').write_text(json.dumps({'status':'Full reading of6lessons73questions complete; first5pairs corrected, SAT correction/execution/independent review pending.','date':'2026-10-05','reviewed_files':[str(p) for p in Path(b).iterdir() if p.suffix=='.md' or p.name.endswith('.questions.json')],'findings':findings,'omissions':[{'lesson':'logp-invariants','claim':'Fixed RSA milliseconds runtime','reason':'No reproducible benchmark configuration supplied; explicit gap note added.'}],'limitations':['Execution pending; independent verification pending.']},ensure_ascii=False,indent=2)+'\n')
