from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.domain.billing_service import BillingService  # noqa: E402
from src.integrations.google_play_gateway import GooglePlayPurchaseInfo  # noqa: E402
from src.repositories import billing as billing_repo  # noqa: E402
from src.repositories.storage import configure_database_path, init_storage  # noqa: E402


class DisabledYooKassaGateway:
    is_configured = False


class CapturingNotifier:
    def __init__(self) -> None:
        self.payment_successes: list[tuple[str, str]] = []

    async def notify_payment_success(
        self,
        client_id: str,
        plan_title: str,
        provider: str = 'YooKassa',
    ) -> None:
        self.payment_successes.append((client_id, f'{provider}: {plan_title}'))


class ActiveGooglePlayGateway:
    is_configured = True

    def __init__(self) -> None:
        self.acknowledged: list[tuple[str, str, str]] = []

    def verify_subscription(self, *, package_name: str, product_id: str, purchase_token: str):
        return GooglePlayPurchaseInfo(
            package_name=package_name,
            product_id=product_id,
            purchase_token=purchase_token,
            status='SUBSCRIPTION_STATE_ACTIVE',
            order_id='GPA.1234-5678-9012-34567',
            expiry_time='2026-06-23T00:00:00Z',
            auto_renewing=True,
        )

    def acknowledge_subscription(self, *, package_name: str, product_id: str, purchase_token: str) -> None:
        self.acknowledged.append((package_name, product_id, purchase_token))


class GooglePlayBillingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temp_dir_context = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.temp_dir = Path(self.temp_dir_context.name)
        configure_database_path(self.temp_dir / 'appslides.db')
        init_storage(self.temp_dir / 'appslides.db')
        self.notifier = CapturingNotifier()
        self.google_gateway = ActiveGooglePlayGateway()
        self.service = BillingService(
            gateway=DisabledYooKassaGateway(),
            google_play_gateway=self.google_gateway,
            offer_url='https://example.com/offer',
            support_username='@support',
            support_max_url='https://max.ru/example_support',
            return_url='appslides://billing/return',
            test_mode=False,
            notifier=self.notifier,
        )

    def tearDown(self) -> None:
        self.temp_dir_context.cleanup()

    async def test_verify_google_play_purchase_grants_subscription(self) -> None:
        result = await self.service.verify_google_play_purchase(
            client_id='as_google_client',
            package_name='com.appslides.slideai',
            product_id='slide_ai_week',
            purchase_token='purchase-token-1',
        )

        self.assertEqual(result.status, 'paid')
        self.assertEqual(result.plan.key, 'week')
        self.assertIsNotNone(result.summary.active_subscription)
        self.assertEqual(result.summary.active_subscription.provider, 'google_play')
        self.assertEqual(result.summary.active_subscription.remaining, 10)
        self.assertEqual(self.google_gateway.acknowledged, [
            ('com.appslides.slideai', 'slide_ai_week', 'purchase-token-1'),
        ])
        self.assertEqual(len(self.notifier.payment_successes), 1)

        payment = billing_repo.get_payment('purchase-token-1')
        self.assertIsNotNone(payment)
        self.assertEqual(payment.provider, 'google_play')
        self.assertEqual(payment.status, 'paid')


if __name__ == '__main__':
    unittest.main()
