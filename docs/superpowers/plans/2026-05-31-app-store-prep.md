# App Store Prep Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare the AppSlides Flutter/backend copy for an App Store/TestFlight track without requiring Apple secrets until signing and upload.

**Architecture:** Keep Android Google Play billing intact and add a separate `app_store` provider path for iOS. The Flutter app selects billing behavior by platform/config, while the backend exposes Apple-specific verification/restore/notification endpoints with testable stubs and clear env requirements.

**Tech Stack:** Flutter/Dart, `in_app_purchase`, iOS/Xcode project files, FastAPI/Python, SQLite repositories, pytest, App Store Server API-ready configuration.

---

### Task 1: iOS Shell Readiness

**Files:**
- Create: `app/ios/Podfile`
- Modify: `app/ios/Runner/Info.plist`
- Modify: `app/ios/Runner.xcodeproj/project.pbxproj`
- Modify: `app/pubspec.yaml`
- Verify: `flutter pub get`, `flutter analyze`

- [x] Add a standard Flutter iOS `Podfile` with iOS platform 13.0 and generated plugin support.
- [x] Set iOS Bundle ID to `com.appslides.slideai` for Runner and `com.appslides.slideai.RunnerTests` for tests.
- [x] Set iOS display name to `Slide AI`.
- [x] Increment Flutter build version above the current `0.1.0+13`.
- [x] Leave Apple signing team empty until Apple Developer account data is available.
- [ ] Run Flutter dependency and analyzer checks.

### Task 2: Flutter Billing Provider Split

**Files:**
- Modify: `app/lib/core/config/app_config.dart`
- Create: `app/lib/features/billing/store_billing_service.dart`
- Modify: `app/lib/features/billing/google_play_billing_service.dart`
- Modify: `app/lib/features/billing/billing_controller.dart`
- Modify: `app/lib/data/api/appslides_api_client.dart`
- Modify: `app/lib/data/repositories/appslides_repository.dart`
- Modify: `app/lib/domain/models/billing_payment.dart`
- Test: `app/test/billing_provider_test.dart`

- [x] Add `app_store` as a supported billing provider.
- [x] Add Apple product IDs for `slide_ai_week` and `slide_ai_month`.
- [x] Add `/v1/billing/app-store/verify` and `/v1/billing/app-store/restore` client calls.
- [x] Keep existing Google Play flow unchanged on Android.
- [x] Add an App Store purchase service using `in_app_purchase` product details and verification payloads.
- [x] Add tests for provider selection and product mapping where possible on Windows.

### Task 3: Backend Apple IAP Skeleton

**Files:**
- Modify: `backend/src/core/settings.py`
- Create: `backend/src/integrations/app_store_gateway.py`
- Modify: `backend/src/domain/billing_plans.py`
- Modify: `backend/src/domain/billing_service.py`
- Modify: `backend/src/api/billing.py`
- Modify: `backend/src/schemas/billing.py`
- Test: `backend/tests/test_app_store_billing.py`

- [x] Add Apple env settings: bundle id, app apple id, issuer id, key id, private key/file, environment, test mode.
- [x] Add an App Store gateway with a deterministic test mode and explicit “not configured” errors.
- [x] Add plan lookup by Apple product ID.
- [x] Add `verify_app_store_purchase`, `restore_app_store_purchase`, and notifications entry point.
- [x] Reuse existing billing tables for MVP by storing Apple transaction IDs in generic payment fields.
- [x] Add pytest coverage for configured/unconfigured/test verification paths.

### Task 4: App Store Operations Docs

**Files:**
- Modify: `APP_STORE_RESEARCH.md`
- Modify: `OPERATIONS.md`
- Modify: `README.md`
- Modify: `app/README.md`
- Modify: `backend/README.md`
- Create: `docs/store/app_store_listing.md`

- [x] Promote fixed App Store decisions from research into operations docs.
- [x] Document Apple keys requested only at signing/upload/backend verification stage.
- [x] Document macOS/Codemagic commands for `flutter build ipa`.
- [x] Add App Store metadata draft, subscription texts, and review notes.
- [x] Keep paths project-relative so this folder can be moved.

### Task 5: Verification

**Commands:**
- `python -m pytest backend/tests/test_app_store_billing.py backend/tests/test_google_play_billing.py backend/tests/test_billing_service.py`
- `python -m pytest backend/tests`
- `flutter pub get`
- `flutter analyze`
- `flutter test`

- [x] Run focused backend tests.
- [x] Run full backend tests if focused tests pass.
- [x] Run Flutter dependency, analyzer, and widget tests.
- [x] Record any Windows-only iOS limitations clearly in the final report.
