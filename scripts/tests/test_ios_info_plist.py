from __future__ import annotations

import plistlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INFO_PLIST = ROOT / "app" / "ios" / "Runner" / "Info.plist"


def test_ios_info_plist_contains_required_privacy_purpose_strings() -> None:
    info = plistlib.loads(INFO_PLIST.read_bytes())

    required_keys = [
        "NSLocationWhenInUseUsageDescription",
        "NSCameraUsageDescription",
        "NSPhotoLibraryUsageDescription",
    ]

    for key in required_keys:
        assert isinstance(info.get(key), str)
        assert len(info[key].strip()) >= 20
