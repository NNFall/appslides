# Backend

## Current Runtime

- Production backend is deployed on:
  - `http://185.171.83.116:8011`
- Mobile/web client is fixed to this endpoint.
- Server layout on the remote host:
  - `/root/appslides/backend`
  - `/root/appslides/data`
  - `/root/appslides/templates`
  - `/root/appslides/temp`
  - `/root/appslides/logs`
- SQLite is mounted outside the container:
  - `/root/appslides/data/appslides.db`
- Fonts are not uploaded separately; the container uses system font fallbacks.
- Billing target for the current MVP is `YooKassa` in live mode, wired through backend APIs and chat-style client flow.
- Billing summary/generation checks now auto-sync unfinished YooKassa payments, so a paid subscription can become active without the user manually reopening a specific payment poll route.
- Backend now forwards legacy-style admin notifications into the separate Telegram admin bot using `ADMIN_BOT_TOKEN + ADMIN_IDS`.
- Current notification events mirrored from the legacy Telegram bot:
  - new client first seen;
  - outline created;
  - outline updated by comment;
  - YooKassa payment success;
  - manual renewal success/failure;
  - auto-renew success/failure with payment status and payment id;
  - subscription canceled;
  - presentation generation success/failure;
  - file conversion success/failure.
- Operational workflow for `git -> push -> deploy -> restart` is documented in `../OPERATIONS.md`.

Р—РґРµСЃСЊ Р±СѓРґРµС‚ СЃРµСЂРІРµСЂРЅР°СЏ С‡Р°СЃС‚СЊ `AppSlides`.

РќР°Р·РЅР°С‡РµРЅРёРµ backend:

- СЂР°Р±РѕС‚Р° СЃ AI/API;
- РіРµРЅРµСЂР°С†РёСЏ outline/title/slides;
- РіРµРЅРµСЂР°С†РёСЏ РёР·РѕР±СЂР°Р¶РµРЅРёР№;
- СЃР±РѕСЂРєР° `PPTX`;
- РєРѕРЅРІРµСЂС‚Р°С†РёСЏ `PDF/DOCX/PPTX`;
- РґРѕР»РіРёРµ С„РѕРЅРѕРІС‹Рµ job-Р·Р°РґР°С‡Рё;
- РјРёРЅРёРјР°Р»СЊРЅС‹Р№ СЃРµСЂРІРµСЂРЅС‹Р№ state: РїРѕР»СЊР·РѕРІР°С‚РµР»Рё, СѓСЃС‚СЂРѕР№СЃС‚РІР°, РїРѕРґРїРёСЃРєРё, РїР»Р°С‚РµР¶Рё, entitlements, jobs;
- Р°РґРјРёРЅ-РёРЅСЃС‚СЂСѓРјРµРЅС‚С‹ Рё С‚РµС…Р»РѕРіРёРєР°.

РўРµС…РЅРѕР»РѕРіРёС‡РµСЃРєРѕРµ РЅР°РїСЂР°РІР»РµРЅРёРµ РЅР° С‚РµРєСѓС‰РµРј СЌС‚Р°РїРµ:

- Python backend;
- API-СЃР»РѕР№ РїРѕРІРµСЂС… Р»РѕРіРёРєРё РёР· `telegrambot/services`;
- РґР°Р»СЊРЅРµР№С€Р°СЏ С†РµР»СЊ: РІС‹РЅРµСЃС‚Рё РїСЂРѕРґСѓРєС‚РѕРІС‹Рµ СЃРµСЂРІРёСЃС‹ РёР· Telegram-Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№.

РЎС‚Р°СЂС‚РѕРІР°СЏ СЃС‚СЂСѓРєС‚СѓСЂР°:

```text
backend/
  src/
    api/
    core/
    domain/
    integrations/
    jobs/
    repositories/
    schemas/
  tests/
  runtime/
    templates/
    temp/
```

РўРµРєСѓС‰РёР№ СЃС‚Р°С‚СѓСЃ:

- РїРѕРґРЅСЏС‚ РїРµСЂРІС‹Р№ `FastAPI`-РєР°СЂРєР°СЃ;
- РµСЃС‚СЊ `healthcheck`;
- РµСЃС‚СЊ РїРµСЂРІС‹Рµ endpoints РґР»СЏ РіРµРЅРµСЂР°С†РёРё Рё РїРµСЂРµСЃР±РѕСЂРєРё outline;
- РµСЃС‚СЊ sync render Рё async job flow РґР»СЏ РїСЂРµР·РµРЅС‚Р°С†РёР№ Рё РєРѕРЅРІРµСЂС‚Р°С†РёР№;
- РµСЃС‚СЊ convenience download routes РїРѕРІРµСЂС… job-СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ;
- РµСЃС‚СЊ Р»РѕРєР°Р»СЊРЅС‹Рµ smoke-С‚РµСЃС‚С‹ РЅР° `unittest` Р±РµР· РїСЂРёРІСЏР·РєРё Рє СЂРµР°Р»СЊРЅРѕРјСѓ AI;
- `backend/.venv` СѓР¶Рµ РїРѕРґРЅСЏС‚ Р»РѕРєР°Р»СЊРЅРѕ Рё Р·Р°РІРёСЃРёРјРѕСЃС‚Рё СѓСЃС‚Р°РЅРѕРІР»РµРЅС‹;
- Р»РѕРєР°Р»СЊРЅС‹Р№ backend СѓСЃРїРµС€РЅРѕ СЃС‚Р°СЂС‚СѓРµС‚ Рё РѕС‚РІРµС‡Р°РµС‚ РЅР° `GET /v1/health`;
- backend Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё РїРѕРґС…РІР°С‚С‹РІР°РµС‚ `.env` РёР·:
  - `backend/.env`
  - РєРѕСЂРЅСЏ РїСЂРѕРµРєС‚Р°
  - `telegrambot/.env`

Р‘С‹СЃС‚СЂС‹Р№ Р·Р°РїСѓСЃРє:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

РџРѕР»РµР·РЅС‹Рµ endpoints:

- `GET /v1/health`
- `GET /v1/artifacts/{artifact_id}`
- `POST /v1/conversions/jobs`
- `GET /v1/conversions/jobs/{job_id}`
- `GET /v1/conversions/jobs/{job_id}/download`
- `GET /v1/templates/presentation`
- `POST /v1/presentations/outline`
- `POST /v1/presentations/outline/revise`
- `POST /v1/presentations/render`
- `POST /v1/presentations/jobs`
- `GET /v1/presentations/jobs/{job_id}`
- `GET /v1/presentations/jobs/{job_id}/download/pptx`
- `GET /v1/presentations/jobs/{job_id}/download/pdf`
- `GET /v1/billing/summary`
- `POST /v1/billing/payments`
- `GET /v1/billing/payments/{payment_id}`
- `POST /v1/billing/subscription/cancel`
- `POST /v1/promo/redeem`

Р”Р»СЏ billing Рё generation-Р·Р°РїСЂРѕСЃРѕРІ РєР»РёРµРЅС‚ РїРµСЂРµРґР°РµС‚ `X-AppSlides-Client-Id`.
РџСЂРѕРјРѕРєРѕРґС‹ С‚РµРїРµСЂСЊ РјРѕР¶РЅРѕ РіР°СЃРёС‚СЊ РЅР°РїСЂСЏРјСѓСЋ РёР· РјРѕР±РёР»СЊРЅРѕРіРѕ РєР»РёРµРЅС‚Р°: backend РїСЂРёРЅРёРјР°РµС‚ РєРѕРґ, РЅР°С‡РёСЃР»СЏРµС‚ РіРµРЅРµСЂР°С†РёРё РЅР° `client_id` СѓСЃС‚Р°РЅРѕРІРєРё Рё РІРѕР·РІСЂР°С‰Р°РµС‚ РѕР±РЅРѕРІР»С‘РЅРЅС‹Р№ billing summary.
После успешной активации backend также отправляет admin-уведомление с client_id, кодом промокода и числом начисленных генераций.

