# AppSlides Plan


## Promo Admin Notify - 2026-05-07

- Added backend-side admin notification for successful promo redemption.
- Notification now includes shortened `client_id`, promo code, added token count and current usage `used/max_uses`.
- Event is emitted from `POST /v1/promo/redeem`, so it works regardless of whether the code was typed manually in chat or triggered by any future client flow.
## Network Retry UX - 2026-05-06

- Added a cross-flow mobile handling rule for transport errors:
  - internet/backend transport failures must not surface as raw `ClientException` text in chat;
  - the user must see a short Russian explanation and a retry action;
  - this rule now covers presentation outline, presentation render/status refresh, and conversion start/status refresh.
- Implemented MVP recovery model:
  - manual retry buttons inside chat;
  - exact replay for outline request using stored `topic + slides_total`;
  - exact replay for render continuation using the current prepared draft;
  - exact status refresh retry for already created presentation/conversion jobs.
- Explicitly not implemented yet:
  - automatic replay after reconnect;
  - persistent offline request queue across cold restart;
  - global network-resume orchestration for every pending action.

## Р”РѕРєСѓРјРµРЅС‚Р°С†РёСЏ РґР»СЏ РїРѕРІС‚РѕСЂРЅРѕРіРѕ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёСЏ РїСЂРѕРґСѓРєС‚Р° - 2026-05-03

- Р—Р°С„РёРєСЃРёСЂРѕРІР°РЅРѕ РЅРѕРІРѕРµ РїСЂРѕРґСѓРєС‚РѕРІРѕРµ С‚СЂРµР±РѕРІР°РЅРёРµ:
  - С‚РµРєСѓС‰РёР№ СЂРµРїРѕР·РёС‚РѕСЂРёР№ `appslides` РґРѕР»Р¶РµРЅ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊСЃСЏ РЅРµ С‚РѕР»СЊРєРѕ РєР°Рє РѕРґРёРЅ РїСЂРѕРґСѓРєС‚, РЅРѕ Рё РєР°Рє РїРµСЂРµРёСЃРїРѕР»СЊР·СѓРµРјС‹Р№ РєР°СЂРєР°СЃ РїСЂРёР»РѕР¶РµРЅРёСЏ РґР»СЏ РґСЂСѓРіРёС… AI-РЅРёС€;
  - РІ Р±СѓРґСѓС‰РµРј РЅР° С‚РѕР№ Р¶Рµ РїР»Р°С‚С„РѕСЂРјРµ РјРѕРіСѓС‚ СЃРѕР±РёСЂР°С‚СЊСЃСЏ РїСЂРѕРґСѓРєС‚С‹ РїРѕРґ РўР°СЂРѕ, РіРµРЅРµСЂР°С†РёСЋ РёР·РѕР±СЂР°Р¶РµРЅРёР№/РІРёРґРµРѕ, РїРµСЃРЅРё Рё РґСЂСѓРіРёРµ chat-driven AI-СЃС†РµРЅР°СЂРёРё;
  - СЃР»РµРґСѓСЋС‰РµРјСѓ Р°РіРµРЅС‚Сѓ РјРѕР¶РµС‚ РїРµСЂРµРґР°РІР°С‚СЊСЃСЏ СѓР¶Рµ РґСЂСѓРіР°СЏ РїР°РїРєР° Telegram-Р±РѕС‚Р° РєР°Рє РёСЃС‚РѕС‡РЅРёРє РїСЂРµРґРјРµС‚РЅРѕР№ Р»РѕРіРёРєРё, Р° С‚РµРєСѓС‰РёР№ Flutter/backend/admin/deploy-РєР°СЂРєР°СЃ РґРѕР»Р¶РµРЅ РѕСЃС‚Р°РІР°С‚СЊСЃСЏ Р±Р°Р·РѕР№.
- Р’ СЌС‚РѕРј РїСЂРѕС…РѕРґРµ Р·Р°РґР°С‡Р° РїРѕ РґРѕРєСѓРјРµРЅС‚Р°С†РёРё РІС‹РїРѕР»РЅРµРЅР°:
  - [x] РІС‹РЅРµСЃРµРЅ РѕС‚РґРµР»СЊРЅС‹Р№ Р°РґР°РїС‚Р°С†РёРѕРЅРЅС‹Р№ РіРёРґ РІРјРµСЃС‚Рѕ РїРµСЂРµРіСЂСѓР·РєРё backend/frontend README;
  - [x] РІС‹РЅРµСЃРµРЅ РѕС‚РґРµР»СЊРЅС‹Р№ С„Р°Р№Р» СЃ РїСЂР°РІРёР»Р°РјРё СЂРµР°Р»РёР·Р°С†РёРё Рё РїР»Р°С‚С„РѕСЂРјРµРЅРЅС‹РјРё РёРЅРІР°СЂРёР°РЅС‚Р°РјРё;
  - [x] РІС‹РЅРµСЃРµРЅ РѕС‚РґРµР»СЊРЅС‹Р№ handoff-С„Р°Р№Р» РґР»СЏ СЃР»РµРґСѓСЋС‰РµР№ РЅРµР№СЂРѕСЃРµС‚Рё РёР»Рё СЂР°Р·СЂР°Р±РѕС‚С‡РёРєР°.
- РќРѕРІС‹Р№ handoff-РїР°РєРµС‚:
  - `PRODUCT_ADAPTATION_GUIDE.md`
  - `IMPLEMENTATION_RULES.md`
  - `AGENT_HANDOFF.md`
- РљР°Рє РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ:
  - РїСЂРёРєР»Р°РґС‹РІР°С‚СЊ РїР°РїРєСѓ РЅРѕРІРѕРіРѕ Telegram-Р±РѕС‚Р° РїРѕ РЅСѓР¶РЅРѕР№ РЅРёС€Рµ;
  - РїСЂРёРєР»Р°РґС‹РІР°С‚СЊ РЅРѕРІС‹Рµ handoff-РґРѕРєСѓРјРµРЅС‚С‹ РёР· СЌС‚РѕРіРѕ СЂРµРїРѕР·РёС‚РѕСЂРёСЏ;
  - СЃС‚Р°РІРёС‚СЊ СЃР»РµРґСѓСЋС‰РµРјСѓ Р°РіРµРЅС‚Сѓ Р·Р°РґР°С‡Сѓ СЃРѕС…СЂР°РЅРёС‚СЊ РїР»Р°С‚С„РѕСЂРјРµРЅРЅС‹Р№ shell Рё Р·Р°РјРµРЅРёС‚СЊ С‚РѕР»СЊРєРѕ product/domain-СЃР»РѕРё.

## Admin Telegram Bot Pivot - 2026-04-30

- Product decision is fixed:
  - admin access for `appslides` will not be built inside the Flutter app;
  - admin access will be moved into a separate Telegram bot for admins;
  - access control must stay ENV-based through Telegram user IDs;
  - runtime admin whitelist must support both:
    - static IDs from `.env`;
    - dynamic extra admins stored in the database, matching the legacy bot behavior.
- Source of truth for admin behavior is the legacy Telegram bot code, not a newly invented panel UX.
- Legacy admin command set already identified from `telegrambot/main.py` and `telegrambot/handlers/admin.py`:
  - `/botstats`
  - `/adstats`
  - `/adstats_all`
  - `/adtag`
  - `/tag`
  - `/sub_on`
  - `/sub_off`
  - `/sub_check`
  - `/sub_cancel`
  - `/genpromo` РІ admin-Р±РѕС‚Рµ С‚РµРїРµСЂСЊ РѕС‚РґР°С‘С‚ РіРѕС‚РѕРІСѓСЋ РєРѕРїРёСЂСѓРµРјСѓСЋ РєРѕРјР°РЅРґСѓ `/promo CODE` РґР»СЏ РїРµСЂРµСЃС‹Р»РєРё РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ
  - `/admin_add`
  - `/admin_del`
  - `/admin_list`
  - `/templates`
  - `/template_set`
- Migration requirement:
  - preserve command names;
  - preserve command semantics;
  - preserve admin-only access checks;
  - preserve message formatting where it is still useful;
  - preserve template-management flow, including file upload state for `/template_set`;
  - preserve promo/deeplink logic for ad tags and promo codes where applicable.
- Expected admin bot scope:
  - bot statistics;
  - traffic-tag statistics;
  - manual subscription/token operations;
  - subscription inspection/cancelation;
  - promo generation;
  - admin list management;
  - template download/replacement;
  - backend-driven admin notifications from product events.
- Planned implementation shape:
  - separate `telegram_admin_bot/` package;
  - `aiogram`-based runtime;
  - isolated config via `.env`;
  - direct integration with the active `appslides` backend database/service layer;
  - no coupling to the mobile UI.
- Completed in the current pass:
  - [x] separate `telegram_admin_bot/` package created;
  - [x] ENV-based super-admin access retained through `ADMIN_IDS`;
  - [x] dynamic DB-based extra-admin support restored through `admins` table;
  - [x] legacy admin command names restored in the new bot;
  - [x] `sub_on`, `sub_off`, `sub_check`, `sub_cancel` adapted to `client_id` instead of Telegram `user_id`;
  - [x] template listing and upload-replacement flow restored;
  - [x] promo code creation restored on the new backend schema;
  - [x] promo redemption flow simplified to manual `/promo CODE` input in the app;
  - [x] new installs now use shortened `client_id` format `as_<10 hex>` while keeping existing stored IDs intact;
  - [x] ad-tag schema and tag-statistics support restored for the new backend database;
  - [x] shared admin schema added into the main `appslides` SQLite storage;
  - [x] admin bot dockerized and added into the production compose stack;
  - [x] admin bot deployed on `185.171.83.116` together with backend.
  - [x] backend event notifications restored into the admin Telegram bot for:
    - new client first seen;
    - outline created;
    - outline updated by comment;
    - YooKassa payment success;
    - manual renewal success/failure;
    - auto-renew success/failure with payment status and payment id;
    - subscription cancel;
    - presentation generation success/failure;
    - file conversion success/failure.
