#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/NNFall/appslides.git}"
PROJECT_DIR="${PROJECT_DIR:-$HOME/ASappslides}"
BRANCH="${BRANCH:-codex/app-store-prep}"
FLUTTER_DIR="${FLUTTER_DIR:-$HOME/development/flutter}"

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
  echo "CocoaPods not found. Installing with gem."
  sudo gem install cocoapods
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
cd ios
pod install

echo "Bootstrap complete. Next:"
echo "  cd \"$PROJECT_DIR\""
echo "  ./scripts/macos/build_ios_app_store.sh"
