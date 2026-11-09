"""Append-only journal that returns only what changed since a cursor."""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

__version__ = "0.1.0"


def default_journal() -> Path:
    return Path.cwd() / ".deltacursor.jsonl"


def encode_cursor(seq: int) -> str:
    raw = json.dumps({"seq": seq}, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def decode_cursor(token: str) -> int:
    try:
        data = json.loads(base64.urlsafe_b64decode(token.encode("ascii")))
        return int(data["seq"])
    except Exception as exc:
        raise ValueError("invalid cursor") from exc


def read_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def append_event(path: Path, kind: str, body: dict | str) -> dict:
    events = read_events(path)
    seq = (events[-1]["seq"] + 1) if events else 1
    if isinstance(body, str):
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"text": body}
    else:
        payload = body
    event = {"seq": seq, "kind": kind, "body": payload}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, separators=(",", ":")) + "\n")
    return event


def since(path: Path, cursor: str | None) -> dict:
    events = read_events(path)
    start = decode_cursor(cursor) if cursor else 0
    new = [e for e in events if e["seq"] > start]
    last = events[-1]["seq"] if events else 0
    return {
        "events": new,
        "count": len(new),
        "cursor": encode_cursor(last),
        "from": start,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="deltacursor",
        description="Append-only journal that returns only what changed since a cursor.",
    )
    parser.add_argument("--journal", help="journal file (default: ./.deltacursor.jsonl)")
    parser.add_argument("--version", action="version", version=f"deltacursor {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="create an empty journal if it does not exist")

    p_append = sub.add_parser("append", help="append an event")
    p_append.add_argument("--kind", default="note")
    p_append.add_argument("body", help="JSON object or plain text")

    p_since = sub.add_parser("since", help="print events after a cursor (omit cursor for the full log)")
    p_since.add_argument("cursor", nargs="?", default=None)
    p_since.add_argument("--json", action="store_true")

    sub.add_parser("cursor", help="print the current cursor without events")

    args = parser.parse_args(argv)
    path = Path(args.journal) if args.journal else default_journal()
    try:
        if args.cmd == "init":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            print(f"journal {path}")
            print(f"cursor {encode_cursor(0)}")
            return 0
        if args.cmd == "append":
            event = append_event(path, args.kind, args.body)
            print(f"seq {event['seq']}")
            print(f"cursor {encode_cursor(event['seq'])}")
            return 0
        if args.cmd == "since":
            result = since(path, args.cursor)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"count {result['count']}")
                print(f"cursor {result['cursor']}")
                for event in result["events"]:
                    print(json.dumps(event, separators=(",", ":")))
            return 0
        if args.cmd == "cursor":
            events = read_events(path)
            last = events[-1]["seq"] if events else 0
            print(encode_cursor(last))
            return 0
        return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
