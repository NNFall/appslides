from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.domain.billing_service import BillingService  # noqa: E402
from src.integrations.yookassa_gateway import YooKassaGatewayError  # noqa: E402
from src.repositories import billing as billing_repo  # noqa: E402
from src.repositories.storage import configure_database_path, init_storage  # noqa: E402


class StubNotifier:
    def __init__(self) -> None:
        self.auto_renew_errors: list[dict[str, object]] = []
        self.renewal_errors: list[dict[str, object]] = []

    async def notify_auto_renew_error(self, **kwargs) -> None:
        self.auto_renew_errors.append(kwargs)

    async def notify_renewal_error(self, **kwargs) -> None:
        self.renewal_errors.append(kwargs)


class RecurringUnsupportedGateway:
    is_configured = True

    def create_redirect_payment(self, **kwargs):
        raise YooKassaGatewayError(
            user_message='Автосписания YooKassa для этого магазина пока не включены. Попробуйте позже или выберите разовый тариф.',
            reason="This store can't make recurring payments. Contact the YooMoney manager to learn more",
            code='recurring_not_enabled',
        )

    def create_recurring_payment(self, **kwargs):
        raise YooKassaGatewayError(
            user_message='Автосписания YooKassa для этого магазина пока не включены. Попробуйте позже или выберите разовый тариф.',
            reason="This store can't make recurring payments. Contact the YooMoney manager to learn more",
            code='recurring_not_enabled',
        )


class BillingServiceErrorHandlingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temp_dir_context = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.temp_dir = Path(self.temp_dir_context.name)
        self.db_path = self.temp_dir / 'appslides.db'
        configure_database_path(self.db_path)
        init_storage(self.db_path)
        self.notifier = StubNotifier()
        self.service = BillingService(
            gateway=RecurringUnsupportedGateway(),
            offer_url='https://example.com/offer',
            support_username='@support',
            return_url='appslides://billing/return',
            test_mode=False,
            notifier=self.notifier,
        )

    def tearDown(self) -> None:
        self.temp_dir_context.cleanup()

    async def test_redirect_payment_returns_clean_runtime_error_for_recurring_forbidden(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            await self.service.create_payment(
                client_id='appslides_test_client',
                plan_key='week',
                context='new',
            )

        self.assertEqual(
            str(ctx.exception),
            'Автосписания YooKassa для этого магазина пока не включены. Попробуйте позже или выберите разовый тариф.',
        )
        self.assertEqual(billing_repo.list_open_payments('appslides_test_client'), [])

    async def test_auto_renew_loop_handles_gateway_error_without_crashing(self) -> None:
        subscription = billing_repo.create_subscription(
            client_id='appslides_auto_client',
            plan_key='week',
            limit=10,
            days=7,
            provider='yookassa',
            auto_renew=1,
            payment_method_id='pm_test_1',
        )
        overdue_ends_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'UPDATE billing_subscriptions SET ends_at = ? WHERE id = ?',
                (overdue_ends_at, subscription.id),
            )
            conn.commit()

        processed = await self.service.process_due_auto_renewals_once()

        self.assertEqual(processed, 1)
        self.assertEqual(len(self.notifier.auto_renew_errors), 1)
        self.assertIn(
            "This store can't make recurring payments",
            str(self.notifier.auto_renew_errors[0]['reason']),
        )


if __name__ == '__main__':
    unittest.main()
