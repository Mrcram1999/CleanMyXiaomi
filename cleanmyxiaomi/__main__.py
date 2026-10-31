"""Machine-readable CLI; the agent translates explanations into the user's language."""
import argparse
import json
import os
from pathlib import Path
import sys

from . import __version__
from .adb import ADB, SafetyError, discover, identity
from .engine import apply, audit, make_plan, restore, validate_plan
from .policy import DATA, load_profile, validate_profile
from .storage import device_lock, read_json, save_new


def output(value):
    print(json.dumps(value, indent=2, ensure_ascii=True))


def parser():
    p = argparse.ArgumentParser(prog="cleanmyxiaomi", description="Audit first. Only explicitly approved, device-tested changes can be applied.")
    p.add_argument("--version", action="version", version=__version__)
    p.add_argument("--adb", help="Explicit path to a trusted adb executable")
    p.add_argument("--serial", help="Exact USB device serial; never selected automatically")
    subs = p.add_subparsers(dest="command", required=True)
    subs.add_parser("doctor", help="Discover ADB and print official installation guidance")
    subs.add_parser("devices", help="List devices without selecting one")
    subs.add_parser("detect", help="Identify the selected device")
    subs.add_parser("profiles", help="List reviewed profiles and their limitations")
    check = subs.add_parser("validate-profile", help="Check schema only; does not approve a profile")
    check.add_argument("path")
    a = subs.add_parser("audit", help="Read-only device and package inventory")
    a.add_argument("--out", required=True)
    pplan = subs.add_parser("plan", help="Create a read-only dry run")
    pplan.add_argument("--profile", default="xiaomi-audit")
    pplan.add_argument("--out", required=True)
    dry = subs.add_parser("dry-run", help="Validate and display a saved plan without ADB")
    dry.add_argument("--plan", required=True)
    clean = subs.add_parser("cleanup", help="Apply only a reviewed, explicitly approved plan")
    clean.add_argument("--plan", required=True)
    clean.add_argument("--journal", required=True)
    clean.add_argument("--approve", required=True, help="Full SHA-256 of the plan approved by the user")
    clean.add_argument("--confirm-device", required=True)
    recover = subs.add_parser("restore", help="Preview restore by default; --apply requires fresh approval")
    recover.add_argument("--journal", required=True)
    recover.add_argument("--apply", action="store_true")
    recover.add_argument("--approve")
    recover.add_argument("--confirm-device")
    recover.add_argument("--out", help="Save a restore preview (not valid with --apply)")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "doctor":
            try:
                adb = discover(args.adb)
                version = ADB(adb).run("version", targeted=False)
                found = {"path": adb, "version": version}
            except SafetyError as exc:
                found = {"error": str(exc)}
            output({"python": sys.version.split()[0], "adb": found,
                    "official_download": "https://developer.android.com/tools/releases/platform-tools",
                    "guide": "docs/SETUP.md", "automatic_install": False})
            return 0 if "path" in found else 2
        if args.command == "profiles":
            registry = read_json(DATA / "registry.json")
            output([load_profile(name) for name in sorted(registry["profiles"])])
            return 0
        if args.command == "validate-profile":
            profile = validate_profile(read_json(args.path))
            output({"schema_valid": True, "profile": profile["id"], "approval_granted": False})
            return 0
        if args.command == "dry-run":
            envelope = read_json(args.plan)
            validate_plan(envelope)
            output(envelope)
            return 0
        adb = ADB(args.adb, args.serial)
        if args.command == "devices":
            output(adb.devices())
            return 0
        if args.serial is None:
            raise SafetyError("--serial is required; run devices to inspect the list")
        # All our sessions share a lock outside the checkout, including read-only audits.
        state_dir = Path.home() / ".cleanmyxiaomi" / "locks"
        with device_lock(args.serial, state_dir):
            if args.command == "detect":
                result = identity(adb)
            elif args.command == "audit":
                result = audit(adb)
                save_new(args.out, result)
            elif args.command == "plan":
                result = make_plan(adb, args.profile)
                save_new(args.out, result)
            elif args.command == "cleanup":
                result = apply(adb, read_json(args.plan), args.journal, args.approve, args.confirm_device)
            else:
                if args.apply and args.out:
                    raise SafetyError("--out is only supported for a restore preview")
                result = restore(adb, args.journal, args.approve, args.confirm_device, dry_run=not args.apply)
                if args.out:
                    save_new(args.out, result)
            output(result)
        return 0
    except (SafetyError, OSError, ValueError, KeyError, TypeError) as exc:
        output({"error": str(exc), "result": "stopped", "recovery": "Preserve any journal; see docs/RECOVERY.md. Do not blindly retry cleanup."})
        return 2
    except KeyboardInterrupt:
        output({"result": "interrupted", "recovery": "Preserve the journal; preview restore before making further changes."})
        return 130


if __name__ == "__main__":
    sys.exit(main())
