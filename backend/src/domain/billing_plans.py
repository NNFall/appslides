from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BillingPlan:
    key: str
    title: str
    price_rub: int
    limit: int
    days: int
    recurring: bool
    google_play_product_id: str | None = None


PLANS: dict[str, BillingPlan] = {
    'week': BillingPlan(
        key='week',
        title='Неделя',
        price_rub=199,
        limit=10,
        days=7,
        recurring=True,
        google_play_product_id='slide_ai_week',
    ),
    'month': BillingPlan(
        key='month',
        title='Месяц',
        price_rub=499,
        limit=50,
        days=30,
        recurring=True,
        google_play_product_id='slide_ai_month',
    ),
    'one10': BillingPlan(
        key='one10',
        title='Разово 10',
        price_rub=199,
        limit=10,
        days=7,
        recurring=False,
    ),
    'one40': BillingPlan(
        key='one40',
        title='Разово 40',
        price_rub=499,
        limit=50,
        days=7,
        recurring=False,
    ),
}


def get_plan(plan_key: str) -> BillingPlan:
    try:
        return PLANS[plan_key]
    except KeyError as exc:  # pragma: no cover - defensive
        raise ValueError(f'Unknown billing plan: {plan_key}') from exc


def list_plans() -> list[BillingPlan]:
    return list(PLANS.values())


def get_plan_by_google_play_product_id(product_id: str) -> BillingPlan:
    for plan in PLANS.values():
        if plan.google_play_product_id == product_id:
            return plan
    raise ValueError(f'Unknown Google Play product id: {product_id}')
