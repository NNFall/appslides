from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


ClientIdStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=128)]
PlanKeyStr = Literal['week', 'month', 'one10', 'one40']
PaymentContextStr = Literal['new', 'renew']


class BillingPlanItem(BaseModel):
    model_config = ConfigDict(extra='forbid')

    key: PlanKeyStr
    title: str
    price_rub: Annotated[int, Field(ge=1)]
    limit: Annotated[int, Field(ge=1)]
    days: Annotated[int, Field(ge=1)]
    recurring: bool
    google_play_product_id: str | None = None
    app_store_product_id: str | None = None


class BillingSubscriptionItem(BaseModel):
    model_config = ConfigDict(extra='forbid')

    plan_key: str
    status: str
    remaining: int
    starts_at: str
    ends_at: str
    auto_renew: bool
    provider: str


class BillingSummaryResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    client_id: str
    support_username: str
    support_max_url: str
    offer_url: str
    privacy_policy_url: str
    terms_of_use_url: str
    test_mode: bool
    plans: list[BillingPlanItem]
    active_subscription: BillingSubscriptionItem | None
    latest_valid_subscription: BillingSubscriptionItem | None


class CreateBillingPaymentRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    plan_key: PlanKeyStr
    context: PaymentContextStr = 'new'


class BillingPaymentResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    payment_id: str
    status: str
    confirmation_url: str | None
    test_mode: bool
    summary: BillingSummaryResponse


class VerifyGooglePlayPurchaseRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    package_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=255)]
    product_id: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=255)]
    purchase_token: Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=4096)]


class VerifyAppStorePurchaseRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    product_id: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=255)]
    transaction_id: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=255)] | None = None
    verification_data: Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=8192)]
    verification_source: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=64)]
    local_verification_data: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=8192)] | None = None


class RestoreAppStorePurchaseRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    product_id: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=255)]
    original_transaction_id: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=255)]


class AppStoreNotificationRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    signedPayload: Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=20000)]