- Next required study before implementation:
  - inspect each admin handler end-to-end against the current `appslides` backend schema;
  - map old Telegram `user_id` logic to current mobile `client_id` world where needed;
  - decide which admin commands must operate on `client_id`, which on payment/subscription records, and which need helper lookup commands first.

## Concurrent Generation Note - 2026-04-30

- Clarified requirement:
  - the goal is not just "make one request async";
  - the real goal is to let several users generate presentations in parallel without one user waiting for the full completion of another.
- Current backend already has partial concurrency:
  - `POST /v1/presentations/jobs` creates a background job instead of blocking the client;
  - each presentation job is started in its own Python thread;
  - slide image generation inside one presentation already runs with bounded parallelism through `asyncio.gather(...)` and `Semaphore(image_concurrency)`;
  - outline generation already parallelizes `title + outline`;
  - file conversion also runs as a background job.
- Current limitation:
  - provider calls are wrapped with `asyncio.to_thread(...)`, but the provider clients themselves are still blocking `requests + polling + sleep`;
  - there is no real central worker pool/queue manager yet;
  - there is no explicit global concurrency cap per provider or per heavy local stage;
  - there is no webhook-based provider completion path yet, so provider waits still consume local worker capacity.
- Important architectural conclusion:
  - yes, `Replicate` supports async predictions by default and recommends polling or webhooks for long tasks:
    - https://replicate.com/docs/topics/predictions/create-a-prediction
    - https://replicate.com/docs/topics/predictions/lifecycle/
  - yes, `Kie.ai` documents its generation tasks as asynchronous and explicitly exposes task creation plus later status lookup/callback usage:
    - https://docs.kie.ai/index
    - https://docs.kie.ai/market/common/get-task-detail
- Therefore the correct target architecture is:
  - create provider tasks quickly;
  - release request threads quickly;
  - persist external task IDs;
  - poll or receive callbacks separately;
  - continue local assembly only when upstream AI artifacts are ready;
  - keep a bounded local worker pool for PPTX/PDF assembly and conversion.
- Practical target for MVP hardening:
  - support at least `~5` parallel end-to-end presentation generations with controlled degradation instead of full serialization;
  - avoid a model where user #5 waits for users #1-#4 to fully finish before their own AI stage even starts.
- Planned backend refactor for this:
  - remove product dependence on sync `POST /v1/presentations/render` in the client flow;
  - keep job-based API as the canonical path;
  - split one render job into stages:
    - outline/slide text creation
    - image task fan-out
    - provider status tracking
    - local PPTX build
    - local PDF conversion
  - replace ad-hoc thread spawning with a bounded worker model;
  - add explicit concurrency limits for:
    - AI text requests
    - AI image requests
    - LibreOffice conversions
  - optionally move provider completion from pure polling to callbacks/webhooks where stable.

## Design Pivot вЂ” 2026-04-26

- Product direction changed: the mobile client must imitate a Telegram bot, not a classic app with tabs and separate feature screens.
- Active UI requirement:
  - one single chat window;
  - no bottom navigation, no dashboard shell, no separate menu sections;
  - interaction through message feed, inline/reply-style buttons and free-text input;
  - Telegram-like header, wallpaper, message bubbles, keyboard area and file cards;
  - bot-first flow for presentation generation, conversion, help, history, settings and balance.
- Current design archive is saved in `old_design/flutter_ui_v1/`.
- New local design brief is saved in `instructions/design_refs/telegram_bot_ui_brief.md`.
- Business requirement updated:
  - target store for MVP is `RuStore`;
  - billing target from the product side is `YooKassa`;
  - `Telegram Stars` is dropped from the mobile roadmap.
- Important implementation note:
  - the product requirement is now `RuStore + YooKassa`, but before release we still need a separate moderation/payment validation pass against current RuStore monetization rules, because official RuStore docs as of 2026-04-26 actively promote `Pay SDK` for in-app purchases and subscriptions:
    - https://www.rustore.ru/help/en/sdk/pay
    - https://www.rustore.ru/help/en/developers/monetization/manage-subscriptions

## Runtime Lock-in вЂ” 2026-04-27

- Active backend endpoint is fixed:
  - `http://185.171.83.116:8011`
- Flutter client no longer allows changing backend URL locally.
- Remote deployment target is fixed to:
  - host `185.171.83.116`
  - app dir `/root/appslides`
  - Docker host port `8011`
- Billing implementation direction is now concrete:
  - `YooKassa` live mode through backend billing APIs
  - `X-AppSlides-Client-Id` is the persistent client key for subscriptions, limits and payments
  - chat command `/balance` is the single entry point for plan selection, payment launch, polling and cancellation
  - unfinished YooKassa payments must auto-sync on resume/summary checks so the paywall does not depend on a manual refresh
- Operational discipline is now fixed:
  - every large/important change should be committed and pushed to GitHub
  - backend changes should be redeployed to the remote server right after validation
  - the canonical commands live in `OPERATIONS.md`

## UX Fix Pack вЂ” 2026-04-28

- Source of truth for the next pass is the latest phone QA from the user.
- This pass is not about new features first; it is about closing the current Telegram-style UX gap end-to-end before moving further.
- Mandatory fixes in this batch:
  - composer cleanup:
    - remove the idle placeholder text `РЎРѕРѕР±С‰РµРЅРёРµ`;
    - remove the fake Telegram controls that do nothing;
    - simplify the header and composer so there are no dead icons;
    - make the input area visually closer to Telegram and easier to scan;
    - collapse the mobile keyboard automatically right after sending text;
  - process message lifecycle:
    - plan generation temporary message must disappear once the outline arrives;
    - payment creation temporary message must disappear once the invoice is created;
    - presentation render temporary messages must be reduced and cleaned up on success;
    - job id/status message must remain only when generation fails, for debugging;
  - paywall rewrite:
    - template-step paywall message must say the presentation is almost ready and ask the user to finish the final step through subscription;
    - one-time package options must be removed from the client flow;
    - success-after-payment message must be cleaner and should not show management buttons except `Р“Р»Р°РІРЅРѕРµ РјРµРЅСЋ`;
    - noisy transient billing transport errors must not leak into the chat feed when the flow can continue safely;
  - text rendering:
    - support richer formatting for bot messages;
    - make the offer link inline and clickable inside the message text;
    - remove the redundant offer preview block from payment success;
  - file behavior on phone:
    - presentation result files must behave like real files from the chat;
    - tapping a file card must open the file flow instead of doing nothing;
    - generated files should be downloaded locally automatically or transparently on first tap without extra friction;
  - visual polish:
    - keep moving sizes, spacing and card styling closer to the Telegram references while removing decorative but non-functional controls.

- Completed in the current pass:
  - [x] idle composer placeholder removed;
  - [x] fake Telegram icons removed from header and bottom bar;
  - [x] keyboard now collapses right after sending text;
  - [x] outline progress message is deleted when the outline arrives;
  - [x] payment creation progress message is deleted when the invoice arrives;
  - [x] render progress is reduced to meaningful messages only;
  - [x] job id/status message is cleaned up on success and intentionally preserved on failure;
  - [x] template-step paywall now uses the вЂњpresentation is almost readyвЂќ wording;
  - [x] one-time billing package buttons removed from the client paywall flow;
  - [x] markdown-style rich text enabled for bot messages;
  - [x] offer link is now inline and clickable;
  - [x] redundant offer preview block removed from the success flow;
  - [x] transient billing transport noise is suppressed from the chat feed;
  - [x] success-after-payment message now only keeps `Р“Р»Р°РІРЅРѕРµ РјРµРЅСЋ`;
  - [x] presentation file cards now download/open as real files on mobile;
  - [x] local auto-prefetch of generated result files is enabled for non-web platforms.

- Billing parity improvements after the QA pass:
  - [x] automatic YooKassa polling in the app is now closer to the Telegram bot logic;
  - [x] the app polls payment status every `10 seconds`;
  - [x] automatic polling now stops after `15 minutes` instead of running indefinitely;
  - [x] temporary transport errors during polling no longer terminate the whole payment-wait flow;
  - [x] when polling reaches the timeout window, the chat shows a clean follow-up message with the same payment actions.

- Local chat persistence hardening:
  - [x] transcript restore now waits correctly for the async storage read instead of racing against app startup;
  - [x] chat history restore now keeps bot/user messages, file cards, template preview blocks and inline keyboards;
  - [x] the current conversation step and pending paywall template are now stored together with the transcript;
  - [x] legacy transcript storage is migrated forward instead of being silently dropped on upgrade.
  - [x] transcript storage on mobile is moved from async prefs-only persistence to a dedicated flushed JSON file in app documents storage;
  - [x] chat snapshot now gets flushed again when the app goes to background or is being closed.
  - [x] real-device Android release check passed: after `force-stop`, relaunch restores the same chat thread without debug-only helpers.


## РЎС‚Р°С‚СѓСЃ

- РџСЂРѕРµРєС‚: `appslides`
- РџРѕСЃР»РµРґРЅРµРµ РѕР±РЅРѕРІР»РµРЅРёРµ: `2026-04-30`
- РўРµРєСѓС‰РёР№ СЌС‚Р°Рї: `Backend/admin infrastructure expansion + separate Telegram admin bot MVP`
- РўРµРєСѓС‰РёР№ С„РѕРєСѓСЃ: `РґРѕРІРµСЃС‚Рё РѕС‚РґРµР»СЊРЅС‹Р№ admin Telegram bot РґРѕ РїРѕР»РЅРѕР№ РїСЂРёРіРѕРґРЅРѕСЃС‚Рё РґР»СЏ prod-РѕРїРµСЂР°С†РёР№`

