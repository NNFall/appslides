# Operations

## Canonical Workflow

After every large or important change:

1. Run local checks that match the changed area.
2. Commit the project state to Git.
3. Push the current branch to GitHub.
4. If backend files changed, redeploy the server and restart the container.
5. Update the project docs and plan if the runtime flow, deployment flow, or product behavior changed.

## GitHub Repository

- Repository: `https://github.com/NNFall/appslides`
- Local root: repository root

## Backend Runtime

- Server IP: `185.171.83.116`
- SSH user: `root`
- Remote app dir: `/root/PMappslides`
- Public backend endpoint: `http://185.171.83.116:8021`
- Docker service: `appslides_backend`
- Docker container: `pmappslides_backend`

## Standard Git Flow

```powershell
git status -sb
git add .
git commit -m "short meaningful message"
git push -u origin main
```

If work is already on an existing branch:

```powershell
git status -sb
git add .
git commit -m "short meaningful message"
git push
```

## Standard Backend Deploy

```powershell
python scripts\deploy\deploy_backend_remote.py `
  --host 185.171.83.116 `
  --user root `
  --password <SERVER_PASSWORD> `
  --port 22 `
  --remote-dir /root/PMappslides `
  --host-port 8021
```

The deploy script:

- uploads `backend/`, `telegram_admin_bot/`, `templates/`, `docker-compose.yml` and `.env`
- keeps persistent data outside the container
- rebuilds and restarts Docker Compose
- expects the public port to remain `8021`
- starts only backend unless `PM_ADMIN_BOT_TOKEN` is set locally; this avoids breaking the existing RuStore admin bot by reusing the same Telegram token

## Runtime Temp Cleanup

The backend creates temporary files for uploads, conversions and presentation rendering under `TEMP_DIR`.

Production mapping:

- container path: `/app/runtime/temp`
- host path: `/root/appslides/temp`
- cleanup buckets: `uploads/`, `conversions/`, `presentations/`

Cleanup is performed by the backend itself, not by the old Telegram bot. The loop starts with `appslides_backend` and deletes expired entries according to:

- `TEMP_TTL_SECONDS`: how long temp files live
- `TEMP_CLEAN_INTERVAL`: how often the cleanup loop runs

Current production deploy passes these values from local env when available. The legacy bot env currently provides `TEMP_TTL_SECONDS=3600` and `TEMP_CLEAN_INTERVAL=600`, so production temp artifacts are removed after about 1 hour.

When cleanup removes temp folders/files, it also deletes matching rows from the backend `artifacts` table. It only touches `TEMP_DIR/uploads`, `TEMP_DIR/conversions` and `TEMP_DIR/presentations`; it must not touch templates, fonts, the database, Docker data or logs.

Useful read-only checks:

```bash
du -xh --max-depth=2 /root/appslides/temp 2>/dev/null | sort -h | tail -50
docker compose logs --tail=200 appslides_backend
```

Expected successful log line:

```text
Temp cleanup removed dirs=<n> files=<n> artifact_rows=<n>
```

## Server Disk Diagnostics

`/var` is the standard Linux directory for variable runtime data: service logs, systemd journal, package cache, Docker/containerd image layers, container writable data and other service state.

Current server disk pressure is mainly from:

- `/var/lib/containerd`: Docker/containerd image layers and build-related content
- `/var/log/journal`: systemd journal logs
- `/root/appslides/temp`: application temp files, now covered by backend cleanup

Do not delete these blindly. Safe candidates after confirmation:

- Docker build cache: `docker builder prune`
- old unused Docker resources: inspect with `docker system df` first
- systemd journal retention: `journalctl --vacuum-size=1G`

Docker cache pruning should not stop running containers, but future builds can be slower because layers need to be downloaded or rebuilt again.

## App Store / iOS Track

Current App Store copy: `ASappslides`.

Fixed iOS decisions:

- Bundle ID: `com.appslides.slideai`
- Display name: `Slide AI`
- Flutter billing provider for iOS: `app_store`
- App Store product IDs:
  - `slide_ai_week`
  - `slide_ai_month`

iOS privacy manifest:

- File: `app/ios/Runner/PrivacyInfo.xcprivacy`
- It is included in the `Runner` target resources.
- It declares no tracking and no collected data in the manifest itself.
- It declares required-reason API usage for app-local preferences and local file metadata:
  - `NSPrivacyAccessedAPICategoryUserDefaults` with reason `CA92.1`
  - `NSPrivacyAccessedAPICategoryFileTimestamp` with reason `C617.1`
- Before any TestFlight/App Store build, run:

```powershell
python scripts\validate_ios_privacy_manifest.py
```

App Store Connect privacy labels are still separate from this file. They must describe the real product behavior: presentation prompts and uploaded files go to the backend/AI services, a pseudonymous client ID is used for billing/entitlements, and purchases are processed through Apple IAP for the iOS build.

Backend endpoints added for Apple IAP:

```text
POST /v1/billing/app-store/verify
POST /v1/billing/app-store/restore
POST /v1/billing/app-store/notifications
```

Required backend env for real App Store Server API:

```text
APP_STORE_BUNDLE_ID=com.appslides.slideai
APP_STORE_APP_APPLE_ID=
APP_STORE_ISSUER_ID=
APP_STORE_KEY_ID=
APP_STORE_PRIVATE_KEY=
APP_STORE_PRIVATE_KEY_FILE=
APP_STORE_ENVIRONMENT=sandbox
APP_STORE_TEST_MODE=0
```

Local tests can use `APP_STORE_TEST_MODE=1`; production must use Apple keys from App Store Connect. Do not commit `.p8` keys.

macOS/Codemagic build command:

```bash
cd app
flutter pub get
cd ios && pod install && cd ..
flutter build ios \
  --release \
  --no-codesign \
  --dart-define=APPSLIDES_BILLING_PROVIDER=app_store \
  --dart-define=APPSLIDES_APP_STORE_WEEK_PRODUCT_ID=slide_ai_week \
  --dart-define=APPSLIDES_APP_STORE_MONTH_PRODUCT_ID=slide_ai_month

flutter build ipa \
  --dart-define=APPSLIDES_BILLING_PROVIDER=app_store \
  --dart-define=APPSLIDES_APP_STORE_WEEK_PRODUCT_ID=slide_ai_week \
  --dart-define=APPSLIDES_APP_STORE_MONTH_PRODUCT_ID=slide_ai_month
```

Windows limitation: local Windows can run Flutter analyzer/tests and backend tests, but cannot produce the final signed `.ipa`.

Codemagic scaffold:

- Config file: `codemagic.yaml` in the repository root.
- Workflow: `ios-testflight-scaffold`.
- Placeholder env groups: `codemagic_app_store_connect` and `codemagic_ios_signing`.
- Required encrypted App Store Connect variables: `APP_STORE_CONNECT_PRIVATE_KEY`, `APP_STORE_CONNECT_KEY_IDENTIFIER`, `APP_STORE_CONNECT_ISSUER_ID`.
- Required signing setup: Apple Distribution certificate and App Store provisioning profile/signing access for `com.appslides.slideai`.
- The workflow runs `flutter analyze`, `flutter test`, and passes Codemagic `BUILD_NUMBER` into `flutter build ipa` so every upload can have a larger iOS build number.
- The scaffold builds a signed `.ipa` but keeps `submit_to_testflight=false` and `submit_to_app_store=false` until manual review of App Store Connect metadata is complete.
- Before review, verify the App Store build has the **Restore App Store purchase** button in Balance / Subscription and that it refreshes entitlement state after reinstall/device change.

Do not store `.p8`, `.p12`, `.cer`, `.mobileprovision`, provisioning profiles, generated `.ipa`, `.xcarchive`, or dSYM archives in Git.

## Local Validation Before Push

