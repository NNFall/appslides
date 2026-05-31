from __future__ import annotations

import plistlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "app" / "ios" / "Runner" / "PrivacyInfo.xcprivacy"
PROJECT = ROOT / "app" / "ios" / "Runner.xcodeproj" / "project.pbxproj"

REQUIRED_API_REASONS = {
    "NSPrivacyAccessedAPICategoryUserDefaults": {"CA92.1"},
    "NSPrivacyAccessedAPICategoryFileTimestamp": {"C617.1"},
}


def main() -> int:
    errors: list[str] = []

    if not MANIFEST.exists():
        errors.append(f"missing {MANIFEST.relative_to(ROOT)}")
    else:
        with MANIFEST.open("rb") as handle:
            payload = plistlib.load(handle)

        if payload.get("NSPrivacyTracking") is not False:
            errors.append("NSPrivacyTracking must be false")

        accessed = payload.get("NSPrivacyAccessedAPITypes")
        if not isinstance(accessed, list):
            errors.append("NSPrivacyAccessedAPITypes must be an array")
            accessed = []

        actual: dict[str, set[str]] = {}
        for item in accessed:
            if not isinstance(item, dict):
                continue
            category = item.get("NSPrivacyAccessedAPIType")
            reasons = item.get("NSPrivacyAccessedAPITypeReasons")
            if isinstance(category, str) and isinstance(reasons, list):
                actual[category] = {reason for reason in reasons if isinstance(reason, str)}

        for category, required_reasons in REQUIRED_API_REASONS.items():
            missing = required_reasons - actual.get(category, set())
            if missing:
                errors.append(f"{category} missing reasons: {', '.join(sorted(missing))}")

    project_text = PROJECT.read_text(encoding="utf-8")
    if "PrivacyInfo.xcprivacy" not in project_text:
        errors.append("PrivacyInfo.xcprivacy is not referenced by the Xcode project")
    if "PrivacyInfo.xcprivacy in Resources" not in project_text:
        errors.append("PrivacyInfo.xcprivacy is not included in the Runner resources phase")

    if errors:
        print("iOS privacy manifest validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("iOS privacy manifest validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