## Р§С‚Рѕ СѓР¶Рµ СЃРґРµР»Р°РЅРѕ

- [x] РР·СѓС‡РµРЅ [telegrambot/README.md](telegrambot/README.md)
- [x] РР·СѓС‡РµРЅ [telegrambot/agents.md](telegrambot/agents.md)
- [x] РР·СѓС‡РµРЅС‹ РєР»СЋС‡РµРІС‹Рµ РјРѕРґСѓР»Рё С‚РµРєСѓС‰РµРіРѕ Р±РѕС‚Р°:
  - `handlers/start.py`
  - `handlers/presentation_gen.py`
  - `handlers/file_converter.py`
  - `handlers/subscription.py`
  - `handlers/admin.py`
  - `services/kie_api.py`
  - `services/pptx_builder.py`
  - `services/converter.py`
  - `services/payment.py`
  - `services/auto_renew.py`
  - `services/mailer.py`
  - `database/db.py`
  - `database/models.py`
- [x] РЎРѕР·РґР°РЅР° Р±Р°Р·РѕРІР°СЏ СЃС‚СЂСѓРєС‚СѓСЂР° РєР°С‚Р°Р»РѕРіРѕРІ `backend/` Рё `app/`
- [x] РЎРѕР·РґР°РЅ `FastAPI`-РєР°СЂРєР°СЃ backend
- [x] Р”РѕР±Р°РІР»РµРЅС‹ `GET /v1/health`, `POST /v1/presentations/outline`, `POST /v1/presentations/outline/revise`
- [x] Р”РѕР±Р°РІР»РµРЅ `GET /v1/templates/presentation` РґР»СЏ РєР°С‚Р°Р»РѕРіР° РґРёР·Р°Р№РЅРѕРІ
- [x] Р’С‹РЅРµСЃРµРЅС‹ prompts Рё text-generation Р»РѕРіРёРєР° РІ `backend/src/`
- [x] Р’С‹РЅРµСЃРµРЅ `converter` РІ `backend/src/jobs/file_converter.py`
- [x] РџРµСЂРµРЅРµСЃРµРЅ `pptx_builder` РІ `backend/src/jobs/pptx_builder.py`
- [x] Р”РѕР±Р°РІР»РµРЅ РїРµСЂРІС‹Р№ sync render endpoint `POST /v1/presentations/render`
- [x] Р”РѕР±Р°РІР»РµРЅ download endpoint `GET /v1/artifacts/{artifact_id}`
- [x] Р”РѕР±Р°РІР»РµРЅР° in-memory job model РґР»СЏ render/conversion Р·Р°РґР°С‡
- [x] Р”РѕР±Р°РІР»РµРЅС‹ async endpoints РґР»СЏ presentation jobs
- [x] Р”РѕР±Р°РІР»РµРЅС‹ multipart conversion job endpoints
- [x] Р”РѕР±Р°РІР»РµРЅС‹ convenience download routes РґР»СЏ async jobs
- [x] Р”РѕР±Р°РІР»РµРЅ `backend/.env.example` Рё `backend/requirements.txt`
- [x] РџСЂРѕРІРµСЂРµРЅ РёРјРїРѕСЂС‚ backend-РїСЂРёР»РѕР¶РµРЅРёСЏ Р»РѕРєР°Р»СЊРЅРѕ
- [x] РџСЂРѕРІРµСЂРµРЅ end-to-end render: `PPTX`
- [x] РџСЂРѕРІРµСЂРµРЅ end-to-end render: `PDF`
- [x] Р”РѕР±Р°РІР»РµРЅС‹ backend smoke-С‚РµСЃС‚С‹ РЅР° `unittest`
- [x] РЎРѕР·РґР°РЅ СЂСѓС‡РЅРѕР№ Flutter-ready scaffold РІ `app/`
- [x] Р”РѕР±Р°РІР»РµРЅ app data/API layer РїРѕРґ backend endpoints
- [x] РџРѕРґРєР»СЋС‡РµРЅ СЌРєСЂР°РЅ РіРµРЅРµСЂР°С†РёРё РїСЂРµР·РµРЅС‚Р°С†РёРё Рє backend API
- [x] РџРѕРґРєР»СЋС‡РµРЅ СЌРєСЂР°РЅ РєРѕРЅРІРµСЂС‚Р°С†РёРё Рє backend API
- [x] Р”РѕР±Р°РІР»РµРЅР° Р»РѕРєР°Р»СЊРЅР°СЏ persistent-history РІ РїСЂРёР»РѕР¶РµРЅРёРё
- [x] РЈСЃС‚Р°РЅРѕРІР»РµРЅ Flutter SDK Р»РѕРєР°Р»СЊРЅРѕ РЅР° РџРљ
- [x] `app/` РїРµСЂРµРІРµРґРµРЅ РІ РЅР°СЃС‚РѕСЏС‰РёР№ Flutter-РїСЂРѕРµРєС‚ СЃ platform folders
- [x] РџСЂРѕР№РґРµРЅС‹ `flutter analyze`, `flutter test`, `flutter build web`
- [x] РЎРѕР±СЂР°РЅ Android APK: `app/build/app/outputs/flutter-apk/app-release.apk`
- [x] Р”РѕР±Р°РІР»РµРЅРѕ Р»РѕРєР°Р»СЊРЅРѕРµ СЃРѕС…СЂР°РЅРµРЅРёРµ download artifacts РІ app storage
- [x] Р”РѕР±Р°РІР»РµРЅ persistent-index Р»РѕРєР°Р»СЊРЅС‹С… С„Р°Р№Р»РѕРІ РІ `app/`
- [x] РСЃРїСЂР°РІР»РµРЅ Android toolchain: `cmdline-tools` + licenses
- [x] Р”РѕР±Р°РІР»РµРЅ runtime-config backend endpoint РІ `app/`
- [x] РџРѕРґРЅСЏС‚ Р»РѕРєР°Р»СЊРЅС‹Р№ `backend/.venv`, СѓСЃС‚Р°РЅРѕРІР»РµРЅС‹ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё Рё РїСЂРѕС…РѕРґСЏС‚ smoke-С‚РµСЃС‚С‹
- [x] Р”РѕР±Р°РІР»РµРЅС‹ PowerShell helper scripts РґР»СЏ backend start/stop/health
- [x] Р”РѕР±Р°РІР»РµРЅРѕ offline-РѕС‚РєСЂС‹С‚РёРµ Рё СѓРґР°Р»РµРЅРёРµ Р»РѕРєР°Р»СЊРЅС‹С… СЃРѕС…СЂР°РЅРµРЅРЅС‹С… С„Р°Р№Р»РѕРІ
- [x] РђРєС‚РёРІРЅС‹Р№ Flutter UI РїРµСЂРµРІРµРґРµРЅ СЃ tab-shell РЅР° single-screen Telegram-style chat
- [x] РЎРѕС…СЂР°РЅРµРЅ Р°СЂС…РёРІ СЃС‚Р°СЂРѕРіРѕ РґРёР·Р°Р№РЅР° РІ `old_design/flutter_ui_v1/`
- [x] Р”РѕР±Р°РІР»РµРЅР° Р»РѕРєР°Р»СЊРЅР°СЏ persistent chat-Р»РµРЅС‚Р° РґР»СЏ bot-style РёРЅС‚РµСЂС„РµР№СЃР°
- [x] Р§Р°С‚РѕРІС‹Р№ UI РїРѕРґРѕРіРЅР°РЅ Р±Р»РёР¶Рµ Рє Telegram РїРѕ РіРµРѕРјРµС‚СЂРёРё: СѓР·РєР°СЏ РєРѕР»РѕРЅРєР°, reply-РєРЅРѕРїРєРё, composer Рё document cards
- [x] Р”Р»СЏ `Р‘Р°Р»Р°РЅСЃ / РџРѕРґРїРёСЃРєР°` РґРѕР±Р°РІР»РµРЅ Telegram-like preview-Р±Р»РѕРє РѕС„РµСЂС‚С‹ РІРЅСѓС‚СЂРё СЃРѕРѕР±С‰РµРЅРёСЏ
- [x] Р”РѕР±Р°РІР»РµРЅС‹ bot-like РєР°СЂС‚РѕС‡РєРё С„Р°Р№Р»РѕРІ СЃ РґРµР№СЃС‚РІРёСЏРјРё `РћС‚РєСЂС‹С‚СЊ` / `РЈРґР°Р»РёС‚СЊ`
- [ ] РџРѕРґРЅСЏС‚СЊ backend MVP
- [ ] РџРѕРґРЅСЏС‚СЊ Flutter MVP
- [ ] РџРµСЂРµРЅРµСЃС‚Рё РіРµРЅРµСЂР°С†РёСЋ РїСЂРµР·РµРЅС‚Р°С†РёР№
- [ ] РџРµСЂРµРЅРµСЃС‚Рё РєРѕРЅРІРµСЂС‚Р°С†РёСЋ С„Р°Р№Р»РѕРІ
- [ ] РџРµСЂРµРЅРµСЃС‚Рё РїРѕРґРїРёСЃРєРё Рё Р±РёР»Р»РёРЅРі
- [ ] РЎРѕР±СЂР°С‚СЊ iOS MVP

## Р§С‚Рѕ СЏ РїРѕРЅСЏР» РїРѕ С‚РµРєСѓС‰РµРјСѓ `telegrambot`

РўРµРєСѓС‰РёР№ Р±РѕС‚ СѓР¶Рµ СЃРѕРґРµСЂР¶РёС‚ РїРѕС‡С‚Рё РІРµСЃСЊ РїСЂРѕРґСѓРєС‚РѕРІС‹Р№ backend, С‚РѕР»СЊРєРѕ Р·Р°РІСЏР·Р°РЅРЅС‹Р№ РЅР° Telegram:

