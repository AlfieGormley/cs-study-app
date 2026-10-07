exec(open('/tmp/cs-study-audit-2026-10-04/fix-root.py').read().split("go=['https:")[0])
report=json.loads(Path('docs/audit-root.json').read_text());findings=report['findings']
b='content/software-engineering/03-testing/'
src=['https://abseil.io/resources/swe-book/html/ch11.html','https://docs.pytest.org/en/stable/explanation/goodpractices.html','https://martinfowler.com/articles/practical-test-pyramid.html']
patch(b+'test-why-pyramid.md',[
('Once written, it runs in milliseconds, forever, for free.', 'Small tests can run quickly and repeatedly, but execution resources, upkeep and diagnosis all have costs.'),
('A bug that is fixed and covered by a test stays fixed.', 'A regression test can catch the same failure again, provided it still exercises the relevant path and runs with useful assertions.'),
('unlike a wiki page it cannot silently go out of date: if it is wrong, it fails.', 'it can expose a mismatch between the tested expectation and implementation. A stale or incorrect expectation can still pass if the code agrees with it.'),
('pytest finds files named `test_*.py`, runs every function whose name starts with `test`,', 'By default, pytest collects `test_*.py` and `*_test.py` files and eligible test-prefixed functions and methods; configuration can change discovery. It runs the collected tests'),
('Running `pytest -q` prints:', 'For these three tests, illustrative `pytest -q` output is (elapsed time varies):'),
('Most bugs live at boundaries:', 'Boundary cases are valuable targets:'),
('Each step up buys realism and costs speed, reliability and precision.', 'Broader tests often exercise more real components and can cost more time and effort to diagnose. These are tendencies, not guaranteed timings or failure rates. The table is illustrative:'),
('Small tests run in a single process (often a single thread) with no sleeping or I/O.', "Under the Google scheme described here, small tests use one thread in one process, without sleeping or external I/O; hermetic in-memory filesystem access is an exception."),
('You now know the fix works, and the bug cannot quietly return.', 'You have evidence for the exercised case and a check that can detect that regression if it recurs on the covered path.')], 'Remove absolute testing guarantees, correct pytest discovery and qualify illustrative timings and test-size definitions.',src)
def pyramid(q):
 q[2]['options'][3]['explanation']='Correct. It exercises the components along the selected journey through the configured system boundary; it does not necessarily visit every service or every path.'
 q[2]['workedExample']=q[2]['workedExample'].replace('exercises everything together', 'exercises the selected journey together')
 q[7]['options'][2]['explanation']='Large tests may span machines, but a test confined to one host can also be classified large because of other resource limits. The smallest permitted class for the stated scenario is medium.'
 q[7]['prompt']=q[7]['prompt'].replace('What size is it?', 'What is the smallest permitted size, assuming it meets that class\'s other limits?')
 q[9]['workedExample']=q[9]['workedExample'].replace('a network call breaks the single-process constraint', 'a network call breaks the small-test network-access constraint')
 q[10]['options'][3]['explanation']='Correct. Confirming the expected failure shows that this test reproduces the reported case; its later pass is evidence for that case, not proof of all correctness.'
