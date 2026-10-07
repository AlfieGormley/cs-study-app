---
id: test-integration-e2e
title: Integration and end-to-end tests, contract testing
level: intermediate
minutes: 15
summary: Testing your code against real databases and services, keeping integration tests isolated, using a few end-to-end tests well, and catching broken service boundaries with consumer-driven contract tests.
---

Unit tests tell you each piece works on its own. They cannot tell you whether the pieces fit. Your SQL might be wrong for the real database, your JSON field might be called `email` while the other service sends `mail`, and your config might point at the wrong queue. Those bugs live at the **seams**, and you need tests that exercise the seams.

## Integration tests: narrow and broad

"Integration test" means different things to different people. Martin Fowler separates two kinds:

- **Narrow** integration tests exercise the code that talks to one external thing (your repository class against a real database, your HTTP client against a local server), with everything else doubled or absent.
- **Broad** integration tests bring up many real services together and test through all of them.

Narrow tests are fast enough to run on every commit and fail for a specific reason. Broad tests overlap heavily with end-to-end tests and inherit their slowness and flakiness. When people say "write more integration tests", the useful version is almost always narrow.

## Testing against a real database

The classic integration test checks your data-access code against a real database engine.

```python
class UserRepo:
    def __init__(self, conn):
        self.conn = conn

    def add(self, email):
        cur = self.conn.execute(
            "INSERT INTO users(email) "
            "VALUES (?)", (email,))
        return cur.lastrowid

    def by_email(self, email):
        row = self.conn.execute(
            "SELECT id FROM users "
            "WHERE email = ?",
            (email,)).fetchone()
        return row[0] if row else None
```

### Keep tests isolated with rollbacks

Creating a fresh database per test is slow. A standard pattern is one connection for the whole module (or session) plus a transaction per test that is **rolled back** afterwards:

```python
@pytest.fixture(scope="module")
def conn():
    c = sqlite3.connect(":memory:")
    c.execute(
        "CREATE TABLE users ("
        "id INTEGER PRIMARY KEY,"
        "email TEXT UNIQUE NOT NULL)")
    yield c
    c.close()

@pytest.fixture
def repo(conn):
    yield UserRepo(conn)
    conn.rollback()  # undo this test
```

```python
def test_add_then_find(repo):
    uid = repo.add("a@x.io")
    assert repo.by_email("a@x.io") == uid

def test_unique_email(repo):
    repo.add("a@x.io")
    with pytest.raises(
            sqlite3.IntegrityError):
        repo.add("a@x.io")

def test_isolated(repo):
    assert repo.by_email("a@x.io") is None
```

All three pass. Remove the `rollback()` and two of them fail: `test_unique_email` hits the row left by the first test on its *first* insert, and `test_isolated` finds a user that should not exist.

> [!warning] Rollback isolation has holes
> If the code under test calls `commit()` itself, the rollback cannot undo it. Neither can it undo side effects outside the database (files, queues, emails). Code that manages its own transactions needs explicit cleanup, such as truncating tables after each test.

### Use the same engine as production

The example uses SQLite because it needs no setup. That is fine for illustration, but SQLite is far more lenient than Postgres or MySQL:

```python
c.execute("CREATE TABLE t "
          "(n INTEGER, s VARCHAR(3))")
c.execute("INSERT INTO t VALUES "
          "('abc', 'too long')")
# succeeds in SQLite: 'abc' is
# stored in an INTEGER column, and
# VARCHAR(3) is not enforced
```

Postgres rejects both. SQL dialects also differ (`RETURNING`, JSON operators, upserts, locking). Tests on a different engine can pass while production fails.

The modern answer is **Testcontainers**, which starts a real database in a throwaway Docker container from your test code:

```python
from testcontainers.postgres import (
    PostgresContainer)

@pytest.fixture(scope="session")
def pg_url():
    with PostgresContainer(
            "postgres:16") as pg:
        yield pg.get_connection_url()
```

Starting a container takes a few seconds, so do it once per session and isolate tests with transactions or table truncation.

## Testing HTTP clients and other services

A narrow integration test can run the real client against a local **stub server**, such as WireMock. Python libraries `responses` and `respx` instead intercept client-library calls in-process; they are not local HTTP servers and exercise a different boundary.

Keeping the client code real can check URL construction, headers, query encoding, JSON parsing, timeout and retry behaviour, and how you handle a 503 or a malformed body.

An in-process interceptor does not exercise real sockets, TLS or actual network timeouts; injected exceptions only check handling. Neither approach alone establishes whether canned responses match what the real service sends. That is the job of contract tests, below.

## End-to-end tests

An E2E test drives the whole deployed system from the outside. For a web app, that usually means a real browser controlled by a tool such as **Playwright** or Selenium:

```python
from playwright.sync_api import expect

def test_checkout(page):
    page.goto("https://staging.shop/")
    page.get_by_role(
        "button", name="Add to basket"
    ).click()
    page.get_by_role(
        "link", name="Checkout").click()
    expect(page.get_by_text(
        "Order confirmed")).to_be_visible()
```

E2E tests provide evidence that selected journeys work through the tested wiring and configuration; they do not prove correctness for all users, inputs or environments. They are also slow, expensive and the most prone to flakiness. Use them deliberately:

- **Cover a few critical journeys**: sign up, log in, buy, pay. Not every edge case; push those down the pyramid.
- **Wait for conditions, never for time.** Playwright's `expect` retries until the element appears or a timeout passes. `time.sleep(2)` is slow when the page is fast and flaky when it is slow.
- **Own your test data.** Each test creates the user and products it needs, with unique names, rather than relying on shared records that another test may change.
- **Use stable selectors**: roles, labels or dedicated test ids, not CSS paths that change with every redesign.
- **Wrap pages in page objects** (`CheckoutPage.pay_with(card)`) so a UI change means editing one class, not forty tests.

> [!note] Shared staging environments
> A single staging environment shared by many teams is a common source of E2E pain: someone else's half-deployed service breaks your tests. Ephemeral per-branch environments help, as does moving most cross-service checks to contract tests.

## The microservice problem

Picture two services. **Orders** (the *consumer*) calls **Users** (the *provider*) at `GET /users/42` and reads `email`.

```
 Orders  --GET /users/42-->  Users
         <-- {id, email} --
```

Each team tests well in isolation. Orders' tests stub the Users API with `{"id": 42, "email": "a@x.io"}`. Users' tests check their own endpoint. Then the Users team renames `email` to `primary_email`. Every test in both repositories passes. Production breaks.

The stub encoded Orders' *belief* about Users, and nothing checked that belief. You could catch it with broad E2E tests that deploy both services, but those are slow, flaky and need every service up at once. **Contract tests** check the seam directly instead.

## Contract testing

A **contract** is a precise description of the requests a consumer will send and the parts of the responses it relies on. It is tested from both sides:

1. **Consumer side**: the consumer's tests run against a mock provider that records the interactions they need. This produces the contract.
2. **Provider side**: the provider's CI replays every contract against the real provider and checks each response satisfies it.

The idea in miniature:

```python
CONTRACT = {
  "request": {"method": "GET",
              "path": "/users/42"},
  "response": {"status": 200,
               "fields": {"id": int,
                          "email": str}},
}

def test_provider_honours_contract():
    req = CONTRACT["request"]
    exp = CONTRACT["response"]
    status, body = provider_handle(
        req["method"], req["path"])
    assert status == exp["status"]
    for f, typ in exp["fields"].items():
        assert isinstance(body[f], typ)
```

If the provider returns `{"id": 42, "email": "a@x.io", "created": "..."}`, the test passes. The extra `created` field is fine, because the consumer does not use it. If the provider renames `email`, the lookup fails with `KeyError: 'email'` in the *provider's* build, before deploy.

### Consumer-driven contracts and Pact

**Pact** is one tool for this. Consumer tests, written against a Pact mock server, generate a pact file. A **Pact Broker** (or PactFlow) stores pacts from every consumer, and providers verify the relevant consumer contracts selected by version and environment in CI. Its `can-i-deploy` check answers "is this version of Users compatible with every consumer version currently in production?"

The key property is **consumer-driven**: the contract lists only what consumers actually use. Changes outside the recorded contract can still break consumers if their real dependencies were omitted; contracts need adequate consumer tests. This turns "we can never change this API" into "we can change anything no consumer depends on, and we will know immediately if we break one".

Alternatives include **provider-driven** contracts, where the provider publishes an OpenAPI or protobuf schema and consumers are checked against it. Schemas catch type and shape changes well but say nothing about which fields any consumer actually needs.

### One contract suite for fakes and real implementations

The same idea checks your own fakes. This sketch assumes adapters exposing the same add(email) method and ValueError contract; these are not the earlier raw UserRepo or two-argument InMemoryUsers. Write behavioural tests once and run them against each adapter:

```python
@pytest.fixture(params=[InMemoryUsers,
                        SqliteUsers])
def users(request):
    return request.param()

def test_duplicate_rejected(users):
    users.add("a@x.io")
    with pytest.raises(ValueError):
        users.add("a@x.io")
```

pytest runs each test twice, once per implementation. If the fake stops enforcing uniqueness, its run fails, so hundreds of fast unit tests built on it can keep trusting it.

## Choosing what to use

| Risk | Best test |
|---|---|
| Wrong SQL or mapping | Narrow integration, real DB |
| HTTP client handling | Client vs stub server |
| API drift between services | Contract test |
| Wiring, config, UI journey | A few E2E tests |

## Key takeaways
- Integration tests check seams; prefer narrow ones that exercise one real dependency at a time.
- Isolate database tests with per-test rollback or cleanup, and test against the same engine as production (Testcontainers makes that cheap).
- Keep E2E tests to critical journeys, wait on conditions not time, own your test data and use stable selectors.
- Stubs of other services encode beliefs; contract tests (e.g. Pact) check those beliefs against the real provider before deploy.
- Run one shared contract suite against both fakes and real implementations to detect drift in the behaviours that suite covers.

## Further reading
- [Integration Test — Martin Fowler](https://martinfowler.com/bliki/IntegrationTest.html)
- [Contract Test — Martin Fowler](https://martinfowler.com/bliki/ContractTest.html)
- [Consumer-Driven Contracts — martinfowler.com](https://martinfowler.com/articles/consumerDrivenContracts.html)
- [Pact documentation](https://docs.pact.io/)
- [Testcontainers](https://testcontainers.com/)
- [Larger Testing — Software Engineering at Google, ch. 14](https://abseil.io/resources/swe-book/html/ch14.html)
- [Playwright for Python](https://playwright.dev/python/docs/intro)
- [Datatypes in SQLite](https://www.sqlite.org/datatype3.html)