1. Р“РµРЅРµСЂР°С†РёСЏ РїСЂРµР·РµРЅС‚Р°С†РёРё:
   - РїРѕР»СЊР·РѕРІР°С‚РµР»СЊ РІРІРѕРґРёС‚ С‚РµРјСѓ;
   - РІС‹Р±РёСЂР°РµС‚ С‡РёСЃР»Рѕ СЃР»Р°Р№РґРѕРІ;
   - Р±РѕС‚ РіРµРЅРµСЂРёСЂСѓРµС‚ title + outline С‡РµСЂРµР· `KieClient`;
   - РїРѕР»СЊР·РѕРІР°С‚РµР»СЊ РїСЂРёРЅРёРјР°РµС‚ РёР»Рё СЂРµРґР°РєС‚РёСЂСѓРµС‚ РїР»Р°РЅ;
   - РІС‹Р±РёСЂР°РµС‚ РѕРґРёРЅ РёР· 4 С€Р°Р±Р»РѕРЅРѕРІ;
   - Р±РѕС‚ РіРµРЅРµСЂРёСЂСѓРµС‚ С‚РµРєСЃС‚С‹ СЃР»Р°Р№РґРѕРІ Рё РёР·РѕР±СЂР°Р¶РµРЅРёСЏ;
   - СЃРѕР±РёСЂР°РµС‚ `PPTX` С‡РµСЂРµР· `python-pptx`;
   - РєРѕРЅРІРµСЂС‚РёСЂСѓРµС‚ РІ `PDF` С‡РµСЂРµР· LibreOffice;
   - РѕС‚РґР°РµС‚ РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ РіРѕС‚РѕРІС‹Рµ С„Р°Р№Р»С‹.

2. РљРѕРЅРІРµСЂС‚Р°С†РёСЏ С„Р°Р№Р»РѕРІ:
   - `PDF -> DOCX`
   - `DOCX -> PDF`
   - `PPTX -> PDF`
   - РѕСЃРЅРѕРІРЅРѕР№ РїСѓС‚СЊ С‡РµСЂРµР· LibreOffice, fallback РґР»СЏ `PDF -> DOCX` С‡РµСЂРµР· `pdf2docx`.

3. РњРѕРЅРµС‚РёР·Р°С†РёСЏ:
   - С‚Р°СЂРёС„С‹ `week`, `month`, `one10`, `one40`;
   - РїРѕРґРїРёСЃРєРё Рё СЂР°Р·РѕРІС‹Рµ РїР°РєРµС‚С‹ РіРµРЅРµСЂР°С†РёР№;
   - `YooKassa` Рё `Telegram Stars`;
   - Р°РІС‚РѕРїСЂРѕРґР»РµРЅРёРµ СЃ `payment_method_id`;
   - Р»РѕРіРёРєР° СЃРїРёСЃР°РЅРёСЏ/РїРµСЂРµРЅРѕСЃР°/expiring СѓР¶Рµ СЂРµР°Р»РёР·РѕРІР°РЅР°.

4. Р”Р°РЅРЅС‹Рµ:
   - Р»РѕРєР°Р»СЊРЅР°СЏ `SQLite`;
   - РїРѕР»СЊР·РѕРІР°С‚РµР»Рё, РїРѕРґРїРёСЃРєРё, РіРµРЅРµСЂР°С†РёРё, РїР»Р°С‚РµР¶Рё, РїСЂРѕРјРѕРєРѕРґС‹, Р°РґРјРёРЅС‹, СЂРµРєР»Р°РјРЅС‹Рµ РјРµС‚РєРё, СЃРѕСЃС‚РѕСЏРЅРёРµ СЂР°СЃСЃС‹Р»РєРё.

5. РћРїРµСЂР°С†РёРѕРЅРЅС‹Р№ СЃР»РѕР№:
   - Р°РґРјРёРЅ-РєРѕРјР°РЅРґС‹;
   - СѓРІРµРґРѕРјР»РµРЅРёСЏ Р°РґРјРёРЅР°Рј;
   - Р°РІС‚РѕСЂР°СЃСЃС‹Р»РєР°;
   - РѕС‡РёСЃС‚РєР° РІСЂРµРјРµРЅРЅС‹С… С„Р°Р№Р»РѕРІ;
   - Docker-ready РґРµРїР»РѕР№.

Р’С‹РІРѕРґ: Р·Р°РЅРѕРІРѕ РёР·РѕР±СЂРµС‚Р°С‚СЊ РїСЂРѕРґСѓРєС‚РѕРІСѓСЋ Р»РѕРіРёРєСѓ РЅРµ РЅСѓР¶РЅРѕ. РќСѓР¶РЅРѕ РІС‹РЅРµСЃС‚Рё РµРµ РёР· Telegram-РѕР±СЂР°Р±РѕС‚С‡РёРєРѕРІ РІ РѕС‚РґРµР»СЊРЅС‹Р№ backend API Рё РґР°С‚СЊ РµР№ РЅРѕРІС‹Р№ РєР»РёРµРЅС‚ РЅР° Flutter.

## Р“Р»Р°РІРЅС‹Р№ Р°СЂС…РёС‚РµРєС‚СѓСЂРЅС‹Р№ РІС‹РІРѕРґ

РќРѕРІС‹Р№ РїСЂРѕРµРєС‚ РЅРµР»СЊР·СЏ СЃС‚СЂРѕРёС‚СЊ РєР°Рє "Flutter-РєР»РёРµРЅС‚, РєРѕС‚РѕСЂС‹Р№ СЃР°Рј РІСЃРµ РґРµР»Р°РµС‚ РЅР° СѓСЃС‚СЂРѕР№СЃС‚РІРµ".

РџСЂР°РІРёР»СЊРЅРѕРµ СЂР°Р·РґРµР»РµРЅРёРµ РґР»СЏ MVP С‚Р°РєРѕРµ:

- `app/`:
  - UI;
  - Р»РѕРєР°Р»СЊРЅР°СЏ РёСЃС‚РѕСЂРёСЏ Р·Р°РїСЂРѕСЃРѕРІ;
  - Р»РѕРєР°Р»СЊРЅС‹Р№ СЃРїРёСЃРѕРє СЃРѕР·РґР°РЅРЅС‹С… С„Р°Р№Р»РѕРІ;
  - Р»РѕРєР°Р»СЊРЅС‹Рµ С‡РµСЂРЅРѕРІРёРєРё Рё РїРѕР»СЊР·РѕРІР°С‚РµР»СЊСЃРєРёРµ РЅР°СЃС‚СЂРѕР№РєРё;
  - РїСЂРѕСЃРјРѕС‚СЂ СЃС‚Р°С‚СѓСЃР° Р·Р°РґР°С‡;
  - СЃРєР°С‡РёРІР°РЅРёРµ Рё С…СЂР°РЅРµРЅРёРµ СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ РЅР° СѓСЃС‚СЂРѕР№СЃС‚РІРµ;
  - РѕРїС†РёРѕРЅР°Р»СЊРЅРѕ РѕС„Р»Р°Р№РЅ-РґРѕСЃС‚СѓРї Рє СѓР¶Рµ СЃРѕС…СЂР°РЅРµРЅРЅС‹Рј РјР°С‚РµСЂРёР°Р»Р°Рј.

- `backend/`:
  - РѕР±СЂР°С‰РµРЅРёСЏ Рє Kie/Replicate Рё РґСЂСѓРіРёРј AI/API;
  - РіРµРЅРµСЂР°С†РёСЏ outline/title/slides;
  - РіРµРЅРµСЂР°С†РёСЏ РёР»Р»СЋСЃС‚СЂР°С†РёР№;
  - СЃР±РѕСЂРєР° `PPTX`;
  - РєРѕРЅРІРµСЂС‚Р°С†РёСЏ `PPTX/PDF/DOCX`;
  - РѕР±СЂР°Р±РѕС‚РєР° РґРѕР»РіРёС… Р·Р°РґР°С‡;
  - РјРёРЅРёРјР°Р»СЊРЅР°СЏ СЃРµСЂРІРµСЂРЅР°СЏ СѓС‡РµС‚РЅР°СЏ Р·Р°РїРёСЃСЊ/entitlement;
  - Р±РёР»Р»РёРЅРі, receipt validation, Р»РёРјРёС‚С‹, Р°РЅС‚РёР°Р±СЊСЋР·;
  - С€Р°Р±Р»РѕРЅС‹, РїСЂРѕРјРѕРєРѕРґС‹, Р°РґРјРёРЅ-С„СѓРЅРєС†РёРё.

Р’Р°Р¶РЅРѕ: "С…СЂР°РЅРёС‚СЊ РІСЃРµ Р»РѕРєР°Р»СЊРЅРѕ РЅР° СѓСЃС‚СЂРѕР№СЃС‚РІРµ" РґР»СЏ MVP СЂР°Р·СѓРјРЅРѕ С‚РѕР»СЊРєРѕ РґР»СЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЊСЃРєРѕРіРѕ РєРѕРЅС‚РµРЅС‚Р° Рё РёСЃС‚РѕСЂРёРё. Р”Р»СЏ РїРѕРґРїРёСЃРєРё, Р»РёРјРёС‚РѕРІ, РїСЂРѕРІРµСЂРєРё РѕРїР»Р°С‚ Рё job-СЃС‚Р°С‚СѓСЃРѕРІ РјРёРЅРёРјР°Р»СЊРЅС‹Р№ СЃРµСЂРІРµСЂРЅС‹Р№ state РІСЃРµ СЂР°РІРЅРѕ РЅСѓР¶РµРЅ.

