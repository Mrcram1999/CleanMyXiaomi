"""Local integrity envelopes and a durable, append-only operation journal."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path

from .adb import SafetyError, require


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def digest(data):
    return hashlib.sha256(canonical(data)).hexdigest()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result
    p = Path(path)
    require(p.stat().st_size < 16_000_000, "JSON file too large")
    try:
        return json.loads(p.read_text(encoding="utf-8"), object_pairs_hook=unique)
    except (ValueError, UnicodeError) as exc:
        raise SafetyError("Invalid JSON") from exc


def save_new(path, data):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def seal(data):
    return {"sha256": digest(data), "data": data}


def unseal(envelope):
    require(isinstance(envelope, dict) and set(envelope) == {"sha256", "data"}, "Invalid integrity envelope")
    require(digest(envelope["data"]) == envelope["sha256"], "File checksum mismatch")
    return envelope["data"]


@contextmanager
def device_lock(serial, state_dir):
    root = Path(state_dir)
    root.mkdir(parents=True, exist_ok=True)
    p = root / (hashlib.sha256(serial.encode()).hexdigest() + ".lock")
    try:
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise SafetyError(f"Device lock exists: {p}. Confirm no cleaner is running before removing a stale lock.") from exc
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(str(os.getpid()))
            stream.flush()
            os.fsync(stream.fileno())
        yield
    finally:
        p.unlink()


class Journal:
    def __init__(self, path, create=False):
        self.path = Path(path)
        if create:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(fd)
        self.events = self.read(self.path)

    @staticmethod
    def read(path):
        p = Path(path)
        require(p.stat().st_size < 16_000_000, "Journal too large")
        events = []
        previous = "0" * 64
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except ValueError as exc:
                raise SafetyError("Truncated journal; preserve it and use docs/RECOVERY.md") from exc
            require(set(event) == {"data", "previous", "sha256"}, "Invalid journal entry")
            require(event["previous"] == previous and digest({"data": event["data"], "previous": previous}) == event["sha256"],
                    "Journal hash chain mismatch")
            previous = event["sha256"]
            events.append(event)
        return events

    def append(self, data):
        previous = self.events[-1]["sha256"] if self.events else "0" * 64
        payload = {"data": data, "previous": previous}
        event = {**payload, "sha256": digest(payload)}
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        self.events.append(event)
