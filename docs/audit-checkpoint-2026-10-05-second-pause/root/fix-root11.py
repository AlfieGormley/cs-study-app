exec(open('/tmp/cs-study-audit-2026-10-04/fix-root.py').read().split("go=['https:")[0])
report=json.loads(Path('docs/audit-root.json').read_text());findings=report['findings']
b='content/software-engineering/02-design-patterns/'
src=['https://docs.oracle.com/javase/tutorial/java/javaOO/lambdaexpressions.html','https://docs.python.org/3/reference/import.html','https://docs.python.org/3/howto/sorting.html','https://www.norvig.com/design-patterns/design-patterns.pdf']
patch(b+'pattern-why.md',[
('a file, a socket, an in-memory buffer or a test fake.', 'a text file, a socket adapter exposing that contract, an in-memory text buffer or a test fake. A raw socket does not provide write(text).'),
('        self.inner = inner\n        self.tries = tries', '        if type(tries) is not int or tries < 1:\n            raise ValueError("positive tries")\n        self.inner = inner\n        self.tries = tries'),
('says in seven words', 'conveys succinctly'),
('For example, the strategy pattern in Java needs an interface and a class per strategy.', 'Older Java examples often use an interface and explicit classes; Java 8 and later also support lambdas and method references for functional-interface strategies.'),
('(Uppercase letters sort before lowercase in Unicode code-point order, which is why `Fig` comes first in the default sort.)', '(For the ASCII letters here, uppercase F precedes lowercase a and p in code-point order. This is not a universal ordering rule for all Unicode upper- and lowercase letters.)')], 'Update Java strategy examples, restrict Unicode assertion, fix write-contract and invalid retry count.',src)
def why(q):
 q[4]['workedExample']=q[4]['workedExample'].replace('duck typing already enforces it at run time', 'Python attempts the operations at runtime; neither duck typing nor annotations proactively validate the complete behavioural contract')
 q[5]['workedExample']=q[5]['workedExample'].replace('The module system already guarantees one copy of module state.', 'Normal imports of the same name reuse its cached module within one interpreter; reloads, cache changes, aliases and separate processes limit this sharing.')
 q[5]['options'][2]['explanation']='Correct within normal same-name imports in one interpreter. Reloads, aliases and separate processes can create separate state.'
 q[8]['workedExample']=q[8]['workedExample'].replace('Java needs an interface and classes; Python uses a callable.', 'Java can use a functional interface with a lambda or method reference; Python can pass a callable directly.')
questions(b+'pattern-why.questions.json',why,'Correct Java lambda support, module-singleton scope and runtime contract enforcement.',src)
src=['https://docs.python.org/3/library/copy.html','https://docs.python.org/3/reference/import.html','https://docs.python.org/3/library/collections.html#collections.defaultdict','https://docs.spring.io/spring-framework/reference/core/beans/factory-scopes.html']
patch(b+'pattern-creational.md',[
('`list` is the factory it calls for missing keys.', '`list` is the factory it calls for missing-key indexing (d[key]); get() does not invoke it.'),
('The client holds one factory and asks it for every part, so it can never mix families.', 'If the client obtains every part from one correctly implemented factory, the family stays consistent. The pattern itself does not prevent bypassing the factory or a faulty implementation.'),
('`copy.deepcopy()` copies everything reachable.', '`copy.deepcopy()` recursively copies supported components, respecting memoisation and class hooks. It can preserve shared objects and returns some objects, including functions and classes, unchanged.'),
('**a module is already a singleton**. Python imports each module once and caches it in `sys.modules`, so a module-level object is shared by everyone who imports it.', '**ordinary imports share a cached module within one interpreter**. Normal imports of the same name reuse sys.modules; reloads, aliases, cache manipulation and separate processes mean this is not a universal singleton guarantee.'),
('**Spring beans** are singletons by default, but managed by the container and injected,', '**Spring beans** default to singleton scope per bean definition per container, not one object globally across all containers; they are managed and injected,'),
('- Abstract factory guarantees matching families of objects', '- Abstract factory centralises creation of matching families of objects'),
('class CsvWriter:\n', 'class CsvWriter:\n    # Toy: fields contain no commas,\n    # quotes or newlines. Use csv.writer\n    # for general CSV serialization.\n')], 'Bound deep-copy, factory and singleton claims; identify limited toy CSV implementation.',src)
def creation(q):
 q[1]['options'][2]['explanation']='Correct for ordinary imports of the same module name within one interpreter. A module-level object is shared there; explicit injection can make the dependency clearer.'
 q[1]['workedExample']=q[1]['workedExample'].replace('Python already guarantees one copy of each **module**:', 'For ordinary same-name imports in one interpreter,').replace('No `__new__` tricks, no metaclass.', 'Reloads, aliases and separate processes are exceptions to this sharing. No __new__ tricks or metaclass are needed for the ordinary case.')
 q[2]['prompt']=q[2]['prompt'].replace('whenever a missing key is accessed', 'when a missing key is indexed with d[key] (not d.get(key))')
 q[3]['options'][2]['explanation']='Correct. A correctly implemented factory supplies matching products if the client consistently obtains them through that factory.'
 q[4]['workedExample']=q[4]['workedExample'].replace('```python\n@dataclass', '```python\nfrom dataclasses import dataclass\n\n@dataclass')
 q[8]['prompt']=q[8]['prompt'].replace('a prototype `Session` object', 'a custom Session object with ordinary instance attributes and no copy or serialization hooks')
 q[8]['workedExample']=q[8]['workedExample'].replace('`deepcopy` walks every reachable attribute and copies it', 'For this ordinary object without hooks, deepcopy traverses its stored state').replace('Even if it worked, two pools sharing one OS socket would be broken.', 'Sharing a connection is safe only under an explicit ownership and concurrency contract; blindly copying pool state does not establish that contract.')
 q[9]['prompt']=q[9]['prompt'].replace('How many classes must change', 'Counting only the explicitly declared factory interface and its concrete factory classes, how many classes must change')
