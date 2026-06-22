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


class AdminStatsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir_context = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.temp_dir = Path(self.temp_dir_context.name)
        configure_database_path(self.temp_dir / 'appslides.db')
        init_storage(self.temp_dir / 'appslides.db')

    def tearDown(self) -> None:
        self.temp_dir_context.cleanup()

    def test_botstats_counts_app_store_paid_payments(self) -> None:
        billing_repo.touch_client('as_ios_client')
        billing_repo.touch_client('as_yookassa_client')
        billing_repo.create_payment(
            client_id='as_ios_client',
            provider='app_store',
            amount=199,
            currency='APPLE',
            plan_key='week',
            external_payment_id='ios_transaction_1',
            status='paid',
            payment_method_id='ios_original_transaction_1',
        )
        billing_repo.create_payment(
            client_id='as_yookassa_client',
            provider='yookassa',
            amount=499,
            currency='RUB',
            plan_key='month',
            external_payment_id='yookassa_payment_1',
            status='paid',
        )

        stats = admin_repo.get_bot_stats_full()

        self.assertEqual(stats['paid_payments'], 2)
        self.assertEqual(stats['paid_users'], 2)
        self.assertEqual(stats['revenue_rub'], 698)


if __name__ == '__main__':
    unittest.main()
