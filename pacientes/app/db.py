import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row


@contextmanager
def connection():
    with psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row) as conn:
        yield conn


def query_one(statement, params=()):
    with connection() as conn:
        return conn.execute(statement, params).fetchone()


def query_all(statement, params=()):
    with connection() as conn:
        return conn.execute(statement, params).fetchall()