questions(b+'pattern-creational.questions.json',creation,'Specify missing-key dispatch, import scope, copy hooks and factory-class counting.',src)
src=['https://docs.python.org/3/library/functools.html','https://docs.python.org/3/reference/datamodel.html#slots','https://flask.palletsprojects.com/en/stable/api/#flask.Flask.route','https://docs.djangoproject.com/en/5.2/ref/models/querysets/','https://docs.python.org/3/library/io.html']
patch(b+'pattern-structural.md',[
('**`functools.lru_cache`, `functools.wraps`**, and the decorators in Flask (`@app.route`) and pytest (`@pytest.fixture`) apply the idea to functions.', '**`functools.lru_cache`** adds caching to a callable; **`functools.wraps`** helps preserve wrapper metadata. Python decorator syntax is broader than the GoF pattern: Flask route decorators register a view and can return it unchanged; decorators need not wrap calls.'),
('are thousands to millions of times slower than a local call.', 'can have much higher and more variable latency than a local call; the ratio depends on the work and environment.'),
("`request.user` isn't loaded from the database until you first touch it.", '`request.user` defers authentication lookup until needed; whether that lookup queries a database depends on the session and authentication backend.'),
('follows redirects and decodes the response, all in one call.', 'follows redirects and returns a Response. Text decoding and JSON parsing are accessed through the response API; a one-shot call does not share a persistent session pool across unrelated calls.'),
("Very deep trees can hit Python's recursion limit (1,000 frames by default).", 'Very deep trees can hit the active recursion limit; inspect sys.getrecursionlimit() rather than assuming a universal depth.'),
('return f"<circle r={r}>"', 'return f\'<circle r="{r}" />\''),
("That's 2 shapes plus 2 renderers instead of 2 × 2 subclasses", 'Extending the example to 2 shapes gives 2 shapes plus 2 renderers instead of 2 × 2 concrete combinations'),
('from functools import lru_cache\n\nclass Glyph:\n    def __init__(self, char, font):\n        self.char = char\n        self.font = font', 'from functools import lru_cache\nfrom dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass Glyph:\n    char: str\n    font: str'),
('`__slots__`** is a related memory trick: it removes the per-instance `__dict__`,', '`__slots__`** is a related memory technique: it can avoid a per-instance __dict__ when bases do not supply one and the class does not request one,')], 'Correct decorator semantics, lazy backend and network assumptions, SVG syntax and immutable flyweight example.',src)
def structural(q):
 q[0]['prompt']=q[0]['prompt'].replace('charge(amount, card)', 'charge(amount_pence, card)')
 q[0]['options'][1]['explanation']='Correct. The adapter translates names and argument order while preserving this example\'s integer-pence unit contract.'
 q[0]['workedExample']=q[0]['workedExample'].replace('def charge(self, amount, card):\n        pence = round(amount * 100)', 'def charge(self, amount_pence, card):\n        pence = amount_pence').replace('converting units', 'preserving the stated units')
 q[5]['prompt']=q[5]['prompt'].replace('`customer` is a lazily loaded foreign key.', 'Each order has a non-null customer foreign key that is not cached or prefetched, and the manager performs no automatic joins.')
 q[6]['options'][0]['text']='requests.get(url), which creates a temporary session and delegates transport and response handling through adapters and connection pools'
 q[8]['prompt']=q[8]['prompt'].replace('In CPython,', 'In a standard CPython build with its -5..256 small-integer cache,')
