exec(open('/tmp/cs-study-audit-2026-10-04/fix-root.py').read().split("go=['https:")[0])
report=json.loads(Path('docs/audit-root.json').read_text());findings=report['findings']
base='content/software-engineering/01-principles/'
src=['https://martinfowler.com/bliki/DesignStaminaHypothesis.html','https://peps.python.org/pep-0008/','https://science.nasa.gov/mission/mars-climate-orbiter/']
patch(base+'sep-clean-code.md',[
('Robert C. Martin estimates the ratio of reading to writing at well over 10 to 1.','The exact ratio varies by task; no measured ratio is established here.'),
("Martin Fowler's *design stamina hypothesis* says that well-structured code is slower to write at first but faster to change after a few weeks. Messy code gets slower to change as it grows.","Martin Fowler's *design stamina hypothesis* proposes that investing in structure can repay its initial cost through easier later changes. His suggested payoff after weeks is explicitly a judgment, not a measured universal crossover."),
('Inside a module, rename freely; modern editors do it safely.', 'Inside a module, editor refactoring tools can help, but check dynamic references, configuration and tests before treating a rename as safe.'),
('# After\nADULT_AGE = 18','# After\nfrom dataclasses import dataclass\n\nADULT_AGE = 18'),
('The "after" version tells a story at one altitude.', 'These checkout fragments illustrate organisation; the tax rule and service calls are placeholders, not a complete tax or transaction implementation. The "after" version tells a story at one altitude.')], 'Distinguish design hypothesis from measured payoff, remove unsupported read/write ratio and qualify refactoring/example scope.',src)
def clean(q):
 q[0]['workedExample']=q[0]['workedExample'].replace('class Status(IntEnum):','from enum import IntEnum\n\nclass Status(IntEnum):')
 q[2]['prompt']=q[2]['prompt'].replace('def export(report, compress, email):','def export(report, compress, email): ...')
 q[2]['workedExample']=q[2]['workedExample'].replace('email):\n','email): ...\n').replace('at least four modes','up to four flag combinations').replace('data = export(report)\nsend(compress(data))','data = compress(export(report))\n# No send: the original call had email=False.')
 q[3]['workedExample']=q[3]['workedExample'].replace('5. Note the original also checks stock *after* reserving, which is probably a logic bug. Side effects hidden in queries make bugs like this easy to miss.', '5. These fragments only illustrate separating effects from a query. A real reservation must account for existing reservations and atomically check and update availability; splitting a concurrent check from its update can oversell.')
questions(base+'sep-clean-code.questions.json',clean,'Preserve the no-email behaviour in the split refactor and mark stock example concurrency limits.',src)
src=['https://connascence.io/','https://peps.python.org/pep-0544/','https://martinfowler.com/ieeeSoftware/coupling.pdf']
patch(base+'sep-coupling-cohesion.md',[
('the answer is nearly always the same:', 'one possible cause is'),
('Low coupling means you can change one without changing the other.', 'Low coupling reduces how often a change in one requires changing the other.'),
('From tightest (worst) to loosest (best):', 'A traditional ordering from tighter to looser coupling follows. It is a design heuristic, not a universal ranking of harm:'),
("But it means `greet` can only be called by code that has a whole `User`, and tests must build one.","The dependency here is on an object exposing `name`. In dynamically typed Python it need not be a complete `User`; a small test double with that attribute works."),
('Every importer depends on everything in it, and nobody owns it.', 'Importers can become coupled to unrelated module-level imports and initialisation; ownership may also become unclear.'),
('The class is really two:', 'This suggests two concerns:'),
('Robert C. Martin\'s package metrics give a rough number. For a module:', 'A module-level variant of Robert C. Martin\'s package metrics gives a rough number. Here we count distinct modules (other formulations count classes across package boundaries):'),
('- **Instability** `I = Ce / (Ca + Ce)`, from 0 (stable) to 1 (unstable).','- **Instability** `I = Ce / (Ca + Ce)`, from 0 (stable) to 1 (unstable), when the denominator is positive. An isolated module has an undefined ratio unless a tool specifies a convention.'),
('A module with I near 1 is free to change because nobody depends on it.', 'A value near 1 means outgoing dependencies dominate, not that nobody depends on it. Exactly I = 1 means Ca = 0 and Ce > 0. The ratio measures structural dependence, not observed change frequency.'),
("Depending on Python's standard library is coupling, but it almost never changes.","Depending on documented Python standard-library APIs is coupling to compatibility commitments; releases can still deprecate or remove APIs.")], 'Correct duck typing, package-instability interpretation and categorical coupling claims.',src)
def coupling(q):
 q[2]['workedExample']=q[2]['workedExample'].replace('and nobody owns the file', 'and ownership may become unclear')
 q[4]['workedExample']=q[4]['workedExample'].replace('everything depends on it, it depends on nothing','at least one module depends on it and it depends on no modules').replace('nothing depends on it. Free to change.', 'no modules depend on it, and it has at least one dependency. This does not guarantee safe or cost-free changes.').replace('means touching six modules', 'can affect its six dependent modules')
 q[8]['options'][1]['explanation']=q[8]['options'][1]['explanation'].replace('versioning means changes are additive', 'an explicit compatibility policy can require additive changes; versioning alone does not make changes compatible')
 q[10]['workedExample']=q[10]['workedExample'].replace('`reporting` I = 0.9 (few dependents, changes often)', '`reporting` I = 0.9 (more outgoing than incoming dependencies; no measured change rate is given)').replace('So `domain` now changes whenever `reporting` does', 'So an incompatible change in the part of `reporting` used by `domain` may force a domain change')
 q[10]['options'][2]['text']='The stable dependencies principle: a structurally stable package depends on a structurally less stable one, potentially propagating incompatible changes into widely used code'
