---
id: test-pytest-fixtures
sourceLesson: test-unit-testing
title: Control setup, cleanup and fixture lifetimes
level: basic
minutes: 3
summary: Tests request fixtures by argument name; fixtures can request other fixtures.
---

Assume `import pytest`. A fixture supplies a test dependency and can clean it up afterwards. The following examples are API sketches: `Account`, `open_connection` and `db_url` stand for application code, not functions supplied by pytest.

### Setup and teardown: fixtures

A **pytest fixture** is a function that provides something a test needs. A test asks for it by naming it as a parameter.

```python
@pytest.fixture
def account():
    return Account(balance=100)

def test_withdraw(account):
    account.withdraw(30)
    assert account.balance == 70
```

Once a fixture reaches `yield`, its teardown normally runs even if the test fails. Setup failure before the yield and abrupt process termination need separate handling:

```python
@pytest.fixture
def conn():
    c = open_connection()
    # Pause setup; resume cleanup after use.
    yield c
    # Release the connection after the test.
    c.close()
```

By default a fixture is **function-scoped**: it runs fresh for every test that uses it. `scope="module"` or `scope="session"` shares one instance across many tests, which is faster for expensive setup but risks tests leaking state into each other.

```
scope="function"  setup/teardown per test
scope="module"    once per test file
scope="session"   once per whole run
```

Fixtures can depend on other fixtures. A common pattern is a session-scoped database connection plus a function-scoped transaction that is rolled back after each test (the later database and contract units).

pytest ships useful built-in fixtures too:

- `tmp_path`: a fresh temporary directory (a `pathlib.Path`) per test.
- `monkeypatch`: temporarily set environment variables or attributes, undone after the test.
- `capsys`: capture what the code prints.

```python
def test_default_db_url(monkeypatch):
    # Exercise the missing-setting fallback.
    monkeypatch.delenv("DB_URL",
                       raising=False)
    assert db_url() == "sqlite://"
```

## Key takeaways
- Tests request fixtures by argument name; fixtures can request other fixtures.
- Yield teardown normally runs after a test even when it fails, provided setup reached yield.
- Wider fixture scopes save setup work but need isolation for mutable state.

## Further reading
- [How to use fixtures — pytest docs](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [How to monkeypatch — pytest docs](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