## Р§С‚Рѕ РїРµСЂРµРЅРѕСЃРёРј Р±РµР· РёР·РјРµРЅРµРЅРёСЏ РёРґРµРё

РР· С‚РµРєСѓС‰РµРіРѕ Р±РѕС‚Р° РЅСѓР¶РЅРѕ СЃРѕС…СЂР°РЅРёС‚СЊ РїРѕС‡С‚Рё РѕРґРёРЅ РІ РѕРґРёРЅ:

- СЃС†РµРЅР°СЂРёР№ РіРµРЅРµСЂР°С†РёРё РїСЂРµР·РµРЅС‚Р°С†РёРё;
- С€Р°Р±Р»РѕРЅРЅС‹Р№ `PPTX`-builder;
- РєРѕРЅРІРµСЂС‚Р°С†РёСЋ С‡РµСЂРµР· LibreOffice;
- prompts Рё fallback-Р»РѕРіРёРєСѓ РґР»СЏ AI;
- СѓС‡РµС‚ РіРµРЅРµСЂР°С†РёР№ Рё С‚Р°СЂРёС„РѕРІ;
- РїСЂРѕРјРѕРєРѕРґС‹;
- Р°РґРјРёРЅ-СѓРІРµРґРѕРјР»РµРЅРёСЏ;
- С„РѕРЅРѕРІС‹Рµ РІРѕСЂРєРµСЂС‹;
- РѕС‡РёСЃС‚РєСѓ РІСЂРµРјРµРЅРЅС‹С… С„Р°Р№Р»РѕРІ;
- СЃС‚СЂСѓРєС‚СѓСЂСѓ РїСЂРѕРґСѓРєС‚РѕРІС‹С… С€Р°РіРѕРІ: `С‚РµРјР° -> РїР»Р°РЅ -> РїСЂР°РІРєР° -> РґРёР·Р°Р№РЅ -> РіРµРЅРµСЂР°С†РёСЏ -> РІС‹РґР°С‡Р°`.

## Р§С‚Рѕ РЅСѓР¶РЅРѕ РёР·РјРµРЅРёС‚СЊ РїСЂРёРЅС†РёРїРёР°Р»СЊРЅРѕ

### 1. Telegram FSM -> РјРѕР±РёР»СЊРЅС‹Рµ СЌРєСЂР°РЅС‹ Рё Р»РѕРєР°Р»СЊРЅС‹Р№ state

РЎРµР№С‡Р°СЃ СЃРѕСЃС‚РѕСЏРЅРёРµ СЃС†РµРЅР°СЂРёСЏ Р¶РёРІРµС‚ РІ `aiogram FSM`.

Р’ РЅРѕРІРѕР№ РІРµСЂСЃРёРё:

- РєР°Р¶РґС‹Р№ С€Р°Рі СЃС‚Р°РЅРµС‚ СЌРєСЂР°РЅРѕРј/СЃРѕСЃС‚РѕСЏРЅРёРµРј Flutter;
- РїСЂРѕРјРµР¶СѓС‚РѕС‡РЅС‹Р№ РїСЂРѕРіСЂРµСЃСЃ С…СЂР°РЅРёС‚СЃСЏ Р»РѕРєР°Р»СЊРЅРѕ;
- backend Р±СѓРґРµС‚ РїРѕР»СѓС‡Р°С‚СЊ СѓР¶Рµ РЅРѕСЂРјР°Р»РёР·РѕРІР°РЅРЅС‹Р№ payload, Р° РЅРµ РїРѕС‚РѕРє Telegram-СЃРѕРѕР±С‰РµРЅРёР№.

### 2. РњРѕРЅРѕР»РёС‚РЅС‹Р№ Р±РѕС‚ -> API + worker

РЎРµР№С‡Р°СЃ Telegram-Р±РѕС‚ СЃР°Рј:

- РїСЂРёРЅРёРјР°РµС‚ РІРІРѕРґ;
- С…РѕРґРёС‚ РІ AI;
- СЃРѕР±РёСЂР°РµС‚ С„Р°Р№Р»С‹;
- Р¶РґРµС‚ РєРѕРЅРІРµСЂС‚Р°С†РёСЋ;
- С€Р»РµС‚ СЂРµР·СѓР»СЊС‚Р°С‚.

Р’ РЅРѕРІРѕР№ РІРµСЂСЃРёРё:

- API РїСЂРёРЅРёРјР°РµС‚ Р·Р°РїСЂРѕСЃ;
- СЃРѕР·РґР°РµС‚ job;
- worker РІС‹РїРѕР»РЅСЏРµС‚ С‚СЏР¶РµР»СѓСЋ СЂР°Р±РѕС‚Сѓ;
- РєР»РёРµРЅС‚ РѕРїСЂР°С€РёРІР°РµС‚ СЃС‚Р°С‚СѓСЃ РёР»Рё РїРѕР»СѓС‡Р°РµС‚ push/event.

### 3. Telegram-РїР»Р°С‚РµР¶Рё -> РјРѕР±РёР»СЊРЅС‹Р№ Р±РёР»Р»РёРЅРі

РЎС…РµРјСѓ `YooKassa + Telegram Stars` РЅРµР»СЊР·СЏ РїСЂРѕСЃС‚Рѕ РїРµСЂРµРЅРµСЃС‚Рё РІ РЅР°С‚РёРІРЅС‹Рµ РїСЂРёР»РѕР¶РµРЅРёСЏ РєР°Рє РµСЃС‚СЊ.

Р”Р»СЏ РјРѕР±РёР»СЊРЅРѕРіРѕ MVP РЅСѓР¶РЅРѕ СЃСЂР°Р·Сѓ РїСЂРѕРµРєС‚РёСЂРѕРІР°С‚СЊ РѕС‚РґРµР»СЊРЅС‹Р№ billing-layer:

- iOS: `StoreKit / In-App Purchase`;
- Android: `Google Play Billing`;
- backend: РІР°Р»РёРґР°С†РёСЏ receipt/purchase token Рё РІС‹РґР°С‡Р° entitlements.

Р’РµР±-РѕРїР»Р°С‚Р° С‡РµСЂРµР· YooKassa РјРѕР¶РµС‚ РѕСЃС‚Р°С‚СЊСЃСЏ РєР°Рє РѕС‚РґРµР»СЊРЅС‹Р№ РєР°РЅР°Р» РїРѕР·Р¶Рµ, РЅРѕ РЅРµ РєР°Рє РѕСЃРЅРѕРІРЅРѕР№ РїСѓС‚СЊ РґР»СЏ РјРѕР±РёР»СЊРЅС‹С… СЃС‚РѕМЃСЂРѕРІ.

РћС„РёС†РёР°Р»СЊРЅС‹Рµ РёСЃС‚РѕС‡РЅРёРєРё РґР»СЏ СЌС‚РѕРіРѕ СЂРµС€РµРЅРёСЏ:

- Apple App Store Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Apple StoreKit / In-App Purchase overview: https://developer.apple.com/storekit/
- Google Play Billing overview: https://developer.android.com/google/play/billing

## Р¦РµР»РµРІР°СЏ Р°СЂС…РёС‚РµРєС‚СѓСЂР° MVP

### РљР»РёРµРЅС‚ `Flutter`

Р РµРєРѕРјРµРЅРґРѕРІР°РЅРЅР°СЏ СЃС‚СЂСѓРєС‚СѓСЂР°:

```text
app/
  lib/
    bootstrap/          # Р·Р°РїСѓСЃРє, РєРѕРЅС„РёРі РѕРєСЂСѓР¶РµРЅРёР№, DI
    app/                # App widget, router, theme
    core/               # network, storage, errors, constants
    data/               # DTO, repositories, local/remote data sources
    domain/             # entities, use cases
    features/
      home/
      presentation/
      converter/
      subscription/
      history/
      settings/
    shared/             # РѕР±С‰РёРµ widgets, ui kit, helpers
  assets/
    images/
    icons/
  test/
```

РџРµСЂРІС‹Р№ РЅР°Р±РѕСЂ СЌРєСЂР°РЅРѕРІ:

1. Splash / bootstrap
2. Home
3. Create presentation
4. Outline review/edit
5. Design picker
6. Generation progress
7. Result files
8. Converter
9. Subscription / paywall
10. Local history
11. Settings / support

### Backend `Python`

РћРїС‚РёРјР°Р»СЊРЅС‹Р№ РїСѓС‚СЊ РјРёРіСЂР°С†РёРё: РѕСЃС‚Р°РІРёС‚СЊ backend РЅР° Python, С‡С‚РѕР±С‹ РїРµСЂРµРёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ РєРѕРґ РёР· `telegrambot/services` РїРѕС‡С‚Рё РЅР°РїСЂСЏРјСѓСЋ.

Р РµРєРѕРјРµРЅРґРѕРІР°РЅРЅР°СЏ СЃС‚СЂСѓРєС‚СѓСЂР°:

```text
backend/
  src/
    api/               # FastAPI routers
    core/              # config, security, settings, logging
    domain/            # entities, business contracts
    integrations/      # Kie, Replicate, payments, external APIs
    jobs/              # async jobs / workers
    repositories/      # DB access
    schemas/           # Pydantic models
  tests/
  runtime/
    templates/
    temp/
```

Р РµРєРѕРјРµРЅРґРѕРІР°РЅРЅС‹Р№ СЃС‚РµРє backend:

- `FastAPI` РґР»СЏ HTTP API;
- `Pydantic` РґР»СЏ РєРѕРЅС‚СЂР°РєС‚РѕРІ;
- `Redis` РґР»СЏ РѕС‡РµСЂРµРґРё Р·Р°РґР°С‡ Рё РєСЌС€Р° СЃС‚Р°С‚СѓСЃРѕРІ;
- `PostgreSQL` РґР»СЏ РјРёРЅРёРјР°Р»СЊРЅРѕРіРѕ СЃРµСЂРІРµСЂРЅРѕРіРѕ state;
- РѕС‚РґРµР»СЊРЅС‹Р№ worker-РїСЂРѕС†РµСЃСЃ РґР»СЏ С‚СЏР¶РµР»С‹С… Р·Р°РґР°С‡;
- Docker-РґРµРїР»РѕР№ РЅР° РІР°С€ РѕР±Р»Р°С‡РЅС‹Р№ СЃРµСЂРІРµСЂ.

РџРѕС‡РµРјСѓ РЅРµ СЃС‚РѕРёС‚ РѕСЃС‚Р°РІР»СЏС‚СЊ РІСЃРµ РЅР° СЃРµСЂРІРµСЂРЅРѕР№ `SQLite`:

- РїРѕР№РґСѓС‚ РїР°СЂР°Р»Р»РµР»СЊРЅС‹Рµ mobile-Р·Р°РїСЂРѕСЃС‹;
- Р±СѓРґСѓС‚ С„РѕРЅРѕРІС‹Рµ Р·Р°РґР°С‡Рё;
- Р±СѓРґРµС‚ Р±РёР»Р»РёРЅРі Рё РёРґРµРјРїРѕС‚РµРЅС‚РЅРѕСЃС‚СЊ РѕРїР»Р°С‚;
- РїРѕР·Р¶Рµ РїРѕРЅР°РґРѕР±РёС‚СЃСЏ web Рё, РІРµСЂРѕСЏС‚РЅРѕ, Р°РґРјРёРЅ-РїР°РЅРµР»СЊ.

РџСЂРё СЌС‚РѕРј С„Р°Р№Р»С‹, РёСЃС‚РѕСЂРёСЏ Рё С‡Р°С‚С‹ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РІСЃРµ СЂР°РІРЅРѕ РјРѕР¶РЅРѕ РґРµСЂР¶Р°С‚СЊ Р»РѕРєР°Р»СЊРЅРѕ РЅР° СѓСЃС‚СЂРѕР№СЃС‚РІРµ, Р° РІ backend С…СЂР°РЅРёС‚СЊ С‚РѕР»СЊРєРѕ РјРµС‚Р°РґР°РЅРЅС‹Рµ Рё entitlement.

## Р§С‚Рѕ С…СЂР°РЅРёС‚СЃСЏ Р»РѕРєР°Р»СЊРЅРѕ, Р° С‡С‚Рѕ РЅР° СЃРµСЂРІРµСЂРµ

### Р›РѕРєР°Р»СЊРЅРѕ РІ РїСЂРёР»РѕР¶РµРЅРёРё

- РёСЃС‚РѕСЂРёСЏ С‡Р°С‚РѕРІ/Р·Р°РїСЂРѕСЃРѕРІ;
- СЃРїРёСЃРѕРє СЃРѕР·РґР°РЅРЅС‹С… РїСЂРµР·РµРЅС‚Р°С†РёР№ Рё РєРѕРЅРІРµСЂС‚Р°С†РёР№;
- Р»РѕРєР°Р»СЊРЅС‹Рµ РїСѓС‚Рё Рє С„Р°Р№Р»Р°Рј;
- РїРѕР»СЊР·РѕРІР°С‚РµР»СЊСЃРєРёРµ С‡РµСЂРЅРѕРІРёРєРё;
- РєСЌС€ С€Р°Р±Р»РѕРЅРѕРІ Рё РїСЂРµРІСЊСЋ;
- UI-РїСЂРµРґРїРѕС‡С‚РµРЅРёСЏ;
- РІСЂРµРјРµРЅРЅС‹Рµ С„Р°Р№Р»С‹ РґРѕ/РїРѕСЃР»Рµ Р·Р°РіСЂСѓР·РєРё.

### РќР° СЃРµСЂРІРµСЂРµ

- install/user id;
- active subscription / credits / entitlements;
- purchase receipts / payment records;
- job id, status, error, timestamps;
- С€Р°Р±Р»РѕРЅС‹ Рё РёС… РІРµСЂСЃРёРё;
- РїСЂРѕРјРѕРєРѕРґС‹;
- Р°РґРјРёРЅСЃРєР°СЏ Р°РЅР°Р»РёС‚РёРєР°;
- С‚РµС…Р»РѕРіРё.

### РќРµ С…СЂР°РЅРёРј РЅР° СЃРµСЂРІРµСЂРµ РІ MVP

- РїРѕР»РЅСѓСЋ РёСЃС‚РѕСЂРёСЋ РїРѕР»СЊР·РѕРІР°С‚РµР»СЊСЃРєРёС… С‡Р°С‚РѕРІ;
- Р°СЂС…РёРІ РІСЃРµС… СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ;
- РѕР±Р»Р°С‡РЅСѓСЋ РјРµРґРёР°С‚РµРєСѓ.

## РџСЂРµРґР»Р°РіР°РµРјС‹Р№ API-РєРѕРЅС‚СѓСЂ MVP

### Auth / device

- `POST /v1/devices/register`
- `POST /v1/devices/refresh`
- `GET /v1/me`

### Templates

- `GET /v1/templates/presentation`

### Presentation flow

- `POST /v1/presentations/outline`
- `POST /v1/presentations/outline/revise`
- `POST /v1/presentations/jobs`
- `GET /v1/presentations/jobs/{job_id}`
- `GET /v1/presentations/jobs/{job_id}/download/pptx`
- `GET /v1/presentations/jobs/{job_id}/download/pdf`

### Conversion flow

- `POST /v1/conversions/jobs`
- `GET /v1/conversions/jobs/{job_id}`
- `GET /v1/conversions/jobs/{job_id}/download`

### Billing

- `GET /v1/plans`
- `POST /v1/billing/ios/validate`
- `POST /v1/billing/android/validate`
- `GET /v1/subscription`
- `POST /v1/promo/activate`

### Admin later

- `GET /v1/admin/stats`
- `POST /v1/admin/templates`
- `POST /v1/admin/promocodes`

## РљР°СЂС‚Р° РјРёРіСЂР°С†РёРё: СЃС‚Р°СЂС‹Р№ РєРѕРґ -> РЅРѕРІС‹Р№ РєРѕРґ

### РџРµСЂРµРЅРѕСЃ РІ backend РїРѕС‡С‚Рё РЅР°РїСЂСЏРјСѓСЋ

- `telegrambot/services/kie_api.py`
  -> `backend/src/integrations/ai/`
- `telegrambot/services/pptx_builder.py`
  -> `backend/src/jobs/presentation_builder.py`
- `telegrambot/services/converter.py`
  -> `backend/src/jobs/file_converter.py`
- `telegrambot/services/payment.py`
  -> `backend/src/integrations/payments/legacy_reference.py`
- `telegrambot/services/auto_renew.py`
  -> `backend/src/jobs/subscription_renewal.py`
- `telegrambot/services/mailer.py`
  -> `backend/src/jobs/mailer.py`
- `telegrambot/database/models.py`
  -> `backend/src/repositories/`

### Р Р°СЃС‰РµРїР»РµРЅРёРµ Telegram handlers РЅР° client + backend

- `telegrambot/handlers/presentation_gen.py`
  -> `app/lib/features/presentation/...`
  + `backend/src/api/presentations.py`
  + `backend/src/jobs/presentation_generation.py`

- `telegrambot/handlers/file_converter.py`
  -> `app/lib/features/converter/...`
  + `backend/src/api/conversions.py`

- `telegrambot/handlers/subscription.py`
  -> `app/lib/features/subscription/...`
  + `backend/src/api/billing.py`

- `telegrambot/handlers/start.py`
  -> `app/lib/features/home/...`
  + onboarding/navigation/state bootstrap

- `telegrambot/handlers/admin.py`
  -> РїРѕРєР° РЅРµ РІ РјРѕР±РёР»СЊРЅРѕРµ РїСЂРёР»РѕР¶РµРЅРёРµ;
  -> РїРѕР·Р¶Рµ РІ РѕС‚РґРµР»СЊРЅСѓСЋ internal admin panel / web admin.

## Р­С‚Р°РїС‹ СЂРµР°Р»РёР·Р°С†РёРё

## Р­С‚Р°Рї 0. РђСЂС…РёС‚РµРєС‚СѓСЂРЅР°СЏ С„РёРєСЃР°С†РёСЏ

- [x] РР·СѓС‡РёС‚СЊ С‚РµРєСѓС‰РµРіРѕ Р±РѕС‚Р°
- [x] Р—Р°С„РёРєСЃРёСЂРѕРІР°С‚СЊ РїР»Р°РЅ
- [x] РЎРѕР·РґР°С‚СЊ РЅРѕРІСѓСЋ СЃС‚СЂСѓРєС‚СѓСЂСѓ РєР°С‚Р°Р»РѕРіРѕРІ
- [ ] РЈС‚РІРµСЂРґРёС‚СЊ СЃС‚РµРє backend Рё mobile state management

## Р­С‚Р°Рї 1. Р’С‹РЅРѕСЃ backend-СЏРґСЂР° РёР· Telegram

- [x] РЎРѕР·РґР°С‚СЊ backend-РєРѕРЅС„РёРі Рё Р±Р°Р·РѕРІС‹Р№ FastAPI skeleton
- [x] РџРµСЂРµРЅРµСЃС‚Рё prompts, AI clients, pptx builder, converter
- [x] РћС„РѕСЂРјРёС‚СЊ СЌС‚Рѕ РєР°Рє СЃРµСЂРІРёСЃС‹ Р±РµР· Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РѕС‚ Telegram objects
- [x] Р’РІРµСЃС‚Рё job model: `queued / running / done / failed`
- [x] РќР°СЃС‚СЂРѕРёС‚СЊ runtime templates/temp