questions(b+'pattern-structural.questions.json',structural,'Use explicit integer currency units, state N+1/cache assumptions and correct Requests facade description.',src)
src=['https://docs.oracle.com/javase/tutorial/java/javaOO/lambdaexpressions.html','https://docs.python.org/3/library/logging.html','https://docs.djangoproject.com/en/5.2/topics/migrations/#reversing-migrations','https://redux.js.org/understanding/thinking-in-redux/three-principles']
patch(b+'pattern-behavioural-1.md',[
('Where Java needs an interface and a class per strategy, Python usually just passes a function:', 'Java can use lambdas or method references for functional-interface strategies; Python commonly passes a function directly:'),
('it stays alive forever and keeps receiving events.', 'it remains reachable while the subject retains it and can keep receiving events.'),
('a logger passes each record to every attached handler.', 'a logger routes eligible records to handlers subject to levels, filters and propagation settings.'),
('which is what users expect from every editor.', 'which is the conventional linear undo-stack policy. Some editors preserve branching histories instead.'),
('each operation (`AddField`, `RenameModel`) knows how to apply itself forwards and backwards (`database_forwards` and `database_backwards`), so `migrate` can roll back.', 'operations represent schema or data changes. Reversible operations support forwards/backwards execution; some operations or data changes are irreversible, and reversing schema operations need not restore lost data.'),
('**Redux actions** and **event sourcing** take the idea further: the log of commands or events *is* the source of truth.', '**Redux actions** describe changes processed by reducers; Redux\'s store holds the current state and does not inherently persist an action log. **Event sourcing** instead treats the persisted event history as authoritative. Commands request changes; events record facts, so they are not interchangeable.'),
('a redo stack must be cleared on a new action.', 'a conventional linear redo stack is cleared on a new action.')], 'Correct modern strategy support, logger filtering, migration reversibility and Redux vs event-sourcing semantics.',src)
def behavioural1(q):
 q[0]['workedExample']=q[0]['workedExample'].replace("so the core `cost` doesn't need retesting", 'while the core cost code can stay unchanged. Still run regression tests and validate the new strategy and registration')
 q[3]['workedExample']=q[3]['workedExample'].replace('correct editor behaviour', 'the intended linear-history policy in this example')
 q[7]['options'][0]['explanation']='Correct. Migration operations package changes as objects. Reversibility depends on the operation and supplied reverse implementation; not every migration can be undone.'
 q[7]['workedExample']=q[7]['workedExample'].replace('applied or reversed → yes', 'applied, and reversed when supported → yes')
 q[9]['options'][3]['text']='If refunding is permitted and supported, request an idempotent compensating refund and track its actual outcome alongside the capture'
 q[9]['options'][3]['explanation']='Correct. A refund is a new external operation that can fail or remain pending; do not mark the capture as erased or the refund as successful before confirmation.'
