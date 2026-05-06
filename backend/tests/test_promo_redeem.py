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


class PromoRedeemRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir_context = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.temp_dir = Path(self.temp_dir_context.name)
        self.db_path = self.temp_dir / 'appslides.db'
        configure_database_path(self.db_path)
        init_storage(self.db_path)

    def tearDown(self) -> None:
        self.temp_dir_context.cleanup()

    def test_redeem_promo_adds_tokens_and_consumes_use(self) -> None:
        admin_repo.create_promo_code('promo1234', 10, 1)

        result = admin_repo.redeem_promo_code(
            client_id='appslides_test_client',
            code='promo1234',
        )

        self.assertEqual(result.code, 'promo1234')
        self.assertEqual(result.tokens, 10)
        self.assertEqual(result.used, 1)
        self.assertEqual(result.max_uses, 1)

        subscription = billing_repo.get_subscription_for_use('appslides_test_client')
        self.assertIsNotNone(subscription)
        self.assertEqual(subscription.remaining, 10)

    def test_same_client_cannot_redeem_twice(self) -> None:
        admin_repo.create_promo_code('promo5678', 5, 2)
        admin_repo.redeem_promo_code(
            client_id='appslides_test_client',
            code='promo5678',
        )

        with self.assertRaises(ValueError) as ctx:
            admin_repo.redeem_promo_code(
                client_id='appslides_test_client',
                code='promo5678',
            )

        self.assertIn('уже активирован', str(ctx.exception))

    def test_promo_becomes_inactive_after_limit(self) -> None:
        admin_repo.create_promo_code('promo9999', 3, 1)
        admin_repo.redeem_promo_code(
            client_id='appslides_client_a',
            code='promo9999',
        )

        with self.assertRaises(ValueError) as ctx:
            admin_repo.redeem_promo_code(
                client_id='appslides_client_b',
                code='promo9999',
            )

        self.assertIn('исчерпан', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
