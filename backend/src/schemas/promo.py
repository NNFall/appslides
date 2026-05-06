from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from src.schemas.billing import BillingSummaryResponse


PromoCodeStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=4, max_length=64)]


class RedeemPromoRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    code: PromoCodeStr


class PromoRedeemResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    code: str
    tokens_added: Annotated[int, Field(ge=1)]
    used: Annotated[int, Field(ge=0)]
    max_uses: Annotated[int, Field(ge=1)]
    summary: BillingSummaryResponse