questions(b+'pattern-behavioural-1.questions.json',behavioural1,'Retain regression testing and qualify undo, migration and compensation guarantees.',src)
src=['https://docs.python.org/3/library/unittest.html','https://peps.python.org/pep-0249/#optional-db-api-extensions','https://docs.djangoproject.com/en/5.2/ref/models/querysets/#iterator','https://docs.python.org/3/library/stdtypes.html#iterator-types','https://docs.python.org/3/library/ast.html']
patch(b+'pattern-behavioural-2.md',[
('`run()` calls `setUp()`, then your test method, then `tearDown()`.', '`run()` normally calls setUp, the test and tearDown; tearDown is not run if setUp fails. Cleanup registered with addCleanup has separate guarantees.'),
('Iterators are also **lazy**: they produce items on demand. That lets you stream a 10 GB file line by line, or page through an API, in constant memory.', 'The iterator protocol obtains one item per next() call; it does not require lazy construction or constant memory. Streaming can avoid loading the entire input, but memory still depends on buffering, maximum line/page size, retained output and traversal state (O(tree height) for this recursive generator).'),
('An iterator, unlike an iterable, is exhausted after one pass.', 'An iterator is also iterable; once exhausted it stays exhausted. A re-iterable collection such as a list can supply a fresh iterator for another pass.'),
('DB-API cursors are iterable, and server-side cursors stream rows rather than loading them all.', 'Many DB-API drivers provide iterable cursors (an optional DB-API extension). Server-side cursor modes can fetch batches without loading the whole result into the client.'),
('`.iterator()` streams results without caching them.', '`.iterator()` bypasses the QuerySet result cache; database-driver buffering and backend support determine whether results are actually streamed.'),
('remember iterators are lazy and single-use.', 'remember iterators can be exhausted, and the protocol alone does not guarantee lazy or bounded-memory execution.')], 'Correct iterable/iterator relationship, memory bounds, DB cursor optionality and setup-failure cleanup.',src)
def behavioural2(q):
 q[1]['workedExample']+='\n\nThis is the normal successful-setup path; if setUp fails, unittest skips the test and tearDown (registered cleanups are separate).'
 q[7]['prompt']=q[7]['prompt'].replace('Which is cheaper, and why?', 'Which addition can be localised to one new visitor class without editing existing node classes or passes?')
 q[7]['options'][3]['text']='The linting pass can be localised to one new visitor; handling Await may require updates across existing visitors'
 q[7]['options'][3]['explanation']='Correct for the classic visitor structure. Locality is the advantage; one new visitor may still need many methods, so class count alone does not establish lower implementation effort.'
 q[7]['workedExample']+='\n\nThis compares where changes live, not their total cost: up to 30 new methods can exceed the work of 8 small handler changes.'
 q[8]['prompt']=q[8]['prompt'].replace('`visitor.visitAdd(this)`', '`visitor.visit(this)` with overloads visit(Node) and visit(Add)')
questions(b+'pattern-behavioural-2.questions.json',behavioural2,'Distinguish visitor change locality from effort and specify actual overloaded double-dispatch call.',src)
src=['https://git-scm.com/docs/git-log','https://docs.python.org/3/tutorial/controlflow.html','https://martinfowler.com/bliki/StranglerFigApplication.html']
patch(b+'pattern-anti-patterns.md',[
('Version control remembers everything, so deleting code is reversible. Use coverage data, logging or a metric on the old branch in production to prove it\'s unused, then remove it.', 'Committed code remains recoverable while its history is retained. Use callers, configuration, representative production telemetry and owner knowledge to build evidence that a branch is unused; an observation window with zero hits is not proof that rare or scheduled paths never need it.'),
('every class\'s real dependencies are hidden inside its method bodies.', 'dependencies obtained this way are hidden inside method bodies.'),
('A 5,000-line', 'A 5,000-line')], 'Do not treat version control or zero observed traffic as proof that code deletion is harmless.',src)
def anti(q):
 q[2]['workedExample']='1. Preserve the rule before changing it: total > 249.99 is not generally equivalent to total >= 250 when fractional pennies are possible.\n2. Name the existing values:\n\n```python\nPAID_STATE_CODE = 4\nFREE_SHIPPING_OVER = 249.99\n\nif (order.state == PAID_STATE_CODE\n        and total > FREE_SHIPPING_OVER):\n    ship_cost = 0\n```\n\n3. Converting to an Enum, Decimal or integer pennies can be a separate deliberate migration, with a specified rounding and boundary policy. A readability refactor should not silently change that policy.'
 q[3]['workedExample']=q[3]['workedExample'].replace('That means', 'That may mean').replace('Next time, adding a currency is one table row.', 'Centralising shared currency metadata can reduce repeated edits; payments, formatting and business support may still require additional changes.')
 q[4]['workedExample']=q[4]['workedExample'].replace('Zero hits → remove the flag, the branch and `_old_price`.', 'Combine zero hits with caller/configuration review, rare-path coverage and owner confirmation, then remove with a rollback plan. Absence of observed traffic alone is not proof.')
 q[5]['prompt']=q[5]['prompt'].replace('Select all that apply.', 'Assume no separate compatibility, construction-lifecycle or isolation need justifies the extra layer. Select all that apply.')
 q[8]['workedExample']=q[8]['workedExample'].replace('A 5,000-line file changed twice a year matters less than a 1,500-line file changed every week.', 'Frequent changes make the smaller file a plausible maintenance hotspot, but incident severity, security exposure and business impact also matter; this metric does not prove which file is most costly.')
questions(b+'pattern-anti-patterns.questions.json',anti,'Preserve threshold semantics during refactoring and qualify unused-code and hotspot conclusions.',src)
for name in ['pattern-why','pattern-creational','pattern-structural','pattern-behavioural-1','pattern-behavioural-2','pattern-anti-patterns']:
 for ext in ['.md','.questions.json']:report['reviewed_files'].append(b+name+ext)
report['findings']=findings
Path('docs/audit-root.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