Р РµР·СѓР»СЊС‚Р°С‚ СЌС‚Р°РїР°:

- backend СѓРјРµРµС‚ СЃРіРµРЅРµСЂРёСЂРѕРІР°С‚СЊ РїСЂРµР·РµРЅС‚Р°С†РёСЋ Рё РІРµСЂРЅСѓС‚СЊ Р°СЂС‚РµС„Р°РєС‚С‹ `PPTX/PDF` РїРѕ API;
- backend СѓРјРµРµС‚ РєРѕРЅРІРµСЂС‚РёСЂРѕРІР°С‚СЊ РґРѕРєСѓРјРµРЅС‚С‹;
- РґР»СЏ РґРѕР»РіРёС… РѕРїРµСЂР°С†РёР№ СѓР¶Рµ РµСЃС‚СЊ async job API СЃРѕ СЃС‚Р°С‚СѓСЃР°РјРё;
- РЅРёРєР°РєРѕР№ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РѕС‚ Telegram РІРЅСѓС‚СЂРё РїСЂРѕРґСѓРєС‚РѕРІС‹С… СЃРµСЂРІРёСЃРѕРІ РґР»СЏ РЅРѕРІРѕРіРѕ API-РєРѕРЅС‚СѓСЂР°;
- СЃР»РµРґСѓСЋС‰РёР№ С€Р°Рі РїРѕСЃР»Рµ СЃС‚Р°Р±РёР»РёР·Р°С†РёРё backend: РїРѕРґРєР»СЋС‡РµРЅРёРµ Flutter-РєР»РёРµРЅС‚Р° Рє СЌС‚РёРј async endpoints.

## Р­С‚Р°Рї 2. РњРёРЅРёРјР°Р»СЊРЅР°СЏ СЃРµСЂРІРµСЂРЅР°СЏ РјРѕРґРµР»СЊ РґР°РЅРЅС‹С…

- [ ] РЎРїСЂРѕРµРєС‚РёСЂРѕРІР°С‚СЊ `users/devices`
- [ ] РЎРїСЂРѕРµРєС‚РёСЂРѕРІР°С‚СЊ `plans/subscriptions/entitlements`
- [ ] РЎРїСЂРѕРµРєС‚РёСЂРѕРІР°С‚СЊ `jobs`
- [ ] РЎРїСЂРѕРµРєС‚РёСЂРѕРІР°С‚СЊ `payments/receipts`
- [x] Р”РѕР±Р°РІРёС‚СЊ РїСЂРѕРјРѕРєРѕРґС‹
  - `/genpromo` РІ admin-Р±РѕС‚Рµ С‚РµРїРµСЂСЊ РѕС‚РґР°С‘С‚ РіРѕС‚РѕРІСѓСЋ РєРѕРїРёСЂСѓРµРјСѓСЋ РєРѕРјР°РЅРґСѓ `/promo CODE` РґР»СЏ РїРµСЂРµСЃС‹Р»РєРё РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ
  - РјРѕР±РёР»СЊРЅС‹Р№ РєР»РёРµРЅС‚ РіР°СЃРёС‚ РїСЂРѕРјРѕРєРѕРґ С‡РµСЂРµР· СЂСѓС‡РЅРѕР№ РІРІРѕРґ СЌС‚РѕР№ РєРѕРјР°РЅРґС‹ РІ С‡Р°С‚Рµ

Р РµР·СѓР»СЊС‚Р°С‚ СЌС‚Р°РїР°:

- РµСЃС‚СЊ РјРёРЅРёРјР°Р»СЊРЅС‹Р№ СЃРµСЂРІРµСЂРЅС‹Р№ state Р±РµР· С…СЂР°РЅРµРЅРёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЊСЃРєРёС… С„Р°Р№Р»РѕРІ Рё РґР»РёРЅРЅРѕР№ РёСЃС‚РѕСЂРёРё.

## Р­С‚Р°Рї 3. Flutter foundation

- [x] РЎРѕР·РґР°С‚СЊ СЂСѓС‡РЅРѕР№ Flutter scaffold РІРЅСѓС‚СЂРё `app/`
- [x] РќР°СЃС‚СЂРѕРёС‚СЊ Р±Р°Р·РѕРІС‹Р№ shell/navigation
- [x] РќР°СЃС‚СЂРѕРёС‚СЊ С‚РµРјСѓ Рё Р±Р°Р·РѕРІС‹Рµ СЌРєСЂР°РЅС‹
- [x] РџРѕРґРЅСЏС‚СЊ СЂРµР°Р»СЊРЅС‹Р№ Flutter SDK-РїСЂРѕРµРєС‚ РєРѕРјР°РЅРґРѕР№ `flutter pub get`
- [x] РќР°СЃС‚СЂРѕРёС‚СЊ HTTP client
- [x] РќР°СЃС‚СЂРѕРёС‚СЊ Р»РѕРєР°Р»СЊРЅРѕРµ С…СЂР°РЅРёР»РёС‰Рµ
- [x] РќР°СЃС‚СЂРѕРёС‚СЊ Р±Р°Р·РѕРІС‹Р№ DI/state management

Р РµРєРѕРјРµРЅРґР°С†РёСЏ:

- state management: `Riverpod`;
- local storage: `Drift` РёР»Рё `Hive/Isar` РґР»СЏ MVP;
- networking: `Dio`.

## Р­С‚Р°Рї 4. Р­РєСЂР°РЅ РіРµРЅРµСЂР°С†РёРё РїСЂРµР·РµРЅС‚Р°С†РёРё

- [x] Р­РєСЂР°РЅ РІРІРѕРґР° С‚РµРјС‹
- [x] Р’С‹Р±РѕСЂ РєРѕР»РёС‡РµСЃС‚РІР° СЃР»Р°Р№РґРѕРІ
- [x] Preview outline
- [x] Р СѓС‡РЅРѕРµ СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёРµ outline
- [x] Р’С‹Р±РѕСЂ РґРёР·Р°Р№РЅР°
- [x] Р­РєСЂР°РЅ РїСЂРѕРіСЂРµСЃСЃР° job
- [x] Р­РєСЂР°РЅ СЂРµР·СѓР»СЊС‚Р°С‚Р° Рё СЃРєР°С‡РёРІР°РЅРёСЏ С„Р°Р№Р»РѕРІ

## Р­С‚Р°Рї 5. Р­РєСЂР°РЅ РєРѕРЅРІРµСЂС‚Р°С†РёРё С„Р°Р№Р»РѕРІ

- [x] Р’С‹Р±РѕСЂ С„Р°Р№Р»Р°
- [x] Р’С‹Р±РѕСЂ С†РµР»РµРІРѕРіРѕ С„РѕСЂРјР°С‚Р°
- [x] Р—Р°РіСЂСѓР·РєР° РЅР° backend
- [x] РЎС‚Р°С‚СѓСЃ job
- [x] РЎРєР°С‡РёРІР°РЅРёРµ СЂРµР·СѓР»СЊС‚Р°С‚Р°
- [x] РЎРѕС…СЂР°РЅРµРЅРёРµ РІ Р»РѕРєР°Р»СЊРЅСѓСЋ РёСЃС‚РѕСЂРёСЋ

## Р­С‚Р°Рї 6. РџРѕРґРїРёСЃРєРё Рё РїР»Р°С‚РµР¶Рё

- [ ] РЈС‚РІРµСЂРґРёС‚СЊ store-СЃС‚СЂР°С‚РµРіРёСЋ
- [ ] Р РµР°Р»РёР·РѕРІР°С‚СЊ `plans` API
- [ ] Р РµР°Р»РёР·РѕРІР°С‚СЊ paywall РІ РїСЂРёР»РѕР¶РµРЅРёРё
- [ ] Р РµР°Р»РёР·РѕРІР°С‚СЊ receipt validation РЅР° backend
- [ ] Р РµР°Р»РёР·РѕРІР°С‚СЊ restore purchases
- [ ] Р РµР°Р»РёР·РѕРІР°С‚СЊ entitlement sync

РљСЂРёС‚РёС‡РЅРѕ:

- РЅРµ РїРµСЂРµРЅРѕСЃРёС‚СЊ Telegram Stars РІ РјРѕР±РёР»СЊРЅРѕРµ РїСЂРёР»РѕР¶РµРЅРёРµ;
- РЅРµ СЃС‚СЂРѕРёС‚СЊ iOS MVP РІРѕРєСЂСѓРі РїСЂСЏРјРѕР№ YooKassa-РѕРїР»Р°С‚С‹ С†РёС„СЂРѕРІРѕРіРѕ РєРѕРЅС‚РµРЅС‚Р° РІРЅСѓС‚СЂРё app.

## Р­С‚Р°Рї 7. Р›РѕРєР°Р»СЊРЅР°СЏ РёСЃС‚РѕСЂРёСЏ Рё С„Р°Р№Р»РѕРІС‹Р№ РјРµРЅРµРґР¶РјРµРЅС‚

- [x] РўР°Р±Р»РёС†Р° Р»РѕРєР°Р»СЊРЅРѕР№ РёСЃС‚РѕСЂРёРё Р·Р°РїСЂРѕСЃРѕРІ
- [x] РўР°Р±Р»РёС†Р° Р»РѕРєР°Р»СЊРЅС‹С… С„Р°Р№Р»РѕРІ
- [x] РџРѕРІС‚РѕСЂРЅРѕРµ РѕС‚РєСЂС‹С‚РёРµ СЂРµР·СѓР»СЊС‚Р°С‚Р° Р±РµР· СЃРµСЂРІРµСЂР°
- [x] РЈРґР°Р»РµРЅРёРµ Р»РѕРєР°Р»СЊРЅС‹С… РјР°С‚РµСЂРёР°Р»РѕРІ
- [ ] РћРіСЂР°РЅРёС‡РµРЅРёРµ РєСЌС€Р° Рё TTL

