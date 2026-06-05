from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.repositories import admin as admin_repo  # noqa: E402
from src.repositories import billing as billing_repo  # noqa: E402
from src.repositories.storage import configure_database_path, init_storage  # noqa: E402


class AdminRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir_context = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.temp_dir = Path(self.temp_dir_context.name)
        self.db_path = self.temp_dir / 'appslides.db'
        configure_database_path(self.db_path)
        init_storage(self.db_path)

    def tearDown(self) -> None:
        self.temp_dir_context.cleanup()

    def test_resolve_client_id_accepts_shortened_notification_value(self) -> None:
        client_id = 'appslides_mplk3ude_cbb30b9a29f6bcd0d3'
        billing_repo.touch_client(client_id)

        resolved, candidates = admin_repo.resolve_client_id('appslides_m…bcd0d3')

        self.assertEqual(resolved, client_id)
        self.assertEqual(candidates, [client_id])

    def test_resolve_client_id_accepts_three_dot_shortened_value(self) -> None:
        client_id = 'appslides_mplk3ude_cbb30b9a29f6bcd0d3'
        billing_repo.touch_client(client_id)

        resolved, candidates = admin_repo.resolve_client_id('appslides_m...bcd0d3')

        self.assertEqual(resolved, client_id)
        self.assertEqual(candidates, [client_id])


if __name__ == '__main__':
    unittest.main()
