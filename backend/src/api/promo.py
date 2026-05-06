from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.billing import _summary_response
from src.core.dependencies import get_billing_service, get_known_client_id
from src.domain.billing_service import BillingService
from src.repositories import admin as admin_repo
from src.schemas.promo import PromoRedeemResponse, RedeemPromoRequest


router = APIRouter(prefix='/v1/promo', tags=['promo'])


@router.post('/redeem', response_model=PromoRedeemResponse)
async def redeem_promo_code(
    payload: RedeemPromoRequest,
    client_id: str = Depends(get_known_client_id),
    billing_service: BillingService = Depends(get_billing_service),
) -> PromoRedeemResponse:
    try:
        result = admin_repo.redeem_promo_code(client_id=client_id, code=payload.code)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    summary = await billing_service.get_summary(client_id)
    return PromoRedeemResponse(
        code=result.code,
        tokens_added=result.tokens,
        used=result.used,
        max_uses=result.max_uses,
        summary=_summary_response(summary),
    )