questions(b+'test-why-pyramid.questions.json',pyramid,'Clarify E2E scope, size constraints and evidential limits of regression tests.',src)
src=['https://docs.pytest.org/en/stable/how-to/fixtures.html','https://docs.pytest.org/en/stable/how-to/assert.html','https://docs.pytest.org/en/stable/reference/reference.html']
patch(b+'test-unit-testing.md',[
('The test passes only if the block raises `ValueError`', 'The test passes only if the block raises `ValueError` or a subclass'),
('Code after a `yield` runs as teardown, even if the test fails:', 'Once a fixture reaches `yield`, its teardown normally runs even if the test fails. Setup failure before the yield and abrupt process termination need separate handling:'),
('A good rule: if a pure refactor (no behaviour change) breaks a test, the test was coupled to implementation.', 'A test broken by a behaviour-preserving refactor is a prompt to inspect implementation coupling, including dependencies that the test patches.'),
('The first test breaks if someone renames `_cache`,', 'The second example checks repeated output equality; it does not prove that caching occurs. If avoiding repeat source calls is part of the contract, inject a recording source and verify that requirement. The first test breaks if someone renames `_cache`,')], 'Clarify fixture cleanup and exception matching; repeated equal outputs do not establish caching.',src)
def unit(q):
 q[5]['prompt']=q[5]['prompt'].replace('just after `test_c`, before the module finishes', 'at the end of test_c\'s body, before pytest starts its teardown phase')
 q[7]['prompt']=q[7]['prompt'].replace('make a unit test **non-repeatable**', 'introduce a risk of **non-repeatable outcomes**, depending on its assertions')
 q[7]['options'][0]['explanation']='The assertion can depend on wall-clock time; merely reading time does not guarantee that pass/fail changes.'
 q[7]['options'][1]['explanation']='Uncontrolled random inputs can expose different paths. They do not necessarily change pass/fail if the asserted property always holds.'
 q[7]['options'][4]['explanation']='A fresh directory isolates this source of state. It does not guarantee repeatability of all filesystem operations or make a disk-using test small under Google\'s classification.'
 q[10]['prompt']=q[10]['prompt'].replace('a test file.', 'a file of small, focused unit tests.')
questions(b+'test-unit-testing.questions.json',unit,'Specify fixture inspection phase and distinguish nondeterministic inputs from guaranteed flaky outcomes.',src)
src=['https://docs.python.org/3/library/unittest.mock.html','https://docs.stripe.com/api/idempotent_requests']
patch(b+'test-doubles.md',[
('A `Mock` accepts any attribute access and any call,', 'An unrestricted `Mock` accepts most ordinary attribute access and arbitrary call arguments (some special and misspelled assertion names are rejected),'),
('A bare `Mock` accepts anything,', 'A bare `Mock` accepts most ordinary method names and arbitrary call arguments,'),
('`Mock(spec=Mailer)` only allows attributes that exist on `Mailer`, so typos raise `AttributeError`.', '`Mock(spec=Mailer)` restricts attribute lookup to names on the spec, so unknown method lookups raise `AttributeError`. Use `spec_set` to restrict setting unknown attributes too.'),
('"the card was charged once and only once".', '"the payment adapter was invoked once in this scenario". A call-count assertion does not prove that a remote payment occurred exactly once; provider idempotency and failure-path integration tests address that separate concern.')], 'Correct mock/spec restrictions and distinguish local invocation counts from real payment effects.',src)
def doubles(q):
 q[3]['prompt']=q[3]['prompt'].replace('What happens when this test runs?', 'Assume checkout was imported before the patch. What happens when this test runs?')
 q[9]['prompt']=q[9]['prompt'].replace('a bug that makes the real tax calculator charge 0% VAT on books', 'a bug that makes the real calculator return 0% instead of this scenario\'s required 20% tax')
 q[11]['options'][0]['explanation']='Correct for the local adapter-invocation requirement. It does not prove successful delivery of an email by a remote provider.'
 q[11]['options'][1]['text']='Checking that this checkout code invokes its payment adapter once when handling the same logical request twice'
 q[11]['options'][1]['explanation']='Correct for the local call-count requirement. Exactly-once remote payment effects need additional idempotency and failure-path checks.'
 q[11]['workedExample']=q[11]['workedExample'].replace('the number of charges is the point', 'the number of local adapter calls is the asserted contract, not proof of remote payment effects')