### Backend

```powershell
python -m unittest discover -s backend/tests -v
python -m compileall backend/src
```

### Admin Telegram Bot

```powershell
python -m compileall telegram_admin_bot
python -c "import telegram_admin_bot.main; print('admin bot import ok')"
```

### Flutter App

```powershell
& 'C:\Users\User\develop\flutter\bin\flutter.bat' pub get
& 'C:\Users\User\develop\flutter\bin\flutter.bat' analyze
& 'C:\Users\User\develop\flutter\bin\flutter.bat' test
& 'C:\Users\User\develop\flutter\bin\flutter.bat' build web
& 'C:\Users\User\develop\flutter\bin\flutter.bat' build apk
```

### iOS / App Store Config

```powershell
python scripts\validate_ios_privacy_manifest.py
```

### Google Play Android Build

Google Play build work happens in `app/`.

Current Google Play package name:

```text
com.appslides.slideai
```

Current fixed backend URL in the Google Play Flutter build:

```text
http://185.171.83.116:8021
```

Current Google Play billing product IDs expected by the app:

```text
slide_ai_week
slide_ai_month
```

Local test APK:

```powershell
cd app
& 'C:\Users\User\develop\flutter\bin\flutter.bat' build apk --release
```

Google Play upload artifact:

```powershell
cd app
& 'C:\Users\User\develop\flutter\bin\flutter.bat' build appbundle --release
```

Expected output:

```text
app/build/app/outputs/bundle/release/app-release.aab
```

Before real Play Console upload, configure release signing with an upload key. The current project still has debug signing in `app/android/app/build.gradle.kts`, which is acceptable for local checks only, not for a store release.

Release signing files:

```text
app/android/key.properties.example
app/android/key.properties
app/android/upload-keystore.jks
```

Only `key.properties.example` is committed. `key.properties` and keystore files are ignored by Git.

Google Play billing can be overridden at build time if Play Console IDs differ:

```powershell
& 'C:\Users\User\develop\flutter\bin\flutter.bat' build appbundle --release `
  --dart-define=APPSLIDES_BILLING_PROVIDER=google_play `
  --dart-define=APPSLIDES_GOOGLE_PLAY_PACKAGE_NAME=com.appslides.slideai `
  --dart-define=APPSLIDES_GOOGLE_PLAY_WEEK_PRODUCT_ID=slide_ai_week `
  --dart-define=APPSLIDES_GOOGLE_PLAY_MONTH_PRODUCT_ID=slide_ai_month
```

Backend Google Play verification requires one of:

```env
GOOGLE_PLAY_SERVICE_ACCOUNT_FILE=/data/google-play-service-account.json
GOOGLE_PLAY_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```

Google Play RTDN endpoint for Pub/Sub push subscriptions:

```text
http://185.171.83.116:8021/v1/billing/google-play/rtdn
```

RTDN only works for subscriptions already verified by the app once, because the backend maps Google `purchaseToken` to the local `client_id` during `/v1/billing/google-play/verify`.

PM admin bot requires a separate Telegram bot token:

```env
PM_ADMIN_BOT_TOKEN=
PM_ADMIN_BOT_USERNAME=
PM_ADMIN_IDS=
```

Do not reuse the RuStore/admin bot token in this stack. Telegram long polling supports only one active `getUpdates` consumer per bot token, so reusing the same token can make one of the admin bots stop responding.

## Notes

- The mobile/web client is hard-wired to `http://185.171.83.116:8021`.
- Local backend URL switching inside the app is intentionally disabled.
- YooKassa is currently integrated in backend live mode and driven through the chat `/balance` flow.
- Successful payment should now be reflected both on app resume and on later summary/generation checks because the backend auto-syncs unfinished payments.
- The separate `telegram_admin_bot/` works against the same SQLite database as the backend and uses `client_id` for subscription commands.
- The production compose stack now includes both `appslides_backend` and `appslides_admin_bot`.
