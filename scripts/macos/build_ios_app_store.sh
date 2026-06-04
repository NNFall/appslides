#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$HOME/ASappslides}"
BRANCH="${BRANCH:-codex/app-store-prep}"
BUILD_NUMBER="${BUILD_NUMBER:-1}"
SYNC_GIT="${SYNC_GIT:-0}"
IOS_TEAM_ID="${IOS_TEAM_ID:-WH73RJDJXC}"
IOS_BUNDLE_ID="${IOS_BUNDLE_ID:-com.appslides.slideai}"
IOS_PROVISIONING_PROFILE="${IOS_PROVISIONING_PROFILE:-Macin}"
IOS_EXPORT_METHOD="${IOS_EXPORT_METHOD:-app-store-connect}"
MAC_KEYCHAIN_PATH="${MAC_KEYCHAIN_PATH:-$HOME/Library/Keychains/login.keychain-db}"

export PATH="$HOME/development/flutter/bin:$PATH"
export PATH="$HOME/.gem/ruby/2.6.0/bin:$PATH"
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
export RUBYOPT="-rlogger ${RUBYOPT:-}"

cd "$PROJECT_DIR"
if [[ "$SYNC_GIT" == "1" ]]; then
  git fetch origin
  git checkout "$BRANCH"
  git pull --ff-only origin "$BRANCH"
fi

cd app
flutter pub get
flutter precache --ios
flutter analyze
flutter test

cd ios
pod install
cd ..

flutter build ios --release --no-codesign \
  --dart-define=APPSLIDES_BACKEND_BASE_URL=http://185.171.83.116:8031 \
  --dart-define=APPSLIDES_BILLING_PROVIDER=app_store \
  --dart-define=APPSLIDES_APP_STORE_WEEK_PRODUCT_ID=slide_ai_week \
  --dart-define=APPSLIDES_APP_STORE_MONTH_PRODUCT_ID=slide_ai_month

if [[ "${BUILD_SIGNED_IPA:-0}" == "1" ]]; then
  if [[ -n "${MAC_KEYCHAIN_PASSWORD:-}" ]]; then
    security unlock-keychain -p "$MAC_KEYCHAIN_PASSWORD" "$MAC_KEYCHAIN_PATH"
    security set-keychain-settings -lut 21600 "$MAC_KEYCHAIN_PATH"
    security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$MAC_KEYCHAIN_PASSWORD" "$MAC_KEYCHAIN_PATH" >/dev/null
  fi

  EXPORT_OPTIONS_PLIST="${EXPORT_OPTIONS_PLIST:-$PWD/build/ios/AppStoreExportOptions.plist}"
  mkdir -p "$(dirname "$EXPORT_OPTIONS_PLIST")"
  cat > "$EXPORT_OPTIONS_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>method</key>
  <string>$IOS_EXPORT_METHOD</string>
  <key>teamID</key>
  <string>$IOS_TEAM_ID</string>
  <key>signingStyle</key>
  <string>manual</string>
  <key>signingCertificate</key>
  <string>Apple Distribution</string>
  <key>provisioningProfiles</key>
  <dict>
    <key>$IOS_BUNDLE_ID</key>
    <string>$IOS_PROVISIONING_PROFILE</string>
  </dict>
  <key>stripSwiftSymbols</key>
  <true/>
  <key>destination</key>
  <string>export</string>
</dict>
</plist>
PLIST

  flutter build ipa --release \
    --build-number="$BUILD_NUMBER" \
    --export-options-plist="$EXPORT_OPTIONS_PLIST" \
    --dart-define=APPSLIDES_BACKEND_BASE_URL=http://185.171.83.116:8031 \
    --dart-define=APPSLIDES_BILLING_PROVIDER=app_store \
    --dart-define=APPSLIDES_APP_STORE_WEEK_PRODUCT_ID=slide_ai_week \
    --dart-define=APPSLIDES_APP_STORE_MONTH_PRODUCT_ID=slide_ai_month
fi

echo "iOS no-codesign build complete."
echo "Signed IPA is built only when BUILD_SIGNED_IPA=1 and Apple signing is configured."
