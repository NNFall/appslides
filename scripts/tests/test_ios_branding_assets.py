from __future__ import annotations

import plistlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INFO_PLIST = ROOT / "app" / "ios" / "Runner" / "Info.plist"
APP_ICON = (
    ROOT
    / "app"
    / "ios"
    / "Runner"
    / "Assets.xcassets"
    / "AppIcon.appiconset"
    / "Icon-App-1024x1024@1x.png"
)
PUBSPEC = ROOT / "app" / "pubspec.yaml"


def test_ios_display_name_matches_app_store_title() -> None:
    info = plistlib.loads(INFO_PLIST.read_bytes())

    assert info["CFBundleDisplayName"] == "Slide AI: PPTX & PDF Maker"
    assert info["CFBundleName"] == "SlideAI"


def test_ios_marketing_icon_is_not_flutter_placeholder() -> None:
    assert APP_ICON.exists()
    assert APP_ICON.stat().st_size > 50_000


def test_flutter_declares_brand_avatar_asset() -> None:
    content = PUBSPEC.read_text(encoding="utf-8")

    assert "assets/brand/slide_ai_avatar.jpg" in content