questions(base+'sep-coupling-cohesion.questions.json',coupling,'Avoid equating dependency ratios with change frequency or versioning with compatibility.',src)
src=['https://martinfowler.com/bliki/BeckDesignRules.html','https://martinfowler.com/bliki/Yagni.html','https://www.lockheedmartin.org/en-us/news/features/history/johnson.html','https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction']
patch(base+'sep-dry-kiss-yagni.md',[
('"Keep it simple, stupid" is usually traced to Kelly Johnson, lead engineer at Lockheed\'s Skunk Works, who wanted aircraft that an average mechanic could repair in the field with ordinary tools.', 'Lockheed Martin associates "Keep it simple, stupid" with Kelly Johnson and the Skunk Works engineering approach.'),
("It's also quadratic: `sum(..., [])` copies the accumulated list each time.","Even on a flat list of n elements it takes Θ(n²) time: `sum(..., [])` copies both operands each time. The recursive `extend` version avoids that flat-list penalty, although deep nesting still adds repeated copying and recursion overhead."),
('In priority order, a simple design:', "In Fowler's presentation of Beck's rules, a simple design:"),
('Note the order: clarity beats removing duplication, and both beat minimising the number of classes.', 'Correctness comes first and minimising elements comes last. Formulations differ on the middle two: Fowler notes that clarity and removing duplication usually reinforce one another; they are not a universally agreed tie-breaking order.'),
('From Extreme Programming (Ron Jeffries):', 'Popularised in Extreme Programming:'),
('are DRY and tightly coupled: every change to the library forces both to redeploy.', 'can couple their evolution. Compatible, versioned releases can be adopted independently; a breaking shared-model change may instead force coordination.')], 'Clarify principle provenance and limits, quadratic copying assumptions and independently versioned shared libraries.',src)
def dry(q):
 q[5]['prompt']=q[5]['prompt'].replace('time complexity', 'tight asymptotic time complexity')
 q[5]['options'][3]['explanation']='Every input element must be visited; that establishes an Ω(n) lower bound, not an O(n) upper bound.'
 q[5]['options'][2]['explanation']='Correct. Copying the growing left operand alone costs n(n−1)/2; including the one-element right operand gives n(n+1)/2 element-reference copies, still Θ(n²).'
 q[5]['workedExample']=q[5]['workedExample'].replace('Total copies: 0 + 1 + ... + (n−1) = n(n−1)/2', 'Total copies of both operands: 1 + 2 + ... + n = n(n+1)/2')
 q[7]['prompt']=q[7]['prompt'].replace("Kent Beck's rules of simple design are, in priority order:","In Fowler's displayed ordering, the simple-design rules are:").replace('What do the rules suggest?', 'Using that displayed ordering for this example, what should you prefer?')
 q[7]['options'][1]['explanation']='Correct for the ordering stated in the question. Historical formulations swap the middle two rules, and Fowler says they usually reinforce one another.'
 q[7]['workedExample']+='\n\nThis is an exercise in the stated ordering, not proof of a universal priority between clarity and removing duplication.'
 q[10]['workedExample']=q[10]['workedExample'].replace('the six months of effort on multi-currency', 'the effort originally spent on multi-currency').replace('six months of effort', 'early development effort')
