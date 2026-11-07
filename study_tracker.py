"""Local progress tracker for the five CompTIA Security+ SY0-701 domains."""
from __future__ import annotations
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DOMAINS = {
    "1": "General Security Concepts",
    "2": "Threats, Vulnerabilities, and Mitigations",
    "3": "Security Architecture",
    "4": "Security Operations",
    "5": "Security Program Management and Oversight",
}
STATUSES = {"not-started", "in-progress", "reviewed"}
DEFAULT_PATH = Path.home() / ".securityplus-study-progress.json"


def load_progress(path: str | Path = DEFAULT_PATH) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    domains = data.get("domains") if isinstance(data.get("domains"), dict) else {}
    return {"domains": domains}


def save_progress(data: dict[str, Any], path: str | Path = DEFAULT_PATH) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(target.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, target)


def set_status(domain: str, status: str, path: str | Path = DEFAULT_PATH) -> None:
    if domain not in DOMAINS:
        raise ValueError("Domain must be between 1 and 5.")
    if status not in STATUSES:
        raise ValueError(f"Status must be one of: {', '.join(sorted(STATUSES))}.")
    data = load_progress(path)
    current = data["domains"].get(domain, {})
    data["domains"][domain] = {
        "title": DOMAINS[domain],
        "status": status,
        "note": str(current.get("note", ""))[:500],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    save_progress(data, path)


def set_note(domain: str, note: str, path: str | Path = DEFAULT_PATH) -> None:
    if domain not in DOMAINS:
        raise ValueError("Domain must be between 1 and 5.")
    if len(note) > 500:
        raise ValueError("Notes are limited to 500 characters.")
    data = load_progress(path)
    current = data["domains"].get(domain, {})
    data["domains"][domain] = {
        "title": DOMAINS[domain],
        "status": current.get("status", "not-started"),
        "note": note,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    save_progress(data, path)


def render_progress(path: str | Path = DEFAULT_PATH) -> str:
    data = load_progress(path)
    rows = []
    reviewed = 0
    for key, title in DOMAINS.items():
        item = data["domains"].get(key, {})
        status = item.get("status", "not-started")
        if status == "reviewed":
            reviewed += 1
        rows.append(f"D{key} | {title} | {status} | {item.get('note', '')}")
    rows.append(f"\nProgress: {reviewed}/5 domains marked reviewed.")
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Track local Security+ SY0-701 study progress.")
    parser.add_argument("--file", default=str(DEFAULT_PATH), help="Progress file (default: in your home directory).")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("list", help="Show all domains and their progress.")
    p_set = sub.add_parser("set", help="Update a domain status.")
    p_set.add_argument("domain", choices=DOMAINS)
    p_set.add_argument("status", choices=sorted(STATUSES))
    p_note = sub.add_parser("note", help="Save a short revision note for a domain.")
    p_note.add_argument("domain", choices=DOMAINS)
    p_note.add_argument("text")
    args = parser.parse_args()
    try:
        if args.action == "set":
            set_status(args.domain, args.status, args.file)
        elif args.action == "note":
            set_note(args.domain, args.text, args.file)
        print(render_progress(args.file))
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