РџСЂРёРјРµСЂ Р·Р°РїСЂРѕСЃР° РЅР° outline:

```json
{
  "topic": "РЈРґРёРІРёС‚РµР»СЊРЅС‹Рµ С„Р°РєС‚С‹ Рѕ РєРѕСЃРјРѕСЃРµ РґР»СЏ С€РєРѕР»СЊРЅРёРєРѕРІ",
  "slides_total": 7
}
```

РџСЂРёРјРµСЂ РѕС‚РІРµС‚Р°:

```json
{
  "title": "РЈРґРёРІРёС‚РµР»СЊРЅС‹Рµ С„Р°РєС‚С‹ Рѕ РєРѕСЃРјРѕСЃРµ",
  "outline": [
    "Р§С‚Рѕ С‚Р°РєРѕРµ РєРѕСЃРјРѕСЃ",
    "РљР°Рє СѓСЃС‚СЂРѕРµРЅР° РЎРѕР»РЅРµС‡РЅР°СЏ СЃРёСЃС‚РµРјР°"
  ],
  "slides_total": 7,
  "content_slides": 6
}
```

РџСЂРёРјРµСЂ Р·Р°РїСЂРѕСЃР° РЅР° СЂРµРЅРґРµСЂ РїСЂРµР·РµРЅС‚Р°С†РёРё:

```json
{
  "topic": "РЈРґРёРІРёС‚РµР»СЊРЅС‹Рµ С„Р°РєС‚С‹ Рѕ РєРѕСЃРјРѕСЃРµ РґР»СЏ С€РєРѕР»СЊРЅРёРєРѕРІ",
  "title": "Р¤Р°РєС‚С‹ Рѕ РєРѕСЃРјРѕСЃРµ",
  "outline": [
    "Р§С‚Рѕ С‚Р°РєРѕРµ РєРѕСЃРјРѕСЃ",
    "РЎРѕР»РЅРµС‡РЅР°СЏ СЃРёСЃС‚РµРјР°",
    "РРЅС‚РµСЂРµСЃРЅС‹Рµ РїР»Р°РЅРµС‚С‹",
    "РљРѕРјРµС‚С‹ Рё Р°СЃС‚РµСЂРѕРёРґС‹",
    "РљРѕСЃРјРѕСЃ Рё С‡РµР»РѕРІРµРє",
    "Р‘СѓРґСѓС‰РµРµ РёСЃСЃР»РµРґРѕРІР°РЅРёР№"
  ],
  "design_id": 1,
  "generate_pdf": true
}
```

Р§С‚Рѕ РґРµР»Р°РµС‚ `render` СЃРµР№С‡Р°СЃ:

- РіРµРЅРµСЂРёСЂСѓРµС‚ С‚РµРєСЃС‚С‹ СЃР»Р°Р№РґРѕРІ;
- РіРµРЅРµСЂРёСЂСѓРµС‚ РёР»Рё РїРѕРґСЃС‚Р°РІР»СЏРµС‚ placeholder-РёР·РѕР±СЂР°Р¶РµРЅРёСЏ;
- СЃРѕР±РёСЂР°РµС‚ `PPTX` РїРѕ РІС‹Р±СЂР°РЅРЅРѕРјСѓ С€Р°Р±Р»РѕРЅСѓ;
- РїС‹С‚Р°РµС‚СЃСЏ СЃРѕР±СЂР°С‚СЊ `PDF`, РµСЃР»Рё `generate_pdf=true` Рё РґРѕСЃС‚СѓРїРµРЅ LibreOffice;
- СЂРµРіРёСЃС‚СЂРёСЂСѓРµС‚ Р°СЂС‚РµС„Р°РєС‚С‹ Рё РѕС‚РґР°РµС‚ `download_url`.

Р’Р°Р¶РЅРѕ:

- РїРѕРєР° СЌС‚Рѕ СЃРёРЅС…СЂРѕРЅРЅС‹Р№ render endpoint, РЅРµ job queue;
- download-С…СЂР°РЅРёР»РёС‰Рµ СЃРµР№С‡Р°СЃ in-memory РЅР° РїСЂРѕС†РµСЃСЃ, СЌС‚Рѕ РїСЂРѕРјРµР¶СѓС‚РѕС‡РЅС‹Р№ СЌС‚Р°Рї РґРѕ РїРѕР»РЅРѕС†РµРЅРЅРѕР№ job/DB РјРѕРґРµР»Рё.

Async jobs:

- `POST /v1/presentations/jobs` СЃРѕР·РґР°РµС‚ С„РѕРЅРѕРІСѓСЋ Р·Р°РґР°С‡Сѓ СЂРµРЅРґРµСЂР°;
- `GET /v1/presentations/jobs/{job_id}` РѕС‚РґР°РµС‚ СЃС‚Р°С‚СѓСЃ `queued/running/succeeded/failed`;
- `GET /v1/presentations/jobs/{job_id}/download/pptx` Рё `GET /v1/presentations/jobs/{job_id}/download/pdf` РѕС‚РґР°СЋС‚ РёС‚РѕРіРѕРІС‹Рµ С„Р°Р№Р»С‹, РєРѕРіРґР° job Р·Р°РІРµСЂС€РµРЅР°;
- `POST /v1/conversions/jobs` РїСЂРёРЅРёРјР°РµС‚ multipart upload Рё СЃРѕР·РґР°РµС‚ С„РѕРЅРѕРІСѓСЋ Р·Р°РґР°С‡Сѓ РєРѕРЅРІРµСЂС‚Р°С†РёРё;
- `GET /v1/conversions/jobs/{job_id}` РѕС‚РґР°РµС‚ СЃС‚Р°С‚СѓСЃ Рё Р°СЂС‚РµС„Р°РєС‚ РїРѕСЃР»Рµ Р·Р°РІРµСЂС€РµРЅРёСЏ.
- `GET /v1/conversions/jobs/{job_id}/download` РѕС‚РґР°РµС‚ РёС‚РѕРіРѕРІС‹Р№ СЃРєРѕРЅРІРµСЂС‚РёСЂРѕРІР°РЅРЅС‹Р№ С„Р°Р№Р».

РўРµРєСѓС‰РµРµ РѕРіСЂР°РЅРёС‡РµРЅРёРµ job model:

- store Р·Р°РґР°С‡ Рё download registry Р¶РёРІСѓС‚ РІ РїР°РјСЏС‚Рё РїСЂРѕС†РµСЃСЃР°;
- РїРѕСЃР»Рµ СЂРµСЃС‚Р°СЂС‚Р° СЃРµСЂРІРµСЂР° СЃС‚Р°С‚СѓСЃС‹ Рё СЃСЃС‹Р»РєРё РїСЂРѕРїР°РґСѓС‚;
- СЌС‚Рѕ РїСЂРѕРјРµР¶СѓС‚РѕС‡РЅС‹Р№ СЌС‚Р°Рї РґРѕ Redis/Postgres.

Smoke-РїСЂРѕРІРµСЂРєР°:

```bash
python -m unittest discover -s backend/tests -v
```

Р”Р»СЏ `fastapi.testclient` РІ backend requirements С‚РµРїРµСЂСЊ РІРєР»СЋС‡РµРЅ `httpx`.

PowerShell helper scripts:

```powershell
# СЃС‚Р°СЂС‚ backend РІ С„РѕРЅРµ
.\scripts\dev\start_backend.ps1

# healthcheck
.\scripts\dev\backend_health.ps1

# РѕСЃС‚Р°РЅРѕРІРєР° backend
.\scripts\dev\stop_backend.ps1
```

Р§С‚Рѕ РїСЂРѕРІРµСЂСЏРµС‚СЃСЏ СЃРµР№С‡Р°СЃ:

- `GET /v1/health`
- `GET /v1/templates/presentation`
- `POST /v1/presentations/outline`
- async presentation job + `download/pptx`
- async conversion job + `download`
