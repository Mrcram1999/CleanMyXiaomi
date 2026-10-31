"""Closed registry: never convert a package name or an AI guess into approval."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

from .adb import PROPERTIES, package_name, require
from .storage import read_json

DATA = Path(__file__).parent / "data"
SCOPE_KEYS = set(PROPERTIES) - {"boot_serial"}
# Defense in depth, not an exhaustive identification of every critical component.
PROTECTED_PREFIXES = ("com.android.", "com.google.", "com.qualcomm.", "com.mediatek.",
                      "com.miui.security", "com.miui.home", "com.miui.power", "com.miui.guard", "com.miui.packageinstaller",
                      "com.xiaomi.account", "com.xiaomi.finddevice", "com.xiaomi.xmsf", "com.xiaomi.mipicks")
PROTECTED_WORDS = ("launcher", "systemui", "telephony", "permissioncontroller", "settings", "updater",
                   "bluetooth", "network", "inputmethod", "keyguard", "auth", "security", "backup")


def allowed_name(name):
    package_name(name)
    require(not name.startswith(PROTECTED_PREFIXES) and not any(w in name.lower() for w in PROTECTED_WORDS),
            f"Protected component: {name}")


def validate_profile(profile):
    require(set(profile) == {"schema", "id", "status", "description", "scope", "packages", "review"}, "Invalid profile fields")
    require(profile["schema"] == 1 and re.fullmatch(r"[a-z0-9-]+", profile["id"]), "Invalid profile schema or id")
    require(profile["status"] in ("approved-audit-only", "approved-device-tested"), "Profile has not been approved")
    require(isinstance(profile["packages"], list), "Invalid packages")
    require(isinstance(profile["description"], str) and profile["description"], "Missing profile description")
    if profile["status"] == "approved-audit-only":
        require(profile["packages"] == [] and profile["scope"] == {}, "Audit-only profiles must not contain changes or claim tested builds")
        return profile
    scope = profile["scope"]
    require(set(scope) == SCOPE_KEYS, "Device-tested profiles must specify every firmware identity field")
    require(all(isinstance(v, str) and not any(c in v for c in "*?\n\r") for v in scope.values()), "Wildcards and malformed scope are prohibited")
    require(all(scope[k] for k in ("manufacturer", "brand", "model", "device", "fingerprint", "incremental", "android", "sdk")), "Incomplete scope")
    review = profile["review"]
    require(set(review) == {"reviewer", "tested_on", "evidence", "restore_verified", "essential_checks"}, "Missing review evidence")
    require(isinstance(review["reviewer"], str) and review["reviewer"].strip(), "Missing reviewer")
    require(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", review["tested_on"])), "Missing test date")
    require(review["restore_verified"] is True, "Restore test required")
    require(isinstance(review["evidence"], str) and review["evidence"].startswith("https://"), "Public evidence URL required")
    require(set(review["essential_checks"]) == {"boot", "calls", "sms", "wifi", "mobile-data", "camera", "notifications", "updates", "accounts"}, "Incomplete real-device checks")
    seen = set()
    require(bool(profile["packages"]), "Device-tested profiles must include tested packages")
    for entry in profile["packages"]:
        require(set(entry) == {"name", "version_code", "purpose", "side_effects", "evidence"}, "Invalid package review fields")
        allowed_name(entry["name"])
        require(entry["name"] not in seen, "Duplicate profile package")
        seen.add(entry["name"])
        require(isinstance(entry["version_code"], str) and entry["version_code"].isdigit(), "Exact package version required")
        require(all(isinstance(entry[k], str) and entry[k].strip() for k in ("purpose", "side_effects", "evidence")), "Missing package-specific evidence or side effects")
        require(entry["evidence"].startswith("https://"), "Package evidence must be an HTTPS URL")
    return profile


def load_profile(profile_id, data_dir=DATA):
    require(bool(re.fullmatch(r"[a-z0-9-]+", profile_id)), "Invalid profile id")
    registry = read_json(Path(data_dir) / "registry.json")
    require(registry["schema"] == 1 and profile_id in registry["profiles"], "Profile is not in the approved registry")
    path = Path(data_dir) / "profiles" / (profile_id + ".json")
    content = path.read_bytes()
    require(hashlib.sha256(content).hexdigest() == registry["profiles"][profile_id], "Profile hash differs from reviewed registry")
    profile = validate_profile(read_json(path))
    require(profile["id"] == profile_id, "Profile ID mismatch")
    return profile


def match(profile, device):
    if profile["status"] == "approved-device-tested":
        require(all(device.get(k) == v for k, v in profile["scope"].items()), "Profile does not match this exact device/firmware/region")
