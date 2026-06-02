from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = ROOT / "scripts" / "macos" / "bootstrap_ios_builder.sh"
BUILD = ROOT / "scripts" / "macos" / "build_ios_app_store.sh"


def test_macos_ios_build_script_targets_as_backend_and_app_store_billing() -> None:
    content = BUILD.read_text(encoding="utf-8")

    assert "APPSLIDES_BACKEND_BASE_URL=http://185.171.83.116:8031" in content
    assert "APPSLIDES_BILLING_PROVIDER=app_store" in content
    assert "APPSLIDES_APP_STORE_WEEK_PRODUCT_ID=slide_ai_week" in content
    assert "APPSLIDES_APP_STORE_MONTH_PRODUCT_ID=slide_ai_month" in content
    assert "185.171.83.116:8021" not in content
    assert "flutter build ios --release --no-codesign" in content


def test_macos_bootstrap_script_checks_required_ios_tools() -> None:
    content = BOOTSTRAP.read_text(encoding="utf-8")

    assert "flutter doctor -v" in content
    assert "xcodebuild -version" in content
    assert "pod --version" in content
    assert "git clone" in content
