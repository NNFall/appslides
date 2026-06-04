from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PBXPROJ = ROOT / "app" / "ios" / "Runner.xcodeproj" / "project.pbxproj"


def test_release_and_profile_use_app_store_signing_team() -> None:
    content = PBXPROJ.read_text(encoding="utf-8")

    assert "DEVELOPMENT_TEAM = WH73RJDJXC;" in content
    assert content.count('CODE_SIGN_IDENTITY = "Apple Distribution";') >= 2
    assert content.count("CODE_SIGN_STYLE = Manual;") >= 2
    assert content.count("PROVISIONING_PROFILE_SPECIFIER = Macin;") >= 2
    assert "PRODUCT_BUNDLE_IDENTIFIER = com.appslides.slideai;" in content
    assert 'CODE_SIGN_IDENTITY = "iPhone Developer";' in content
    assert content.count('"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Developer";') == 1
    assert '"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "Apple Distribution";' not in content
