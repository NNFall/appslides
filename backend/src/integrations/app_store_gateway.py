from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import requests


APP_STORE_PRODUCTION_BASE_URL = 'https://api.storekit.itunes.apple.com'
APP_STORE_SANDBOX_BASE_URL = 'https://api.storekit-sandbox.itunes.apple.com'
ACTIVE_APP_STORE_STATUSES = {'active', 'subscribed'}


@dataclass(frozen=True)
class AppStorePurchaseInfo:
    product_id: str
    transaction_id: str
    original_transaction_id: str
    status: str
    environment: str
    expires_at: str | None
    auto_renewing: bool

    @property
    def is_active(self) -> bool:
        return self.status in ACTIVE_APP_STORE_STATUSES


class AppStoreGatewayError(RuntimeError):
    def __init__(self, message: str, *, reason: str | None = None) -> None:
        super().__init__(message)
        self.reason = reason or message


class AppStoreGateway:
    def __init__(
        self,
        *,
        bundle_id: str,
        app_apple_id: str,
        issuer_id: str,
        key_id: str,
        private_key: str = '',
        private_key_file: str = '',
        environment: str = 'sandbox',
        test_mode: bool = False,
    ) -> None:
        self._bundle_id = bundle_id.strip()
        self._app_apple_id = app_apple_id.strip()
        self._issuer_id = issuer_id.strip()
        self._key_id = key_id.strip()
        self._private_key = private_key.strip()
        self._private_key_file = private_key_file.strip()
        self._environment = environment.strip().lower() or 'sandbox'
        self._test_mode = test_mode

    @property
    def is_configured(self) -> bool:
        if self._test_mode:
            return bool(self._bundle_id)
        return bool(
            self._bundle_id
            and self._issuer_id
            and self._key_id
            and (self._private_key or self._private_key_file)
        )

    def verify_purchase(
        self,
        *,
        product_id: str,
        transaction_id: str | None,
        verification_data: str,
        verification_source: str,
        local_verification_data: str | None = None,
    ) -> AppStorePurchaseInfo:
        if not self.is_configured:
            raise AppStoreGatewayError('App Store Billing is not configured')

        if self._test_mode:
            return self._test_purchase(product_id, transaction_id or verification_data)

        if not transaction_id:
            raise AppStoreGatewayError(
                'App Store transaction id is required for server verification.',
            )

        data = self._get_transaction_info(transaction_id)
        return self._purchase_from_signed_transaction(
            fallback_product_id=product_id,
            fallback_transaction_id=transaction_id,
            signed_transaction_info=str(data.get('signedTransactionInfo') or ''),
        )

    def restore_purchase(
        self,
        *,
        product_id: str,
        original_transaction_id: str,
    ) -> AppStorePurchaseInfo:
        if not self.is_configured:
            raise AppStoreGatewayError('App Store Billing is not configured')

        if self._test_mode:
            return self._test_purchase(product_id, original_transaction_id)

        data = self._get_transaction_history(original_transaction_id)
        signed_transactions = data.get('signedTransactions')
        if not isinstance(signed_transactions, list) or not signed_transactions:
            raise AppStoreGatewayError(
                'App Store transaction history is empty.',
                reason=f'original_transaction_id={original_transaction_id}',
            )

        return self._purchase_from_signed_transaction(
            fallback_product_id=product_id,
            fallback_transaction_id=original_transaction_id,
            signed_transaction_info=str(signed_transactions[-1] or ''),
        )

    def decode_notification(self, signed_payload: str) -> dict[str, Any]:
        if not signed_payload.strip():
            raise AppStoreGatewayError('App Store notification payload is empty.')
        return self._decode_jws_payload(signed_payload)

    def _test_purchase(self, product_id: str, transaction_id: str) -> AppStorePurchaseInfo:
        safe_transaction_id = transaction_id.strip() or 'test_app_store_transaction'
        return AppStorePurchaseInfo(
            product_id=product_id,
            transaction_id=safe_transaction_id,
            original_transaction_id=safe_transaction_id,
            status='active',
            environment='sandbox',
            expires_at=(datetime.now(UTC) + timedelta(days=30)).isoformat(),
            auto_renewing=True,
        )

    def _get_transaction_info(self, transaction_id: str) -> dict[str, Any]:
        return self._request(f'/inApps/v1/transactions/{transaction_id}')

    def _get_transaction_history(self, original_transaction_id: str) -> dict[str, Any]:
        return self._request(f'/inApps/v1/history/{original_transaction_id}')

    def _request(self, path: str) -> dict[str, Any]:
        response = requests.get(
            f'{self._base_url}{path}',
            headers={'Authorization': f'Bearer {self._authorization_token()}'},
            timeout=20,
        )
        if response.status_code >= 400:
            raise AppStoreGatewayError(
                'App Store Server API request failed.',
                reason=f'{response.status_code}: {response.text[:500]}',
            )
        data = response.json()
        return data if isinstance(data, dict) else {'data': data}

    @property
    def _base_url(self) -> str:
        if self._environment == 'production':
            return APP_STORE_PRODUCTION_BASE_URL
        return APP_STORE_SANDBOX_BASE_URL

    def _authorization_token(self) -> str:
        try:
            import jwt
        except ImportError as exc:  # pragma: no cover - environment/config issue
            raise AppStoreGatewayError(
                'PyJWT with crypto support is not installed on the backend.',
                reason=str(exc),
            ) from exc

        now = datetime.now(UTC)
        payload = {
            'iss': self._issuer_id,
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(minutes=15)).timestamp()),
            'aud': 'appstoreconnect-v1',
            'bid': self._bundle_id,
        }
        headers = {
            'alg': 'ES256',
            'kid': self._key_id,
            'typ': 'JWT',
        }
        return str(
            jwt.encode(
                payload,
                self._private_key_material(),
                algorithm='ES256',
                headers=headers,
            )
        )

    def _private_key_material(self) -> str:
        if self._private_key:
            return self._private_key.replace('\\n', '\n')
        if self._private_key_file:
            return Path(self._private_key_file).expanduser().read_text(encoding='utf-8')
        raise AppStoreGatewayError('App Store private key is not configured.')

    def _purchase_from_signed_transaction(
        self,
        *,
        fallback_product_id: str,
        fallback_transaction_id: str,
        signed_transaction_info: str,
    ) -> AppStorePurchaseInfo:
        payload = self._decode_jws_payload(signed_transaction_info)
        product_id = str(payload.get('productId') or fallback_product_id)
        transaction_id = str(payload.get('transactionId') or fallback_transaction_id)
        original_transaction_id = str(payload.get('originalTransactionId') or transaction_id)
        environment = str(payload.get('environment') or self._environment)
        expires_at = self._timestamp_ms_to_iso(payload.get('expiresDate'))
        revoked = bool(payload.get('revocationDate'))
        expired = False
        if expires_at:
            try:
                expired = datetime.fromisoformat(expires_at) <= datetime.now(UTC)
            except ValueError:
                expired = False
        status = 'active' if not revoked and not expired else 'expired'
        return AppStorePurchaseInfo(
            product_id=product_id,
            transaction_id=transaction_id,
            original_transaction_id=original_transaction_id,
            status=status,
            environment=environment,
            expires_at=expires_at,
            auto_renewing=not expired and not revoked,
        )

    def _decode_jws_payload(self, signed_payload: str) -> dict[str, Any]:
        parts = signed_payload.split('.')
        if len(parts) < 2:
            raise AppStoreGatewayError('Invalid App Store signed payload.')
        raw_payload = parts[1]
        padding = '=' * (-len(raw_payload) % 4)
        try:
            decoded = base64.urlsafe_b64decode(raw_payload + padding).decode('utf-8')
            data = json.loads(decoded)
        except Exception as exc:  # noqa: BLE001
            raise AppStoreGatewayError('Invalid App Store signed payload JSON.') from exc
        if not isinstance(data, dict):
            raise AppStoreGatewayError('Invalid App Store signed payload data.')
        return data

    def _timestamp_ms_to_iso(self, value: object) -> str | None:
        if value in (None, ''):
            return None
        try:
            timestamp = int(value) / 1000
        except (TypeError, ValueError):
            return None
        return datetime.fromtimestamp(timestamp, UTC).isoformat()
