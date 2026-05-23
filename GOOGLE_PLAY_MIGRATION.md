# Google Play Migration Plan

This document tracks the Android Google Play version of the AppSlides mobile app.

## Product Decision

- Google Play package name: `com.appslides.slideai`.
- Store display language: English first.
- Upload format: Android App Bundle (`.aab`), not APK, for the Play Console production/internal tracks.
- Billing model: Google Play Billing subscriptions and/or in-app products instead of YooKassa.
- RuStore/YooKassa flow must not be shown in the Google Play build.

## Official Rules Used

- Google Play requires new apps to publish with Android App Bundles. Google Play then generates optimized APKs for devices from the uploaded bundle.
- For digital goods and in-app features distributed through Google Play, Google Play Billing is the default required payment system unless a policy exception applies.
- Google Billing purchase flow must be verified before granting benefits:
  - show products;
  - launch purchase flow;
  - verify purchase on backend;
  - grant entitlement;
  - acknowledge the purchase.
- For subscriptions, backend should stay in sync through Google Play Developer API and Real-time Developer Notifications (RTDN) where possible.

Source links:

- Android App Bundles: https://developer.android.com/guide/app-bundle
- Google Play Billing integration: https://developer.android.com/google/play/billing/integrate
- Google Play Billing backend integration: https://developer.android.com/google/play/billing/backend
- Purchase lifecycle and RTDN: https://developer.android.com/google/play/billing/lifecycle
- Google Play payments policy: https://support.google.com/googleplay/android-developer/answer/9858738

## Current Prep Done

- Android `namespace` changed to `com.appslides.slideai`.
- Android `applicationId` changed to `com.appslides.slideai`.
- Kotlin `MainActivity` package moved to `com.appslides.slideai`.
- Android launcher label changed to `Slide AI`.
- Flutter build number incremented to `0.1.0+10`.
- Release signing scaffold added through `app/android/key.properties`.
- `app/android/key.properties` and keystore files are ignored by Git; only `app/android/key.properties.example` is committed.
- Fixed backend URL changed to the separate PM backend: `http://185.171.83.116:8021`.
- Backend presentation prompts and fallback text are now English-first for the PM/Google Play backend.
- Flutter dependency `in_app_purchase` added.
- Client-side Google Play purchase flow scaffold added:
  - loads Play products;
  - starts purchase flow;
  - sends product ID, package name and purchase token to backend;
  - completes purchase only after backend verification succeeds.
- Backend verification endpoint scaffold added:
  - `POST /v1/billing/google-play/verify`;
  - validates package name;
  - maps Play product IDs to existing tariff keys;
  - verifies subscription token through Google Play Developer API when service account is configured;
  - grants existing AppSlides entitlement after successful verification;
  - acknowledges the Google Play purchase after granting entitlement.

## Build Commands

For local APK testing:

```powershell
cd app
flutter build apk --release
```

For Google Play upload:

```powershell
cd app
flutter build appbundle --release
```

Expected Play artifact:

```text
app/build/app/outputs/bundle/release/app-release.aab
```

Important: Google Play requires a properly signed release bundle. The current project still uses debug signing for release builds, so release signing must be configured before uploading to Play Console.

Release signing setup:

1. Generate or receive the upload keystore.
2. Put it under `app/android/`, for example `app/android/upload-keystore.jks`.
3. Copy `app/android/key.properties.example` to `app/android/key.properties`.
4. Fill real passwords and alias in `key.properties`.
5. Rebuild the AAB.

`key.properties` and keystore files must never be committed.

## Required Play Console Setup

1. Create the app in Play Console with package name `com.appslides.slideai`.
2. Enable Play App Signing.
3. Create an upload key and configure Flutter/Gradle release signing.
4. Create subscription products/base plans in Play Console.
5. Add license testers and use internal testing before production.
6. Prepare English store listing:
   - app name;
   - short description;
   - full description;
   - screenshots;
   - icon/feature graphic if required;
   - privacy policy URL;
   - data safety form;
   - content rating questionnaire.

## Proposed Product IDs

Final IDs must be created in Play Console before code wiring.

- `slide_ai_week`: weekly subscription.
- `slide_ai_month`: monthly subscription.

Current YooKassa tariffs can map to Google Play subscriptions:

- `week`: weekly access and generation limit.
- `month`: monthly access and generation limit.

If Google Play product IDs differ, update the mapping in the app and backend together.

## Client Migration Tasks

1. Add Flutter Google Billing dependency.
   - Preferred package: `in_app_purchase` with Android support through Google Play Billing.
2. Replace YooKassa invoice-opening flow in chat with native Google purchase flow.
3. Query available subscriptions from Google Play before showing tariff buttons.
4. Start purchase through Play Billing when user taps a plan.
5. Send purchase token, product ID and package name to backend.
6. Restore purchases on app startup/resume.
7. Hide external payment texts:
   - YooKassa;
   - offer checkout link;
   - external browser payment instructions.
8. Translate customer-facing UI/messages to English for the Google Play build.

## Backend Migration Tasks

1. Add provider mode, for example `BILLING_PROVIDER=google_play|yookassa`.
2. Keep existing entitlement model (`client_id`, subscriptions, remaining generations), but add Google purchase fields:
   - package name;
   - product ID;
   - purchase token;
   - order ID;
   - subscription/base plan metadata where available.
3. Add endpoint for purchase verification:

```text
POST /v1/billing/google-play/verify
```

Request should include:

```json
{
  "package_name": "com.appslides.slideai",
  "product_id": "slide_ai_week",
  "purchase_token": "...",
  "client_id": "as_..."
}
```

4. Verify token with Google Play Developer API on the backend before granting generations. Done as scaffold, pending real service-account credentials.
5. Acknowledge successful purchases after entitlement is granted. Done as scaffold.
6. Add RTDN handler later for renewals, cancellations, grace period, hold and expiry.
7. Send admin Telegram notifications for Google Play events the same way YooKassa events are sent now. Initial purchase success notification is wired.

## Backend Env For Google Play

```env
GOOGLE_PLAY_PACKAGE_NAME=com.appslides.slideai
GOOGLE_PLAY_SERVICE_ACCOUNT_FILE=
GOOGLE_PLAY_SERVICE_ACCOUNT_JSON=
GOOGLE_PLAY_TEST_MODE=0
```

Use one credential option:

- `GOOGLE_PLAY_SERVICE_ACCOUNT_FILE`: path to JSON on the server.
- `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON`: full JSON content in env.

The service account must have access to the Play Console app and Android Publisher API.

## Backend Compatibility Rule

The RuStore/YooKassa build and Google Play build should not be mixed in one runtime flow. The clean target is:

- RuStore build: YooKassa endpoints and Russian payment copy.
- Google Play build: Google Play Billing endpoints and English payment copy.

The Google Play backend is deployed separately to `/root/PMappslides` on port `8021`. Do not overwrite `/root/appslides` and do not reuse the RuStore admin Telegram bot token in this stack.

## Release Blocking Items

- Release signing scaffold exists, but the real upload keystore/passwords are not configured yet.
- Google Play subscription product IDs are not known yet.
- Google Play Developer API service account is not configured yet.
- RTDN Pub/Sub is not configured yet.
- UI text is still mostly Russian.
- Google Play verification code exists, but cannot be validated end-to-end until the app, products and test users exist in Play Console.
