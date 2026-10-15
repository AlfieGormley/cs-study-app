---
id: test-database-isolation
sourceLesson: test-integration-e2e
title: Test database seams with realistic isolation
level: intermediate
minutes: 5
summary: Narrow integration tests exercise one real boundary rather than an entire service estate.
---

Assume `import sqlite3` and `import pytest`. The repository and fixture code below belong in the same test module.

Unit tests tell you each piece works on its own. They cannot tell you whether the pieces fit. Your SQL might be wrong for the real database, your JSON field might be called `email` while the other service sends `mail`, and your config might point at the wrong queue. Those bugs live at the **seams**, and you need tests that exercise the seams.

## Integration tests: narrow and broad

"Integration test" means different things to different people. Martin Fowler separates two kinds:

- **Narrow** integration tests exercise the code that talks to one external thing (your repository class against a real database, your HTTP client against a local server), with everything else doubled or absent.
- **Broad** integration tests bring up many real services together and test through all of them.

Narrow tests often fit every-commit feedback and make a boundary failure easier to localise, although execution duration depends on the dependency. Broad tests overlap with end-to-end tests and often cost more to run and diagnose. Prefer a narrow check when it covers the risk; broad checks still serve whole-system risks.

## Testing against a real database

The classic integration test checks your data-access code against a real database engine.

```python
class UserRepo:
    def __init__(self, conn):
        self.conn = conn

    def add(self, email):
        # Parameters keep data out of SQL.
        cur = self.conn.execute(
            "INSERT INTO users(email) "
            "VALUES (?)", (email,))
        # SQLite reports the inserted row
        # id.
        return cur.lastrowid

    def by_email(self, email):
        row = self.conn.execute(
            "SELECT id FROM users "
            "WHERE email = ?",
            (email,)).fetchone()
        # Missing email is represented by
        # None.
        return row[0] if row else None
```

### Keep tests isolated with transaction rollback

Creating a fresh database per test can be slow when setup is expensive. A standard pattern is one connection for the whole module (or session) plus a transaction per test that is undone afterwards with a **transaction rollback**:

```python
@pytest.fixture(scope="module")
def conn():
    c = sqlite3.connect(":memory:")
    c.execute(
        "CREATE TABLE users ("
        "id INTEGER PRIMARY KEY,"
        "email TEXT UNIQUE NOT NULL)")
    # Pause setup; resume cleanup after use.
    yield c
    # Release the connection after the test.
    c.close()

@pytest.fixture
def repo(conn):
    yield UserRepo(conn)
    # Undo changes that were not committed.
    conn.rollback()  # undo this test
```

```python
def test_add_then_find(repo):
    # Read back the id assigned by SQLite.
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
> If the code under test calls `commit()` itself, the transaction rollback cannot undo it. Neither can it undo side effects outside the database (files, queues, emails). Code that manages its own transactions needs explicit cleanup, such as truncating tables after each test.

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
    # This needs a running Docker engine.
    with PostgresContainer(
            "postgres:16") as pg:
        yield pg.get_connection_url()
```

Container startup can take seconds or longer, especially when an image must be downloaded, so consider doing it once per session and isolate tests with transactions or table truncation.

## Key takeaways
- Narrow integration tests exercise one real boundary rather than an entire service estate.
- Per-test rollback isolates uncommitted database changes, but cannot undo an outer commit or outside side effects.
- Use the production engine to catch dialect and type differences.

## Further reading
- [Integration Test — Martin Fowler](https://martinfowler.com/bliki/IntegrationTest.html)
- [Testcontainers](https://testcontainers.com/)
- [Larger Testing — Software Engineering at Google, ch. 14](https://abseil.io/resources/swe-book/html/ch14.html)
- [Datatypes in SQLite](https://www.sqlite.org/datatype3.html)
