---
id: test-patch-autospec
sourceLesson: test-doubles
title: Patch the lookup name and constrain mocks
level: intermediate
minutes: 3
summary: Patch the name the caller looks up at runtime.
---

Assume `from unittest.mock import Mock, patch, create_autospec` in these illustrative snippets. The two-file example shows where references live; its payment function is a placeholder, not a real payment integration.

## Patch where it is looked up

`unittest.mock.patch` temporarily replaces a name while a test runs. The most common mistake is patching the wrong name.

```python
# payments.py
def charge(card, amount):
    ...  # real network call

# checkout.py
from payments import charge

def place_order(card, total):
    # This name is resolved in checkout.
    r = charge(card, total)
    if r["status"] == "paid":
        return "ok"
    return "declined"
```

`from payments import charge` copies a reference to the function into `checkout`'s namespace when `checkout` is imported. So:

```python
# WRONG: checkout still holds the
# original charge, so the real call runs
with patch("payments.charge") as f:
    f.return_value = {"status": "paid"}
    place_order("4242", 10)

# RIGHT: replace the name checkout uses
with patch("checkout.charge") as f:
    f.return_value = {"status": "paid"}
    assert place_order("4242", 10) == "ok"
```

The rule from the Python docs: **patch where an object is looked up, not where it is defined.** If `checkout.py` instead did `import payments` and called `payments.charge(...)`, then patching `"payments.charge"` would work, because the lookup happens on the `payments` module at call time.

```
from payments import charge
  checkout.charge -> original function
  patch "checkout.charge"

import payments
  checkout -> payments module
  patch "payments.charge"
```

## Mocks lie: spec and autospec

A bare `Mock` accepts most ordinary method names and arbitrary call arguments, which means it cannot tell you when you have used it wrongly.

```python
m = Mock()
m.chrage("4242", 10)       # typo
m.charge.assert_not_called()   # passes
```

Worse, when the real API changes (say `charge` gains a required `currency` argument), every test using a bare `Mock` keeps passing while production fails.

Two defences:

- `Mock(spec=Mailer)` restricts attribute lookup to names on the spec, so unknown method lookups raise `AttributeError`. Use `spec_set` to restrict setting unknown attributes too. It does not check the arguments passed to methods.
- `create_autospec(Mailer)` or `patch(..., autospec=True)` also checks **call signatures**, so a missing argument raises `TypeError`.

```python
fake = create_autospec(payments.charge)
fake("4242")      # TypeError: missing
                  # 'amount'
```

> [!warning] Misspelled assertions
> `m.assert_called_once()` checks something; `m.asert_called_once()` used to silently do nothing and return a new `Mock`. Recent Python versions raise `AttributeError` for names starting with `assert`, `assret`, `asert`, `aseert` or `assrt`, and for a few common slips such as `called_once_with`. Other typos, like `asssert_called_once`, still pass silently. Prefer `spec` or `autospec`.

## Key takeaways
- Patch the name the caller looks up at runtime.
- spec checks allowed attributes; autospec also checks supported call signatures.
- Bare mocks can accept misspellings and hide incompatible interface changes.

## Further reading
- [unittest.mock — Python docs](https://docs.python.org/3/library/unittest.mock.html)
- [How to monkeypatch — pytest docs](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
