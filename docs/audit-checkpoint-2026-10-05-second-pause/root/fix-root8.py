exec(open('/tmp/cs-study-audit-2026-10-04/fix-root.py').read().split("go=['https:")[0])
report=json.loads(Path('docs/audit-root.json').read_text());findings=report['findings']
p='content/software-engineering/01-principles/sep-error-handling'
src=['https://docs.python.org/3/reference/compound_stmts.html#the-try-statement','https://doc.rust-lang.org/reference/attributes/diagnostics.html#the-must_use-attribute','https://docs.stripe.com/api/idempotent_requests','https://peps.python.org/pep-0765/']
patch(p+'.md',[
('Most production incidents happen on the other paths:', 'Failure paths deserve explicit design:'),
('**Bugs** (programmer errors) can\'t be handled meaningfully at runtime. Catching an `AttributeError` and carrying on just hides the bug and corrupts state. Let it fail, log it, and fix it.', '**Bugs** need diagnosis and correction. Do not silently continue as though the operation succeeded. A service may safely contain a failing request or worker, roll back its changes and report the error; process termination is not always necessary.'),
('in Rust the compiler forces you to handle or explicitly propagate (`?`).', 'Rust normally warns when a `Result` marked `must_use` is discarded. This is a lint, not an unconditional compilation error; code can explicitly discard it, so meaningful handling still needs review.'),
('| `else` | `try` finished with no exception |', '| `else` | `try` completed normally, without an exception or exiting via `return`, `break` or `continue` |'),
('| `finally` | always, on the way out |', '| `finally` | on normal Python control-flow exit, including exceptions and returns; abrupt process termination can prevent cleanup |'),
('Python 3.14 now emits', 'CPython 3.14 now emits'),
('which guarantee release even on error:', 'which invoke their cleanup protocol on ordinary scope exit, including exceptions (not abrupt process termination):'),
('@dataclass(frozen=True)', 'from dataclasses import dataclass\n\n@dataclass(frozen=True)'),
('        if not 1 <= self.value <= 99:', '        if type(self.value) is not int:\n            raise TypeError("integer required")\n        if not 1 <= self.value <= 99:')], 'Correct Rust must-use enforcement, Python else/finally semantics and domain type validation; avoid universal crash advice.',src)
def fq(q):
 q[2]['options'][1]['explanation']='Here the try block completes normally, so else runs. A return, break or continue exiting try would skip else even without an exception.'
 q[3]['prompt']=q[3]['prompt'].replace('What does `fetch()` return?', 'Under CPython 3.14 with default warning handling, what does `fetch()` return?')
 q[4]['workedExample']=q[4]['workedExample'].replace("There's no gap to race.", 'This removes the separate existence-check race; it does not by itself prevent malicious path/symlink substitution or all filesystem races.')
 q[7]['options'][2]['text']='The first request may still succeed after timeout, so blind retries can charge twice. Reuse a provider-supported idempotency key for the same logical charge'
 q[7]['workedExample']=q[7]['workedExample'].replace('Or query the charge status before retrying.', 'Reconcile an authoritative terminal status if needed. A single not-found or pending status check does not prove the original request cannot still complete; do not replace deduplication with a racy check.')
 q[8]['options'][3]['text']='The try block confuses a missing email field with a cache miss. Guard only cache[uid], then send after the try/except so both hit and loaded-miss paths send'
 q[8]['options'][3]['explanation']='Correct. Moving send after the handler preserves sending after a successful reload. An else-only send would still skip the cache-miss path.'
questions(p+'.questions.json',fq,'Correct payment retry race, cache-miss send path, TOCTOU scope and Python control-flow conditions.',src)
for ext in ['.md','.questions.json']: report['reviewed_files'].append(p+ext)
report['findings']=findings
Path('docs/audit-root.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