questions(b+'test-doubles.questions.json',doubles,'Specify patch timing, avoid an unstated real-world tax rule and correct exactly-once implications.',src)
src=['https://docs.python.org/3/library/sqlite3.html','https://docs.pact.io/getting_started/how_pact_works','https://playwright.dev/python/docs/test-assertions','https://www.sqlite.org/datatype3.html']
patch(b+'test-integration-e2e.md',[
('For code that calls another service over HTTP, the narrow integration test runs your real client against a **stub server**: a local HTTP server (WireMock, or Python libraries such as `responses` and `respx` that intercept requests) that returns canned responses.', 'A narrow integration test can run the real client against a local **stub server**, such as WireMock. Python libraries `responses` and `respx` instead intercept client-library calls in-process; they are not local HTTP servers and exercise a different boundary.'),
('This checks things unit tests with a mocked client cannot:', 'Keeping the client code real can check'),
('What it cannot check is whether the canned responses match', 'An in-process interceptor does not exercise real sockets, TLS or actual network timeouts; injected exceptions only check handling. Neither approach alone establishes whether canned responses match'),
('E2E tests are the only tests that prove the real thing works for a user, wiring and configuration included.', 'E2E tests provide evidence that selected journeys work through the tested wiring and configuration; they do not prove correctness for all users, inputs or environments.'),
('**Pact** is the best-known tool for this.', '**Pact** is one tool for this.'),
('providers verify against all of them in CI.', 'providers verify the relevant consumer contracts selected by version and environment in CI.'),
('The provider is free to change anything else.', 'Changes outside the recorded contract can still break consumers if their real dependencies were omitted; contracts need adequate consumer tests.'),
('so fakes cannot drift.', 'to detect drift in the behaviours that suite covers.'),
('The same idea keeps your own fakes honest. Write the behavioural tests once and run them against every implementation:', 'The same idea checks your own fakes. This sketch assumes adapters exposing the same add(email) method and ValueError contract; these are not the earlier raw UserRepo or two-argument InMemoryUsers. Write behavioural tests once and run them against each adapter:')], 'Distinguish HTTP interception from real servers, bound contract guarantees and identify adapter placeholders.',src)
def integration(q):
 q[0]['options'][3]['text']='Clicking through sign-up in a browser against the full running application'
 q[1]['workedExample']=q[1]['workedExample'].replace('and deterministic as long as the timeout is generous', 'and less timing-sensitive, but can still fail if the condition never becomes true before timeout')
 q[4]['prompt']=q[4]['prompt'].replace("the app writes `'GBPX'`", "the app performs an ordinary parameterised INSERT of `'GBPX'`, with no explicit cast or truncation")
 q[8]['options'][2]['explanation']='Correct. A plain rollback or savepoint cannot undo a real outer COMMIT. Use explicit cleanup, an isolated database, or a framework-supported test transaction that intercepts application commits before they reach the outer transaction.'
 q[8]['workedExample']=q[8]['workedExample'].replace('run the code against a nested transaction (savepoint) if your framework supports it', 'use a framework test transaction that confines application commits to managed savepoints (a bare savepoint alone does not survive an outer COMMIT)')
