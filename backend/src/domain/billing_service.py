from __future__ import annotations

import asyncio
import base64
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Literal

from src.domain.billing_plans import (
    BillingPlan,
    get_plan_by_app_store_product_id,
    get_plan,
    get_plan_by_google_play_product_id,
    list_plans,
)
from src.integrations.admin_notifier import AdminNotifier
from src.integrations.app_store_gateway import AppStoreGateway, AppStoreGatewayError
from src.integrations.google_play_gateway import GooglePlayGateway, GooglePlayGatewayError
from src.integrations.yookassa_gateway import (
    YooKassaGateway,
    YooKassaGatewayError,
    YooKassaPaymentInfo,
)
from src.repositories import billing as billing_repo


PaymentStatus = Literal['pending', 'paid', 'canceled', 'failed', 'succeeded']

GOOGLE_PLAY_RTDN_EVENTS = {
    1: 'recovered',
    2: 'renewed',
    3: 'canceled',
    4: 'purchased',
    5: 'on_hold',
    6: 'grace_period',
    7: 'restarted',
    10: 'paused',
    12: 'revoked',
    13: 'expired',
}
GOOGLE_PLAY_ACTIVE_NOTIFICATION_TYPES = {1, 2, 4, 6, 7}
GOOGLE_PLAY_CANCEL_NOTIFICATION_TYPES = {3}
GOOGLE_PLAY_EXPIRE_NOTIFICATION_TYPES = {5, 10, 12, 13}
APP_STORE_ACTIVE_NOTIFICATION_TYPES = {'SUBSCRIBED', 'DID_RENEW', 'DID_RECOVER'}
APP_STORE_EXPIRE_NOTIFICATION_TYPES = {'EXPIRED', 'REFUND', 'REVOKE'}


@dataclass(frozen=True)
class BillingSummary:
    client_id: str
    plans: list[BillingPlan]
    support_username: str
    support_max_url: str
    offer_url: str
    privacy_policy_url: str
    terms_of_use_url: str
    test_mode: bool
    active_subscription: billing_repo.StoredSubscription | None
    latest_valid_subscription: billing_repo.StoredSubscription | None


@dataclass(frozen=True)
class BillingPaymentResult:
    payment_id: str
    plan: BillingPlan
    status: str
    confirmation_url: str | None
    test_mode: bool
    summary: BillingSummary


