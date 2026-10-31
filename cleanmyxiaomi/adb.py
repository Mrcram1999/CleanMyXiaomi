"""Small ADB boundary: argv only, explicit serial, bounded calls, USB only."""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess


class SafetyError(RuntimeError):
    """An operation cannot be established as safe within the supported scope."""


def require(condition, message):
    if not condition:
        raise SafetyError(message)


def package_name(value):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+", value),
            "Invalid package identifier")
    return value


def discover(explicit=None):
    if explicit:
        p = Path(explicit).expanduser().resolve()
        require(p.is_file(), "ADB path is not a file")
        return str(p)
    candidates = [shutil.which("adb")]
    for key in ("ANDROID_SDK_ROOT", "ANDROID_HOME"):
        if os.environ.get(key):
            candidates.append(str(Path(os.environ[key]) / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb")))
    candidates += [str(Path.home() / "Library/Android/sdk/platform-tools/adb"),
                   str(Path.home() / "Android/Sdk/platform-tools/adb")]
    if os.environ.get("LOCALAPPDATA"):
        candidates.append(str(Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk/platform-tools/adb.exe"))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    raise SafetyError("ADB not found. Run the doctor command and read docs/SETUP.md; no automatic installation occurs.")


class ADB:
    def __init__(self, executable=None, serial=None):
        self.executable = discover(executable)
        if serial is not None:
            require(bool(re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", serial)) and not serial.startswith("-"), "Invalid serial")
        self.serial = serial

    def run(self, *args, targeted=True):
        if targeted:
            require(self.serial is not None, "An explicit --serial is required")
        command = [self.executable] + (["-s", self.serial] if targeted else []) + list(args)
        env = os.environ.copy()
        for key in ("ADB_SERVER_SOCKET", "ANDROID_ADB_SERVER_PORT", "ANDROID_ADB_SERVER_ADDRESS", "ANDROID_SERIAL"):
            require(not env.get(key), f"Unset {key}: only the local default ADB server is supported")
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="strict",
                                    timeout=30, check=False, env=env, shell=False)
        except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
            raise SafetyError(f"ADB failed or timed out: {type(exc).__name__}; inspect the journal before retrying") from exc
        require(result.returncode == 0, f"ADB command failed: {result.stderr.strip()[:400]}")
        require(len(result.stdout) < 16_000_000, "ADB output too large")
        return result.stdout.strip()

    def shell(self, *args):
        # adb shell itself serializes argv; prohibit shell syntax at this second boundary.
        require(all(re.fullmatch(r"[A-Za-z0-9_./:-]+", a) for a in args), "Unsafe remote argument")
        return self.run("shell", *args)

    def devices(self):
        output = self.run("devices", "-l", targeted=False)
        devices = []
        for line in output.splitlines():
            if not line.strip() or line.startswith(("List of devices", "*")):
                continue
            fields = line.split()
            require(len(fields) >= 2, "Unrecognized ADB device listing")
            devices.append({"serial": fields[0], "state": fields[1], "details": " ".join(fields[2:])})
        return devices

    def ready(self):
        selected = [d for d in self.devices() if d["serial"] == self.serial]
        require(len(selected) == 1 and selected[0]["state"] == "device", "Selected phone is missing, offline, unauthorized, or ambiguous")
        require(self.run("get-devpath").startswith("usb:"), "Only a directly connected USB device is supported")
        require(self.shell("id", "-u") == "2000", "Only the ordinary non-root ADB shell is supported")
        require(self.shell("am", "get-current-user") == "0", "Switch to the owner (user 0); secondary users/work profiles are unsupported")


PROPERTIES = {
    "manufacturer": "ro.product.manufacturer", "brand": "ro.product.brand",
    "model": "ro.product.model", "device": "ro.product.device",
    "fingerprint": "ro.build.fingerprint", "incremental": "ro.build.version.incremental",
    "android": "ro.build.version.release", "sdk": "ro.build.version.sdk",
    "miui": "ro.miui.ui.version.name", "hyperos": "ro.mi.os.version.name",
    "region": "ro.miui.region", "boot_serial": "ro.boot.serialno",
}


def identity(adb):
    adb.ready()
    data = {key: adb.shell("getprop", prop) for key, prop in PROPERTIES.items()}
    require(all(data[k] for k in ("manufacturer", "brand", "model", "device", "fingerprint", "incremental", "sdk", "boot_serial")),
            "Required device identity properties are unavailable")
    require(all(len(v) < 512 and not any(ord(c) < 32 for c in v) for v in data.values()), "Malformed device property")
    require(data["manufacturer"].lower() in ("xiaomi", "redmi", "poco") and data["brand"].lower() in ("xiaomi", "redmi", "poco"),
            "Not an identified Xiaomi/Redmi/POCO device")
    require(data["sdk"].isdigit() and int(data["sdk"]) >= 26, "Only Android 8+ is supported")
    require(data["miui"] or data["hyperos"], "MIUI/HyperOS identity not available; refusing to infer firmware")
    require(adb.shell("getprop", "ro.kernel.qemu") != "1", "Emulators are not supported")
    return {"serial": adb.serial, "user": 0, **data}


def package_list(output):
    result = set()
    for line in output.splitlines():
        require(line.startswith("package:"), "Unrecognized package listing")
        value = package_name(line.removeprefix("package:"))
        require(value not in result, "Duplicate package listing")
        result.add(value)
    return result


def inventory(adb):
    all_packages = package_list(adb.shell("pm", "list", "packages", "--user", "0"))
    enabled = package_list(adb.shell("pm", "list", "packages", "-e", "--user", "0"))
    disabled = package_list(adb.shell("pm", "list", "packages", "-d", "--user", "0"))
    require(all_packages and not enabled & disabled and enabled | disabled == all_packages, "Inconsistent package inventory; rerun audit")
    return {"installed": sorted(all_packages), "enabled": sorted(enabled), "disabled": sorted(disabled)}


def package_state(adb, package):
    package_name(package)
    output = adb.shell("dumpsys", "package", package)
    sections = re.split(r"(?m)^\s{2}Package \[", output)[1:]
    matches = [s for s in sections if s.startswith(package + "]")]
    require(len(matches) == 1, f"Cannot uniquely parse installed package {package}")
    section = matches[0].split("\n", 1)[-1]
    # Exclude hidden system package and later top-level sections.
    section = re.split(r"(?m)^\S", section, maxsplit=1)[0]
    versions = re.findall(r"(?m)^\s+versionCode=(\d+)\b", section)
    users = re.findall(r"(?m)^\s+User 0: (.*)$", section)
    require(len(versions) == 1 and len(users) == 1, f"Missing or ambiguous state for {package}")
    fields = dict(re.findall(r"(\w+)=([^\s]+)", users[0]))
    require(fields.get("installed") == "true" and fields.get("hidden") == "false" and fields.get("suspended") == "false",
            f"Package is not installed normally, is hidden, or suspended: {package}")
    value = fields.get("enabled")
    require(value in ("0", "1", "2", "3", "4"), f"Unknown enabled state for {package}")
    return {"version_code": versions[0], "enabled_state": int(value)}
