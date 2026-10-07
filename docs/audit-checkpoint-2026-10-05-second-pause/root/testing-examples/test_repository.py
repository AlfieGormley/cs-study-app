import sqlite3
import pytest
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