class BillingService:
    def __init__(
        self,
        *,
        gateway: YooKassaGateway,
        google_play_gateway: GooglePlayGateway,
        app_store_gateway: AppStoreGateway | None = None,
        offer_url: str,
        support_username: str,
        support_max_url: str,
        return_url: str,
        test_mode: bool,
        notifier: AdminNotifier,
        privacy_policy_url: str = 'https://dimonk95.github.io/slideaiappgoogle',
        terms_of_use_url: str = 'https://www.apple.com/legal/internet-services/itunes/dev/stdeula/',
    ) -> None:
        self._gateway = gateway
        self._google_play_gateway = google_play_gateway
        self._app_store_gateway = app_store_gateway
        self._offer_url = offer_url
        self._support_username = support_username
        self._support_max_url = support_max_url
        self._return_url = return_url
        self._test_mode = test_mode
        self._notifier = notifier
        self._privacy_policy_url = privacy_policy_url
        self._terms_of_use_url = terms_of_use_url

    @property
    def is_configured(self) -> bool:
        return self._gateway.is_configured

    async def get_summary(self, client_id: str) -> BillingSummary:
        billing_repo.touch_client(client_id)
        await self._sync_open_payments(client_id)
        active = billing_repo.get_active_subscription(client_id)
        latest = active or billing_repo.get_latest_valid_subscription(client_id)
        return BillingSummary(
            client_id=client_id,
            plans=list_plans(),
            support_username=self._support_username,
            support_max_url=self._support_max_url,
            offer_url=self._offer_url,
            privacy_policy_url=self._privacy_policy_url,
            terms_of_use_url=self._terms_of_use_url,
            test_mode=self._test_mode,
            active_subscription=active,
            latest_valid_subscription=latest,
        )

    async def can_start_generation(self, client_id: str) -> bool:
        billing_repo.touch_client(client_id)
        await self._sync_open_payments(client_id)
        return billing_repo.get_subscription_for_use(client_id) is not None

    async def consume_generation(self, client_id: str) -> bool:
        return billing_repo.decrement_subscription(client_id)

    async def create_payment(
        self,
        *,
        client_id: str,
        plan_key: str,
        context: str = 'new',
    ) -> BillingPaymentResult:
        if not self.is_configured:
            raise RuntimeError('YooKassa is not configured')

        billing_repo.touch_client(client_id)
        plan = get_plan(plan_key)

        if context == 'renew' and plan.recurring:
            active = billing_repo.get_active_subscription(client_id)
            if active and active.provider == 'yookassa' and active.payment_method_id:
                try:
                    payment = await asyncio.to_thread(
                        self._gateway.create_recurring_payment,
                        plan=plan,
                        client_id=client_id,
                        payment_method_id=active.payment_method_id,
                    )
                except YooKassaGatewayError as exc:
                    await self._notifier.notify_renewal_error(
                        client_id=client_id,
                        plan_key=plan.key,
                        plan_title=plan.title,
                        tokens=plan.limit,
                        amount_rub=plan.price_rub,
                        status='error',
                        payment_id='-',
                        reason=exc.reason,
                    )
                    raise RuntimeError(exc.user_message) from exc
                except Exception as exc:  # noqa: BLE001
                    await self._notifier.notify_renewal_error(
                        client_id=client_id,
                        plan_key=plan.key,
                        plan_title=plan.title,
                        tokens=plan.limit,
                        amount_rub=plan.price_rub,
                        status='error',
                        payment_id='-',
                        reason=str(exc),
                    )
                    raise
                billing_repo.create_payment(
                    client_id=client_id,
                    provider='yookassa',
                    amount=plan.price_rub,
                    currency='RUB',
                    plan_key=plan.key,
                    external_payment_id=payment.payment_id,
                    status='paid' if payment.status == 'succeeded' else payment.status,
                    payment_method_id=payment.payment_method_id,
                    confirmation_url=payment.confirmation_url,
                )
                if payment.status == 'succeeded':
                    billing_repo.renew_subscription(active.id, plan.key, plan.limit, plan.days)
                    await self._notifier.notify_renewal_success(
                        client_id=client_id,
                        plan_key=plan.key,
                        plan_title=plan.title,
                        tokens=plan.limit,
                        amount_rub=plan.price_rub,
                        status=payment.status,
                        payment_id=payment.payment_id,
                    )
                else:
                    await self._notifier.notify_renewal_error(
                        client_id=client_id,
                        plan_key=plan.key,
                        plan_title=plan.title,
                        tokens=plan.limit,
                        amount_rub=plan.price_rub,
                        status=payment.status or 'unknown',
                        payment_id=payment.payment_id,
                        reason=f'Payment did not succeed, status={payment.status or "unknown"}',
                    )
                summary = await self.get_summary(client_id)
                return BillingPaymentResult(
                    payment_id=payment.payment_id,
                    plan=plan,
                    status='paid' if payment.status == 'succeeded' else payment.status,
                    confirmation_url=payment.confirmation_url,
                    test_mode=self._test_mode,
                    summary=summary,
                )

        try:
            payment = await asyncio.to_thread(
                self._gateway.create_redirect_payment,
                plan=plan,
                client_id=client_id,
                return_url=self._return_url or self._offer_url,
                save_payment_method=plan.recurring,
            )
        except YooKassaGatewayError as exc:
            raise RuntimeError(exc.user_message) from exc
        billing_repo.create_payment(
            client_id=client_id,
            provider='yookassa',
            amount=plan.price_rub,
            currency='RUB',
            plan_key=plan.key,
            external_payment_id=payment.payment_id,
            status='pending',
            confirmation_url=payment.confirmation_url,
        )
        summary = await self.get_summary(client_id)
        return BillingPaymentResult(
            payment_id=payment.payment_id,
            plan=plan,
            status='pending',
            confirmation_url=payment.confirmation_url,
            test_mode=self._test_mode,
            summary=summary,
        )

    async def sync_payment(self, *, client_id: str, payment_id: str) -> BillingPaymentResult:
        payment = billing_repo.get_payment(payment_id)
        if payment is None or payment.client_id != client_id:
            raise LookupError('Payment not found')

        plan = get_plan(payment.plan_key)
        if payment.status not in {'pending', 'waiting_for_capture'}:
            summary = await self.get_summary(client_id)
            return BillingPaymentResult(
                payment_id=payment.external_payment_id,
                plan=plan,
                status=payment.status,
                confirmation_url=payment.confirmation_url,
                test_mode=self._test_mode,
                summary=summary,
            )

        remote = await asyncio.to_thread(self._gateway.get_payment, payment.external_payment_id)
        if remote is None:
            summary = await self.get_summary(client_id)
            return BillingPaymentResult(
                payment_id=payment.external_payment_id,
                plan=plan,
                status='pending',
                confirmation_url=payment.confirmation_url,
                test_mode=self._test_mode,
                summary=summary,
            )

        status = await self._apply_remote_payment(client_id, payment.plan_key, remote)
        stored = billing_repo.get_payment(payment.external_payment_id) or payment
        summary = await self.get_summary(client_id)
        return BillingPaymentResult(
            payment_id=stored.external_payment_id,
            plan=plan,
            status=status,
            confirmation_url=stored.confirmation_url,
            test_mode=self._test_mode,
            summary=summary,
        )

    async def verify_google_play_purchase(
        self,
        *,
        client_id: str,
        package_name: str,
        product_id: str,
        purchase_token: str,
    ) -> BillingPaymentResult:
        if not self._google_play_gateway.is_configured:
            raise RuntimeError('Google Play Billing is not configured')

        billing_repo.touch_client(client_id)
        plan = get_plan_by_google_play_product_id(product_id)
        existing_payment = billing_repo.get_payment(purchase_token)

        if existing_payment is not None and existing_payment.status == 'paid':
            if billing_repo.get_subscription_for_use(client_id) is None:
                billing_repo.create_subscription(
                    client_id=client_id,
                    plan_key=plan.key,
                    limit=plan.limit,
                    days=plan.days,
                    provider='google_play',
                    auto_renew=1 if plan.recurring else 0,
                    payment_method_id=existing_payment.payment_method_id,
                )
            summary = await self.get_summary(client_id)
            return BillingPaymentResult(
                payment_id=purchase_token,
                plan=plan,
                status='paid',
                confirmation_url=None,
                test_mode=False,
                summary=summary,
            )

        try:
            purchase = await asyncio.to_thread(
                self._google_play_gateway.verify_subscription,
                package_name=package_name,
                product_id=product_id,
                purchase_token=purchase_token,
            )
        except GooglePlayGatewayError as exc:
            raise RuntimeError(exc.reason) from exc

        status = 'paid' if purchase.is_active else 'failed'
        if existing_payment is None:
            billing_repo.create_payment(
                client_id=client_id,
                provider='google_play',
                amount=plan.price_rub,
                currency='GOOGLE',
                plan_key=plan.key,
                external_payment_id=purchase_token,
                status=status,
                payment_method_id=purchase.order_id,
                confirmation_url=None,
            )
        else:
            billing_repo.update_payment_status(
                purchase_token,
                status,
                payment_method_id=purchase.order_id,
            )

        if purchase.is_active:
            billing_repo.create_subscription(
                client_id=client_id,
                plan_key=plan.key,
                limit=plan.limit,
                days=plan.days,
                provider='google_play',
                auto_renew=1 if plan.recurring else 0,
                payment_method_id=purchase.order_id,
            )
            try:
                await asyncio.to_thread(
                    self._google_play_gateway.acknowledge_subscription,
                    package_name=package_name,
                    product_id=product_id,
                    purchase_token=purchase_token,
                )
            except GooglePlayGatewayError:
                # Do not revoke entitlement after a successful verification; log/alerting can be added later.
                pass
            await self._notifier.notify_payment_success(client_id, plan.title, provider='Google Play')

        summary = await self.get_summary(client_id)
        return BillingPaymentResult(
            payment_id=purchase_token,
            plan=plan,
            status=status,
            confirmation_url=None,
            test_mode=False,
            summary=summary,
        )

    async def handle_google_play_rtdn(self, payload: dict[str, Any]) -> dict[str, Any]:
        message = self._decode_google_play_rtdn_payload(payload)
        if isinstance(message.get('testNotification'), dict):
            return {'status': 'processed', 'event': 'test'}

        if not self._google_play_gateway.is_configured:
            raise RuntimeError('Google Play Billing is not configured')

        notification = message.get('subscriptionNotification')
        if not isinstance(notification, dict):
            return {'status': 'ignored', 'reason': 'unsupported_message'}

        notification_type = int(notification.get('notificationType') or 0)
        purchase_token = str(notification.get('purchaseToken') or '').strip()
        product_id = str(notification.get('subscriptionId') or '').strip()
        package_name = str(message.get('packageName') or self._google_play_gateway.package_name).strip()
        if not purchase_token or not product_id or not package_name:
            raise ValueError('Invalid Google Play RTDN payload')

        event = GOOGLE_PLAY_RTDN_EVENTS.get(notification_type, f'notification_{notification_type}')
        existing_payment = billing_repo.get_payment(purchase_token)
        if existing_payment is None:
            return {
                'status': 'ignored',
                'event': event,
                'reason': 'unknown_purchase_token',
                'purchase_token': purchase_token,
            }

        plan = get_plan_by_google_play_product_id(product_id)
        client_id = existing_payment.client_id

        if notification_type in GOOGLE_PLAY_CANCEL_NOTIFICATION_TYPES:
            billing_repo.cancel_subscription(client_id)
            return {'status': 'processed', 'event': event, 'client_id': client_id}

        if notification_type in GOOGLE_PLAY_EXPIRE_NOTIFICATION_TYPES:
            self._expire_latest_google_play_subscription(client_id)
            billing_repo.update_payment_status(purchase_token, 'canceled')
            return {'status': 'processed', 'event': event, 'client_id': client_id}

        try:
            purchase = await asyncio.to_thread(
                self._google_play_gateway.verify_subscription,
                package_name=package_name,
                product_id=product_id,
                purchase_token=purchase_token,
            )
        except GooglePlayGatewayError as exc:
            raise RuntimeError(exc.reason) from exc

        if not purchase.is_active:
            self._expire_latest_google_play_subscription(client_id)
            billing_repo.update_payment_status(
                purchase_token,
                'failed',
                payment_method_id=purchase.order_id,
            )
            return {'status': 'processed', 'event': event, 'client_id': client_id}

        current_order_id = existing_payment.payment_method_id
        is_new_google_order = bool(purchase.order_id and purchase.order_id != current_order_id)
        should_grant = (
            notification_type in GOOGLE_PLAY_ACTIVE_NOTIFICATION_TYPES
            and (
                billing_repo.get_subscription_for_use(client_id) is None
                or (notification_type == 2 and is_new_google_order)
            )
        )
        billing_repo.update_payment_status(
            purchase_token,
            'paid',
            payment_method_id=purchase.order_id,
        )
        if should_grant:
            billing_repo.create_subscription(
                client_id=client_id,
                plan_key=plan.key,
                limit=plan.limit,
                days=plan.days,
                provider='google_play',
                auto_renew=1 if plan.recurring and purchase.auto_renewing else 0,
                payment_method_id=purchase.order_id,
            )
            if notification_type == 2:
                await self._notifier.notify_payment_success(client_id, plan.title, provider='Google Play renewal')

        return {'status': 'processed', 'event': event, 'client_id': client_id}

    async def verify_app_store_purchase(
        self,
        *,
        client_id: str,
        product_id: str,
        transaction_id: str | None,
        verification_data: str,
        verification_source: str,
        local_verification_data: str | None,
    ) -> BillingPaymentResult:
        gateway = self._require_app_store_gateway()
        billing_repo.touch_client(client_id)
        plan = get_plan_by_app_store_product_id(product_id)
        try:
            purchase = await asyncio.to_thread(
                gateway.verify_purchase,
                product_id=product_id,
                transaction_id=transaction_id,
                verification_data=verification_data,
                verification_source=verification_source,
                local_verification_data=local_verification_data,
            )
        except AppStoreGatewayError as exc:
            raise RuntimeError(exc.reason) from exc

        self._ensure_app_store_product_matches(product_id, purchase.product_id)
        return await self._apply_app_store_purchase(client_id, plan.key, purchase)

    async def restore_app_store_purchase(
        self,
        *,
        client_id: str,
        product_id: str,
        original_transaction_id: str,
    ) -> BillingPaymentResult:
        gateway = self._require_app_store_gateway()
        billing_repo.touch_client(client_id)
        plan = get_plan_by_app_store_product_id(product_id)
        try:
            purchase = await asyncio.to_thread(
                gateway.restore_purchase,
                product_id=product_id,
                original_transaction_id=original_transaction_id,
            )
        except AppStoreGatewayError as exc:
            raise RuntimeError(exc.reason) from exc

        self._ensure_app_store_product_matches(product_id, purchase.product_id)
        return await self._apply_app_store_purchase(client_id, plan.key, purchase)

    async def handle_app_store_notification(self, signed_payload: str) -> dict[str, Any]:
        gateway = self._require_app_store_gateway()
        try:
            data = await asyncio.to_thread(gateway.decode_notification, signed_payload)
        except AppStoreGatewayError as exc:
            raise RuntimeError(exc.reason) from exc

        notification_type = str(data.get('notificationType') or 'unknown')
        subtype = str(data.get('subtype') or '')
        payload_data = data.get('data')
        if not isinstance(payload_data, dict):
            return {
                'status': 'ignored',
                'event': notification_type,
                'subtype': subtype,
                'reason': 'missing_data',
            }

        signed_transaction_info = str(payload_data.get('signedTransactionInfo') or '').strip()
        if not signed_transaction_info:
            return {
                'status': 'ignored',
                'event': notification_type,
                'subtype': subtype,
                'reason': 'missing_transaction',
            }

        try:
            purchase = gateway.purchase_from_signed_transaction(
                fallback_product_id=str(payload_data.get('productId') or ''),
                fallback_transaction_id=str(payload_data.get('transactionId') or ''),
                signed_transaction_info=signed_transaction_info,
            )
        except AppStoreGatewayError as exc:
            raise RuntimeError(exc.reason) from exc

        try:
            plan = get_plan_by_app_store_product_id(purchase.product_id)
        except ValueError:
            return {
                'status': 'ignored',
                'event': notification_type,
                'subtype': subtype,
                'reason': 'unknown_product',
                'product_id': purchase.product_id,
            }

        existing_payment = (
            billing_repo.get_payment(purchase.transaction_id)
            or billing_repo.get_payment_by_payment_method_id(purchase.original_transaction_id)
        )
        if existing_payment is None:
            await self._notifier.notify_app_store_unknown_transaction(
                event=notification_type,
                product_id=purchase.product_id,
                transaction_id=purchase.transaction_id,
                original_transaction_id=purchase.original_transaction_id,
            )
            return {
                'status': 'ignored',
                'event': notification_type,
                'subtype': subtype,
                'reason': 'unknown_original_transaction',
                'original_transaction_id': purchase.original_transaction_id,
            }

        client_id = existing_payment.client_id
        if notification_type in APP_STORE_EXPIRE_NOTIFICATION_TYPES:
            self._expire_latest_app_store_subscription(client_id)
            if billing_repo.get_payment(purchase.transaction_id) is not None:
                billing_repo.update_payment_status(purchase.transaction_id, 'canceled')
            return {
                'status': 'processed',
                'event': notification_type,
                'subtype': subtype,
                'client_id': client_id,
            }

        if notification_type in APP_STORE_ACTIVE_NOTIFICATION_TYPES:
            if purchase.is_active:
                await self._apply_app_store_purchase(client_id, plan.key, purchase)
            else:
                self._expire_latest_app_store_subscription(client_id)
                if billing_repo.get_payment(purchase.transaction_id) is not None:
                    billing_repo.update_payment_status(purchase.transaction_id, 'failed')
            return {
                'status': 'processed',
                'event': notification_type,
                'subtype': subtype,
                'client_id': client_id,
            }

        return {
            'status': 'processed',
            'event': notification_type,
            'subtype': subtype,
            'client_id': client_id,
        }

    async def cancel_subscription(self, client_id: str) -> BillingSummary:
        canceled = billing_repo.cancel_subscription(client_id)
        if canceled:
            await self._notifier.notify_subscription_canceled(client_id)
        return await self.get_summary(client_id)

    def _require_app_store_gateway(self) -> AppStoreGateway:
        if self._app_store_gateway is None or not self._app_store_gateway.is_configured:
            raise RuntimeError('App Store Billing is not configured')
        return self._app_store_gateway

    def _ensure_app_store_product_matches(self, expected_product_id: str, actual_product_id: str) -> None:
        if expected_product_id != actual_product_id:
            raise RuntimeError('App Store product id mismatch')

    async def _apply_app_store_purchase(
        self,
        client_id: str,
        plan_key: str,
        purchase,
    ) -> BillingPaymentResult:
        plan = get_plan(plan_key)
        external_id = purchase.transaction_id or self._fallback_app_store_payment_id(
            purchase.original_transaction_id,
        )
        existing_payment = billing_repo.get_payment(external_id)

        status = 'paid' if purchase.is_active else 'failed'
        if existing_payment is None:
            billing_repo.create_payment(
                client_id=client_id,
                provider='app_store',
                amount=plan.price_rub,
                currency='APPLE',
                plan_key=plan.key,
                external_payment_id=external_id,
                status=status,
                payment_method_id=purchase.original_transaction_id,
                confirmation_url=None,
            )
        else:
            billing_repo.update_payment_status(
                external_id,
                status,
                payment_method_id=purchase.original_transaction_id,
            )

        if (
            purchase.is_active
            and existing_payment is not None
            and existing_payment.status == 'paid'
            and existing_payment.client_id == client_id
        ):
            summary = await self.get_summary(client_id)
            return BillingPaymentResult(
                payment_id=external_id,
                plan=plan,
                status=status,
                confirmation_url=None,
                test_mode=False,
                summary=summary,
            )

        if purchase.is_active:
            billing_repo.create_subscription(
                client_id=client_id,
                plan_key=plan.key,
                limit=plan.limit,
                days=plan.days,
                provider='app_store',
                auto_renew=1 if plan.recurring and purchase.auto_renewing else 0,
                payment_method_id=purchase.original_transaction_id,
            )
            if existing_payment is None or existing_payment.status != 'paid':
                await self._notifier.notify_payment_success(client_id, plan.title, provider='App Store')

        summary = await self.get_summary(client_id)
        return BillingPaymentResult(
            payment_id=external_id,
            plan=plan,
            status=status,
            confirmation_url=None,
            test_mode=False,
            summary=summary,
        )

    def _fallback_app_store_payment_id(self, value: str) -> str:
        digest = hashlib.sha256(value.encode('utf-8')).hexdigest()[:32]
        return f'appstore_{digest}'

    def _expire_latest_google_play_subscription(self, client_id: str) -> None:
        subscription = billing_repo.get_latest_subscription(client_id)
        if subscription is None or subscription.provider != 'google_play':
            return
        billing_repo.expire_subscription(subscription.id)

    def _expire_latest_app_store_subscription(self, client_id: str) -> None:
        subscription = billing_repo.get_latest_subscription(client_id)
        if subscription is None or subscription.provider != 'app_store':
            return
        billing_repo.expire_subscription(subscription.id)

    def _decode_google_play_rtdn_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        message = payload.get('message')
        if not isinstance(message, dict):
            raise ValueError('Invalid Google Play RTDN Pub/Sub envelope')

        encoded = str(message.get('data') or '').strip()
        if not encoded:
            raise ValueError('Google Play RTDN message.data is empty')

        try:
            decoded = base64.b64decode(encoded).decode('utf-8')
            data = json.loads(decoded)
        except Exception as exc:  # noqa: BLE001
            raise ValueError('Google Play RTDN message.data is invalid') from exc
        if not isinstance(data, dict):
            raise ValueError('Google Play RTDN message.data is not an object')
        return data

    async def process_due_auto_renewals_once(self) -> int:
        if not self.is_configured:
            return 0

        processed = 0
        for subscription in billing_repo.get_due_auto_renew_subscriptions():
            plan = get_plan(subscription.plan_key)
            payment_method_id = (subscription.payment_method_id or '').strip()
            if not payment_method_id:
                billing_repo.expire_subscription(subscription.id)
                await self._notifier.notify_auto_renew_error(
                    client_id=subscription.client_id,
                    plan_key=plan.key,
                    plan_title=plan.title,
                    tokens=plan.limit,
                    amount_rub=plan.price_rub,
                    status='error',
                    payment_id='-',
                    reason='payment_method_id is missing',
                    expires_subscription=True,
                )
                processed += 1
                continue

            try:
                remote = await asyncio.to_thread(
                    self._gateway.create_recurring_payment,
                    plan=plan,
                    client_id=subscription.client_id,
                    payment_method_id=payment_method_id,
                )
            except YooKassaGatewayError as exc:
                next_try = billing_repo.postpone_autorenew_attempt(subscription.id, days=1)
                await self._notifier.notify_auto_renew_error(
                    client_id=subscription.client_id,
                    plan_key=plan.key,
                    plan_title=plan.title,
                    tokens=plan.limit,
                    amount_rub=plan.price_rub,
                    status='error',
                    payment_id='-',
                    reason=exc.reason,
                    next_try=next_try,
                )
                processed += 1
                continue
            except Exception as exc:  # noqa: BLE001
                next_try = billing_repo.postpone_autorenew_attempt(subscription.id, days=1)
                await self._notifier.notify_auto_renew_error(
                    client_id=subscription.client_id,
                    plan_key=plan.key,
                    plan_title=plan.title,
                    tokens=plan.limit,
                    amount_rub=plan.price_rub,
                    status='error',
                    payment_id='-',
                    reason=str(exc),
                    next_try=next_try,
                )
                processed += 1
                continue

            billing_repo.create_payment(
                client_id=subscription.client_id,
                provider='yookassa',
                amount=plan.price_rub,
                currency='RUB',
                plan_key=plan.key,
                external_payment_id=remote.payment_id,
                status='paid' if remote.status == 'succeeded' else remote.status,
                payment_method_id=remote.payment_method_id or payment_method_id,
                confirmation_url=remote.confirmation_url,
            )
            if remote.status == 'succeeded':
                billing_repo.renew_subscription(
                    subscription.id,
                    plan.key,
                    plan.limit,
                    plan.days,
                )
                await self._notifier.notify_auto_renew_success(
                    client_id=subscription.client_id,
                    plan_key=plan.key,
                    plan_title=plan.title,
                    tokens=plan.limit,
                    amount_rub=plan.price_rub,
                    status=remote.status,
                    payment_id=remote.payment_id,
                )
            elif remote.status == 'canceled':
                next_try = billing_repo.postpone_autorenew_attempt(subscription.id, days=1)
                await self._notifier.notify_auto_renew_error(
                    client_id=subscription.client_id,
                    plan_key=plan.key,
                    plan_title=plan.title,
                    tokens=plan.limit,
                    amount_rub=plan.price_rub,
                    status=remote.status,
                    payment_id=remote.payment_id,
                    reason=f'Payment did not succeed, status={remote.status}',
                    next_try=next_try,
                )
            else:
                next_try = billing_repo.postpone_autorenew_attempt(subscription.id, days=1)
                await self._notifier.notify_auto_renew_error(
                    client_id=subscription.client_id,
                    plan_key=plan.key,
                    plan_title=plan.title,
                    tokens=plan.limit,
                    amount_rub=plan.price_rub,
                    status=remote.status or 'unknown',
                    payment_id=remote.payment_id,
                    reason=f'Payment did not succeed, status={remote.status or "unknown"}',
                    next_try=next_try,
                )
            processed += 1

        return processed

    async def _sync_open_payments(self, client_id: str, limit: int = 3) -> None:
        if not self.is_configured:
            return

        for payment in billing_repo.list_open_payments(client_id, limit=limit):
            try:
                remote = await asyncio.to_thread(
                    self._gateway.get_payment,
                    payment.external_payment_id,
                )
            except Exception:  # noqa: BLE001
                continue

            if remote is None:
                continue

            await self._apply_remote_payment(client_id, payment.plan_key, remote)

    async def _apply_remote_payment(
        self,
        client_id: str,
        plan_key: str,
        remote: YooKassaPaymentInfo,
    ) -> str:
        plan = get_plan(plan_key)
        existing = billing_repo.get_payment(remote.payment_id)
        previous_status = (existing.status if existing else '').strip().lower()
        if remote.status == 'succeeded':
            auto_renew = 1 if plan.recurring and remote.payment_method_id else 0
            billing_repo.create_subscription(
                client_id=client_id,
                plan_key=plan.key,
                limit=plan.limit,
                days=plan.days,
                provider='yookassa',
                auto_renew=auto_renew,
                payment_method_id=remote.payment_method_id,
            )
            billing_repo.update_payment_status(
                remote.payment_id,
                'paid',
                payment_method_id=remote.payment_method_id,
                confirmation_url=remote.confirmation_url,
            )
            if previous_status != 'paid':
                await self._notifier.notify_payment_success(client_id, plan.title)
            return 'paid'
        if remote.status == 'canceled':
            billing_repo.update_payment_status(
                remote.payment_id,
                'canceled',
                payment_method_id=remote.payment_method_id,
                confirmation_url=remote.confirmation_url,
            )
            return 'canceled'

        billing_repo.update_payment_status(
            remote.payment_id,
            remote.status,
            payment_method_id=remote.payment_method_id,
            confirmation_url=remote.confirmation_url,
        )
        return remote.status
