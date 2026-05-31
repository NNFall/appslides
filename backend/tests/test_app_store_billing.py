from __future__ import annotations

import base64
import json
import sys
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
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

    async def test_app_store_notification_renewal_refreshes_known_subscription(self) -> None:
        await self.service.verify_app_store_purchase(
            client_id='as_ios_client',
            product_id='slide_ai_week',
            transaction_id='200000000000001',
            verification_data='test_app_store_receipt_1',
            verification_source='app_store',
            local_verification_data='test_local_receipt_1',
        )
        billing_repo.decrement_subscription('as_ios_client')
        signed_payload = _app_store_notification_payload(
            notification_type='DID_RENEW',
            product_id='slide_ai_week',
            transaction_id='200000000000003',
            original_transaction_id='200000000000001',
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )

        result = await self.service.handle_app_store_notification(signed_payload)

        self.assertEqual(result['status'], 'processed')
        self.assertEqual(result['event'], 'DID_RENEW')
        self.assertEqual(result['client_id'], 'as_ios_client')
        active = billing_repo.get_active_subscription('as_ios_client')
        self.assertIsNotNone(active)
        self.assertEqual(active.remaining, 10)
        payment = billing_repo.get_payment('200000000000003')
        self.assertIsNotNone(payment)
        self.assertEqual(payment.provider, 'app_store')
        self.assertEqual(payment.status, 'paid')
        self.assertEqual(payment.payment_method_id, '200000000000001')

    async def test_app_store_notification_expired_marks_known_subscription_expired(self) -> None:
        await self.service.verify_app_store_purchase(
            client_id='as_ios_client',
            product_id='slide_ai_week',
            transaction_id='200000000000001',
            verification_data='test_app_store_receipt_1',
            verification_source='app_store',
            local_verification_data='test_local_receipt_1',
        )
        signed_payload = _app_store_notification_payload(
            notification_type='EXPIRED',
            product_id='slide_ai_week',
            transaction_id='200000000000004',
            original_transaction_id='200000000000001',
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )

        result = await self.service.handle_app_store_notification(signed_payload)

        self.assertEqual(result['status'], 'processed')
        self.assertEqual(result['event'], 'EXPIRED')
        self.assertEqual(result['client_id'], 'as_ios_client')
        self.assertIsNone(billing_repo.get_subscription_for_use('as_ios_client'))

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


def _app_store_notification_payload(
    *,
    notification_type: str,
    product_id: str,
    transaction_id: str,
    original_transaction_id: str,
    expires_at: datetime,
) -> str:
    transaction = _fake_jws(
        {
            'productId': product_id,
            'transactionId': transaction_id,
            'originalTransactionId': original_transaction_id,
            'environment': 'Sandbox',
            'expiresDate': int(expires_at.timestamp() * 1000),
        }
    )
    return _fake_jws(
        {
            'notificationType': notification_type,
            'subtype': '',
            'data': {
                'signedTransactionInfo': transaction,
            },
        }
    )


def _fake_jws(payload: dict) -> str:
    header = {'alg': 'ES256', 'kid': 'test-key'}
    return '.'.join(
        [
            _b64url_json(header),
            _b64url_json(payload),
            'signature',
        ]
    )


def _b64url_json(data: dict) -> str:
    raw = json.dumps(data, separators=(',', ':')).encode('utf-8')
    return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')


if __name__ == '__main__':
    unittest.main()
