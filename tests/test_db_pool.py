import os
import sys
import unittest
from unittest.mock import patch

import psycopg2.pool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import db  # noqa: E402


class FakePool:
    def __init__(self, failures_before_success=0):
        self.failures_before_success = failures_before_success
        self.getconn_calls = 0
        self.returned_connections = []
        self.connection = object()

    def getconn(self):
        self.getconn_calls += 1

        if self.getconn_calls <= self.failures_before_success:
            raise psycopg2.pool.PoolError("connection pool exhausted")

        return self.connection

    def putconn(self, connection):
        self.returned_connections.append(connection)


class DbConnectionPoolTests(unittest.TestCase):
    def setUp(self):
        self.previous_pool = db._pool
        self.previous_wait = db.DB_POOL_WAIT_SECONDS
        self.previous_interval = db.DB_POOL_RETRY_INTERVAL_SECONDS

    def tearDown(self):
        db._pool = self.previous_pool
        db.DB_POOL_WAIT_SECONDS = self.previous_wait
        db.DB_POOL_RETRY_INTERVAL_SECONDS = self.previous_interval

    def test_reintenta_cuando_el_pool_esta_temporalmente_lleno(self):
        pool = FakePool(failures_before_success=1)

        db._pool = pool
        db.DB_POOL_WAIT_SECONDS = 1.0
        db.DB_POOL_RETRY_INTERVAL_SECONDS = 0.0

        with (
            patch.object(db.time, "monotonic", side_effect=[10.0, 10.0]),
            patch.object(db.time, "sleep") as sleep,
        ):
            with db.conexion() as conn:
                self.assertIs(conn, pool.connection)

        self.assertEqual(pool.getconn_calls, 2)
        self.assertEqual(pool.returned_connections, [pool.connection])
        sleep.assert_called_once_with(0.0)

    def test_falla_solo_despues_de_superar_el_tiempo_de_espera(self):
        pool = FakePool(failures_before_success=100)

        db._pool = pool
        db.DB_POOL_WAIT_SECONDS = 1.0
        db.DB_POOL_RETRY_INTERVAL_SECONDS = 0.02

        with (
            patch.object(db.time, "monotonic", side_effect=[10.0, 11.1]),
            patch.object(db.time, "sleep") as sleep,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "Connection pool exhausted after waiting 1.0s",
            ):
                db.conexion().__enter__()

        self.assertEqual(pool.getconn_calls, 1)
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
