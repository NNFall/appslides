from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.domain.billing_service import BillingService  # noqa: E402
from src.integrations.app_store_gateway import AppStoreGateway  # noqa: E402
from src.repositories import billing as billing_repo  # noqa: E402
from src.repositories.storage import configure_database_path, init_storage  # noqa: E402


class DisabledYooKassaGateway:
    is_configured = False


class DisabledGooglePlayGateway:
    is_configured = False


class CapturingNotifier:
    def __init__(self) -> None:
        self.payment_successes: list[tuple[str, str, str]] = []

    async def notify_payment_success(
        self,
        client_id: str,
        plan_title: str,
        provider: str = 'YooKassa',
    ) -> None:
        self.payment_successes.append((client_id, plan_title, provider))


class AppStoreBillingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temp_dir_context = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.temp_dir = Path(self.temp_dir_context.name)
        configure_database_path(self.temp_dir / 'appslides.db')
        init_storage(self.temp_dir / 'appslides.db')
        self.notifier = CapturingNotifier()
        self.gateway = AppStoreGateway(
            bundle_id='com.appslides.slideai',
            app_apple_id='1234567890',
            issuer_id='issuer-test',
            key_id='key-test',
            private_key='',
            environment='sandbox',
            test_mode=True,
        )
        self.service = BillingService(
            gateway=DisabledYooKassaGateway(),
            google_play_gateway=DisabledGooglePlayGateway(),
            app_store_gateway=self.gateway,
            offer_url='https://example.com/offer',
            support_username='@support',
            support_max_url='https://max.ru/example_support',
            return_url='appslides://billing/return',
            test_mode=False,
            notifier=self.notifier,
        )

    def tearDown(self) -> None:
        self.temp_dir_context.cleanup()

    async def test_verify_app_store_purchase_grants_subscription(self) -> None:
        result = await self.service.verify_app_store_purchase(
            client_id='as_ios_client',
            product_id='slide_ai_week',
            transaction_id='200000000000001',
            verification_data='test_app_store_receipt_1',
            verification_source='app_store',
            local_verification_data='test_local_receipt_1',
        )

        self.assertEqual(result.status, 'paid')
        self.assertEqual(result.plan.key, 'week')
        self.assertIsNotNone(result.summary.active_subscription)
        self.assertEqual(result.summary.active_subscription.provider, 'app_store')
        self.assertEqual(result.summary.active_subscription.remaining, 10)
        self.assertEqual(self.notifier.payment_successes, [
            ('as_ios_client', 'Weekly', 'App Store'),
        ])

        payment = billing_repo.get_payment('200000000000001')
        self.assertIsNotNone(payment)
        self.assertEqual(payment.provider, 'app_store')
        self.assertEqual(payment.status, 'paid')

    async def test_restore_app_store_purchase_reuses_original_transaction(self) -> None:
        result = await self.service.restore_app_store_purchase(
            client_id='as_ios_client',
            product_id='slide_ai_month',
            original_transaction_id='200000000000002',
        )

        self.assertEqual(result.status, 'paid')
        self.assertEqual(result.plan.key, 'month')
        self.assertEqual(result.summary.active_subscription.provider, 'app_store')

    async def test_unconfigured_app_store_gateway_fails_cleanly(self) -> None:
        service = BillingService(
            gateway=DisabledYooKassaGateway(),
            google_play_gateway=DisabledGooglePlayGateway(),
            app_store_gateway=AppStoreGateway(
                bundle_id='',
                app_apple_id='',
                issuer_id='',
                key_id='',
                private_key='',
                environment='sandbox',
                test_mode=False,
            ),
            offer_url='https://example.com/offer',
            support_username='@support',
            support_max_url='https://max.ru/example_support',
            return_url='appslides://billing/return',
            test_mode=False,
            notifier=self.notifier,
        )

        with self.assertRaises(RuntimeError) as ctx:
            await service.verify_app_store_purchase(
                client_id='as_ios_client',
                product_id='slide_ai_week',
                transaction_id='200000000000001',
                verification_data='receipt',
                verification_source='app_store',
                local_verification_data=None,
            )

        self.assertEqual(str(ctx.exception), 'App Store Billing is not configured')


if __name__ == '__main__':
    unittest.main()