## Р­С‚Р°Рї 8. РўРµСЃС‚РёСЂРѕРІР°РЅРёРµ MVP

- [x] Smoke backend
- [ ] Smoke Flutter Android РЅР° СЌРјСѓР»СЏС‚РѕСЂРµ/СѓСЃС‚СЂРѕР№СЃС‚РІРµ
- [ ] Smoke Flutter iOS
- [x] Smoke Flutter Web
- [x] Smoke Flutter analyze/test
- [ ] Р“РµРЅРµСЂР°С†РёСЏ 10+ РїСЂРµР·РµРЅС‚Р°С†РёР№ РїРѕРґСЂСЏРґ
- [ ] РљРѕРЅРІРµСЂС‚Р°С†РёСЏ Р±РѕР»СЊС€РёС… С„Р°Р№Р»РѕРІ
- [ ] РћС€РёР±РєРё AI Рё retry
- [ ] РџРѕС‚РµСЂСЏ СЃРµС‚Рё РІ СЃРµСЂРµРґРёРЅРµ job
- [ ] Restore subscription РїРѕСЃР»Рµ РїРµСЂРµСѓСЃС‚Р°РЅРѕРІРєРё

## Р­С‚Р°Рї 9. РџРѕСЃР»Рµ MVP

- [ ] Web build РЅР° Flutter
- [ ] Cloud sync РёСЃС‚РѕСЂРёРё
- [ ] РћР±Р»Р°С‡РЅРѕРµ С…СЂР°РЅРµРЅРёРµ СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ С‡РµСЂРµР· Cloudflare
- [ ] Internal admin panel
- [ ] РђРЅР°Р»РёС‚РёРєР° СЃРѕР±С‹С‚РёР№
- [ ] Push notifications РїРѕ Р·Р°РІРµСЂС€РµРЅРёСЋ job

## РљР»СЋС‡РµРІС‹Рµ СЂРёСЃРєРё

### Р РёСЃРє 1. РџР»Р°С‚РµР¶Рё РІ mobile stores

Р­С‚Рѕ РЅРµ РєРѕСЃРјРµС‚РёС‡РµСЃРєРёР№ РІРѕРїСЂРѕСЃ, Р° Р°СЂС…РёС‚РµРєС‚СѓСЂРЅС‹Р№. Р•СЃР»Рё Р·Р°Р»РѕР¶РёС‚СЊ РЅРµ С‚Сѓ РїР»Р°С‚РµР¶РЅСѓСЋ СЃС…РµРјСѓ, РїРѕС‚РѕРј РїСЂРёРґРµС‚СЃСЏ РїРµСЂРµРїРёСЃС‹РІР°С‚СЊ paywall, backend entitlements Рё release-РїСЂРѕС†РµСЃСЃ.

### Р РёСЃРє 2. РЎРјРµС€РµРЅРёРµ Р»РѕРєР°Р»СЊРЅРѕРіРѕ С…СЂР°РЅРµРЅРёСЏ Рё СЃРµСЂРІРµСЂРЅРѕР№ РїРѕРґРїРёСЃРєРё

Р•СЃР»Рё РІРѕРѕР±С‰Рµ РЅРµ С…СЂР°РЅРёС‚СЊ СЃРµСЂРІРµСЂРЅС‹Р№ entitlement, РїСЂРёР»РѕР¶РµРЅРёРµ Р»РµРіРєРѕ Р±СѓРґРµС‚ Р»РѕРјР°С‚СЊ РёР»Рё СЂР°СЃСЃРёРЅС…СЂРѕРЅРёР·РёСЂРѕРІР°С‚СЊ.

### Р РёСЃРє 3. Р”РѕР»РіРёРµ Р·Р°РґР°С‡Рё

Р“РµРЅРµСЂР°С†РёСЏ РїСЂРµР·РµРЅС‚Р°С†РёРё Рё РєРѕРЅРІРµСЂС‚Р°С†РёСЏ С„Р°Р№Р»РѕРІ РЅРµ РґРѕР»Р¶РЅС‹ Р¶РёС‚СЊ РІ request-response Р±РµР· job layer.

### Р РёСЃРє 4. РЎР»РёС€РєРѕРј СЂР°РЅРЅРёР№ СЃС‚Р°СЂС‚ СЃ web

РЎРµР№С‡Р°СЃ РїСЂР°РІРёР»СЊРЅРµРµ СЃРЅР°С‡Р°Р»Р° РґРѕРІРµСЃС‚Рё mobile MVP, РїРѕС‚РѕРј РѕС‚РєСЂС‹РІР°С‚СЊ web.

## Р РµС€РµРЅРёСЏ, РєРѕС‚РѕСЂС‹Рµ СЏ РїСЂРµРґР»Р°РіР°СЋ Р·Р°С„РёРєСЃРёСЂРѕРІР°С‚СЊ СЃРµР№С‡Р°СЃ

1. Backend РґРµР»Р°РµРј РЅР° Python, Р° РЅРµ РїРµСЂРµРїРёСЃС‹РІР°РµРј РІСЃРµ Р·Р°РЅРѕРІРѕ РЅР° РґСЂСѓРіРѕР№ СЏР·С‹Рє.
2. Р“РµРЅРµСЂР°С†РёСЏ, РєРѕРЅРІРµСЂС‚Р°С†РёСЏ, AI Рё Р±РёР»Р»РёРЅРі Р¶РёРІСѓС‚ РЅР° СЃРµСЂРІРµСЂРµ.
3. РСЃС‚РѕСЂРёСЏ, С‡РµСЂРЅРѕРІРёРєРё Рё С„Р°Р№Р»С‹ СЂРµР·СѓР»СЊС‚Р°С‚Р° С…СЂР°РЅСЏС‚СЃСЏ Р»РѕРєР°Р»СЊРЅРѕ РЅР° СѓСЃС‚СЂРѕР№СЃС‚РІРµ.
4. Р”Р»СЏ РјРѕР±РёР»СЊРЅС‹С… РѕРїР»Р°С‚ РїСЂРѕРµРєС‚РёСЂСѓРµРј РѕС‚РґРµР»СЊРЅС‹Р№ store billing layer.
5. `telegrambot/` РЅРµ Р»РѕРјР°РµРј; РѕРЅ РѕСЃС‚Р°РµС‚СЃСЏ СЂРµС„РµСЂРµРЅСЃРѕРј Рё РґРѕРЅРѕСЂРѕРј Р»РѕРіРёРєРё РґРѕ РїРѕР»РЅРѕР№ РјРёРіСЂР°С†РёРё.

## Р§С‚Рѕ РґРµР»Р°С‚СЊ СЃР»РµРґСѓСЋС‰РёРј С€Р°РіРѕРј

РЎР»РµРґСѓСЋС‰РёР№ РїСЂР°РєС‚РёС‡РµСЃРєРёР№ Р±Р»РѕРє РїРѕСЃР»Рµ С‚РµРєСѓС‰РµРіРѕ СЃРѕСЃС‚РѕСЏРЅРёСЏ:

1. РџСЂРѕРіРЅР°С‚СЊ `flutter run` РЅР° Android-СЌРјСѓР»СЏС‚РѕСЂРµ РёР»Рё С‚РµР»РµС„РѕРЅРµ СЃ СЂРµР°Р»СЊРЅС‹РјРё `Presentation` / `Converter` flows РїРѕРІРµСЂС… СѓР¶Рµ РїРѕРґРЅСЏС‚РѕРіРѕ Р»РѕРєР°Р»СЊРЅРѕРіРѕ backend.
2. РџРѕСЃР»Рµ smoke РЅР° Android РїРµСЂРµР№С‚Рё Рє РїРѕРґРїРёСЃРєР°Рј, paywall Рё server-side entitlement model.
3. Р”РѕР±РёС‚СЊ РѕРіСЂР°РЅРёС‡РµРЅРёРµ РєСЌС€Р° Рё TTL РґР»СЏ Р»РѕРєР°Р»СЊРЅС‹С… СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ.
4. Р’РєР»СЋС‡РёС‚СЊ Windows Developer Mode, РµСЃР»Рё РїРѕРЅР°РґРѕР±РёС‚СЃСЏ РїРѕР»РЅРѕС†РµРЅРЅС‹Р№ `flutter build windows`.
5. РџРѕСЃР»Рµ mobile MVP РѕС‚РґРµР»СЊРЅРѕ СЂРµС€Р°С‚СЊ web-specific UX Рё cloud sync.

Р­С‚Рѕ СѓР¶Рµ РїСЂР°РІРёР»СЊРЅС‹Р№ СЃР»РµРґСѓСЋС‰РёР№ С€Р°Рі, РїРѕС‚РѕРјСѓ С‡С‚Рѕ backend-РєРѕРЅС‚СѓСЂ РіРµРЅРµСЂР°С†РёРё Рё РєРѕРЅРІРµСЂС‚Р°С†РёРё СЃРѕР±СЂР°РЅ, РёРјРµРµС‚ download routes, РїРѕРєСЂС‹С‚ Р±Р°Р·РѕРІС‹Рј smoke-РЅР°Р±РѕСЂРѕРј, Р° `app/` СѓР¶Рµ РёРјРµРµС‚ DI, presentation flow, converter flow, Р»РѕРєР°Р»СЊРЅСѓСЋ persistent-history, Р»РѕРєР°Р»СЊРЅС‹Р№ С„Р°Р№Р»РѕРІС‹Р№ РёРЅРґРµРєСЃ, СЂР°Р±РѕС‡РёР№ Flutter runtime Рё РїРѕРґРіРѕС‚РѕРІР»РµРЅРЅС‹Р№ Android toolchain.