questions(b+'test-integration-e2e.questions.json',integration,'Clarify E2E scope, timeout limits, PostgreSQL cast assumptions and savepoint isolation.',src)
src=['https://hypothesis.readthedocs.io/en/latest/reference/api.html','https://hypothesis.readthedocs.io/en/latest/tutorial/adapting-strategies.html','https://docs.python.org/3/library/json.html','https://martinfowler.com/bliki/TestDrivenDevelopment.html']
patch(b+'test-tdd-property.md',[
('The tests tell you nothing broke.', 'The tests provide feedback about the behaviours they actually check.'),
('It proves the test can fail: that it runs, checks something, and checks the right thing.', 'It shows that the test can fail. Inspect the failure reason to confirm it concerns the intended missing behaviour, rather than an unrelated setup or import error.'),
('**Every line is covered by a test that was seen to fail**, so the suite is trustworthy.', '**Test-first feedback** connects new behaviour to a failing example; it does not guarantee every line or branch is covered or every assertion is adequate.'),
('**Regression tests for free.**', '**Regression checks develop alongside implementation**, with writing and maintenance costs.'),
('In Python the standard library is **Hypothesis**.', 'In Python, **Hypothesis** is a third-party library; install it separately.'),
('Hypothesis fails it at once and reports the smallest failing input it can find:', 'A Hypothesis run can expose the error and shrink it to a simple counterexample such as the following; discovery time and the exact report are not guaranteed:'),
('Hypothesis also saves failing examples in a local database (`.hypothesis/`) and replays them first on the next run, so a failure doesn\'t vanish when you re-run.', 'With an example database enabled, Hypothesis saves useful failing inputs and reuses them on later runs. The default local profile uses a `.hypothesis/` database; current CI-profile settings can disable the database and use deterministic generation. Explicit `@example` cases are more durable regression checks.'),
('Generation is random, and default runs are short: Hypothesis tries 100 examples per test unless you change `max_examples`.', 'Generation is strategy-guided, not uniform random sampling, and can be deterministic under the CI profile or explicit settings. The default `max_examples=100` limits satisfying generated cases in a successful search, not necessarily all calls including rejected inputs and shrinking.'),
('The round-trip property is right, but with `st.text()` and default settings Hypothesis usually misses it, because random text rarely contains ten identical characters in a row. Restricting the alphabet to `"ab"` makes long runs more likely, and it then finds the bug in some runs but not all.', 'The round-trip property is useful, but a generic text strategy is not a guarantee of reaching long repeated runs. Generate such runs deliberately and pin the known counterexample. No measured discovery rate is asserted here.'),
('shrinks failures to minimal examples.', 'shrinks failures towards simpler examples, without guaranteeing a globally minimal counterexample.')], 'Correct Hypothesis installation, generation/database/default semantics and limits of TDD evidence.',src)
def tdd(q):
 q[1]['options'][3]['text']='To confirm that the test runs and fails for the intended missing behaviour, after inspecting the failure reason'
 q[1]['options'][3]['explanation']='A failing test can still fail for an irrelevant setup problem. A test passing immediately may exercise existing valid behaviour rather than be useless; investigate before adding code.'
 q[1]['workedExample']+='\n\nSeeing any red result is insufficient: verify the expected failure reason.'
 q[2]['workedExample']=q[2]['workedExample'].replace('When nothing simpler fails, it reports that input.', 'It reports the simplified counterexample reached by its search.').replace('The result is the minimal case', 'The result is a simpler case')
 q[3]['options'][2]['explanation']='Correct. It rules out the constant implementation. Two cases do not mathematically force general parsing; a lookup table could pass both, but the examples motivate generalisation.'
 q[3]['workedExample']=q[3]['workedExample'].replace('The simplest code satisfying *both* must read the number and the unit.', 'Reading the number and unit is one small general implementation satisfying both; the tests alone do not uniquely determine it.')
 q[5]['prompt']=q[5]['prompt'].replace('What does Hypothesis report', 'Which is a simple failing counterexample Hypothesis can find')
 q[5]['options'][3]['text']='a=[0], b=[0], where merge returns [0] instead of [0, 0]'
 q[5]['options'][3]['explanation']='Correct. This is a valid minimal-length counterexample. A particular run is not guaranteed to discover it or report exactly these values.'
 q[6]['prompt']=q[6]['prompt'].replace('a JSON serialiser with `dumps` and `loads`', 'Python\'s standard json.dumps/json.loads with unchanged default formatting and generated JSON-native values: string-keyed dictionaries, lists, strings, booleans, None, integers and finite floats (no tuples, non-string keys or non-finite numbers)')
 q[8]['prompt']=q[8]['prompt'].replace('`top_k(items, k)` using a heap', '`top_k(items, k)` using a heap, whose contract returns the largest min(k, len(items)) integer values in descending order for integer k >= 0')
 q[7]['workedExample']='A generic strategy does not guarantee reaching the particular long-run case. Generate repeated runs explicitly, and add @example("a" * 10). The discovery rate of st.text depends on Hypothesis version, settings and generator behaviour; no measured probability is assumed.'
 q[10]['prompt']=q[10]['prompt'].replace('You re-run it', 'With the example database enabled and default local reuse phase, you re-run it')
 q[10]['workedExample']+='\n\nCurrent CI-profile defaults can disable this database and use deterministic generation instead. Check active settings; persist important failures as explicit examples.'
