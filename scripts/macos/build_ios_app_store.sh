#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$HOME/ASappslides}"
BRANCH="${BRANCH:-codex/app-store-prep}"
BUILD_NUMBER="${BUILD_NUMBER:-1}"

export PATH="$HOME/development/flutter/bin:$PATH"
export PATH="$HOME/.gem/ruby/2.6.0/bin:$PATH"
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
export RUBYOPT="-rlogger ${RUBYOPT:-}"

cd "$PROJECT_DIR"
git fetch origin
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

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
  flutter build ipa --release \
    --build-number="$BUILD_NUMBER" \
    --dart-define=APPSLIDES_BACKEND_BASE_URL=http://185.171.83.116:8031 \
    --dart-define=APPSLIDES_BILLING_PROVIDER=app_store \
    --dart-define=APPSLIDES_APP_STORE_WEEK_PRODUCT_ID=slide_ai_week \
    --dart-define=APPSLIDES_APP_STORE_MONTH_PRODUCT_ID=slide_ai_month
fi

echo "iOS no-codesign build complete."
echo "Signed IPA is built only when BUILD_SIGNED_IPA=1 and Apple signing is configured."