questions(base+'sep-dry-kiss-yagni.questions.json',dry,'Correct copy-count arithmetic, lower-bound notation, rule-ordering attribution and six months elapsed vs effort.',src)
src=['https://peps.python.org/pep-0544/','https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html','https://docs.python.org/3/library/typing.html']
patch(base+'sep-solid.md',[
('class Shape(Protocol):','import math\nfrom dataclasses import dataclass\nfrom typing import Protocol\n\nclass Shape(Protocol):'),
('The formal rules for a subtype:', 'Important requirements for behavioural subtyping include:'),
('- **Invariants** of the parent must be preserved.', '- **Invariants** of the parent must be preserved, including constraints on observable state changes over time.'),
('make objects immutable (an immutable square *is* a valid rectangle)', 'use a compatible read-only contract (an immutable square can then be a valid rectangle subtype)'),
('which is also an LSP violation. And any change to `fax`\'s signature makes every implementer and client recompile.', 'which violates LSP if the contract requires those operations to succeed. A changed `fax` signature can affect implementers even when their useful role is only printing; effects on clients and recompilation depend on the change and toolchain.'),
('any object with that method fits, without inheriting anything:', 'a static checker accepts objects with compatible member signatures, without explicit inheritance. An annotation does not enforce that contract at runtime:'),
("`InvoiceService` can't be tested without Postgres and an SMTP server, and switching to a different mail provider means editing billing logic.", '`InvoiceService` constructs concrete clients, making isolated tests and substitutions harder; monkey-patching can still replace those names in Python. Injecting a narrow abstraction makes the seam explicit.'),
('adds a file and an indirection for no benefit.', 'can add indirection without a demonstrated benefit.')], 'Correct runtime/static contract distinctions and overstatements about substitutability, testing and interface changes.',src)
def solid(q):
 q[2]['workedExample']=q[2]['workedExample'].replace('the throwing methods were also a Liskov violation', 'the throwing methods violate Liskov substitution if the original contract promises successful support')
 q[4]['workedExample']=q[4]['workedExample'].replace('means editing `Signup`.', 'is harder without an explicit substitution seam; Python monkey-patching is still possible.')
 q[6]['workedExample']=q[6]['workedExample'].replace('you can pass in a different `PgClient`, but not a different *kind* of store, and type checkers will complain about a fake.', 'the annotation ties statically checked callers to PgClient-compatible types. Python itself will accept another object at runtime; a fake subclass may also satisfy a nominal checker.')
 for i in [2,4,6,7]:
  for key in ['prompt','workedExample']:
   q[i][key]=q[i][key].replace('```python\nclass ', '```python\nfrom typing import Protocol\n\nclass ')
 q[9]['prompt']="`ImmutableRectangle` promises non-negative `width` and `height` and `area() == width * height`. It has no setters; any `with_width` operation may return a new general rectangle. `ImmutableSquare` preserves these promises and additionally has equal sides. Does this subtype violate LSP?"
 q[10]['options'][0]['text']+=' and no identified boundary or isolation need'
 q[10]['options'][0]['explanation']='Correct under the stated absence of a boundary or isolation need. A single implementation alone does not prove an interface is useless; evaluate what dependency it isolates.'
 q[10]['workedExample']=q[10]['workedExample'].replace('Single-implementation interfaces: no second implementation, no fake. No pressure. Indirection only.', 'Single-implementation interfaces: the scenario gives no implementation, testing or boundary need. That absence, not implementation count alone, motivates the criticism.')
 q[11]['options'][0]['explanation']='Unmodifiable lists reject mutation, including add, remove, clear and set. set replaces an element and is not structurally modifying the list in the JDK terminology.'