questions(b+'test-tdd-property.questions.json',tdd,'Correct red-test proof, triangulation, shrinking, JSON domain, top-k contract and Hypothesis reproducibility assumptions.',src)
src=['https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html','https://coverage.readthedocs.io/en/latest/branch.html','https://research.google/pubs/state-of-mutation-testing-at-google/','https://docs.python.org/3/reference/expressions.html#is-not']
patch(b+'test-flaky-coverage-mutation.md',[
('**Flaky tests** fail when nothing is wrong, so people learn to ignore red.', '**Flaky tests** have inconsistent outcomes on unchanged code; they may reveal real intermittent defects as well as test or environment problems.'),
('Most "new failures" were not new bugs at all.', 'Those figures describe that 2016 Google dataset. A transition involving a flaky test does not itself establish that no new product bug exists.'),
('Running `coverage run --branch` gives:', 'If only the seven-statement function is in shipping.py and a separately measured driver invokes it, coverage.py can report the following. Including the test function or driver in the measured file changes the statement total:'),
('**Branch coverage** also checks that each decision went both ways.', '**Branch coverage** tracks alternatives between measured source lines; for these two if statements, each has a true and false outcome. It does not necessarily distinguish every short-circuited boolean subexpression.'),
('Path counts grow exponentially with the number of decisions, which is why nobody targets full path coverage.', 'Independent decisions can produce exponentially many paths, and loops can produce unbounded paths. Full path coverage is often infeasible, though finite small regions can be exhaustively exercised.'),
('you could have shipped that bug.', 'the suite did not detect that change; it may be a meaningful missed fault, an equivalent change or outside the required behaviour.'),
('When `a == b`, both versions return a value equal to `a` and `b`, so the mutant is indistinguishable.', 'For ordinary integer inputs under a value-only maximum contract, equal inputs give equal output values. The mutant is equivalent under that contract, but not universally in Python: callers can observe object identity, and equal-valued floats such as -0.0 and 0.0 have distinguishable signs.'),
('surviving mutants point straight at missing tests, often at boundaries.', 'surviving mutants need triage: they may expose missing boundary tests, equivalent changes or behaviour outside the contract.')], 'Correct flaky-test interpretation, coverage scope and equivalent-mutant assumptions.',src)
def flaky(q):
 q[1]['workedExample']=q[1]['workedExample'].replace('only 82% branch coverage', 'only 50% branch-outcome coverage (82% combined statement-and-branch coverage in the scoped seven-statement report)')
 q[2]['options'][3]['text']='All tests still passed with the code changed, so the suite did not distinguish that mutation'
 q[2]['options'][3]['explanation']='Correct. Inspect whether it is a meaningful missed fault, an equivalent mutation or outside the required contract before calling it a missing test.'
 q[2]['options'][2]['explanation']='Some survivors are equivalent, but survival alone does not establish equivalence. Inspect the contract and changed behaviour.'
 q[9]['prompt']=q[9]['prompt'].replace('What should you do?', 'For ordinary integer inputs and a contract observing only the maximum numeric value (not object identity), what should you do?')
 q[9]['workedExample']+='\n\nThis equivalence relies on the stated contract. Python object identity or signed-zero float observations can distinguish the original and mutant outside it.'
 q[11]['options'][1]['explanation']='Correct. The test is flaky by its varying outcomes, and the root cause is a real intermittent product bug. Retrying does not repair that bug.'
 q[11]['workedExample']=q[11]['workedExample'].replace('the race happens constantly', 'the race may recur and cause user-visible failures; frequency depends on the production workload')
questions(b+'test-flaky-coverage-mutation.questions.json',flaky,'Separate combined from pure branch coverage, qualify equivalent mutants and recognise product races as a cause of flaky outcomes.',src)
for name in ['test-why-pyramid','test-unit-testing','test-doubles','test-integration-e2e','test-tdd-property','test-flaky-coverage-mutation']:
 for ext in ['.md','.questions.json']:report['reviewed_files'].append(b+name+ext)
report['findings']=findings
report.setdefault('execution_checks',[]).append({'scope':'Selected testing lesson blocks','result':'13 pytest examples passed: 3 pricing, 3 SQLite integration, 7 duration-parser cases; separately reproduced branch-coverage arithmetic and unittest.mock denied-name behaviour.','runtime':'Python3.14.4 pytest9.1.1 coverage7.16.2','limitations':'Placeholder apps/services, browser checkout and all Hypothesis generation distributions not executed; no claim of every snippet running.'})
Path('docs/audit-root.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
