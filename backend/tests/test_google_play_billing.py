from __future__ import annotations

import base64
import json
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


class DisabledGooglePlayGateway:
    is_configured = False


class CapturingNotifier:
    def __init__(self) -> None:
        self.payment_successes: list[tuple[str, str]] = []
        self.google_play_restores: list[tuple[str, str]] = []

    async def notify_payment_success(
        self,
        client_id: str,
        plan_title: str,
        provider: str = 'YooKassa',
    ) -> None:
        self.payment_successes.append((client_id, f'{provider}: {plan_title}'))

    async def notify_google_play_subscription_restored(
        self,
        client_id: str,
        plan_title: str,
    ) -> None:
        self.google_play_restores.append((client_id, plan_title))


class ActiveGooglePlayGateway:
    is_configured = True

    def __init__(self) -> None:
        self.acknowledged: list[tuple[str, str, str]] = []
        self.status = 'SUBSCRIPTION_STATE_ACTIVE'
        self.order_id = 'GPA.1234-5678-9012-34567'

    def verify_subscription(self, *, package_name: str, product_id: str, purchase_token: str):
        return GooglePlayPurchaseInfo(
            package_name=package_name,
            product_id=product_id,
            purchase_token=purchase_token,
            status=self.status,
            order_id=self.order_id,
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

    async def test_verify_restored_google_play_purchase_notifies_restore(self) -> None:
        result = await self.service.verify_google_play_purchase(
            client_id='as_google_client',
            package_name='com.appslides.slideai',
            product_id='slide_ai_week',
            purchase_token='restored-purchase-token-1',
            restored=True,
        )

        self.assertEqual(result.status, 'paid')
        self.assertIsNotNone(result.summary.active_subscription)
        self.assertEqual(self.notifier.payment_successes, [])
        self.assertEqual(self.notifier.google_play_restores, [('as_google_client', 'Weekly')])

    async def test_google_play_rtdn_test_notification_does_not_require_gateway(self) -> None:
        service = BillingService(
            gateway=DisabledYooKassaGateway(),
            google_play_gateway=DisabledGooglePlayGateway(),
            offer_url='https://example.com/offer',
            support_username='@support',
            support_max_url='https://max.ru/example_support',
            return_url='appslides://billing/return',
            test_mode=False,
            notifier=self.notifier,
        )
        data = {'testNotification': {'version': '1.0'}}
        payload = {
            'message': {
                'messageId': 'test-rtdn',
                'data': base64.b64encode(json.dumps(data).encode('utf-8')).decode('ascii'),
            },
        }

        result = await service.handle_google_play_rtdn(payload)

        self.assertEqual(result, {'status': 'processed', 'event': 'test'})

    async def test_google_play_rtdn_renewal_refreshes_known_subscription(self) -> None:
        await self.service.verify_google_play_purchase(
            client_id='as_google_client',
            package_name='com.appslides.slideai',
            product_id='slide_ai_week',
            purchase_token='purchase-token-1',
        )
        billing_repo.decrement_subscription('as_google_client')
        self.google_gateway.order_id = 'GPA.renewal-2'
        payload = _pubsub_payload(
            notification_type=2,
            purchase_token='purchase-token-1',
            product_id='slide_ai_week',
        )

        result = await self.service.handle_google_play_rtdn(payload)

        self.assertEqual(result['status'], 'processed')
        self.assertEqual(result['event'], 'renewed')
        active = billing_repo.get_active_subscription('as_google_client')
        self.assertIsNotNone(active)
        self.assertEqual(active.remaining, 10)
        payment = billing_repo.get_payment('purchase-token-1')
        self.assertIsNotNone(payment)
        self.assertEqual(payment.payment_method_id, 'GPA.renewal-2')

    async def test_google_play_rtdn_restart_notifies_restore(self) -> None:
        await self.service.verify_google_play_purchase(
            client_id='as_google_client',
            package_name='com.appslides.slideai',
            product_id='slide_ai_week',
            purchase_token='purchase-token-1',
        )
        billing_repo.expire_subscription(
            billing_repo.get_latest_subscription('as_google_client').id
        )
        payload = _pubsub_payload(
            notification_type=7,
            purchase_token='purchase-token-1',
            product_id='slide_ai_week',
        )

        result = await self.service.handle_google_play_rtdn(payload)

        self.assertEqual(result['status'], 'processed')
        self.assertEqual(result['event'], 'restarted')
        self.assertEqual(self.notifier.google_play_restores, [('as_google_client', 'Weekly')])

    async def test_google_play_rtdn_expired_marks_known_subscription_expired(self) -> None:
        await self.service.verify_google_play_purchase(
            client_id='as_google_client',
            package_name='com.appslides.slideai',
            product_id='slide_ai_week',
            purchase_token='purchase-token-1',
        )
        self.google_gateway.status = 'SUBSCRIPTION_STATE_EXPIRED'
        payload = _pubsub_payload(
            notification_type=13,
            purchase_token='purchase-token-1',
            product_id='slide_ai_week',
        )

        result = await self.service.handle_google_play_rtdn(payload)

        self.assertEqual(result['status'], 'processed')
        self.assertEqual(result['event'], 'expired')
        self.assertIsNone(billing_repo.get_subscription_for_use('as_google_client'))


def _pubsub_payload(*, notification_type: int, purchase_token: str, product_id: str) -> dict:
    rtdn = {
        'version': '1.0',
        'packageName': 'com.appslides.slideai',
        'eventTimeMillis': '1760000000000',
        'subscriptionNotification': {
            'version': '1.0',
            'notificationType': notification_type,
            'purchaseToken': purchase_token,
            'subscriptionId': product_id,
        },
    }
    return {
        'message': {
            'messageId': 'rtdn-test-message',
            'data': base64.b64encode(json.dumps(rtdn).encode('utf-8')).decode('ascii'),
        },
        'subscription': 'projects/appslides/subscriptions/backend-rtdn',
    }


if __name__ == '__main__':
    unittest.main()
