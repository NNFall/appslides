#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/NNFall/appslides.git}"
PROJECT_DIR="${PROJECT_DIR:-$HOME/ASappslides}"
BRANCH="${BRANCH:-codex/app-store-prep}"
FLUTTER_DIR="${FLUTTER_DIR:-$HOME/development/flutter}"
COCOAPODS_VERSION="${COCOAPODS_VERSION:-1.15.2}"

export PATH="$FLUTTER_DIR/bin:$HOME/.gem/ruby/2.6.0/bin:$PATH"
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
export RUBYOPT="-rlogger ${RUBYOPT:-}"

echo "== macOS =="
sw_vers || true

echo "== Xcode =="
xcodebuild -version
xcode-select -p

echo "== Git =="
git --version

if ! command -v flutter >/dev/null 2>&1; then
  echo "Flutter not found. Installing stable Flutter SDK to $FLUTTER_DIR"
  mkdir -p "$(dirname "$FLUTTER_DIR")"
  if [ ! -d "$FLUTTER_DIR/.git" ]; then
    git clone https://github.com/flutter/flutter.git -b stable "$FLUTTER_DIR"
  fi
  export PATH="$FLUTTER_DIR/bin:$PATH"
  if ! grep -q 'development/flutter/bin' "$HOME/.zshrc" 2>/dev/null; then
    printf '\nexport PATH="$HOME/development/flutter/bin:$PATH"\n' >> "$HOME/.zshrc"
  fi
else
  echo "Flutter found: $(command -v flutter)"
fi

flutter --version
flutter doctor -v

if ! command -v pod >/dev/null 2>&1; then
  if sudo -n true 2>/dev/null; then
    echo "CocoaPods not found. Installing with sudo gem."
    sudo gem install cocoapods
  else
    echo "CocoaPods not found and sudo is unavailable. Installing user-local CocoaPods $COCOAPODS_VERSION."
    gem install --user-install "ffi" -v "1.15.5" --no-document
    gem install --user-install "securerandom" -v "0.3.2" --no-document
    gem install --user-install "base64" -v "0.2.0" --no-document
    gem install --user-install "bigdecimal" -v "3.1.8" --no-document
    gem install --user-install "connection_pool" -v "2.4.1" --no-document
    gem install --user-install "drb" -v "2.0.6" --no-document
    gem install --user-install "i18n" -v "1.14.7" --no-document
    gem install --user-install "minitest" -v "5.24.1" --no-document
    gem install --user-install "mutex_m" -v "0.2.0" --no-document
    gem install --user-install "tzinfo" -v "2.0.6" --no-document
    gem install --user-install "zeitwerk" -v "2.6.18" --no-document
    gem install --user-install "activesupport" -v "6.1.7.10" --no-document
    gem install --user-install cocoapods -v "$COCOAPODS_VERSION" --no-document
    export PATH="$HOME/.gem/ruby/2.6.0/bin:$PATH"
  fi
fi
pod --version

if [ ! -d "$PROJECT_DIR/.git" ]; then
  git clone "$REPO_URL" "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"
git fetch origin
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

cd app
flutter pub get
flutter precache --ios
cd ios
pod install

echo "Bootstrap complete. Next:"
echo "  cd \"$PROJECT_DIR\""
echo "  ./scripts/macos/build_ios_app_store.sh"
