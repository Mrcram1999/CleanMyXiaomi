"""Audit → plan → explicit approval → journalled disable → exact-state restore."""
from __future__ import annotations

from datetime import datetime, timezone
import time

from .adb import identity, inventory, package_state, require
from .policy import DATA, allowed_name, load_profile, match
from .storage import Journal, digest, seal, unseal

LIMITATIONS = [
    "Package-state snapshots are not app-data or full-device backups.",
    "No guarantee of removing all ads, improving battery life, or preserving every vendor feature.",
    "ADB package checks cannot prove that calls, boot, updates, and notifications work; check them on the phone.",
    "No real-device cleanup profile ships in v0.1.0; included profiles authorize audit only.",
    "Device properties and version codes are compatibility checks, not hardware or APK cryptographic attestation.",
]


def now():
    return datetime.now(timezone.utc).isoformat()


def capabilities(adb):
    help_text = adb.shell("pm", "help")
    require(all(word in help_text for word in ("disable-user", "default-state", "enable")), "Required cleanup/restore commands are unavailable")


def protected_runtime(adb):
    """Reject active launcher and keyboards as additional runtime protection."""
    home = adb.shell("cmd", "package", "resolve-activity", "--brief", "--user", "0", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME")
    import re
    components = re.findall(r"(?m)^([A-Za-z][A-Za-z0-9_.]+)/[A-Za-z0-9_.$]+$", home)
    require(len(components) == 1, "Cannot establish the current home application")
    keyboards = adb.shell("settings", "--user", "0", "get", "secure", "enabled_input_methods")
    require(keyboards and keyboards != "null", "Cannot establish enabled keyboards")
    values = set(components)
    for entry in keyboards.split(":"):
        component = entry.split(";", 1)[0]
        require("/" in component, "Unrecognized keyboard setting")
        from .adb import package_name
        values.add(package_name(component.split("/", 1)[0]))
    return values


def audit(adb):
    device = identity(adb)
    packages = inventory(adb)
    require(identity(adb) == device, "Device identity changed during audit")
    return {"schema": 1, "kind": "audit", "created": now(), "device": device, "inventory": packages, "limitations": LIMITATIONS}


def make_plan(adb, profile_id, data_dir=DATA):
    profile = load_profile(profile_id, data_dir)
    report = audit(adb)
    match(profile, report["device"])
    actions, skipped = [], []
    if profile["packages"]:
        capabilities(adb)
        protected = protected_runtime(adb)
        for entry in profile["packages"]:
            name = entry["name"]
            require(name not in protected, f"Active launcher or keyboard is protected: {name}")
            if name not in report["inventory"]["installed"]:
                skipped.append({"package": name, "reason": "not-installed"})
                continue
            state = package_state(adb, name)
            require(state["version_code"] == entry["version_code"], f"Unreviewed package version: {name}")
            if name in report["inventory"]["disabled"]:
                skipped.append({"package": name, "reason": "already-disabled"})
                continue
            require(state["enabled_state"] in (0, 1), f"Unsupported original package state: {name}")
            actions.append({"package": name, "before": state, "after": 3,
                            "operation": "disable-user", "purpose": entry["purpose"], "side_effects": entry["side_effects"]})
        require(identity(adb) == report["device"] and inventory(adb) == report["inventory"], "Device changed while planning")
    data = {"schema": 1, "kind": "plan", "created": now(), "created_epoch": time.time(), "device": report["device"],
            "inventory": report["inventory"], "profile": profile_id, "profile_digest": digest(profile),
            "actions": actions, "skipped": skipped, "limitations": LIMITATIONS}
    return seal(data)


def validate_plan(envelope, data_dir=DATA, fresh=False):
    plan = unseal(envelope)
    require(set(plan) == {"schema", "kind", "created", "created_epoch", "device", "inventory", "profile", "profile_digest", "actions", "skipped", "limitations"}, "Invalid plan fields")
    require(plan["schema"] == 1 and plan["kind"] == "plan", "Not a supported plan")
    profile = load_profile(plan["profile"], data_dir)
    require(digest(profile) == plan["profile_digest"], "Approved profile changed; re-plan")
    match(profile, plan["device"])
    if fresh:
        require(type(plan["created_epoch"]) in (float, int) and 0 <= time.time() - plan["created_epoch"] <= 86400, "Plan expired or future-dated; create a fresh plan")
    inv = plan["inventory"]
    require(set(inv) == {"installed", "enabled", "disabled"}, "Invalid inventory")
    for values in inv.values():
        require(isinstance(values, list) and values == sorted(set(values)), "Invalid inventory order or duplicates")
    require(not set(inv["enabled"]) & set(inv["disabled"]) and set(inv["enabled"]) | set(inv["disabled"]) == set(inv["installed"]), "Invalid inventory partition")
    approved = {p["name"]: p for p in profile["packages"]}
    seen = set()
    require(isinstance(plan["actions"], list), "Invalid actions")
    for action in plan["actions"]:
        require(set(action) == {"package", "before", "after", "operation", "purpose", "side_effects"}, "Invalid action fields")
        name = action["package"]
        allowed_name(name)
        require(name in approved and name not in seen and name in inv["enabled"], "Unapproved, duplicate, or previously disabled target")
        seen.add(name)
        require(action["operation"] == "disable-user" and type(action["after"]) is int and action["after"] == 3, "Only disable-user is permitted")
        require(set(action["before"]) == {"version_code", "enabled_state"} and type(action["before"]["enabled_state"]) is int and action["before"]["enabled_state"] in (0, 1), "Invalid original state")
        require(action["before"]["version_code"] == approved[name]["version_code"], "Package version is not approved")
        require(all(action[k] == approved[name][k] for k in ("purpose", "side_effects")), "Plan explanation differs from reviewed profile")
    return plan


def consent(envelope, approval, serial, confirm_device):
    require(approval == envelope["sha256"], "Explicit --approve with the full reviewed SHA-256 is required")
    require(confirm_device == serial == envelope["data"]["device"]["serial"], "Explicit --confirm-device must match the planned serial")


def same_device(adb, plan):
    require(identity(adb) == plan["device"], "Exact device identity/build/user no longer matches; refusing changes")


def apply(adb, envelope, journal_path, approval, confirm_device, data_dir=DATA):
    plan = validate_plan(envelope, data_dir, fresh=True)
    consent(envelope, approval, adb.serial, confirm_device)
    same_device(adb, plan)
    require(inventory(adb) == plan["inventory"], "Package inventory drifted since approval; re-plan")
    if not plan["actions"]:
        return {"result": "no-changes", "reason": "This plan contains no approved changes", "limitations": LIMITATIONS}
    capabilities(adb)
    protected = protected_runtime(adb)
    for action in plan["actions"]:
        require(action["package"] not in protected, "Target became an active launcher or keyboard")
        require(package_state(adb, action["package"]) == action["before"], "Package state/version drifted; re-plan")
    journal = Journal(journal_path, create=True)
    journal.append({"event": "header", "created": now(), "plan": envelope})
    expected = {k: set(v) for k, v in plan["inventory"].items()}
    for action in plan["actions"]:
        name = action["package"]
        same_device(adb, plan)
        require(package_state(adb, name) == action["before"], "Package changed during cleanup")
        require(name not in protected_runtime(adb), "Target became an active launcher or keyboard")
        require(inventory(adb) == {k: sorted(v) for k, v in expected.items()}, "Unexpected inventory drift during cleanup")
        journal.append({"event": "intent", "package": name, "at": now()})
        # Durable intent precedes mutation; restore handles lost acknowledgements.
        adb.shell("pm", "disable-user", "--user", "0", name)
        require(package_state(adb, name) == {**action["before"], "enabled_state": 3}, "Disable verification failed; stop and inspect journal")
        same_device(adb, plan)
        expected["enabled"].remove(name)
        expected["disabled"].add(name)
        require(inventory(adb) == {k: sorted(v) for k, v in expected.items()}, "Unexpected package changes; stop and inspect journal")
        journal.append({"event": "applied", "package": name, "at": now()})
    journal.append({"event": "complete", "at": now()})
    return {"result": "applied", "count": len(plan["actions"]), "journal": str(journal_path), "manual_checks_required": True, "limitations": LIMITATIONS}


def recovery_plan(adb, journal_path, data_dir=DATA):
    journal = Journal(journal_path)
    require(bool(journal.events), "Empty journal: no recorded operation to restore")
    header = journal.events[0]["data"]
    require(header.get("event") == "header", "Missing recovery header")
    plan = validate_plan(header["plan"], data_dir)
    same_device(adb, plan)
    actions = {a["package"]: a for a in plan["actions"]}
    attempted = []
    for event in journal.events[1:]:
        item = event["data"]
        require(item.get("event") in ("intent", "applied", "complete", "restore-intent", "restored", "restore-complete"), "Unknown journal event")
        if "package" in item:
            require(item["package"] in actions, "Journal target is outside the approved plan")
        if item["event"] == "intent":
            require(item["package"] not in attempted, "Duplicate cleanup intent")
            attempted.append(item["package"])
    restores = []
    for name in reversed(attempted):
        before = actions[name]["before"]
        current = package_state(adb, name)
        require(current["version_code"] == before["version_code"], f"Package version changed since cleanup: {name}")
        require(current["enabled_state"] in (before["enabled_state"], 3), f"External state change for {name}; manual review required")
        if current["enabled_state"] == 3:
            restores.append({"package": name, "before": current, "after": before,
                             "operation": "default-state" if before["enabled_state"] == 0 else "enable"})
    report = {"schema": 1, "kind": "restore-plan", "device": plan["device"],
              "journal_head": journal.events[-1]["sha256"], "actions": restores}
    return seal(report), plan, journal


def restore(adb, journal_path, approval=None, confirm_device=None, dry_run=True, data_dir=DATA):
    envelope, plan, journal = recovery_plan(adb, journal_path, data_dir)
    if dry_run:
        return envelope
    consent(envelope, approval, adb.serial, confirm_device)
    capabilities(adb)
    for action in envelope["data"]["actions"]:
        same_device(adb, plan)
        name = action["package"]
        require(package_state(adb, name) == action["before"], "Package changed during restore")
        journal.append({"event": "restore-intent", "package": name, "at": now()})
        adb.shell("pm", action["operation"], "--user", "0", name)
        require(package_state(adb, name) == action["after"], "Restore verification failed; preserve journal and stop")
        same_device(adb, plan)
        journal.append({"event": "restored", "package": name, "at": now()})
    journal.append({"event": "restore-complete", "at": now()})
    return {"result": "restored", "count": len(envelope["data"]["actions"]), "manual_checks_required": True}
