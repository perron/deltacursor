# deltacursor

An append-only journal that returns only what changed since an opaque
cursor. Mid-loop agents should not reread a whole task list, test log, or
event file on every turn.

## Install

```bash
python3 -m pip install -e .
deltacursor --journal ./events.jsonl init
```

## 30-second example

```bash
deltacursor --journal ./events.jsonl init
# prints a cursor

deltacursor --journal ./events.jsonl append --kind test '{"passed": 3}'
deltacursor --journal ./events.jsonl append --kind test '{"passed": 4}'

deltacursor --journal ./events.jsonl since '<cursor-from-init>' --json
# two events, plus a new cursor

deltacursor --journal ./events.jsonl since '<new-cursor>' --json
# count 0 — nothing new
```

`since` is idempotent for a given cursor: calling it twice without a new
append returns the same empty set and the same cursor.

## Credit

Motivated by the mid-loop "return only the delta since the last cursor"
design note circulating in Nov 2026. Original JSONL journal; no source was
copied from any MCP server.
