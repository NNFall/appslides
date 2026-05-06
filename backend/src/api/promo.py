from __future__ import annotations

from html import escape
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse

from src.api.billing import _summary_response
from src.core.dependencies import get_billing_service, get_known_client_id
from src.domain.billing_service import BillingService
from src.repositories import admin as admin_repo
from src.schemas.promo import PromoRedeemResponse, RedeemPromoRequest


router = APIRouter(prefix='/v1/promo', tags=['promo'])
public_router = APIRouter(prefix='/promo', tags=['promo'])


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


@public_router.get('/open', response_class=HTMLResponse, include_in_schema=False)
async def open_promo_code(code: str = '') -> HTMLResponse:
    normalized = code.strip()
    app_link = f'appslides://promo/redeem?code={quote(normalized)}'
    html = f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AppSlides Promo</title>
    <meta http-equiv="refresh" content="0; url={escape(app_link, quote=True)}">
    <style>
      body {{
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #f5f7fb;
        color: #18222d;
        display: grid;
        min-height: 100vh;
        place-items: center;
        padding: 24px;
      }}
      .card {{
        width: min(440px, 100%);
        background: #fff;
        border-radius: 18px;
        box-shadow: 0 12px 36px rgba(24, 34, 45, 0.12);
        padding: 28px 24px;
      }}
      .button {{
        display: inline-block;
        margin-top: 18px;
        padding: 14px 18px;
        border-radius: 12px;
        background: #2f80ed;
        color: #fff;
        text-decoration: none;
        font-weight: 600;
      }}
      code {{
        display: block;
        margin-top: 12px;
        padding: 10px 12px;
        border-radius: 10px;
        background: #eef3f9;
        word-break: break-all;
      }}
    </style>
    <script>
      window.location.replace({app_link!r});
    </script>
  </head>
  <body>
    <div class="card">
      <h1>Открываем AppSlides</h1>
      <p>Если приложение не открылось автоматически, нажми кнопку ниже.</p>
      <a class="button" href="{escape(app_link, quote=True)}">Открыть в приложении</a>
      <code>{escape(app_link)}</code>
    </div>
  </body>
</html>"""
    return HTMLResponse(html)
