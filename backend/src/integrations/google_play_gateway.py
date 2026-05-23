from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


ANDROID_PUBLISHER_SCOPE = 'https://www.googleapis.com/auth/androidpublisher'
ACTIVE_SUBSCRIPTION_STATES = {
    'SUBSCRIPTION_STATE_ACTIVE',
    'SUBSCRIPTION_STATE_IN_GRACE_PERIOD',
}


@dataclass(frozen=True)
class GooglePlayPurchaseInfo:
    package_name: str
    product_id: str
    purchase_token: str
    status: str
    order_id: str | None
    expiry_time: str | None
    auto_renewing: bool

    @property
    def is_active(self) -> bool:
        return self.status in ACTIVE_SUBSCRIPTION_STATES


class GooglePlayGatewayError(RuntimeError):
    def __init__(self, message: str, *, reason: str | None = None) -> None:
        super().__init__(message)
        self.reason = reason or message


class GooglePlayGateway:
    def __init__(
        self,
        *,
        package_name: str,
        service_account_file: str = '',
        service_account_json: str = '',
        test_mode: bool = False,
    ) -> None:
        self._package_name = package_name.strip()
        self._service_account_file = service_account_file.strip()
        self._service_account_json = service_account_json.strip()
        self._test_mode = test_mode

    @property
    def package_name(self) -> str:
        return self._package_name

    @property
    def is_configured(self) -> bool:
        return bool(
            self._package_name
            and (self._service_account_file or self._service_account_json or self._test_mode)
        )

    def verify_subscription(
        self,
        *,
        package_name: str,
        product_id: str,
        purchase_token: str,
    ) -> GooglePlayPurchaseInfo:
        if package_name != self._package_name:
            raise GooglePlayGatewayError(
                'Google Play package name does not match backend configuration.',
                reason=f'{package_name} != {self._package_name}',
            )

        if self._test_mode:
            return self._verify_test_purchase(
                package_name=package_name,
                product_id=product_id,
                purchase_token=purchase_token,
            )

        access_token = self._access_token()
        url = (
            'https://androidpublisher.googleapis.com/androidpublisher/v3/'
            f'applications/{package_name}/purchases/subscriptionsv2/tokens/{purchase_token}'
        )
        response = requests.get(
            url,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=20,
        )
        if response.status_code >= 400:
            raise GooglePlayGatewayError(
                'Google Play purchase verification failed.',
                reason=f'{response.status_code}: {response.text[:500]}',
            )

        data = response.json()
        return self._parse_subscription_v2(
            package_name=package_name,
            product_id=product_id,
            purchase_token=purchase_token,
            data=data,
        )

    def acknowledge_subscription(
        self,
        *,
        package_name: str,
        product_id: str,
        purchase_token: str,
    ) -> None:
        if self._test_mode:
            return

        access_token = self._access_token()
        url = (
            'https://androidpublisher.googleapis.com/androidpublisher/v3/'
            f'applications/{package_name}/purchases/subscriptions/{product_id}/tokens/{purchase_token}:acknowledge'
        )
        response = requests.post(
            url,
            headers={'Authorization': f'Bearer {access_token}'},
            json={},
            timeout=20,
        )
        if response.status_code not in {200, 204, 409}:
            raise GooglePlayGatewayError(
                'Google Play purchase acknowledgement failed.',
                reason=f'{response.status_code}: {response.text[:500]}',
            )

    def _access_token(self) -> str:
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import service_account
        except ImportError as exc:  # pragma: no cover - environment/config issue
            raise GooglePlayGatewayError(
                'google-auth is not installed on the backend.',
                reason=str(exc),
            ) from exc

        if self._service_account_json:
            credentials = service_account.Credentials.from_service_account_info(
                json.loads(self._service_account_json),
                scopes=[ANDROID_PUBLISHER_SCOPE],
            )
        elif self._service_account_file:
            path = Path(self._service_account_file).expanduser()
            credentials = service_account.Credentials.from_service_account_file(
                str(path),
                scopes=[ANDROID_PUBLISHER_SCOPE],
            )
        else:
            raise GooglePlayGatewayError('Google Play service account is not configured.')

        credentials.refresh(Request())
        return str(credentials.token)

    def _verify_test_purchase(
        self,
        *,
        package_name: str,
        product_id: str,
        purchase_token: str,
    ) -> GooglePlayPurchaseInfo:
        if not purchase_token.startswith('test_'):
            raise GooglePlayGatewayError(
                'Google Play test mode accepts only tokens prefixed with test_.',
            )
        return GooglePlayPurchaseInfo(
            package_name=package_name,
            product_id=product_id,
            purchase_token=purchase_token,
            status='SUBSCRIPTION_STATE_ACTIVE',
            order_id=f'test-order-{purchase_token[-12:]}',
            expiry_time=datetime.now(timezone.utc).isoformat(),
            auto_renewing=True,
        )

    def _parse_subscription_v2(
        self,
        *,
        package_name: str,
        product_id: str,
        purchase_token: str,
        data: dict[str, Any],
    ) -> GooglePlayPurchaseInfo:
        status = str(data.get('subscriptionState') or 'SUBSCRIPTION_STATE_UNSPECIFIED')
        line_items = data.get('lineItems')
        line_item = line_items[0] if isinstance(line_items, list) and line_items else {}
        auto_renewing_plan = line_item.get('autoRenewingPlan') if isinstance(line_item, dict) else None
        expiry_time = line_item.get('expiryTime') if isinstance(line_item, dict) else None

        return GooglePlayPurchaseInfo(
            package_name=package_name,
            product_id=product_id,
            purchase_token=purchase_token,
            status=status,
            order_id=data.get('latestOrderId'),
            expiry_time=expiry_time,
            auto_renewing=bool(auto_renewing_plan),
        )
