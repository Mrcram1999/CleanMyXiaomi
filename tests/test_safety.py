"""Synthetic tests: no real-device compatibility claim and no actual ADB calls."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from cleanmyxiaomi.adb import ADB, PROPERTIES, SafetyError, identity, package_list, package_name, package_state
from cleanmyxiaomi.engine import apply, audit, make_plan, restore
from cleanmyxiaomi.policy import DATA, SCOPE_KEYS, allowed_name, load_profile, validate_profile
from cleanmyxiaomi.storage import Journal, device_lock, read_json, save_new, seal


class FakeADB:
    def __init__(self):
        self.serial = "SYNTHETIC123"
        self.props = {v: k + "-synthetic" for k, v in PROPERTIES.items()}
        self.props.update({"ro.product.manufacturer": "Xiaomi", "ro.product.brand": "POCO", "ro.build.version.sdk": "35", "ro.kernel.qemu": "0"})
        self.packages = {"org.example.optional": [0, "100"], "org.example.second": [1, "200"], "com.android.settings": [0, "1"], "org.example.home": [0, "1"], "org.example.keyboard": [0, "1"]}
        self.calls, self.mutations = [], []
        self.fail_after_mutation = self.reject_mutation = False
        self.uid, self.current_user, self.devpath, self.device_status = "2000", "0", "usb:1-1", "device"
        self.home = "org.example.home"

    def devices(self):
        return [{"serial": self.serial, "state": self.device_status, "details": ""}]

    def run(self, *args, **kwargs):
        if args == ("get-devpath",):
            return self.devpath
        raise AssertionError(args)

    ready = ADB.ready

    def shell(self, *args):
        self.calls.append(args)
        if args == ("id", "-u"):
            return self.uid
        if args == ("am", "get-current-user"):
            return self.current_user
        if args[0] == "getprop":
            return self.props.get(args[1], "")
        if args == ("pm", "help"):
            return "disable-user default-state enable"
        if args[:3] == ("cmd", "package", "resolve-activity"):
            return self.home + "/.Home"
        if args[0] == "settings":
            return "org.example.keyboard/.InputMethod;0"
        if args[:3] == ("pm", "list", "packages"):
            names = [n for n, (s, _) in self.packages.items() if ("-e" not in args or s in (0, 1)) and ("-d" not in args or s in (2, 3, 4))]
            return "\n".join("package:" + n for n in sorted(names))
        if args[:2] == ("dumpsys", "package"):
            name = args[2]
            if name not in self.packages:
                return "Unable to find package"
            state, version = self.packages[name]
            return f"Packages:\n  Package [{name}] (abc):\n    userId=10123\n    versionCode={version} minSdk=26 targetSdk=35\n    User 0: ceDataInode=123 installed=true hidden=false suspended=false stopped=false enabled={state}\n    User 10: installed=true hidden=false suspended=false enabled=1\nQueries:\n  other data"
        if args[0] == "pm" and args[1] in ("disable-user", "default-state", "enable"):
            self.mutations.append(args)
            if self.reject_mutation:
                return "Error: operation rejected"
            self.packages[args[-1]][0] = {"disable-user": 3, "default-state": 0, "enable": 1}[args[1]]
            if self.fail_after_mutation:
                self.fail_after_mutation = False
                raise SafetyError("Connection lost after mutation")
            return "Success"
        raise AssertionError(args)


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = self.root / "data"
        (self.data / "profiles").mkdir(parents=True)
        self.adb = FakeADB()
        device = identity(self.adb)
        self.profile = {"schema": 1, "id": "synthetic-test", "status": "approved-device-tested", "description": "TEST ONLY",
                        "scope": {k: device[k] for k in SCOPE_KEYS},
                        "packages": [{"name": n, "version_code": v, "purpose": "Synthetic package", "side_effects": "Synthetic feature stops", "evidence": "https://example.invalid/test"} for n, v in (("org.example.optional", "100"), ("org.example.second", "200"))],
                        "review": {"reviewer": "test-fixture", "tested_on": "2026-10-31", "evidence": "https://example.invalid/test", "restore_verified": True, "essential_checks": ["boot", "calls", "sms", "wifi", "mobile-data", "camera", "notifications", "updates", "accounts"]}}
        self.write_profile()
        self.journal = self.root / "run.journal.jsonl"

    def write_profile(self):
        raw = (json.dumps(self.profile) + "\n").encode()
        (self.data / "profiles/synthetic-test.json").write_bytes(raw)
        (self.data / "registry.json").write_text(json.dumps({"schema": 1, "profiles": {"synthetic-test": hashlib.sha256(raw).hexdigest()}}))

    def plan(self):
        return make_plan(self.adb, "synthetic-test", self.data)

    def apply(self, plan=None, **overrides):
        p = plan or self.plan()
        kwargs = {"approval": p["sha256"], "confirm_device": self.adb.serial, "data_dir": self.data}
        kwargs.update(overrides)
        return apply(self.adb, p, self.journal, **kwargs)

    def test_roundtrip_exact_original_states(self):
        original = copy.deepcopy(self.adb.packages)
        self.assertEqual(self.apply()["count"], 2)
        r = restore(self.adb, self.journal, data_dir=self.data)
        self.assertEqual([a["operation"] for a in r["data"]["actions"]], ["enable", "default-state"])
        self.assertEqual(len(self.adb.mutations), 2)
        self.assertEqual(restore(self.adb, self.journal, r["sha256"], self.adb.serial, False, self.data)["count"], 2)
        self.assertEqual(self.adb.packages, original)
        self.assertEqual(restore(self.adb, self.journal, data_dir=self.data)["data"]["actions"], [])

    def test_read_only_audit_and_plan(self):
        audit(self.adb)
        self.plan()
        self.assertEqual(self.adb.mutations, [])

    def test_bundled_profiles_noop(self):
        for name in ("xiaomi-audit", "redmi-audit", "poco-audit"):
            p = make_plan(self.adb, name)
            self.assertEqual(p["data"]["actions"], [])
            self.assertEqual(apply(self.adb, p, self.journal, p["sha256"], self.adb.serial)["result"], "no-changes")
        self.assertFalse(self.journal.exists())
        self.assertEqual(self.adb.mutations, [])

    def test_consent_required(self):
        for kwargs in ({"approval": None}, {"approval": "yes"}, {"confirm_device": "OTHER"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(SafetyError):
                self.apply(**kwargs)
        self.assertEqual(self.adb.mutations, [])

    def test_device_binding(self):
        for prop in ("ro.boot.serialno", "ro.build.fingerprint", "ro.product.model", "ro.miui.region"):
            p, old = self.plan(), self.adb.props[prop]
            self.adb.props[prop] = "changed"
            with self.subTest(prop=prop), self.assertRaises(SafetyError):
                self.apply(p)
            self.adb.props[prop] = old
        self.assertEqual(self.adb.mutations, [])

    def test_wrong_firmware_profile(self):
        self.adb.props["ro.build.version.incremental"] = "new-ota"
        with self.assertRaises(SafetyError):
            self.plan()

    def test_package_version_drift(self):
        p = self.plan()
        self.adb.packages["org.example.optional"][1] = "101"
        with self.assertRaises(SafetyError):
            self.apply(p)
        self.assertEqual(self.adb.mutations, [])

    def test_inventory_drift(self):
        p = self.plan()
        self.adb.packages["org.example.new"] = [0, "1"]
        with self.assertRaises(SafetyError):
            self.apply(p)

    def test_original_state_drift(self):
        p = self.plan()
        self.adb.packages["org.example.optional"][0] = 1
        with self.assertRaises(SafetyError):
            self.apply(p)

    def test_already_disabled_never_restored(self):
        self.adb.packages["org.example.optional"][0] = 2
        p = self.plan()
        self.assertEqual(p["data"]["skipped"][0]["reason"], "already-disabled")
        self.apply(p)
        r = restore(self.adb, self.journal, data_dir=self.data)
        restore(self.adb, self.journal, r["sha256"], self.adb.serial, False, self.data)
        self.assertEqual(self.adb.packages["org.example.optional"][0], 2)

    def test_absent_package_skipped(self):
        del self.adb.packages["org.example.optional"]
        p = self.plan()
        self.assertEqual(len(p["data"]["actions"]), 1)
        self.assertEqual(p["data"]["skipped"][0]["reason"], "not-installed")

    def test_lost_acknowledgement_restore(self):
        self.adb.fail_after_mutation = True
        with self.assertRaises(SafetyError):
            self.apply()
        self.assertEqual(Journal.read(self.journal)[-1]["data"]["event"], "intent")
        p = restore(self.adb, self.journal, data_dir=self.data)
        self.assertEqual(len(p["data"]["actions"]), 1)
        restore(self.adb, self.journal, p["sha256"], self.adb.serial, False, self.data)
        self.assertEqual(self.adb.packages["org.example.optional"][0], 0)
        self.assertEqual(self.adb.packages["org.example.second"][0], 1)

    def test_false_success_response(self):
        self.adb.reject_mutation = True
        with self.assertRaises(SafetyError):
            self.apply()
        self.assertEqual(len(self.adb.mutations), 1)
        self.assertEqual(restore(self.adb, self.journal, data_dir=self.data)["data"]["actions"], [])

    def test_separate_restore_consent(self):
        p = self.plan()
        self.apply(p)
        with self.assertRaises(SafetyError):
            restore(self.adb, self.journal, p["sha256"], self.adb.serial, False, self.data)
        self.assertEqual(len(self.adb.mutations), 2)

    def test_restore_version_change(self):
        self.apply()
        self.adb.packages["org.example.optional"][1] = "101"
        with self.assertRaises(SafetyError):
            restore(self.adb, self.journal, data_dir=self.data)

    def test_restore_external_state_change(self):
        self.apply()
        self.adb.packages["org.example.optional"][0] = 4
        with self.assertRaises(SafetyError):
            restore(self.adb, self.journal, data_dir=self.data)

    def test_expired_and_future_plan(self):
        for epoch in (0, 999999999999):
            p = self.plan()["data"]
            p["created_epoch"] = epoch
            with self.assertRaises(SafetyError):
                self.apply(seal(p))
        self.assertEqual(self.adb.mutations, [])

    def test_forged_action_with_recomputed_hash(self):
        for name in ("com.android.settings", "org.example.unknown", "org.example.optional;reboot"):
            p = self.plan()["data"]
            p["actions"][0]["package"] = name
            with self.subTest(name=name), self.assertRaises(SafetyError):
                self.apply(seal(p))

    def test_duplicate_action(self):
        p = self.plan()["data"]
        p["actions"].append(p["actions"][0])
        with self.assertRaises(SafetyError):
            self.apply(seal(p))

    def test_uninstall_rejected(self):
        p = self.plan()["data"]
        p["actions"][0]["operation"] = "uninstall"
        with self.assertRaises(SafetyError):
            self.apply(seal(p))

    def test_profile_changed_after_plan(self):
        p = self.plan()
        self.profile["description"] += " changed"
        self.write_profile()
        with self.assertRaises(SafetyError):
            self.apply(p)

    def test_unregistered_and_tampered_profiles(self):
        with self.assertRaises(SafetyError):
            load_profile("unknown", self.data)
        (self.data / "profiles/synthetic-test.json").write_text("{}")
        with self.assertRaises(SafetyError):
            self.plan()

    def test_wildcard_profile(self):
        self.profile["scope"]["fingerprint"] = "*"
        with self.assertRaises(SafetyError):
            validate_profile(self.profile)

    def test_missing_restore_evidence(self):
        self.profile["review"]["restore_verified"] = False
        with self.assertRaises(SafetyError):
            validate_profile(self.profile)

    def test_active_home_protected(self):
        self.adb.home = "org.example.optional"
        with self.assertRaises(SafetyError):
            self.plan()

    def test_journal_not_overwritten(self):
        self.journal.write_text("preserve me")
        with self.assertRaises(FileExistsError):
            self.apply()
        self.assertEqual(self.adb.mutations, [])
        self.assertEqual(self.journal.read_text(), "preserve me")

    def test_journal_tampering(self):
        self.apply()
        self.journal.write_text(self.journal.read_text().replace('"event": "intent"', '"event": "fake"'))
        with self.assertRaises(SafetyError):
            restore(self.adb, self.journal, data_dir=self.data)

    def test_truncated_journal(self):
        self.apply()
        with self.journal.open("a") as f:
            f.write('{"broken":')
        with self.assertRaises(SafetyError):
            restore(self.adb, self.journal, data_dir=self.data)

    def test_root_secondary_user_network_unauthorized_offline(self):
        for attr, value in (("uid", "0"), ("current_user", "10"), ("devpath", "127.0.0.1:5555"), ("device_status", "unauthorized"), ("device_status", "offline")):
            before = getattr(self.adb, attr)
            setattr(self.adb, attr, value)
            with self.subTest(attr=attr, value=value), self.assertRaises(SafetyError):
                audit(self.adb)
            setattr(self.adb, attr, before)
        self.assertEqual(self.adb.mutations, [])

    def test_dump_parses_owner_state(self):
        self.assertEqual(package_state(self.adb, "org.example.optional"), {"version_code": "100", "enabled_state": 0})

    def test_device_lock(self):
        with device_lock(self.adb.serial, self.root / "locks"):
            with self.assertRaises(SafetyError):
                with device_lock(self.adb.serial, self.root / "locks"):
                    pass
        with device_lock(self.adb.serial, self.root / "locks"):
            pass


class BoundaryTests(unittest.TestCase):
    def test_package_injection(self):
        for name in ("x;reboot", "com.x\nreboot", "com.x/a", "--user", "com.x$(id)", "com.*"):
            with self.subTest(name=name), self.assertRaises(SafetyError):
                package_name(name)

    def test_protected_components(self):
        for name in ("com.android.systemui", "com.miui.home", "com.miui.securitycenter", "com.google.android.gms", "com.vendor.launcher", "com.xiaomi.account"):
            with self.subTest(name=name), self.assertRaises(SafetyError):
                allowed_name(name)

    def test_bad_package_listing(self):
        for value in ("Error: denied", "package:com.example.app\npackage:com.example.app"):
            with self.assertRaises(SafetyError):
                package_list(value)

    def test_remote_shell_injection(self):
        adb = ADB(sys.executable, "TEST")
        with patch("subprocess.run") as run, self.assertRaises(SafetyError):
            adb.shell("pm", "disable-user", "com.x;reboot")
        run.assert_not_called()

    def test_explicit_serial_timeout_no_shell(self):
        adb = ADB(sys.executable, "TEST")
        response = subprocess.CompletedProcess([], 0, "ok", "")
        with patch.dict(os.environ, {}, clear=True), patch("subprocess.run", return_value=response) as run:
            self.assertEqual(adb.shell("getprop", "ro.product.model"), "ok")
            args, kwargs = run.call_args
            self.assertEqual(args[0][1:3], ["-s", "TEST"])
            self.assertFalse(kwargs["shell"])
            self.assertEqual(kwargs["timeout"], 30)

    def test_remote_server_rejected(self):
        adb = ADB(sys.executable, "TEST")
        with patch.dict(os.environ, {"ADB_SERVER_SOCKET": "tcp:evil:5037"}), self.assertRaises(SafetyError):
            adb.shell("id", "-u")

    def test_timeout(self):
        adb = ADB(sys.executable, "TEST")
        with patch.dict(os.environ, {}, clear=True), patch("subprocess.run", side_effect=subprocess.TimeoutExpired("adb", 30)), self.assertRaises(SafetyError):
            adb.shell("id", "-u")

    def test_duplicate_json_and_exclusive_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "test.json"
            p.write_text('{"schema":1,"schema":2}')
            with self.assertRaises(SafetyError):
                read_json(p)
            with self.assertRaises(FileExistsError):
                save_new(p, {})

    def test_cli_no_adb_needed(self):
        for args in (("--help",), ("profiles",), ("--version",)):
            result = subprocess.run([sys.executable, "-m", "cleanmyxiaomi", *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_no_shipped_mutating_profile(self):
        registry = read_json(DATA / "registry.json")
        self.assertEqual(len(registry["profiles"]), 3)
        for name in registry["profiles"]:
            self.assertEqual(load_profile(name)["packages"], [])


if __name__ == "__main__":
    unittest.main()
