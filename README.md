# deltacursor

An append-only journal that returns only what changed since an opaque
cursor. Mid-loop agents should not reread a whole task list, test log, or
event file on every turn.

## Install

Python 3.10 or later.

From a checkout:

```bash
python3 -m pip install .
python3 -m pip install -e ".[dev]"  # optional, for tests
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

## Limits

- The journal is a local JSONL file (default `./.deltacursor.jsonl`). It is not safe for concurrent writers.
- Cursors are opaque-looking encodings of a sequence number; they are not a security boundary.
- Invalid JSON or an event missing `seq` is an error and stops the read.
- `init` will not truncate an existing journal.

From GitHub you can also install with:

```bash
python3 -m pip install git+https://github.com/perron/deltacursor.git
```

This package is not published to PyPI.

## License

MIT. See `LICENSE`. Please read `SECURITY.md` before filing a vulnerability report.