questions(base+'sep-solid.questions.json',solid,'Qualify optional operations, nominal vs runtime typing, immutable contracts and interface heuristics.',src)
src=['https://docs.stripe.com/webhooks','https://docs.python.org/3/library/dataclasses.html','https://docs.python.org/3/library/typing.html','https://semver.org/','https://www.rfc-editor.org/rfc/rfc9413.html','https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts']
patch(base+'sep-writing-for-others.md',[
('# Stripe retries webhooks for up to\n# 3 days, so dedupe on event id, not\n# on timestamp.', '# Stripe can deliver an event repeatedly.\n# Dedupe by event id, not its timestamp.'),
('```python\n# Deliberately O(n^2): n <= 8 here and\n# this beats sorting by ~3x in benchmarks.\n```','```python\n# Input is limited to 8 elements by the\n# caller contract; keep this loop simple.\n```\n\n> [!note] Content gap\n> The previous claim of a measured threefold speedup was removed because no benchmark or reproducible setup was available. No performance result is asserted here.\n\nThe webhook fragment only illustrates a comment. Production deduplication needs durable, atomic coordination with the effect. Stripe automatic retries last up to three days in live mode; manual CLI resends can occur up to 30 days later, so three days is not a universal deduplication-retention limit.'),
('```python\ndef retry(fn,', 'The following is a documentation sketch, not an implemented retry helper:\n\n```python\ndef retry(fn,'),
('    the nth failure.', '    failure indexed n = 0, 1, ...; no\n    wait after the final failed attempt.'),
('**Type hints** are documentation that tools verify:', '**Type hints** are documentation that configured static-analysis tools can check. Python does not enforce them at runtime:'),
('a type checker will flag callers that forget.', 'a suitably configured checker can flag unsafe use in code it checks.'),
('model `PaidOrder` with a required `paid_at`.', 'model `PaidOrder` with a required `paid_at` and validate boundary inputs. Python annotations alone still allow an explicitly supplied `None` at runtime.'),
('The [Diátaxis](https://diataxis.fr/) framework (adopted by Cloudflare, Gatsby and others for their developer docs)', 'The [Diátaxis](https://diataxis.fr/) framework'),
('part of the protocol forever', 'a compatibility obligation that is costly to remove'),
('encodes compatibility in `MAJOR.MINOR.PATCH`:', 'encodes compatibility in `MAJOR.MINOR.PATCH`. For a declared public API at version 1.0.0 or later:')], 'Remove unreproducible benchmark, qualify Stripe retries/deduplication, Python typing and API compatibility.',src)
def writing(q):
 q[6]['options'][2]['explanation']='Accepting several explicitly documented aliases can be valid, but does not itself prevent misspellings. Reject unknown strings; enums also need validation at Python API boundaries.'
 q[6]['workedExample']=q[6]['workedExample'].replace('every spelling you accept becomes one you must support forever', 'callers may depend on accepted spellings, so removing them needs a compatibility plan')
 q[9]['options'][1]['text']='Model each state separately, e.g. NewOrder and PaidOrder with a required payment time; validate the time in the Python constructor'
 q[9]['options'][1]['explanation']='Correct. A missing required argument is rejected by the generated constructor, but annotations alone do not reject None. Explicit boundary validation is needed to enforce the value at runtime.'
 q[9]['workedExample']=q[9]['workedExample'].replace('```python\n@dataclass', '```python\nfrom dataclasses import dataclass\nfrom datetime import datetime\n\n@dataclass').replace('    paid_at: datetime\n\nOrder', '    paid_at: datetime\n\n    def __post_init__(self):\n        if not isinstance(self.paid_at, datetime):\n            raise TypeError("payment time required")\n\nOrder')
 q[11]['prompt']=q[11]['prompt'].replace('Which docstring would most help a caller of this function?', 'For a mutable list of finite, non-negative Python int/float scores, which docstring best describes this function?')
 q[11]['options'][2]['text']='`"""Scale finite non-negative scores in place so the max is 1.0. Returns None. Raises ValueError if empty, ZeroDivisionError if the max is 0. Caller must satisfy the input contract."""`'
 q[11]['workedExample']+='\n\nThe non-negative, finite input contract matters: for [-2, -1], division by -1 produces [2, 1], whose maximum is 2 rather than 1. This function does not validate that contract.'
questions(base+'sep-writing-for-others.questions.json',writing,'Enforce the paid-state value in Python and restrict normalisation claims to their actual input domain.',src)
for name in ['sep-clean-code','sep-coupling-cohesion','sep-dry-kiss-yagni','sep-solid','sep-writing-for-others']:
 for ext in ['.md','.questions.json']:
  if base+name+ext not in report['reviewed_files']:report['reviewed_files'].append(base+name+ext)
report['findings']=findings
report.setdefault('omissions',[]).append({'file':base+'sep-writing-for-others.md','claim':'Measured threefold loop speedup','reason':'No benchmark or reproducible setup available; explicitly omitted in lesson.'})
Path('docs/audit-root.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
